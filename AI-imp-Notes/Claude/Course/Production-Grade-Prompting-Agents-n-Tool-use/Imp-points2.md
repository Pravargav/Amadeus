
# Gap 1: Description for `update_record`

```python
"Use this to update a specific field on a customer record. Only call this tool after a read_record call has confirmed the current value and the proposed change has been reviewed. Do not use this for bulk updates or schema changes."
```

### Why this works

- Specifies the tool's intended purpose.
- Requires a `read_record` call before any modification.
- Instructs the model that the change must be reviewed before execution.
- Explicitly prohibits unsupported actions such as bulk updates and schema modifications.
- Reduces the likelihood of unsafe or unintended tool usage.

---

# Gap 2: HITL (Human-in-the-Loop) Checkpoint Code

Insert the following code immediately before executing `update_record`:

```python
if block.type == "tool_use":

    if block.name == "update_record":
        print(
            f"Proposed update, customer_id: {block.input['customer_id']}, "
            f"field: {block.input['field']}, "
            f"new_value: {block.input['new_value']}"
        )

        approval = input("Approve this update? (yes/no): ").strip().lower()

        if approval != "yes":
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": "Update rejected by operator."
            })
            continue

    result = execute_tool(block.name, block.input)

    tool_results.append({
        "type": "tool_result",
        "tool_use_id": block.id,
        "content": result
    })
```

### Why this works

- Applies approval only to the sensitive `update_record` tool.
- Allows read-only tools such as `read_record` to run without interruption.
- Displays the exact record change before execution.
- Requires explicit operator approval.
- Prevents execution when approval is denied.
- Ensures authorization occurs **before** the update is performed, avoiding irreversible changes prior to review.

---

# Complete Filled Version

```python
tools = [
  {
    "name": "read_record",
    "description": "Use this to read a customer record by customer_id.",
    "input_schema": {
      "type": "object",
      "properties": {
        "customer_id": {"type": "string"}
      },
      "required": ["customer_id"]
    }
  },
  {
    "name": "update_record",
    "description": "Use this to update a specific field on a customer record. Only call this tool after a read_record call has confirmed the current value and the proposed change has been reviewed. Do not use this for bulk updates or schema changes.",
    "input_schema": {
      "type": "object",
      "properties": {
        "customer_id": {"type": "string"},
        "field": {"type": "string"},
        "new_value": {"type": "string"}
      },
      "required": ["customer_id", "field", "new_value"]
    }
  }
]

def run_agent_loop(user_request):
    messages = [{"role": "user", "content": user_request}]

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            return response

        if response.stop_reason == "tool_use":
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results = []

            for block in response.content:
                if block.type == "tool_use":

                    if block.name == "update_record":
                        print(
                            f"Proposed update, customer_id: {block.input['customer_id']}, "
                            f"field: {block.input['field']}, "
                            f"new_value: {block.input['new_value']}"
                        )

                        approval = input(
                            "Approve this update? (yes/no): "
                        ).strip().lower()

                        if approval != "yes":
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Update rejected by operator."
                            })
                            continue

                    result = execute_tool(block.name, block.input)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({
                "role": "user",
                "content": tool_results
            })
```
