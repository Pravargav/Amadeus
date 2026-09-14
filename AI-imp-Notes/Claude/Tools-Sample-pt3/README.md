# Part 2 — Multi-turn conversations with tools

Part 1 did **one** tool round trip. This project turns it into a real
conversation: many turns, many tools, one router, one loop.

```bash
pip install anthropic
$env:ANTHROPIC_API_KEY = "sk-ant-..."
python test_multiple_tools.py     # canned turns, nothing to type
python agent.py                   # interactive; 'flow' prints the message flow
```

## Files

| File | Teaches |
|---|---|
| `helpers.py` | the refactor: message handlers, chat function, text extraction, tool detection |
| `tools.py` | scalable tool routing (a registry, not an `if/elif` chain) + 4 tools |
| `agent.py` | the multi-turn pattern and the conversation loop |
| `test_multiple_tools.py` | testing multiple tool usage; the error path |

## The multi-turn tool pattern: two loops

```
while user keeps talking:                        # OUTER - conversation turns
    add_user_message(messages, user_input)
    while response.stop_reason == "tool_use":     # INNER - the tool loop
        add_assistant_message(messages, response.content)
        run every tool_use block
        add_user_message(messages, tool_results)
    print(text_from(response))
```

- **Outer loop** = one pass per human message.
- **Inner loop** = runs 0, 1 or many times *inside a single turn*, because Claude
  may need a second lookup after seeing the first result.
- `messages` is **never reset**. It is the only state in the app, and the entire
  list is re-sent on every API call — that's why turn 3 can say "it".

## The refactored helpers

| Helper | Job |
|---|---|
| `add_user_message(messages, content)` | user turn; `content` = string **or** list of `tool_result` blocks |
| `add_assistant_message(messages, content)` | assistant turn; always pass `response.content` **verbatim** |
| `chat(messages, tools, system)` | the single place that calls `client.messages.create` |
| `text_from(message)` | joins the `text` blocks — filter, never `content[0].text` |
| `wants_tool(message)` | detecting tool requests: `stop_reason == "tool_use"` |
| `tool_use_blocks(message)` | every `tool_use` block (there may be several) |

Note `system=` is its own parameter — there is **no** message with `role: "system"`.

## Scalable tool routing

The `if/elif` router from part 1 grows forever. Instead, each tool registers
itself with its schema:

```python
TOOL_REGISTRY = {}                      # name -> {"schema": ..., "fn": ...}

@tool({"name": "get_price", "description": ..., "input_schema": {...}})
def get_price(product):
    return f"{product} costs ${...}"

ALL_TOOLS = [e["schema"] for e in TOOL_REGISTRY.values()]   # the `tools` param
```

```python
def run_tool(name, tool_input):
    entry = TOOL_REGISTRY.get(name)
    if entry is None:
        return f"Error: no such tool '{name}'"
    try:
        return str(entry["fn"](**tool_input))
    except Exception as e:
        return f"Error running {name}: {e}"
```

Three things this buys you:

1. Adding a tool = adding a function. The router and `ALL_TOOLS` never change.
2. `**tool_input` works because `block.input` is already a dict — so name your
   schema properties exactly like your function parameters.
3. The schema list can't drift from the code that actually runs.

## Tool result blocks & error handling

```python
{
    "type": "tool_result",
    "tool_use_id": block.id,     # must match the tool_use block's id
    "content": output,           # a string (or a list of blocks)
    "is_error": True,            # only when the tool failed
}
```

Error handling rule: a tool that blows up **still gets a `tool_result`**, with
`is_error: True` and the reason in `content`. Never let an exception escape and
never silently skip a block — a missing `tool_result` is a 400, and Claude can
usually recover from an error it can read.

## Understanding the message flow

A two-turn conversation:

```
0  user       "what keyboards do you sell?"
1  assistant  text + tool_use(search_products)          <- turn 1
2  user       tool_result
3  assistant  text                                       <- turn 1 answer
4  user       "how much is it and do we have stock?"      <- turn 2
5  assistant  tool_use(get_price) + tool_use(get_stock)   <- two at once
6  user       tool_result + tool_result                   <- both in ONE message
7  assistant  text                                        <- turn 2 answer
```

- Roles always alternate user / assistant. `tool_result`s are **user** messages,
  which is exactly what keeps that alternation legal.
- A "turn" = one user message plus everything up to the next text-only assistant message.
- N `tool_use` blocks → N `tool_result` blocks in the **single** next user message.
  Splitting them across two messages teaches Claude to stop calling tools in parallel.

## Exam-ready summary

- `stop_reason`: `tool_use` → run tools and loop; `end_turn` → turn is done;
  `max_tokens` → truncated; `pause_turn` → server-side tool, re-send, run nothing.
- Claude never executes your code; it only emits `tool_use` blocks.
- Append `response.content` unmodified — including any `thinking` block.
- The whole history is re-sent every call, so tokens grow each pass (→ prompt caching).
- Cap the inner loop (`for _ in range(10)`) so a stuck model can't spin forever.
- The SDK can drive all of this for you (`client.beta.messages.tool_runner`), but the
  exam wants the manual version — it's the same six moves.
