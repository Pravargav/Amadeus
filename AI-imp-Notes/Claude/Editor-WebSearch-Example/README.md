# Two Claude tools, one small project

A runnable Python project that explains the **text editor tool** and the **web
search tool** — the two tools sit on opposite sides of the single most important
line in tool use: *who actually executes the tool.*

```
editor_backend.py        the text editor, implemented by you (the only real work)
pretty.py                prints every content block so nothing is invisible
demo_01_web_search.py    server-side tool: no loop, results arrive inline
demo_02_text_editor.py   client-side tool: the tool_use / tool_result loop
demo_03_both.py          both tools in one loop -- research, then write a file
sandbox/notes.md         a file with two deliberate errors for demo 2 to fix
```

## Run it

```bash
pip install -r requirements.txt
```

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

```bash
python demo_01_web_search.py "what shipped in the latest Python release?"
```

```bash
python demo_02_text_editor.py
```

```bash
python demo_03_both.py "compare SQLite and DuckDB for analytics"
```

On Windows PowerShell, set the key with `$env:ANTHROPIC_API_KEY = "sk-ant-..."`.

> **What's been verified:** `editor_backend.py` is exercised end to end offline —
> all four commands, plus every error path (path traversal, 0 and >1
> `str_replace` matches, out-of-range `insert_line`, bad `view_range`). The
> three demo scripts compile and import cleanly and their tool definitions are
> checked against the SDK's own param types. The demos' **live API calls were
> not run** — no `ANTHROPIC_API_KEY` was available in the environment where
> this was written.

---

## The one distinction that matters

|                        | **Text editor**                        | **Web search**                          |
| ---------------------- | -------------------------------------- | --------------------------------------- |
| Who executes it        | **You** (client-side)                  | **Anthropic** (server-side)             |
| Code you write         | The whole implementation               | None                                    |
| How the request looks  | `tool_use` block → you act             | already done when you see it            |
| How results get back   | You send a `tool_result`               | Arrive as blocks in the same response   |
| Requests per tool call | ≥ 2 (call, execute, call again)        | 1 (usually)                             |
| Extra loop you need    | The agentic loop                       | Only `pause_turn` resume                |
| Where state lives      | Your filesystem — the API is stateless | Anthropic's side                        |
| What can go wrong      | Path traversal, arbitrary writes       | A quiet error object inside the result  |

Everything else about the two tools follows from that row one.

## Declaring them

Both are **Anthropic-defined**: declare them by `type` and `name` only. The
text editor is additionally **schema-less** — the input shape is baked into the
model, so passing an `input_schema` is wrong.

```python
TEXT_EDITOR_TOOL = {
    "type": "text_editor_20250728",
    "name": "str_replace_based_edit_tool",   # fixed name -- don't rename it
    "max_characters": 10_000,                # optional: caps `view` output
}

WEB_SEARCH_TOOL = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 5,                           # optional
    # "allowed_domains": [...] OR "blocked_domains": [...]  -- never both
    # "user_location": {"type": "approximate", "country": "IN", ...}
}
```

### Versions

Tool versions are dated strings, and picking the wrong one is a silent
downgrade or a 400.

| Tool        | Use this                | Notes                                                                         |
| ----------- | ----------------------- | ----------------------------------------------------------------------------- |
| Text editor | `text_editor_20250728`  | Current — the newest the SDK exposes. `undo_edit` was dropped after the `20250124` version, so keep your own backups (this project writes `.bak` files). |
| Web search  | `web_search_20260209`   | What these demos use. Adds **dynamic filtering**: Claude filters results server-side before they enter the context window. Needs Opus 4.6+ / Sonnet 4.6+. |
| Web search  | `web_search_20250305`   | Basic version, for older models — and the only variant available on Vertex AI. |
| Web search  | `web_search_20260318`   | Newer still. `anthropic` 1.5.0 ships a param type for it, identical to `20260209` plus a `response_inclusion: "full" \| "excluded"` field. Not covered by the docs bundled with this project, so the demos don't default to it — check the current docs before adopting it. |

Two version traps worth knowing:

- With `web_search_20260209`, **do not also declare `code_execution`**. The
  filtering already runs code under the hood; a second execution environment
  confuses the model.
- A custom tool you happen to name `"str_replace_based_edit_tool"` is a
  *different* tool with none of the built-in behaviour. The `type` is what
  makes it the real one.

## The loop (client-side tools only)

```
                +--> messages.create(tools=[...])
                |            |
                |     stop_reason == "tool_use"?
                |        /              \
                |      yes               no --> done, read the text blocks
                |       |
                |   execute each tool_use block locally
                |       |
                +-- append assistant content + ONE user message of tool_results
```

The loop in [demo_02_text_editor.py](demo_02_text_editor.py) is about twenty
lines, and four invariants make it correct:

1. **Append the whole `response.content`**, not just the text. The `tool_use`
   and `thinking` blocks have to survive the round trip.
2. **Every `tool_result` echoes the matching `tool_use_id`.**
3. **All results from one assistant turn go back in one user message.**
   Splitting them across messages silently trains Claude to stop making
   parallel tool calls.
4. **A failed tool still returns a `tool_result`**, with `is_error: True`.
   Dropping it leaves a hole in the transcript that Claude cannot recover from.

On the wire, one round trip looks like this:

```jsonc
// assistant turn -- stop_reason: "tool_use"
{"type": "tool_use", "id": "toolu_01ABC", "name": "str_replace_based_edit_tool",
 "input": {"command": "str_replace", "path": "/notes.md",
           "old_str": "three API requests", "new_str": "as many requests as it takes"}}

// your next user turn
{"type": "tool_result", "tool_use_id": "toolu_01ABC",
 "content": "Replaced 1 occurrence in /notes.md at line 22."}
```

For a **server-side** tool there is no such exchange. You get the past-tense
record instead, in the same response as the answer:

```jsonc
{"type": "server_tool_use", "id": "srvtoolu_01XYZ", "name": "web_search",
 "input": {"query": "duckdb vs sqlite analytics benchmark"}}
{"type": "web_search_tool_result", "tool_use_id": "srvtoolu_01XYZ",
 "content": [{"type": "web_search_result", "title": "...", "url": "..."}]}
```

## The four text editor commands

Implemented in [editor_backend.py](editor_backend.py):

| `command`     | Inputs                               | Contract                                                        |
| ------------- | ------------------------------------ | --------------------------------------------------------------- |
| `view`        | `path`, optional `view_range`        | File contents (return them **numbered**) or a directory listing |
| `create`      | `path`, `file_text`                  | Create or overwrite. Back up first if it exists                  |
| `str_replace` | `path`, `old_str`, `new_str`         | Replace **exactly one** occurrence; error on 0 or >1 matches     |
| `insert`      | `path`, `insert_line`, `insert_text` | Insert after line `insert_line`; `0` means before line 1         |

Two details that make the difference between a tool Claude can use and one it
fights with:

- **Number the lines in `view` output.** `insert_line` is 1-indexed and
  `str_replace` needs exact text; unnumbered output leaves Claude guessing.
- **Be strict about `str_replace` and say why.** Returning *"matched 3 times,
  include more surrounding context"* as an error is what lets Claude widen its
  snippet and retry. A permissive replace-first implementation corrupts files.

## Security

These are the two failure modes that actually bite in this project.

**`path` is untrusted model output.** Confine every operation to a fixed root.
`TextEditorBackend._resolve()` canonicalises the path and refuses anything that
escapes — `..`, symlinks, stray absolute paths, encoded traversal. Never hand
the raw `path` value to `open()`. The same rule applies with more force to the
bash tool (`{"type": "bash_20250124", "name": "bash"}`): run it in a container
or restricted user, allowlist the permitted executables rather than blocklisting
operators, and set timeouts.

**Server-tool errors do not raise.** A failed web search comes back as HTTP
200, with the result block's `content` holding an error object such as
`{"error_code": "max_uses_exceeded"}`. On success that same field is a *list*.
Branch on the shape before you index it — see `_show_search_result()` in
[pretty.py](pretty.py):

```python
content = block.content
if not isinstance(content, list):
    ...  # error object: read content.error_code
```

## Two things you can skip in real code

- **`pause_turn`.** Server tools run their own sampling loop on Anthropic's
  side. If it hits its internal limit you get `stop_reason: "pause_turn"`
  instead of a finished answer. Append the assistant turn and re-send —
  and *don't* add a `"Continue."` user message; the API sees the trailing
  `server_tool_use` block and resumes by itself. Cap the resumes.
- **The manual loop.** These demos hand-roll it because watching it is the
  point. In production, prefer the SDK's tool runner:

  ```python
  runner = client.beta.messages.tool_runner(
      model="claude-opus-5", max_tokens=16_000,
      tools=[TEXT_EDITOR_TOOL, WEB_SEARCH_TOOL],
      messages=[{"role": "user", "content": task}],
  )
  for message in runner:
      ...
  ```

  It still gives you approval gates, error interception, and result
  modification via per-turn hooks. Its one gap is the item above: the Python
  runner does **not** auto-resume `pause_turn` — a paused turn just ends the
  loop with no error, so mirror the history and restart the runner if you mix
  in server tools.

## Reference

- Tool use overview — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview>
- Text editor tool — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool>
- Web search tool — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool>
- Handling stop reasons — <https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons>
