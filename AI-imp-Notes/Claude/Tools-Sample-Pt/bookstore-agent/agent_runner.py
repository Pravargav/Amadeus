"""Approach B -- the same tools via the Tool Runner. Ship this one.

The two halves still both exist on the wire; you just stop hand-maintaining the
schema. `@beta_tool` derives it from the signature, the type hints and the
docstring, and `tool_runner` owns the loop: it calls the API, spots tool_use
blocks, runs your function, feeds the tool_result back, and repeats.

Compare the line count with agent_manual.py. Everything deleted was loop
plumbing, not control -- the runner hands you each assistant message *before*
the tools run, so approval gates, logging and result rewriting are all still
available.

Run:  python agent_runner.py "do you have any Orwell?"
"""

import sys
from typing import Literal

import anthropic
from anthropic import beta_tool

import inventory
import tool_functions

MODEL = "claude-opus-5"

SYSTEM = (
    "You are the assistant for a small bookstore. Use the provided tools to answer "
    "questions about the catalog rather than guessing at titles, prices or stock. "
    "Quote prices in USD."
)


# The docstring is not a comment here -- it BECOMES the tool description and the
# per-property descriptions that Claude reads. Write it for the model: say when
# to call the tool, not only what it does. Type hints become the JSON types, and
# a default value makes the parameter optional in `required`.


@beta_tool
def search_books(query: str, max_results: int = 5) -> str:
    """Search the catalog by title or author for ISBNs, prices and stock counts.

    Call this whenever the user names a book or author but has not given you an
    ISBN -- the other tools require an ISBN.

    Args:
        query: Free-text title or author fragment, e.g. 'Orwell' or 'Algorithms'.
        max_results: How many matches to return. Defaults to 5.
    """
    return tool_functions.search_books(query, max_results)


@beta_tool
def check_stock(isbn: str) -> str:
    """Get the current price and on-hand stock count for a single ISBN.

    Call this before discussing availability or quoting a price, since catalog
    numbers change. Requires an exact ISBN -- use search_books to find one.

    Args:
        isbn: A 13-digit ISBN with no dashes, e.g. 9780451524935.
    """
    return tool_functions.check_stock(isbn)


@beta_tool
def place_order(isbn: str, quantity: Literal[1, 2, 3, 4, 5]) -> str:
    """Purchase copies of a book, decrementing store stock.

    Call this only when the user has clearly asked to buy a specific book. The
    user is asked to confirm before the order is committed, so a call may come
    back declined.

    Args:
        isbn: A 13-digit ISBN with no dashes.
        quantity: Number of copies to buy, 1 to 5.
    """
    # Literal[...] in the signature is what becomes "enum" in the JSON Schema --
    # a plain `int` hint cannot express a value range, so Claude would be free to
    # ask for 9999 copies and the check would fall to runtime.
    # Same gated implementation as the manual version -- the approval prompt is
    # inside tool_functions.place_order, which is exactly why the runner
    # executing tools automatically is safe here.
    return tool_functions.place_order(isbn, quantity)


TOOLS = [search_books, check_stock, place_order]


def run(user_input: str) -> str:
    client = anthropic.Anthropic()

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        thinking={"type": "adaptive"},
        tools=TOOLS,
        messages=[{"role": "user", "content": user_input}],
        max_iterations=10,
    )

    # `for message in runner` yields each assistant turn as it happens, which is
    # where you'd intervene. `runner.until_done()` is the shortcut when you only
    # want the final message.
    final = None
    for message in runner:
        for block in message.content:
            if block.type == "tool_use":
                print(f"  -> calling {block.name}({block.input})")
        final = message

    if final is None:
        return "(no response)"
    if final.stop_reason == "refusal":
        return f"Request declined: {final.stop_details}"
    return "".join(b.text for b in final.content if b.type == "text")


if __name__ == "__main__":
    inventory.init_db()
    prompt = " ".join(sys.argv[1:]) or "Do you have anything by Orwell, and how much is it?"
    print(f"> {prompt}\n")
    print(run(prompt))
