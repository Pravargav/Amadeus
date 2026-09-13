"""Demo 1 -- the WEB SEARCH tool (server-side).

    python demo_01_web_search.py "who won the 2026 Australian Open?"

Key idea: you write NO execution code. You declare the tool, and Anthropic runs
the searches on its own infrastructure. The searches, the results, and Claude's
answer all come back in the SAME response, as extra content blocks:

    server_tool_use  -> the query Claude ran (past tense -- it already ran)
    web_search_tool_result -> the results it got back
    text             -> the answer, with `citations` attached

So there is no tool_use/tool_result loop here. The only loop is `pause_turn`
(below), which is a continuation, not a tool execution.
"""

from __future__ import annotations

import sys

import anthropic

from pretty import show_response

MODEL = "claude-opus-5"

# Declared by type + name only, like every server tool.
#   web_search_20260209 -- current version; adds "dynamic filtering" (Claude
#     writes code server-side to filter results BEFORE they enter the context
#     window). Needs Opus 4.6+/Sonnet 4.6+. Do NOT also declare code_execution:
#     the filtering runs under the hood and a second sandbox confuses the model.
#   web_search_20250305 -- the older basic version, for older models (and the
#     only variant on Vertex AI).
WEB_SEARCH_TOOL = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 5,  # cap the searches per request; optional
    # "allowed_domains": ["arxiv.org"],   # allowlist ...
    # "blocked_domains": ["example.com"], # ... or blocklist. Never both.
    # "user_location": {"type": "approximate", "country": "IN", "timezone": "Asia/Kolkata"},
}

# The server runs its own sampling loop for server tools. If that loop hits its
# internal limit (10 iterations) you get stop_reason == "pause_turn" instead of
# a finished answer. Re-send to resume; cap the resumes so you can't spin.
MAX_RESUMES = 5


def main() -> None:
    question = " ".join(sys.argv[1:]) or (
        "What did Anthropic ship most recently, and when? Cite your sources."
    )

    client = anthropic.Anthropic()
    messages: list[dict] = [{"role": "user", "content": question}]

    for resume in range(MAX_RESUMES + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=16_000,
            thinking={"type": "adaptive"},
            tools=[WEB_SEARCH_TOOL],
            messages=messages,
        )
        show_response(response, label=f"turn {resume + 1}")

        if response.stop_reason != "pause_turn":
            break

        # Append the paused assistant turn and call again. Do NOT add a
        # "Continue." user message -- the API sees the trailing server_tool_use
        # block and resumes on its own.
        messages.append({"role": "assistant", "content": response.content})
        print("\n... paused mid-turn, resuming ...")
    else:
        print(f"\nGiving up: still paused after {MAX_RESUMES} resumes.")


if __name__ == "__main__":
    main()
