"""Demo 2 -- the TEXT EDITOR tool (client-side) and the tool_use/tool_result loop.

    python demo_02_text_editor.py
    python demo_02_text_editor.py "add a Risks section to notes.md"

Key idea: this is the opposite of demo 1. Claude cannot touch your filesystem.
It returns a `tool_use` block describing the edit it wants; YOUR code performs
it and hands back a `tool_result` block carrying the same `tool_use_id`. Repeat
until Claude stops asking. That is the agentic loop, and it is only ~20 lines:

    create  ->  stop_reason == "tool_use"?  ->  execute  ->  append tool_result
      ^                                                              |
      +--------------------------------------------------------------+

Four invariants the loop must respect (each one is a real bug if you skip it):
  1. Append the WHOLE `response.content`, not just the text. The tool_use and
     thinking blocks have to survive the round trip.
  2. Every `tool_result` echoes the matching `tool_use_id`.
  3. All results from one assistant turn go back in ONE user message. Splitting
     them silently teaches Claude to stop calling tools in parallel.
  4. A failed tool still returns a `tool_result`, with `is_error: True`.
     Dropping it breaks the transcript; Claude cannot recover from a hole.
"""

from __future__ import annotations

import sys
from pathlib import Path

import anthropic

from editor_backend import EditorError, TextEditorBackend
from pretty import RULE, show_response

MODEL = "claude-opus-5"
SANDBOX = Path(__file__).parent / "sandbox"

# Anthropic-defined and SCHEMA-LESS: type + name only, never an input_schema.
# The name is fixed -- "str_replace_based_edit_tool" is what the model was
# trained on. A custom tool you happen to name the same thing is a DIFFERENT
# tool with none of the built-in behaviour.
TEXT_EDITOR_TOOL = {
    "type": "text_editor_20250728",
    "name": "str_replace_based_edit_tool",
    "max_characters": 10_000,  # optional: caps `view` output
}

SYSTEM = (
    "You edit files in a small sandbox using the text editor tool. "
    "Paths are relative to the sandbox root, e.g. '/notes.md'. "
    "Always `view` a file before editing it so your `old_str` matches exactly. "
    "When the task is done, summarise what you changed in one or two sentences."
)

MAX_TURNS = 12


def main() -> None:
    task = " ".join(sys.argv[1:]) or (
        "Read /notes.md. Fix the two factual errors marked with TODO, then add a "
        "short 'Summary' section at the end."
    )

    backend = TextEditorBackend(SANDBOX)
    client = anthropic.Anthropic()
    messages: list[dict] = [{"role": "user", "content": task}]

    for turn in range(1, MAX_TURNS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=16_000,
            system=SYSTEM,
            thinking={"type": "adaptive"},
            tools=[TEXT_EDITOR_TOOL],
            messages=messages,
        )
        show_response(response, label=f"turn {turn}")

        # Claude is done talking and wants nothing from us.
        if response.stop_reason != "tool_use":
            break

        # Invariant 1: the full content list goes back, tool_use blocks included.
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": run_tools(backend, response)})
    else:
        print(f"\nStopped after {MAX_TURNS} turns without an end_turn.")

    print(f"\n{RULE}\nsandbox/ now contains:")
    for path in sorted(SANDBOX.rglob("*")):
        print(f"  {path.relative_to(SANDBOX).as_posix()}")


def run_tools(backend: TextEditorBackend, response) -> list[dict]:
    """Execute every tool_use block in one assistant turn.

    Invariant 3: one list, returned as one user message -- even when Claude
    asked for several edits at once.
    """
    results: list[dict] = []

    for block in response.content:
        if block.type != "tool_use":
            continue

        try:
            output = backend.run(block.input)
            print(f"     <- ok: {output}")
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,  # Invariant 2
                    "content": output,
                }
            )
        except EditorError as exc:
            # Invariant 4: an error is a normal tool_result, just flagged.
            print(f"     <- error: {exc}")
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Error: {exc}",
                    "is_error": True,
                }
            )

    return results


if __name__ == "__main__":
    main()
