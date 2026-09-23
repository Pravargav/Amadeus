"""THE SCHEMA HALF.

Pure data. This is the only thing about our tools that Claude ever sees -- it
gets serialized into the prompt on every single request (and is therefore billed
as input tokens every time).

Nothing here executes. These dicts describe a contract; tool_functions.py
honours it. If the two disagree, you find out at runtime.

Note what the descriptions do: they say *when* to call, not just what the tool
is. Recent Opus models reach for tools conservatively, so explicit trigger
conditions measurably raise the should-call rate.
"""

SEARCH_BOOKS = {
    "name": "search_books",  
    "description": (
        "Search the bookstore catalog by title or author, returning ISBNs, prices "
        "and stock counts. Call this whenever the user names a book or author but "
        "has not given you an ISBN -- the other tools require an ISBN."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free-text title or author fragment, e.g. 'Orwell' or 'Algorithms'.",
            },
            "max_results": {
                "type": "integer",
                "description": "How many matches to return. Defaults to 5.",
            },
        },
        "required": ["query"],  
        "additionalProperties": False,
    },
    "strict": True,
}

CHECK_STOCK = {
    "name": "check_stock",
    "description": (
        "Get the current price and on-hand stock count for a single ISBN. Call this "
        "before discussing availability or quoting a price, since catalog numbers "
        "change. Requires an exact ISBN -- use search_books to find one."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "isbn": {
                "type": "string",
                "description": "A 13-digit ISBN with no dashes, e.g. 9780451524935.",
            }
        },
        "required": ["isbn"],
        "additionalProperties": False,
    },
    "strict": True,
}

PLACE_ORDER = {
    "name": "place_order",
    "description": (
        "Purchase copies of a book, decrementing store stock. Call this only when "
        "the user has clearly asked to buy a specific book. The user is asked to "
        "confirm before the order is committed, so a call may come back declined."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "isbn": {
                "type": "string",
                "description": "A 13-digit ISBN with no dashes.",
            },
            "quantity": {
                "type": "integer",
                "enum": [1, 2, 3, 4, 5],
                "description": "Number of copies to buy, 1 to 5.",
            },
        },
        "required": ["isbn", "quantity"],
        "additionalProperties": False,
    },
    "strict": True,
}

ALL = [SEARCH_BOOKS, CHECK_STOCK, PLACE_ORDER]
