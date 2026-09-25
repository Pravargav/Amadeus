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
tly degrade behavior.

