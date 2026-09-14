"""
test_multiple_tools.py - TESTING MULTIPLE TOOL USAGE

Run:  python test_multiple_tools.py

Same agent as agent.py, but with canned turns instead of input(), so you can
watch the pattern without typing. Each prompt is chosen to exercise one case.
"""

from helpers import add_user_message, print_flow
from tools import TOOL_REGISTRY, ALL_TOOLS, run_tool
from agent import run_turn

# --- sanity check the registry before spending any tokens ---
print("registered tools:", list(TOOL_REGISTRY))
print("schemas sent to Claude:", [t["name"] for t in ALL_TOOLS])

# --- the router is plain Python: test it with no API call at all ---
print("\nrouter, direct calls (free - no API involved):")
print(" ", run_tool("get_price", {"product": "laptop"}))
print(" ", run_tool("get_price", {"product": "banana"}))   # error path -> is_error
print(" ", run_tool("nope", {}))                           # unknown tool -> error


TURNS = [
    "What keyboards do you sell?",          # 1 tool  -> search_products
    "How much is it, and is it in stock?",  # 2 tools in ONE assistant message
    "Order 10 more of it.",                 # needs turns 1-2 for "it"
    "What's the price of a banana?",        # tool errors -> Claude recovers
]

messages = []

for i, turn in enumerate(TURNS, start=1):
    print(f"\n=== turn {i} ===")
    print("you >", turn)
    add_user_message(messages, turn)
    print("claude >", run_turn(messages))

print_flow(messages)

"""
What to look for in the output:

  turn 1  one tool_use block           -> inner loop runs once
  turn 2  TWO tool_use blocks in the same assistant message, answered by TWO
          tool_result blocks in a single user message
  turn 3  no new lookup needed for "it" - the history carries it
  turn 4  get_price raises KeyError -> router returns an "Error: ..." string
          with is_error=True -> Claude apologises instead of crashing

And the cost trap: every pass re-sends the entire history, so turn 4 pays for
turns 1-3 as input tokens too. That is why long tool loops get expensive, and
why prompt caching is the standard fix.
"""
