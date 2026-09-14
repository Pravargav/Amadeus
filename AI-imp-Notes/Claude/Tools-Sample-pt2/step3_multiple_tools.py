"""
STEP 3 - Handling Multiple Tool Calls (parallel tool use).

Run:  python step3_multiple_tools.py

One assistant message can carry SEVERAL tool_use blocks at once.
Rule: run them all, then send ALL the tool_result blocks back in
ONE user message. Splitting them across two user messages is wrong -
Claude learns to stop calling tools in parallel.
"""

from helpers import add_user_message, add_assistant_message, chat, text_from
from tools import ALL_TOOLS, run_tool

messages = []
add_user_message(messages, "What's the price of a laptop, and do we have any in stock?")

response = chat(messages, tools=ALL_TOOLS)
add_assistant_message(messages, response.content)

# --- collect every tool_use block, not just the first one ---
tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
print(f"Claude asked for {len(tool_use_blocks)} tool(s)")

# --- run each one, build one tool_result block per tool_use block ---
tool_results = []
for block in tool_use_blocks:
    try:
        output = run_tool(block.name, block.input)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": output,
        })
    except Exception as e:
        # Never drop a failed tool - report it with is_error so Claude can recover.
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": f"Error: {e}",
            "is_error": True,
        })
    print("  ran", block.name, block.input)

# --- ONE user message holding ALL the results ---
add_user_message(messages, tool_results)

final = chat(messages, tools=ALL_TOOLS)
print("\nanswer:", text_from(final))

"""
The middle of the conversation:

{"role": "assistant", "content": [
    {"type": "tool_use", "id": "toolu_A", "name": "get_price", "input": {...}},
    {"type": "tool_use", "id": "toolu_B", "name": "get_stock", "input": {...}},
]}

{"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "toolu_A", "content": "laptop costs $1200"},
    {"type": "tool_result", "tool_use_id": "toolu_B", "content": "laptop: 4 units in stock"},
]}

Counts must match: every tool_use block needs exactly one tool_result block,
in the very next user message. Order of the results does not matter - the ids do.
"""
