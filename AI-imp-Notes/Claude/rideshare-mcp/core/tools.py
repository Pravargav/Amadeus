"""Adapter between MCP tools and the Anthropic tool-use API."""

import json
from typing import List, Literal, Optional

from anthropic.types import Message, ToolResultBlockParam
from mcp.types import CallToolResult, TextContent, Tool

from mcp_client import MCPClient


class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[dict]:
        """Collect every tool from every connected server, in Anthropic's shape.

        The only real work here is the key rename: MCP calls it `inputSchema`,
        Anthropic calls it `input_schema`. That one line is the whole adapter.
        """
        tools = []
        for client in clients.values():
            for t in await client.list_tools():
                tools.append(
                    {
                        "name": t.name,
                        "description": t.description,
                        "input_schema": t.inputSchema,
                    }
                )
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list[MCPClient], tool_name: str
    ) -> Optional[MCPClient]:
        """Routing: which server owns this tool name?"""
        for client in clients:
            tools = await client.list_tools()
            if any(t.name == tool_name for t in tools):
                return client
        return None

    @classmethod
    def _build_tool_result_part(
        cls,
        tool_use_id: str,
        text: str,
        status: Literal["success", "error"],
    ) -> ToolResultBlockParam:
        """`tool_use_id` MUST echo the model's tool_use.id or the API rejects
        the turn. `is_error` tells the model the call failed so it can adapt
        instead of treating an error string as data."""
        return {
            "tool_use_id": tool_use_id,
            "type": "tool_result",
            "content": text,
            "is_error": status == "error",
        }

    @classmethod
    async def execute_tool_requests(
        cls, clients: dict[str, MCPClient], message: Message
    ) -> List[ToolResultBlockParam]:
        """Run every tool_use block in the model's reply, in order.

        Returns one tool_result block per tool_use block -- the API requires
        that pairing to be exact.
        """
        tool_requests = [b for b in message.content if b.type == "tool_use"]
        results: list[ToolResultBlockParam] = []

        for request in tool_requests:
            client = await cls._find_client_with_tool(
                list(clients.values()), request.name
            )

            if client is None:
                results.append(
                    cls._build_tool_result_part(
                        request.id,
                        f"No connected server provides a tool named '{request.name}'",
                        "error",
                    )
                )
                continue

            try:
                output: CallToolResult | None = await client.call_tool(
                    request.name, request.input
                )
                texts = [
                    item.text
                    for item in (output.content if output else [])
                    if isinstance(item, TextContent)
                ]
                results.append(
                    cls._build_tool_result_part(
                        request.id,
                        json.dumps(texts),
                        "error" if output and output.isError else "success",
                    )
                )
            except Exception as exc:
                # A raised exception is ALWAYS an error. (The version of this
                # file in the roots demo checks `output.isError` here, but
                # output is None on this path, so real failures were being
                # reported to the model as successes.)
                message_text = f"Error executing tool '{request.name}': {exc}"
                print(f"  {message_text}")
                results.append(
                    cls._build_tool_result_part(
                        request.id,
                        json.dumps({"error": message_text}),
                        "error",
                    )
                )

        return results
