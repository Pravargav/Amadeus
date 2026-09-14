"""
helpers.py - REFACTORING HELPER FUNCTIONS

In part 1 the round trip was written out by hand. Once you go multi-turn you
repeat the same 5 moves over and over, so they become helpers. This file is
the whole refactor, in three groups:

    1. Message handlers    - add_user_message / add_assistant_message
    2. Chat function       - one place that calls the API
    3. Text extraction     - pull readable text out of a multi-block message

Everything else in the project imports from here. Nothing below knows about
tools - that keeps the layers clean (helpers = plumbing, tools.py = your app).
"""

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = "claude-opus-5"


# ---------------------------------------------------------------
# 1. MESSAGE HANDLERS
#    Both accept a string OR a list of blocks, because `content`
#    is "either a string or a list of blocks" everywhere in the API.
# ---------------------------------------------------------------

def add_user_message(messages, content):
    """User turn. `content` is a string, or a list of tool_result blocks."""
    messages.append({"role": "user", "content": content})
    return messages


def add_assistant_message(messages, content):
    """Assistant turn. Pass `response.content` (the raw block list) verbatim.

    Never rebuild this from the text - the tool_use blocks would be lost and
    your next tool_result would answer a tool_use Claude can no longer see.
    """
    messages.append({"role": "assistant", "content": content})
    return messages


# ---------------------------------------------------------------
# 2. CHAT FUNCTION
#    One wrapper, so model / max_tokens / tools live in a single place.
# ---------------------------------------------------------------

def chat(messages, tools=None, system=None, max_tokens=1000):
    params = {"model": MODEL, "max_tokens": max_tokens, "messages": messages}
    if tools:
        params["tools"] = tools      # passing tools = a "tool-enabled" call
    if system:
        params["system"] = system    # system prompt is its own parameter,
                                     # NOT a message with role "system"
    return client.messages.create(**params)


# ---------------------------------------------------------------
# 3. EXTRACTING TEXT FROM MESSAGES
#    A response may have 0, 1 or many text blocks, plus tool_use
#    blocks, plus a thinking block. So: filter, don't index.
# ---------------------------------------------------------------

def text_from(message):
    """Join every text block. Returns "" if Claude only asked for tools."""
    return "".join(b.text for b in message.content if b.type == "text")


# ---------------------------------------------------------------
# 4. DETECTING TOOL REQUESTS
#    stop_reason is the switch that drives the whole loop.
# ---------------------------------------------------------------

def wants_tool(message):
    """True if Claude paused to request tools. Nothing has executed yet."""
    return message.stop_reason == "tool_use"


def tool_use_blocks(message):
    """Every tool_use block in the reply - there may be more than one."""
    return [b for b in message.content if b.type == "tool_use"]


# ---------------------------------------------------------------
# 5. UNDERSTANDING THE MESSAGE FLOW (a debug printer)
# ---------------------------------------------------------------

def print_flow(messages):
    """Print the conversation as roles + block types, so the shape is obvious."""
    print("\n--- message flow " + "-" * 40)
    for i, m in enumerate(messages):
        content = m["content"]
        if isinstance(content, str):
            summary = f'text("{content[:45]}...")'
        else:
            parts = []
            for b in content:
                t = b["type"] if isinstance(b, dict) else b.type
                name = getattr(b, "name", None) or (b.get("name") if isinstance(b, dict) else None)
                parts.append(f"{t}({name})" if name else t)
            summary = " + ".join(parts)
        print(f"  {i}  {m['role']:<9} {summary}")
    print("-" * 57)
