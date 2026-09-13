"""Demo 3 -- both tools in ONE loop: research on the web, then write a file.

    python demo_03_both.py
    python demo_03_both.py "compare SQLite and DuckDB for analytics"

This is where the distinction pays off. Both tools are declared side by side in
the same `tools` list, but the loop only implements ONE of them:

    web_search (server-side)   -> nothing to execute; results arrive inline
    str_replace_based_edit_tool -> we execute it and return a tool_result

The loop therefore branches on `stop_reason`, not on tool name:

    "pause_turn" -> server tool is mid-flight; re-send to resume, add no user message
    "tool_use"   -> a client tool is pending; execute it, append ONE user message
    anything else-> Claude is finished
"""

from __future__ import annotations

import sys
from pathlib import Path

import anthropic

from demo_01_web_search import WEB_SEARCH_TOOL
from demo_02_text_editor import TEXT_EDITOR_TOOL, run_tools
from editor_backend import TextEditorBackend
from pretty import RULE, show_response

MODEL = "claude-opus-5"
SANDBOX = Path(__file__).parent / "sandbox"

SYSTEM = (
    "You are a research assistant with two tools.\n"
    "- web_search: use it to gather current facts. Anthropic runs it for you.\n"
    "- str_replace_based_edit_tool: use it to write files into a sandbox. "
    "Paths are relative to the sandbox root, e.g. '/report.md'.\n"
    "Research first, then write the file. Keep the report under 300 words and "
    "include a Sources section with the URLs you actually used."
)

MAX_STEPS = 15


def main() -> None:
    topic = " ".join(sys.argv[1:]) or "the current state of small on-device LLMs"
    task = f"Research {topic}, then write your findings to /report.md."

    backend = TextEditorBackend(SANDBOX)
    client = anthropic.Anthropic()
    messages: list[dict] = [{"role": "user", "content": task}]

    for step in range(1, MAX_STEPS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=16_000,
            system=SYSTEM,
            thinking={"type": "adaptive"},
            tools=[WEB_SEARCH_TOOL, TEXT_EDITOR_TOOL],
            messages=messages,
        )
        show_response(response, label=f"step {step}")

        # Always preserve the assistant turn verbatim: it may hold thinking
        # blocks, pending tool_use blocks, and already-completed web search
        # results, and the API needs all of them on the next request.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "pause_turn":
            # Server-side tool loop hit its internal limit. Resume by re-sending;
            # deliberately no user message here.
            print("\n... server tool paused, resuming ...")
            continue

        if response.stop_reason != "tool_use":
            break

        # A client-side tool is waiting on us -- this is the only branch that
        # executes anything locally.
        messages.append({"role": "user", "content": run_tools(backend, response)})
    else:
        print(f"\nStopped after {MAX_STEPS} steps without finishing.")

    report = SANDBOX / "report.md"
    if report.exists():
        print(f"\n{RULE}\nsandbox/report.md\n{RULE}")
        print(report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
