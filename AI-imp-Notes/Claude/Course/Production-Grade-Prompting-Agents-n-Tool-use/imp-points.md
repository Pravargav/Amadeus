```json
System: You are a support ticket processor.

Return ONLY valid JSON.

Schema:
{
  "category": "BILLING | TECHNICAL | ESCALATION",
  "urgency": "LOW | MEDIUM | HIGH",
  "summary": "string"
}

Example:

Input:
My credit card was charged twice.

Output:
{
  "category": "BILLING",
  "urgency": "MEDIUM",
  "summary": "Customer reports duplicate credit card charge."
}
```

-------------------------

# MCP Connector: Controlling Tool Loading Cost

When using the **API MCP Connector**, tool loading behavior is controlled through the `mcp_toolset` object in the `tools` array.

## Key Configuration

### `default_config`
Applies settings to **all tools** on the MCP server.

### `configs`
Allows **per-tool overrides** using the tool name as the key.

---

## Cost Optimization Settings

### 1. `defer_loading`

```json
{
  "defer_loading": true
}
```

- Delays loading a tool's definition until the model actually needs it.
- Reduces initial context size and token usage.
- Useful when an MCP server exposes many tools.

### 2. `enabled`

```json
{
  "enabled": false
}
```

- Enables or disables specific tools.
- Lets you register an MCP server while exposing only selected tools to the model.
- Helps reduce unnecessary context and improve efficiency.

---

## Example

```json
{
  "mcp_toolset": {
    "default_config": {
      "defer_loading": true
    },
    "configs": {
      "search_tool": {
        "enabled": true
      },
      "admin_tool": {
        "enabled": false
      }
    }
  }
}
```

### Result

- All tools use lazy loading (`defer_loading: true`).
- `search_tool` is available to the model.
- `admin_tool` is hidden from the model.

---

## Required Header

When using the MCP Connector, include the beta header:

```http
mcp-client-2025-11-20
```

This header is required for MCP Connector requests.

-----------------

```js
blocks = {}
stop_seen = False
with client.messages.stream(model=model, max_tokens=4096, messages=messages, tools=tools) as stream:
	for event in stream:
    	if event.type == "content_block_start":
        	blocks[event.index] = init_block(event)
    	elif event.type == "content_block_delta":
        	apply_delta(blocks[event.index], event.delta)
    	elif event.type == "message_stop":
        	stop_seen = True
if stop_seen:
	messages.append({"role": "assistant", "content": assemble(blocks)})
else:
	raise StreamInterruptedError(
    	"Stream ended before message_stop; discarding partial turn. Retry from the last complete turn."
	)

```
------------------

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
