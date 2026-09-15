"""WEB SEARCH -- a SERVER-side tool.

    python web_search.py

Notice what is MISSING compared to text_editor_tool.py: there is no
implementation. No `run()`, no commands, no file handling. Anthropic executes
the searches on its own servers, so the only code you write is the parsing of
what comes back.
"""

import anthropic

client = anthropic.Anthropic()

# Same declaration style as the text editor: type + name, no input_schema.
WEB_SEARCH = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 5,                       # optional: cap searches per request
    # "allowed_domains": ["arxiv.org"],  # allowlist OR blocklist -- never both
    # "user_location": {"type": "approximate", "country": "IN"},
}

messages = [{"role": "user", "content": "What is the latest Python release, and when did it ship?"}]

for attempt in range(6):                 # only needed for pause_turn, below
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=2048,
        tools=[WEB_SEARCH],
        messages=messages,
    )
    print(f"\n--- stop_reason: {response.stop_reason} ---")

    # The searches ALREADY RAN. These blocks are a record, not a request.
    for block in response.content:
        if block.type == "server_tool_use":
            # Note: server_tool_use, not tool_use. Different block type.
            print("searched:", block.input["query"])

        elif block.type == "web_search_tool_result":
            # GOTCHA: on success .content is a LIST of results;
            # on failure it's an OBJECT like {"error_code": "max_uses_exceeded"}.
            # Server-tool errors return HTTP 200 -- they never raise.
            if isinstance(block.content, list):
                for item in block.content:
                    print("   -", item.title)
            else:
                print("   search failed:", block.content.error_code)

        elif block.type == "text":
            print("\nClaude:", block.text)

    # "pause_turn" = the server's own loop hit its limit mid-answer.
    # Re-send to resume. Do NOT append a "Continue." message: the API sees the
    # trailing server_tool_use block and picks up where it left off.
    if response.stop_reason != "pause_turn":
        break
    messages.append({"role": "assistant", "content": response.content})
    print("(paused, resuming...)")
