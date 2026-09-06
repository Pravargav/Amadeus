"""Terminal rendering for everything the SERVER pushes at us.

Kept separate from cli.py so main.py can hand these to MCPClient before the
CliApp exists (the client must be connected before the chat is built).
"""

import json

from pyboxen import boxen

# ANSI, deliberately raw so you can see exactly what is being emitted.
DIM = "\x1b[2m"
CYAN = "\x1b[36m"
YELLOW = "\x1b[33m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
RESET = "\x1b[0m"

LEVEL_COLOURS = {
    "debug": DIM,
    "info": CYAN,
    "notice": CYAN,
    "warning": YELLOW,
    "error": RED,
    "critical": RED,
}


async def render_server_log(params) -> None:
    """logging_callback -- handles `notifications/message`.

    Session-scoped: registered once on ClientSession and fires for every log
    notification from any tool call.
    """
    level = getattr(params, "level", "info")
    colour = LEVEL_COLOURS.get(level, CYAN)
    data = params.data
    if not isinstance(data, str):
        data = json.dumps(data)
    print(f"  {colour}[server:{level}]{RESET} {data}", flush=True)


async def render_progress(
    progress: float, total: float | None, message: str | None
) -> None:
    """progress_callback -- handles `notifications/progress`.

    Per-CALL, not per-session: passing this to call_tool() is what makes the
    SDK attach a progressToken, and without that token the server's
    report_progress() calls are silently discarded.
    """
    label = f" {message}" if message else ""

    if total:
        pct = (progress / total) * 100
        filled = int(pct / 5)
        bar = "#" * filled + "." * (20 - filled)
        print(
            f"  {GREEN}[{bar}]{RESET} {pct:5.1f}%{label}",
            flush=True,
        )
    else:
        print(f"  {GREEN}[progress]{RESET} {progress}{label}", flush=True)


def render_sampling_request(params) -> None:
    """Show the user exactly what the server is asking our model to do.

    A client that hides this is asking the user to pay for a prompt they have
    never seen.
    """
    lines = []
    if params.systemPrompt:
        lines.append(f"system: {params.systemPrompt}")
    for msg in params.messages:
        text = getattr(msg.content, "text", str(msg.content))
        if len(text) > 700:
            text = text[:700] + f"\n... [{len(text) - 700} more chars]"
        lines.append(f"{msg.role}: {text}")
    lines.append(f"\nmax_tokens: {params.maxTokens}")

    print(
        boxen(
            "\n".join(lines),
            title="Server requested LLM inference (sampling)",
            style="rounded",
            color="yellow",
            padding=0,
        )
    )


def render_tool_call(tool_name: str, args_json: str) -> None:
    """Render a tool_use block once its arguments have finished streaming."""
    try:
        formatted = json.dumps(json.loads(args_json), indent=2)
    except (json.JSONDecodeError, TypeError, ValueError):
        formatted = args_json or "{}"

    print(
        boxen(
            f"{tool_name}\n\nArguments:\n{formatted}",
            title="Tool Call",
            style="rounded",
            color="blue",
            padding=0,
        )
    )
