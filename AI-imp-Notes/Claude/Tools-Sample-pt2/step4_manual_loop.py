"""
STEP 4 - The manual agentic loop: steps 1-6 wrapped in a `while True`.

Run:  python step4_manual_loop.py

Steps 2 and 3 did exactly ONE round trip. If Claude needs a second tool
call after seeing the first result, you just repeat the same 4 moves:

    call -> append assistant content -> run tools -> append tool_results

The only thing that ends the loop is stop_reason != "tool_use".
"""

from helpers import add_user_message, add_assistant_message, chat, text_from
from tools import ALL_TOOLS, run_tool

messages = []
add_user_message(
    messages,
    "Compare the laptop and the keyboard: price and stock for each, then tell me "
    "which one we should reorder.",
)

while True:
    response = chat(messages, tools=ALL_TOOLS)

    # Claude is done talking -> leave the loop.
    if response.stop_reason != "tool_use":
        add_assistant_message(messages, response.content)
        print("\nFINAL:", text_from(response))
        break

    # Otherwise: keep the multi-block assistant turn, run the tools, reply.
    add_assistant_message(messages, response.content)

    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            print("calling", block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": run_tool(block.name, block.input),
            })

    add_user_message(messages, tool_results)

print("\nturns in history:", len(messages))

"""
Cheat sheet for stop_reason inside the loop:

    "tool_use"   -> run the tools, send tool_results, loop again
    "end_turn"   -> Claude finished; stop
    "max_tokens" -> output was cut off; raise max_tokens or ask for less
    "pause_turn" -> a SERVER-side tool (web search etc.) needs more time:
                    append response.content and re-send, no tools to run

Safety nets worth mentioning in an answer:
  * cap the iterations (e.g. `for _ in range(10)`) so a stuck model can't
    spin forever and burn tokens
  * every loop pass re-sends the whole history, so input tokens grow each
    round - prompt caching is the usual fix
"""
