from anthropic.types import MessageParam

from core.claude import Claude
from core.tools import ToolManager
from mcp_client import MCPClient

SYSTEM_PROMPT = """You are the assistant for a ride-hailing app called RideShare.

Rules:
- Always call estimate_fares before book_ride; book_ride needs a quote_id from it.
- Before touching any file path, call list_allowed_folders. Paths outside those
  folders will be rejected, so never guess.
- Never book or cancel a ride without the user explicitly asking for that ride.
- Be brief. Report fares as INR figures.
"""

# Safety net: the loop below is driven by the model deciding to stop. A model
# that keeps calling tools forever would otherwise spin indefinitely.
MAX_TOOL_ITERATIONS = 10


class Chat:
    def __init__(self, claude_service: Claude, clients: dict[str, MCPClient]):
        self.claude_service = claude_service
        self.clients = clients
        # Conversation state lives here and persists across turns, which is
        # what makes "book the cheapest one" work as a follow-up.
        self.messages: list[MessageParam] = []

    async def _process_query(self, query: str):
        """Override hook: subclasses expand slash commands / @mentions here."""
        self.messages.append({"role": "user", "content": query})

    async def run(self, query: str, stream: bool = False, on_event=None) -> str:
        """The agentic tool loop.

        One user turn can drive many round trips: the model asks for tools, we
        run them, feed the results back, and ask again -- until it answers with
        text instead of a tool call.
        """
        await self._process_query(query)

        final_text = ""
        tools = await ToolManager.get_all_tools(self.clients)

        for _ in range(MAX_TOOL_ITERATIONS):
            if stream and on_event:
                response = await self.claude_service.chat_stream(
                    messages=self.messages,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                    on_event=on_event,
                )
            else:
                response = await self.claude_service.chat(
                    messages=self.messages,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                )

            # Append the raw Message so tool_use blocks survive intact.
            self.claude_service.add_assistant_message(self.messages, response)

            if response.stop_reason != "tool_use":
                final_text = self.claude_service.text_from_message(response)
                break

            if not stream:
                print(self.claude_service.text_from_message(response))

            # Tool execution happens HERE. Everything the server pushes back
            # during these calls -- logs, progress, sampling requests -- lands
            # while this await is outstanding.
            tool_results = await ToolManager.execute_tool_requests(
                self.clients, response
            )

            # Tool results re-enter the conversation as a USER turn. That is
            # what the Anthropic API expects, however odd it reads.
            self.claude_service.add_user_message(self.messages, tool_results)
        else:
            final_text = (
                f"\n[stopped after {MAX_TOOL_ITERATIONS} tool rounds]"
            )

        return final_text
