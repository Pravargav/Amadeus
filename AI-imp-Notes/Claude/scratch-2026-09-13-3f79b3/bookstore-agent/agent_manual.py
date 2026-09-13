"""Approach A -- hand-written schemas + a manual agentic loop.

Both halves are explicit here, which is why it's worth reading once even though
agent_runner.py is what you should actually ship:

    tool_schemas.ALL          -> sent to Claude
    tool_functions.REGISTRY   -> called by us, by name

Run:  python agent_manual.py "do you have any Orwell?"
"""

import sys

import anthropic

import inventory
import tool_functions
import tool_schemas

MODEL = "claude-opus-5"

SYSTEM = (
    "You are the assistant for a small bookstore. Use the provided tools to answer "
    "questions about the catalog rather than guessing at titles, prices or stock. "
    "Quote prices in USD."
)


def execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Dispatch one tool_use block. Returns (result_text, is_error)."""
    fn = tool_functions.REGISTRY.get(name)
    if fn is None:
        # Claude asked for a tool we published but cannot dispatch -- i.e. the
        # schema and the registry drifted apart.
        return f"Error: no implementation registered for tool {name!r}.", True
    try:
        # tool_input is already a parsed dict. Never string-match the raw JSON:
        # escaping of unicode and forward slashes varies between models.
        return fn(**tool_input), False
    except Exception as exc:
        # Hand the failure back as a tool_result with is_error=True so Claude
        # can correct course. Swallowing it or dropping the block breaks the
        # conversation -- every tool_use needs a matching tool_result.
        return f"{type(exc).__name__}: {exc}", True


def run(user_input: str) -> str:
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_input}]

    for _turn in range(10):  # bound the loop; never `while True` against a model
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM,
            thinking={"type": "adaptive"},
            tools=tool_schemas.ALL,
            messages=messages,
            # Server-side refusal fallback: if a safety classifier declines the
            # request, the server retries on another model instead of returning
            # an unusable turn.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )

        if response.stop_reason == "refusal":
            return f"Request declined: {response.stop_details}"

        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # Append the WHOLE content list, not just the text. It carries the
        # tool_use blocks (and thinking blocks) that the next request needs.
        messages.append({"role": "assistant", "content": response.content})

        # Claude may request several tools at once. Run them all and return
        # every result in ONE user message -- splitting them across messages
        # quietly teaches Claude to stop making parallel calls.
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"  -> calling {block.name}({block.input})")
            text, is_error = execute_tool(block.name, block.input)
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,  # must match the tool_use block
                    "content": text,
                    "is_error": is_error,
                }
            )

        messages.append({"role": "user", "content": results})

    return "Gave up after 10 turns."


if __name__ == "__main__":
    inventory.init_db()
    prompt = " ".join(sys.argv[1:]) or "Do you have anything by Orwell, and how much is it?"
    print(f"> {prompt}\n")
    print(run(prompt))
