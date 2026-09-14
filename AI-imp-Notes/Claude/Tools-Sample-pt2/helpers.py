"""
helpers.py - the 4 tiny functions every example in this project uses.

The ONE idea to take into the exam:
    a message is  {"role": ..., "content": ...}
    and `content` is EITHER a plain string OR a LIST OF BLOCKS.

    string form  ->  {"role": "user", "content": "hi"}
    block form   ->  {"role": "user", "content": [{"type": "text", "text": "hi"}]}

The string form is just shorthand for a list with one text block.
Multi-block simply means that list has more than one item, e.g.
a text block AND a tool_use block in the same assistant message.
"""

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = "claude-opus-5"


def add_user_message(messages, content):
    """Append a user turn. `content` may be a string or a list of blocks."""
    messages.append({"role": "user", "content": content})
    return messages


def add_assistant_message(messages, content):
    """Append an assistant turn.

    For tool use you pass `response.content` here (the raw block list),
    NOT just the text. Dropping the tool_use block breaks the conversation:
    a tool_result must always answer a tool_use that Claude can still see.
    """
    messages.append({"role": "assistant", "content": content})
    return messages


def chat(messages, tools=None, max_tokens=1000):
    """One call to POST /v1/messages. Passing `tools` makes it tool-enabled."""
    params = {"model": MODEL, "max_tokens": max_tokens, "messages": messages}
    if tools:
        params["tools"] = tools
    return client.messages.create(**params)


def text_from(message):
    """Pull the text out of a multi-block response (there may be no text block)."""
    return "".join(b.text for b in message.content if b.type == "text")
