"""Makes the two halves visible. No API key and no network needed.

    python show_schemas.py

Prints, for each tool:
  1. the hand-written schema  (tool_schemas.py)      -- what Claude sees
  2. the auto-derived schema  (agent_runner.py)      -- same wire format
  3. the function's actual return value              -- what Claude never sees

Point 3 is the one worth staring at: the functions run perfectly well with no
model in the loop at all. Claude is a caller, not a runtime.
"""

import json

import agent_runner  # decorated tools
import inventory
import tool_functions
import tool_schemas

RULE = "=" * 78


def banner(text: str) -> None:
    print(f"\n{RULE}\n{text}\n{RULE}")


def main() -> None:
    inventory.init_db()

    hand_written = {t["name"]: t for t in tool_schemas.ALL}
    derived = {t.name: t.to_dict() for t in agent_runner.TOOLS}

    for name in hand_written:
        banner(f"TOOL: {name}")

        print("\n-- SCHEMA, hand-written (tool_schemas.py) " + "-" * 34)
        print(json.dumps(hand_written[name], indent=2))

        print("\n-- SCHEMA, derived from the function by @beta_tool " + "-" * 26)
        print(json.dumps(derived[name], indent=2))

        print("\n-- FUNCTION, called directly with no Claude involved " + "-" * 24)
        fn = tool_functions.REGISTRY[name]
        if name == "search_books":
            print("tool_functions.search_books('Orwell', 2) ->")
            print(fn("Orwell", 2))
        elif name == "check_stock":
            print("tool_functions.check_stock('9781449355739') ->")
            print(fn("9781449355739"))
        else:
            print("tool_functions.place_order('9780451524935', 2) ->")
            # Auto-decline so this stays non-interactive and orders nothing.
            tool_functions.APPROVAL_HOOK = lambda _prompt: False
            print(fn("9780451524935", 2))

    banner("WHERE THEY DIFFER")
    print(
        """
Same wire format, and almost the same content. Two differences worth knowing:

  * "strict": true  is absent from the derived schemas. It is a top-level tool
    field rather than part of input_schema, so there is nothing in a function
    signature for the decorator to read it from. Add it by hand if you need the
    exact-validation guarantee.

  * "title" per property is present only in the derived schemas. The API
    ignores it; you just pay a handful of input tokens for it on every request.

Note that place_order's "enum": [1,2,3,4,5] DID survive, because the signature
says `quantity: Literal[1, 2, 3, 4, 5]`. A plain `int` hint would have produced
an unbounded integer and pushed that check out to runtime -- the type hint is
doing real prompt-level work, not just documentation.

Everything else the decorator gets right for free, and unlike a hand-written
dict it cannot drift away from the function it describes.
"""
    )


if __name__ == "__main__":
    main()
