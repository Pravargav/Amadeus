"""
STEP 1 - What a multi-block message actually looks like.

Run:  python step1_multi_block.py

Goal: see with your own eyes that `response.content` is a LIST of blocks,
and that a tool-using reply can hold a text block AND a tool_use block.
"""

from helpers import add_user_message, chat
from tools import ALL_TOOLS

messages = []
add_user_message(messages, "How much does a laptop cost?")

response = chat(messages, tools=ALL_TOOLS)

print("stop_reason:", response.stop_reason)   # -> "tool_use"
print("number of blocks:", len(response.content))
print()

for i, block in enumerate(response.content):
    print(f"--- block {i}: type = {block.type} ---")
    if block.type == "text":
        print("   text:", block.text)
    elif block.type == "tool_use":
        print("   id   :", block.id)          # e.g. toolu_01A...
        print("   name :", block.name)        # "get_price"
        print("   input:", block.input)       # {"product": "laptop"} - already a dict
    elif block.type == "thinking":
        print("   (reasoning block - pass it back unchanged, never edit it)")

"""
Typical shape of response.content:

[
    TextBlock(type="text", text="Let me look that up."),      <- optional
    ToolUseBlock(type="tool_use", id="toolu_01...",            <- the request
                 name="get_price", input={"product": "laptop"}),
]

Exam points:
  * stop_reason == "tool_use"  -> Claude is PAUSING and waiting for you.
    Nothing ran yet. Your code must run the tool.
  * stop_reason == "end_turn"  -> Claude is finished; no tool_result needed.
  * block.input is a parsed dict, not a JSON string - never string-match on it.
  * There can be 0 text blocks, 1 text block, or several blocks + many tool_use
    blocks. Always LOOP over content; never assume content[0] is the text.
"""
