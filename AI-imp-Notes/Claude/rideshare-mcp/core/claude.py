from anthropic import AsyncAnthropic
from anthropic.types import Message


class Claude:
    """Thin wrapper over the Anthropic SDK.

    The client owns this object -- the MCP server never sees it. That is the
    whole premise of sampling: LLM access lives on this side of the wire.
    """

    def __init__(self, model: str):
        # Reads ANTHROPIC_API_KEY from the environment.
        self.client = AsyncAnthropic()
        self.model = model

    # ---------- message-list helpers ----------

    def add_user_message(self, messages: list, message):
        messages.append(
            {
                "role": "user",
                "content": message.content
                if isinstance(message, Message)
                else message,
            }
        )

    def add_assistant_message(self, messages: list, message):
        # Passing a full Message keeps its content blocks verbatim -- essential,
        # because the API requires tool_use blocks to survive into history
        # unchanged so the matching tool_result can be paired with them.
        messages.append(
            {
                "role": "assistant",
                "content": message.content
                if isinstance(message, Message)
                else message,
            }
        )

    def text_from_message(self, message: Message) -> str:
        return "\n".join(
            block.text for block in message.content if block.type == "text"
        )

    # ---------- inference ----------

    def _build_params(
        self,
        messages,
        system,
        temperature,
        stop_sequences,
        tools,
        max_tokens,
        thinking,
        thinking_budget,
    ) -> dict:
        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
        }
        # Only send optional keys when they have a value; the API rejects
        # several of them if passed as None.
        if stop_sequences:
            params["stop_sequences"] = stop_sequences
        if thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget,
            }
        if tools:
            params["tools"] = tools
        if system:
            params["system"] = system
        return params

    async def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=None,
        tools=None,
        max_tokens=8000,
        thinking=False,
        thinking_budget=1024,
    ) -> Message:
        """Non-streaming call. Used by the sampling handler."""
        params = self._build_params(
            messages,
            system,
            temperature,
            stop_sequences,
            tools,
            max_tokens,
            thinking,
            thinking_budget,
        )
        return await self.client.messages.create(**params)

    async def chat_stream(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=None,
        tools=None,
        max_tokens=8000,
        thinking=False,
        thinking_budget=1024,
        on_event=None,
    ) -> Message:
        """Streaming call. Used by the interactive chat loop."""
        params = self._build_params(
            messages,
            system,
            temperature,
            stop_sequences,
            tools,
            max_tokens,
            thinking,
            thinking_budget,
        )

        async with self.client.messages.stream(**params) as stream:
            # The iterator must be drained even with no callback -- the stream
            # cannot assemble a final Message from a partially-read response.
            async for event in stream:
                if on_event:
                    await on_event(event)

            return await stream.get_final_message()
