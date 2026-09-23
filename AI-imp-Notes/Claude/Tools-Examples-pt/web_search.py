"""WEB SEARCH -- a SERVER-side tool.

    python web_search.py

Notice what is MISSING compared to text_editor_tool.py: there is no
implementation. No `run()`, no commands, no file handling. Anthropic executes
the searches on its own servers, so the only code you write is the parsing of
what comes back.
"""

import anthropic

client = anthropic.Anthropic()

WEB_SEARCH = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 5,                      
}

messages = [{"role": "user", "content": "What is the latest Python release, and when did it ship?"}]

for attempt in range(6):                
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=2048,
        tools=[WEB_SEARCH],
        messages=messages,
    )
    print(f"\n--- stop_reason: {response.stop_reason} ---")

    for block in response.content:
        if block.type == "server_tool_use":
            print("searched:", block.input["query"])

        elif block.type == "web_search_tool_result":
            if isinstance(block.content, list):
                for item in block.content:
                    print("   -", item.title)
            else:
                print("   search failed:", block.content.error_code)

        elif block.type == "text":
            print("\nClaude:", block.text)

    if response.stop_reason != "pause_turn":
        break
    messages.append({"role": "assistant", "content": response.content})
    print("(paused, resuming...)")
