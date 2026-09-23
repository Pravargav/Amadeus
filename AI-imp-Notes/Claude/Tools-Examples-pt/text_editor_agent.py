"""THE LOOP -- wires the implementation in text_editor_tool.py to Claude.

    python text_editor_agent.py

The text editor is a CLIENT-side tool, so the conversation ping-pongs:

    Claude: tool_use   ("str_replace /demo.py ...")   <- a REQUEST, nothing ran yet
    You:    tool_result ("Replaced 1 match...")       <- you ran it
    Claude: tool_use   ("view /demo.py")
    You:    tool_result (...)
    Claude: text                                      <- stop_reason "end_turn", done

Compare web_search.py, where none of this exists.
"""

import anthropic

from text_editor_tool import EditorError, TextEditorTool


TEXT_EDITOR = {
    "type": "text_editor_20250728",
    "name": "str_replace_based_edit_tool",
    "max_characters": 10_000,       
}

SYSTEM = (
    "You edit files in a workspace using the text editor tool. "
    "Paths look like '/demo.py'. Always `view` a file before editing it so "
    "your old_str matches exactly."
)

client = anthropic.Anthropic()
editor = TextEditorTool("workspace")

# Give Claude something to fix.
editor.create({
    "command": "create",
    "path": "/demo.py",
    "file_text": "def add(a, b):\n    retrun a - b\n",  
})

messages = [{"role": "user", "content": "Fix the bugs in /demo.py"}]

for turn in range(1, 11):                     
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=2048,
        system=SYSTEM,
        tools=[TEXT_EDITOR],
        messages=messages,
    )
    print(f"\n--- turn {turn} | stop_reason: {response.stop_reason} ---")

    for block in response.content:
        if block.type == "text":
            print("Claude:", block.text)

   
    if response.stop_reason != "tool_use":
        break

    messages.append({"role": "assistant", "content": response.content})

    results = []
    for block in response.content:
        if block.type != "tool_use":
            continue

        print("  wants:", block.input)
        try:
            output = editor.run(block.input)        
            print("  ok:", output)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,           
                "content": output,
            })
        except EditorError as e:
            print("  error:", e)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": f"Error: {e}",
                "is_error": True,                   
            })

 
    messages.append({"role": "user", "content": results})

print("\n--- final file ---")
print(editor.view({"command": "view", "path": "/demo.py"}))
