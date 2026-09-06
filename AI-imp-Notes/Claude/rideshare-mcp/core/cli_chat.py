"""Adds prompts and resources to the plain Chat loop.

Two user-facing conventions:

  /plan_trip Home "Airport T2"   -> fetch an MCP PROMPT and inject it
  @drivers                       -> read an MCP RESOURCE and inline its text

Both are *user-driven*. That is the distinction the exam cares about:
  tools     -> the MODEL decides to call them
  prompts   -> the USER invokes them
  resources -> the USER (or client) attaches them as context
"""

import json
import shlex
from typing import List

from anthropic.types import MessageParam
from mcp.types import Prompt, PromptMessage

from core.chat import Chat
from core.claude import Claude
from mcp_client import MCPClient


class CliChat(Chat):
    def __init__(
        self,
        doc_client: MCPClient,
        clients: dict[str, MCPClient],
        claude_service: Claude,
    ):
        super().__init__(clients=clients, claude_service=claude_service)
        # The server designated as the source of prompts and resources.
        self.doc_client = doc_client

    # ---------- prompts ----------

    async def list_prompts(self) -> list[Prompt]:
        return await self.doc_client.list_prompts()

    async def get_prompt(self, name: str, args: dict[str, str]) -> list[PromptMessage]:
        return await self.doc_client.get_prompt(name, args)

    async def _expand_slash_command(self, query: str) -> str | None:
        """Turn `/name arg1 arg2` into the prompt text the server returns.

        Arguments are mapped POSITIONALLY onto the prompt's declared argument
        names, which we learn from prompts/list.
        """
        parts = shlex.split(query[1:])
        if not parts:
            return None

        name, values = parts[0], parts[1:]
        prompts = {p.name: p for p in await self.list_prompts()}

        if name not in prompts:
            return None

        arg_names = [a.name for a in (prompts[name].arguments or [])]
        args = dict(zip(arg_names, values))

        missing = [a for a in arg_names if a not in args]
        if missing:
            raise ValueError(
                f"/{name} needs: {', '.join(arg_names)} (missing {', '.join(missing)})"
            )

        messages = await self.get_prompt(name, args)
        return "\n\n".join(
            m.content.text
            for m in messages
            if getattr(m.content, "type", None) == "text"
        )

    # ---------- resources ----------

    async def _expand_mentions(self, query: str) -> str:
        """Replace every @token with the contents of rideshare://<token>."""
        blocks = []
        for word in query.split():
            if not word.startswith("@") or len(word) < 2:
                continue
            uri = f"rideshare://{word[1:]}"
            try:
                content = await self.doc_client.read_resource(uri)
            except Exception as exc:
                blocks.append(f"<resource uri='{uri}' error='{exc}'/>")
                continue
            if not isinstance(content, str):
                content = json.dumps(content, indent=2)
            blocks.append(f"<resource uri='{uri}'>\n{content}\n</resource>")

        if not blocks:
            return query
        return query + "\n\n" + "\n".join(blocks)

    # ---------- the override ----------

    async def _process_query(self, query: str):
        if query.startswith("/"):
            expanded = await self._expand_slash_command(query)
            if expanded is not None:
                self.messages.append({"role": "user", "content": expanded})
                return

        query = await self._expand_mentions(query)
        self.messages.append({"role": "user", "content": query})


# ---------------------------------------------------------------------------
# MCP PromptMessage -> Anthropic MessageParam
#
# Only needed if you want to inject a multi-turn prompt verbatim instead of
# flattening it to text. Content may arrive as a dict OR a pydantic object,
# hence the paired .get()/getattr() branches.
# ---------------------------------------------------------------------------
def convert_prompt_message_to_message_param(
    prompt_message: PromptMessage,
) -> MessageParam:
    role = "assistant" if prompt_message.role == "assistant" else "user"
    content = prompt_message.content

    def field(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    if field(content, "type") == "text":
        return {"role": role, "content": field(content, "text", "")}

    if isinstance(content, list):
        blocks = [
            {"type": "text", "text": field(item, "text", "")}
            for item in content
            if field(item, "type") == "text"
        ]
        if blocks:
            return {"role": role, "content": blocks}

    return {"role": role, "content": ""}


def convert_prompt_messages_to_message_params(
    prompt_messages: List[PromptMessage],
) -> List[MessageParam]:
    return [convert_prompt_message_to_message_param(m) for m in prompt_messages]
