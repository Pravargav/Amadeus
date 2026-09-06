"""Entry point.

    uv run main.py ./data [more folders...]

The folders you pass become the ROOTS -- the only places the server may read
or write. Everything else is wired here in dependency order.
"""

import asyncio
import os
import sys
from contextlib import AsyncExitStack

from dotenv import load_dotenv

from core.claude import Claude
from core.cli import CliApp
from core.cli_chat import CliChat
from core.sampling import SamplingHandler
from core.ui import render_progress, render_server_log
from mcp_client import MCPClient

load_dotenv()

claude_model = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
sampling_approval = os.getenv("SAMPLING_APPROVAL", "ask").lower()

assert claude_model, "CLAUDE_MODEL cannot be empty. Update .env"
assert anthropic_api_key, "ANTHROPIC_API_KEY cannot be empty. Update .env"


async def main():
    root_paths = sys.argv[1:]
    if not root_paths:
        print("Usage: uv run main.py <folder> [folder...]")
        print("Example: uv run main.py ./data")
        sys.exit(1)

    # 1. LLM access -- lives entirely on the client side.
    claude_service = Claude(model=claude_model)

    # 2. The sampling handler needs the LLM, so it is built second.
    sampling_handler = SamplingHandler(
        claude_service, auto_approve=(sampling_approval == "auto")
    )

    clients: dict[str, MCPClient] = {}

    async with AsyncExitStack() as stack:
        # 3. Connect. The callbacks passed here decide which capabilities this
        #    client advertises during initialize():
        #      roots    <- roots=...
        #      sampling <- sampling_handler=...
        #      logs     <- on_log=...
        #    on_progress is not a capability; it becomes the default per-call
        #    progress_callback, which is what emits a progressToken.
        ride_client = await stack.enter_async_context(
            MCPClient(
                command="uv",
                args=["run", "mcp_server.py"],
                roots=root_paths,
                sampling_handler=sampling_handler.handle,
                on_log=render_server_log,
                on_progress=render_progress,
            )
        )
        clients["rideshare"] = ride_client

        print("\nRideShare MCP  (mock)")
        print(f"model  : {claude_model}")
        print(f"roots  : {', '.join(root_paths)}")
        print(f"sampling approval: {sampling_approval}")

        # 4. Chat loop, then the REPL on top of it.
        chat = CliChat(
            doc_client=ride_client,
            clients=clients,
            claude_service=claude_service,
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()

    # Leaving the stack tears down the session, closes the pipes and
    # terminates the mcp_server.py subprocess.


if __name__ == "__main__":
    if sys.platform == "win32":
        # The default Windows event loop cannot spawn subprocesses, and this
        # app spawns one for the MCP server.
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
