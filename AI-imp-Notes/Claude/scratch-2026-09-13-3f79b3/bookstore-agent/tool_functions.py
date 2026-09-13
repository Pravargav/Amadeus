"""THE FUNCTION HALF.

Every function here runs in *your* process. Claude never executes any of this
and the API never sees it. All Claude ever does is send back a `tool_use` block
saying "call `place_order` with these arguments" -- turning that into a real
call is entirely your job (see agent_manual.py / agent_runner.py).

Because these are the things that actually happen, this is where the real-world
concerns live: input validation, error messages, and the approval gate on the
one tool that has side effects.
"""

import json

import inventory

# ---------------------------------------------------------------------------
# Approval gate.
#
# NOTE: the gate lives HERE, in the function -- not in the schema. A schema
# description saying "only call this after confirming with the user" is a
# suggestion to a language model, not an access control. Anything irreversible
# gets gated in code that Claude cannot talk its way past.
# ---------------------------------------------------------------------------


def _ask_terminal(prompt: str) -> bool:
    return input(f"\n[approval needed] {prompt} [y/N] ").strip().lower() == "y"


# Swap this out in tests (lambda _: True) or wire it to a real UI.
APPROVAL_HOOK = _ask_terminal


def search_books(query: str, max_results: int = 5) -> str:
    """Search the store's catalog by title or author."""
    results = inventory.search(query, limit=max_results)
    if not results:
        return f"No books matched {query!r}."
    return json.dumps(results, indent=2)


def check_stock(isbn: str) -> str:
    """Look up price and on-hand stock for one ISBN."""
    book = inventory.get_book(isbn)
    if book is None:
        # Returned as a normal string; the caller marks the tool_result
        # is_error=True so Claude knows to recover rather than trust it.
        raise KeyError(f"No book with ISBN {isbn}. Use search_books to find the ISBN first.")
    return json.dumps(
        {
            "isbn": book["isbn"],
            "title": book["title"],
            "price_usd": book["price"],
            "in_stock": book["stock"],
            "available": book["stock"] > 0,
        },
        indent=2,
    )


def place_order(isbn: str, quantity: int) -> str:
    """Buy copies of a book. Decrements stock -- this one is irreversible."""
    if quantity < 1:
        raise ValueError("quantity must be at least 1")

    book = inventory.get_book(isbn)
    if book is None:
        raise KeyError(f"No book with ISBN {isbn}.")

    cost = round(book["price"] * quantity, 2)
    approved = APPROVAL_HOOK(f"Order {quantity} x {book['title']!r} for ${cost:.2f}?")
    if not approved:
        # Returning a normal result (not raising) tells Claude the call was
        # understood and declined, so it reports back instead of retrying.
        return "The user declined this order. Do not retry it; ask what they'd like instead."

    order = inventory.record_order(isbn, quantity)
    return json.dumps(order, indent=2)


# Name -> function. This dict IS the link between the two halves: the string in
# the schema's "name" field has to be a key here, or the manual loop can't
# dispatch. Nothing checks that for you at startup.
REGISTRY = {
    "search_books": search_books,
    "check_stock": check_stock,
    "place_order": place_order,
}
