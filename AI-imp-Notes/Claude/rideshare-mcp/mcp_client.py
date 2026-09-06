"""MCP client with roots, sampling and notification handling wired up.

Everything the server can ask US for is registered in connect(). The set of
callbacks passed to ClientSession() literally determines the capabilities this
client advertises during initialize() -- omit a callback and the matching
server-side call fails.
"""

import json
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.shared.context import RequestContext
from mcp.types import ErrorData, ListRootsResult, Root
from pydantic import AnyUrl, FileUrl


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
        roots: Optional[list[str]] = None,
        sampling_handler=None,
        on_log=None,
        on_progress=None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._roots = self._create_roots(roots) if roots else []
        self._sampling_handler = sampling_handler
        self._on_log = on_log
        self._on_progress = on_progress
        self._session: Optional[ClientSession] = None
        self._exit_stack = AsyncExitStack()

    # ------------------------------------------------------------------
    # ROOTS
    # ------------------------------------------------------------------
    def _create_roots(self, root_paths: list[str]) -> list[Root]:
        """Turn CLI path strings into protocol Root objects.

        resolve() first: roots must be absolute, and resolving here means the
        server receives canonical paths with no ".." segments left in them.
        """
        roots = []
        for path in root_paths:
            p = Path(path).resolve()
            if not p.is_dir():
                raise ValueError(f"Root is not a directory: {p}")
            roots.append(Root(uri=FileUrl(p.as_uri()), name=p.name or str(p)))
        return roots

    async def _handle_list_roots(
        self, context: RequestContext["ClientSession", None]
    ) -> ListRootsResult | ErrorData:
        """Served on demand: the SERVER calls this, not us.

        Because it is answered live rather than sent once at startup, the
        server can never act on a stale whitelist.
        """
        return ListRootsResult(roots=self._roots)

    # ------------------------------------------------------------------
    # CONNECTION
    # ------------------------------------------------------------------
    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )

        # Spawns the server as a child process and hands back its pipes.
        read, write = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        self._session = await self._exit_stack.enter_async_context(
            ClientSession(
                read,
                write,
                # roots capability     <- only advertised if we have roots
                list_roots_callback=self._handle_list_roots
                if self._roots
                else None,
                # sampling capability  <- only advertised if we can run an LLM
                sampling_callback=self._sampling_handler,
                # log notifications    <- session-scoped, one handler for all calls
                logging_callback=self._on_log,
            )
        )

        await self._session.initialize()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError("Not connected. Call connect() first.")
        return self._session

    # ------------------------------------------------------------------
    # CLIENT -> SERVER PRIMITIVES
    # ------------------------------------------------------------------
    async def list_tools(self) -> list[types.Tool]:
        return (await self.session().list_tools()).tools

    async def call_tool(
        self, tool_name: str, tool_input: dict, progress_callback=None
    ) -> types.CallToolResult | None:
        """Invoke a tool.

        progress_callback is PER CALL -- passing it is what makes the SDK put a
        progressToken in the request's _meta, and that token is the server's
        permission to emit notifications/progress. No token, no progress.
        """
        return await self.session().call_tool(
            tool_name,
            tool_input,
            progress_callback=progress_callback or self._on_progress,
        )

    async def list_prompts(self) -> list[types.Prompt]:
        return (await self.session().list_prompts()).prompts

    async def get_prompt(self, prompt_name: str, args: dict[str, str]):
        return (await self.session().get_prompt(prompt_name, args)).messages

    async def list_resources(self) -> list[types.Resource]:
        return (await self.session().list_resources()).resources

    async def read_resource(self, uri: str) -> Any:
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)
            return resource.text
        return None

    # ------------------------------------------------------------------
    # LIFECYCLE
    # ------------------------------------------------------------------
    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
