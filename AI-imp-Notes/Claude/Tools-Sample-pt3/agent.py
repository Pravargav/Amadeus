"""
agent.py - THE MULTI-TURN TOOL PATTERN + THE CONVERSATION LOOP

Run:  python agent.py          (type 'quit' to exit)

There are TWO loops, and mixing them up is the classic beginner mistake:

    OUTER loop  = conversation turns. One pass per human message.
    INNER loop  = the tool loop. Runs as long as Claude keeps asking for
                  tools within a single turn. Can run 0, 1 or many times.

    while user keeps talking:                 <- OUTER (multi-turn)
        add_user_message(...)
        while response.stop_reason == "tool_use":     <- INNER (tool loop)
            run tools, send tool_results
        print the text answer

`messages` is never reset. It is the only state in the program: the whole
history goes back to the API on every single call, which is what makes
turn 3 able to refer to something a tool returned in turn 1.
"""

from helpers import (
    add_user_message,
    add_assistant_message,
    chat,
    text_from,
    wants_tool,
    tool_use_blocks,
    print_flow,
)
from tools import ALL_TOOLS, run_tool_block

SYSTEM = "You are a shop assistant. Use the tools to answer; never guess prices or stock."


def run_turn(messages, verbose=True):
    """One human turn: keep calling tools until Claude produces a real answer."""

    while True:
        response = chat(messages, tools=ALL_TOOLS, system=SYSTEM)

        # Keep the assistant's whole multi-block turn - text AND tool_use.
        add_assistant_message(messages, response.content)

        # DETECTING TOOL REQUESTS: stop_reason is the only thing you branch on.
        if not wants_tool(response):
            return text_from(response)          # "end_turn" -> turn is over

        # HANDLING MULTIPLE TOOL CALLS: one tool_result per tool_use block...
        results = []
        for block in tool_use_blocks(response):
            if verbose:
                print(f"   [tool] {block.name}({block.input})")
            results.append(run_tool_block(block))   # -> TOOL RESULT BLOCK

        # ...all of them in ONE user message, immediately after.
        add_user_message(messages, results)
        # loop again: Claude now sees the results and may ask for more tools


def main():
    messages = []          # <- the single source of truth, never cleared

    print("Shop assistant. Try:")
    print("  what keyboards do you sell?")
    print("  how much is it and do we have stock?      <- 'it' needs turn 1")
    print("  order 10 more                             <- needs turns 1 and 2")
    print("  (type 'quit' to exit, 'flow' to print the message flow)\n")

    while True:                                  # OUTER: multi-turn
        user_input = input("you > ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if user_input.lower() == "flow":
            print_flow(messages)
            continue

        add_user_message(messages, user_input)
        answer = run_turn(messages)              # INNER lives in here
        print("claude >", answer, "\n")

    print_flow(messages)


if __name__ == "__main__":
    main()

"""
UNDERSTANDING THE MESSAGE FLOW - a 2-turn conversation ends up like this:

  0  user       "what keyboards do you sell?"
  1  assistant  text + tool_use(search_products)      <- turn 1 starts
  2  user       tool_result
  3  assistant  text                                  <- turn 1 answer
  4  user       "how much is it and do we have stock?" <- turn 2 starts
  5  assistant  tool_use(get_price) + tool_use(get_stock)   <- two at once
  6  user       tool_result + tool_result              <- both in ONE message
  7  assistant  text                                  <- turn 2 answer

Read the pattern off it:
  * roles always alternate user / assistant - tool_results are "user" messages,
    which is what keeps the alternation valid.
  * a turn is one user message plus everything up to the next text-only
    assistant message.
  * "it" in message 4 only works because messages 0-3 are still in the list.
"""
