# Text editor tool vs. web search tool — study notes

| File | What it is | Needs an API key? |
|---|---|---|
| [text_editor_tool.py](text_editor_tool.py) | **Sample implementation** of the text editor — all 4 commands | No — run it directly |
| [text_editor_agent.py](text_editor_agent.py) | The **loop** that connects it to Claude | Yes |
| [web_search.py](web_search.py) | Web search — notice there's **no implementation** | Yes |

```bash
python text_editor_tool.py
```

That one runs with no key and prints every command working, plus the error
cases. Start there.

---

## 1. The core idea

Both tools are declared the same way. The difference is **who executes them.**

```
SERVER-side (web search)          CLIENT-side (text editor)
--------------------------        -------------------------
You declare the tool              You declare the tool
Anthropic searches                Claude says "run this edit"  <- tool_use
Results come back in the          YOU run it
  SAME response                   You send the output back     <- tool_result
Done. 1 request.                  Claude continues... repeat.
No loop.                          NEEDS A LOOP.
```

That's why `text_editor_tool.py` is 180 lines and `web_search.py` has no
implementation at all: **Anthropic gives you the interface, not the behaviour.**

## 2. How you declare them

Both are **Anthropic-defined**, so both are `type` + `name` only.
**Neither takes an `input_schema`** — a favourite exam trap.

```python
{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}
{"type": "web_search_20260209",  "name": "web_search"}
```

A tool *you* invent needs all three fields:

```python
{"name": "get_weather", "description": "...", "input_schema": {...}}
```

## 3. What Claude actually sends you

For the text editor, `block.input` is a plain dict:

```python
{"command": "str_replace", "path": "/demo.py",
 "old_str": "retrun", "new_str": "return"}
```

Your job: do it, return a string. That string becomes the `tool_result`.

## 4. The 4 commands — how each is implemented

Walk through `text_editor_tool.py` alongside this table.

| `command` | Inputs | Implementation notes |
|---|---|---|
| `view` | `path`, *optional* `view_range` | Directory path → list it. File → **number the lines**. `view_range: [6, -1]` means line 6 to the end |
| `create` | `path`, `file_text` | **Overwrites.** `20250728` has no `undo_edit`, so keep your own `.bak` |
| `str_replace` | `path`, `old_str`, `new_str` | Must match **exactly once**. 0 or 2+ → error. Omitting `new_str` deletes the text |
| `insert` | `path`, `insert_line`, `insert_text` | `insert_line: 0` = top of file, `len(lines)` = append |

There is **no `delete`** command.

The single most important detail: **`str_replace` errors are a feature.**

```python
if hits > 1:
    raise EditorError(f"old_str matched {hits} times. Add surrounding lines...")
```

That message goes back as a `tool_result` with `is_error: True`, Claude reads
it, and retries with more context. A permissive implementation that replaced
the first match would silently corrupt files.

## 5. Security — the one thing you must add yourself

`path` is text the model made up. Confine it to one folder:

```python
full = (self.root / raw.lstrip("/\\")).resolve()   # .resolve() collapses ".."
if not full.is_relative_to(self.root):
    raise EditorError("outside the workspace. Refused.")
```

Without this, `"../../.ssh/id_rsa"` is a valid path. Never pass Claude's raw
`path` to `open()`. Same rule, harder, for the bash tool.

## 6. The loop (client-side only)

```
  messages.create(tools=[...])
          |
   stop_reason == "tool_use"?
      /              \
    no               yes
     |                |
   DONE          run the tool yourself
                      |
              append assistant reply
              + append tool_result
                      |
                  (go back up)
```

Four rules, numbered in the comments of `text_editor_agent.py`:

1. Append the **whole** `response.content`, not just the text.
2. Each `tool_result` carries the **same `tool_use_id`** as its `tool_use`.
3. A failed tool **still** returns a `tool_result`, with `is_error: True`.
4. **All** results from one reply go back in **one** user message.

## 7. Block types you'll be asked to name

| Block | Means |
|---|---|
| `tool_use` | Client-side request — **your turn to act** |
| `tool_result` | *You* send this back |
| `server_tool_use` | Server-side — already ran, just a record |
| `web_search_tool_result` | The search results themselves |

## 8. Versions

| Tool | Current | Older |
|---|---|---|
| Text editor | `text_editor_20250728` | `20250429`, `20250124` (this one had `undo_edit`) |
| Web search | `web_search_20260209` | `web_search_20250305` (basic; only one on Vertex AI) |

## 9. Exam traps

- **No `input_schema`** on text editor, web search, or bash.
- **`str_replace_based_edit_tool` is a fixed name.** A custom tool with the same
  name is a *different* tool with none of the built-in behaviour — the `type`
  field is what makes it real.
- **`str_replace` must match exactly once.**
- **`insert_line: 0`** is the top of the file, not line 1.
- **No `delete` command; no `undo_edit` in `20250728`.**
- **Web search needs no loop** — but `stop_reason` can be `pause_turn` if the
  server's internal loop hits its limit. Re-send to resume, and do **not** add
  a `"Continue."` message.
- **Server-tool errors don't raise.** HTTP 200 with an error object inside the
  result block. On success that field is a *list*; on failure an *object*.
- In production the SDK's **tool runner** drives the loop for you. These files
  hand-roll it because the loop is the thing being taught.

## 10. Quick self-check

1. Which tool needs a `tool_result`? → *text editor*
2. What must every `tool_result` include? → *the matching `tool_use_id`*
3. Does `web_search_20260209` need an `input_schema`? → *no*
4. `str_replace` finds 3 matches — what happens? → *error; Claude retries with more context*
5. Which `stop_reason` means "a client tool is waiting on you"? → *`tool_use`*
6. Which `stop_reason` means "the server paused mid-answer"? → *`pause_turn`*

---

## Running the API ones

```bash
pip install anthropic
```

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

```bash
python text_editor_agent.py
```

```bash
python web_search.py
```

PowerShell: `$env:ANTHROPIC_API_KEY = "sk-ant-..."`

**Verified:** `text_editor_tool.py` was run end to end — all 4 commands,
`view_range`, directory listing, `.bak` backup, and every error path. The two
API scripts compile but their live calls are unrun (no key available here).
