"""The client side of MCP sampling.

The server asks; this runs the inference and hands back a completion. Three
responsibilities, in order:

  1. Show the user the prompt and get consent  (the server is spending THEIR money)
  2. Translate MCP's SamplingMessage -> Anthropic message dicts
  3. Honour the request's parameters: systemPrompt, maxTokens, temperature, stopSequences
"""

import asyncio

from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    ErrorData,
    TextContent,
)

from core.claude import Claude
from core.ui import RED, RESET, render_sampling_request

# JSON-RPC "request cancelled / rejected by user"
USER_REJECTED = -32001


class SamplingHandler:
    def __init__(self, claude_service: Claude, auto_approve: bool = False):
        self.claude = claude_service
        self.auto_approve = auto_approve

    # ---------- 2. translation ----------

    @staticmethod
    def to_anthropic_messages(
        sampling_messages,
    ) -> list[dict]:
        """MCP SamplingMessage -> Anthropic {"role", "content"}.

        MCP's message type is deliberately vendor-neutral, so somebody has to
        do this conversion -- and it has to be the client, because the client
        is the one that picked the vendor.
        """
        messages = []
        for msg in sampling_messages:
            if msg.role not in ("user", "assistant"):
                continue
            if msg.content.type != "text":
                # Non-text content (images, audio) would need a per-provider
                # mapping. Raising beats silently dropping it.
                raise ValueError(
                    f"Unsupported sampling content type: {msg.content.type}"
                )
            messages.append({"role": msg.role, "content": msg.content.text})

        if not messages:
            raise ValueError("Sampling request contained no usable messages")
        return messages

    # ---------- 1. consent ----------

    async def _approved(self, params: CreateMessageRequestParams) -> bool:
        render_sampling_request(params)

        if self.auto_approve:
            print(f"  {RED}(auto-approved: SAMPLING_APPROVAL=auto){RESET}\n")
            return True

        # to_thread keeps the blocking input() off the event loop, so the
        # still-open tools/call request does not time out while we wait.
        answer = await asyncio.to_thread(
            input, "  Allow this inference? [y/N] "
        )
        print()
        return answer.strip().lower() in ("y", "yes")

    # ---------- the callback itself ----------

    async def handle(
        self, context, params: CreateMessageRequestParams
    ) -> CreateMessageResult | ErrorData:
        """Registered as ClientSession(sampling_callback=...).

        Registering it is what makes this client advertise the `sampling`
        capability during initialize(). A server can only sample if the client
        opted in here.
        """
        if not await self._approved(params):
            # Returning ErrorData (rather than raising) sends a clean JSON-RPC
            # error back, so the server's create_message() raises and its tool
            # can handle the refusal gracefully.
            return ErrorData(
                code=USER_REJECTED,
                message="The user declined the sampling request.",
            )

        try:
            messages = self.to_anthropic_messages(params.messages)
        except ValueError as exc:
            return ErrorData(code=-32602, message=str(exc))

        # 3. Honour the server's parameters. Forgetting systemPrompt here is
        #    the most common sampling bug -- the server's instructions are
        #    silently dropped and the answer comes back in the wrong voice.
        message = await self.claude.chat(
            messages=messages,
            system=params.systemPrompt,
            max_tokens=params.maxTokens,
            temperature=params.temperature
            if params.temperature is not None
            else 1.0,
            stop_sequences=params.stopSequences,
        )

        # params.modelPreferences carries the server's cost/speed/intelligence
        # hints. We ignore them and use the configured model -- but we report
        # back which model actually ran, because the server could not choose.
        return CreateMessageResult(
            role="assistant",
            model=self.claude.model,
            stopReason=message.stop_reason,
            content=TextContent(
                type="text", text=self.claude.text_from_message(message)
            ),
        )
