# Multi-block messages & tool use — a 4-file walkthrough

A deliberately tiny project for learning the Claude tool-use round trip.
Two fake tools (`get_price`, `get_stock`), four scripts, one idea per script.

```bash
pip install anthropic
# then, in PowerShell:
$env:ANTHROPIC_API_KEY = "sk-ant-..."
python step1_multi_block.py
```

## Files

| File | Teaches |
|---|---|
| `helpers.py` | `add_user_message`, `add_assistant_message`, `chat`, `text_from` |
| `tools.py` | tool **schema** (what Claude sees) vs tool **function** (what you run) |
| `step1_multi_block.py` | text block vs `tool_use` block; `response.content` is a list |
| `step2_tool_flow.py` | the full round trip, one numbered section per exam topic |
| `step3_multiple_tools.py` | several `tool_use` blocks in one message |
| `step4_manual_loop.py` | the same 4 moves wrapped in `while True` |

## The one mental model

A message is `{"role": ..., "content": ...}` and **content is either a string or a list of blocks**.
`"content": "hi"` is just shorthand for `"content": [{"type": "text", "text": "hi"}]`.
"Multi-block" = that list has more than one item.

Who produces which block:

| Block | Appears in | Made by |
|---|---|---|
| `text` | user or assistant message | you / Claude |
| `tool_use` | **assistant** message | Claude (a request, nothing has run) |
| `tool_result` | **user** message | **your code**, after running the function |

`tool_result` living in a `user` message is the thing most people get wrong.
"User" just means *the side feeding data in* — that's your program.

## The 6 steps

```
1. tool-enabled call     chat(messages, tools=ALL_TOOLS)
2. keep history          add_assistant_message(messages, response.content)   <- whole block list
3. run the function      run_tool(block.name, block.input)
4. tool_result block     {"type":"tool_result", "tool_use_id": block.id, "content": output}
5. follow-up request     add_user_message(messages, [tool_result_block])
6. final call            chat(messages, tools=ALL_TOOLS)  ->  stop_reason "end_turn"
```

Full conversation after one tool call:

```python
[
  {"role": "user",      "content": "How much does a laptop cost?"},
  {"role": "assistant", "content": [                                  # multi-block
      {"type": "text",     "text": "Let me check."},
      {"type": "tool_use", "id": "toolu_01", "name": "get_price",
                           "input": {"product": "laptop"}},
  ]},
  {"role": "user",      "content": [                                  # multi-block
      {"type": "tool_result", "tool_use_id": "toolu_01",
                              "content": "laptop costs $1200"},
  ]},
  {"role": "assistant", "content": [{"type": "text", "text": "It's $1200."}]},
]
```

## `stop_reason`

| Value | Meaning |
|---|---|
| `tool_use` | Claude paused and wants a tool run. **Nothing executed yet.** |
| `end_turn` | Claude finished. Read the text. |
| `max_tokens` | Output was truncated. |
| `pause_turn` | A *server-side* tool needs another round; re-send, run nothing. |

## Things worth memorising

- Claude **never runs your code** — it only emits a `tool_use` block. Execution is 100% yours.
- `block.input` is already a **dict**. Parse it as JSON, never string-match it.
- `tool_use_id` must match the `tool_use` block's `id` exactly.
- Append `response.content` **verbatim** — never rebuild it from the text, and never
  edit or drop a `thinking` block if one is present.
- N `tool_use` blocks → N `tool_result` blocks in **one** following user message.
- A failed tool still gets a `tool_result`, with `"is_error": True`.
- Every loop pass re-sends the whole history, so input tokens grow each round.

## After you've got this

The SDK can drive the loop for you (`client.beta.messages.tool_runner` with the
`@beta_tool` decorator — schemas are generated from the function signature).
Learn the manual loop first: the runner just automates steps 1–6 above.
