"""
STEP 2 - The whole tool-use round trip, one numbered section per exam topic.

Run:  python step2_tool_flow.py

  1. Making Tool-Enabled API Calls
  2. Managing Conversation History with Multi-Block Messages
  3. Running the Tool Function
  4. Tool Result Block
  5. Building the Follow-up Request
  6. Making the Final Request
"""

from helpers import add_user_message, add_assistant_message, chat, text_from
from tools import ALL_TOOLS, run_tool

# =====================================================================
# 1. MAKING TOOL-ENABLED API CALLS
#    A call becomes "tool-enabled" the moment you pass `tools=`.
#    Claude still replies normally; it only *may* ask for a tool.
# =====================================================================
messages = []
add_user_message(messages, "How much does a laptop cost?")

response = chat(messages, tools=ALL_TOOLS)
print("1) stop_reason =", response.stop_reason)          # "tool_use"


# =====================================================================
# 2. MANAGING CONVERSATION HISTORY WITH MULTI-BLOCK MESSAGES
#    Append the assistant's ENTIRE block list, not just its text.
#    response.content is already in the exact shape the API expects.
# =====================================================================
add_assistant_message(messages, response.content)
#           ^^^^^^^^^^^^^^^^ the raw list of blocks, tool_use included
print("2) history is now:", [m["role"] for m in messages])  # ['user', 'assistant']


# =====================================================================
# 3. RUNNING THE TOOL FUNCTION
#    Claude never executes anything. You find the tool_use block,
#    read .name and .input, and call your own Python.
# =====================================================================
tool_use_block = next(b for b in response.content if b.type == "tool_use")

tool_output = run_tool(tool_use_block.name, tool_use_block.input)
print("3) ran", tool_use_block.name, "->", tool_output)


# =====================================================================
# 4. TOOL RESULT BLOCK
#    A tool_result is a block inside a USER message (surprising but true -
#    "user" here means "your program", the side feeding data in).
#    tool_use_id MUST equal the id of the tool_use block it answers.
# =====================================================================
tool_result_block = {
    "type": "tool_result",
    "tool_use_id": tool_use_block.id,   # <- the link between request & answer
    "content": tool_output,             # a string (or a list of blocks)
    # "is_error": True                  # <- add this if your tool blew up
}
print("4) tool_result:", tool_result_block)


# =====================================================================
# 5. BUILDING THE FOLLOW-UP REQUEST
#    Wrap the result block(s) in a list and append as a user turn.
#    History is now: user text -> assistant (text+tool_use) -> user (tool_result)
# =====================================================================
add_user_message(messages, [tool_result_block])
print("5) history is now:", [m["role"] for m in messages])


# =====================================================================
# 6. MAKING THE FINAL REQUEST
#    Same endpoint, same tools, full history. Claude reads the result
#    and writes the real answer -> stop_reason "end_turn".
# =====================================================================
final = chat(messages, tools=ALL_TOOLS)
print("6) stop_reason =", final.stop_reason)             # "end_turn"
print("   answer      =", text_from(final))

add_assistant_message(messages, final.content)           # keep history complete

"""
The finished conversation (3 messages in, 1 more appended):

[
  {"role": "user",      "content": "How much does a laptop cost?"},

  {"role": "assistant", "content": [                       <- MULTI-BLOCK
      {"type": "text",     "text": "Let me check."},
      {"type": "tool_use", "id": "toolu_01", "name": "get_price",
                           "input": {"product": "laptop"}},
  ]},

  {"role": "user",      "content": [                       <- MULTI-BLOCK
      {"type": "tool_result", "tool_use_id": "toolu_01",
                              "content": "laptop costs $1200"},
  ]},

  {"role": "assistant", "content": [
      {"type": "text", "text": "A laptop costs $1200."},
  ]},
]

Three mistakes that cost marks:
  * sending only the text of the assistant turn -> tool_use disappears -> 400.
  * a tool_use_id that does not match -> 400.
  * putting tool_result in an "assistant" message -> it belongs to "user".
"""
