# RideShare MCP — all four MCP concepts in one app

A mock ride-hailing service (Uber-style, entirely fake data) built as an MCP
server plus a CLI agent client. It exists to show **roots**, **notifications**
and **sampling** working together in one place, on top of the `core/` chat
architecture. Transport is **stdio**.

Nothing here calls a real ride API. Fares, drivers and surge are generated
locally in `core/rides.py`.

---

## Setup

```bash
uv sync
```

```bash
cp .env.example .env
```

Then edit `.env` and set `ANTHROPIC_API_KEY`.

## Run

The folders you pass on the command line become the **roots** — the only places
the server may read or write:

```bash
uv run main.py ./data
```

To see the protocol without spending any API tokens (uses a stub model):

```bash
uv run smoke_test.py
```

---

## Where each concept lives

| Concept | Server side | Client side |
|---|---|---|
| **Tools** | `@mcp.tool()` × 8 in [mcp_server.py](mcp_server.py) | [core/tools.py](core/tools.py) `ToolManager` |
| **Notifications** | `ctx.info()`, `ctx.warning()`, `ctx.report_progress()` | [core/ui.py](core/ui.py) `render_server_log`, `render_progress` |
| **Roots** | `is_path_allowed()` in [mcp_server.py](mcp_server.py) | `_handle_list_roots` in [mcp_client.py](mcp_client.py) |
| **Sampling** | `ctx.session.create_message()` in `summarize_spending` | [core/sampling.py](core/sampling.py) `SamplingHandler` |
| **Resources** | `@mcp.resource(...)` × 3 | `read_resource`, `@mention` expansion in [core/cli_chat.py](core/cli_chat.py) |
| **Prompts** | `@mcp.prompt()` × 2 | `/slash` expansion in [core/cli_chat.py](core/cli_chat.py) |
| **Agentic loop** | — | [core/chat.py](core/chat.py) `Chat.run` |

---

## The tools

| Tool | Demonstrates |
|---|---|
| `list_allowed_folders` | roots (read the whitelist) |
| `estimate_fares` | notifications (log + progress + a `warning` level) |
| `book_ride` | notifications (4-stage, ~5s, progress with per-stage messages) |
| `ride_status` | plain tool, no capabilities |
| `cancel_ride` | notifications, error paths |
| `read_trips_folder` | roots gate on a **read** |
| `export_receipt` | roots gate on a **write** + notifications |
| `summarize_spending` | **all three at once**: roots → notifications → sampling |

`summarize_spending` is the one to study. In a single tool call it:

1. Asks the client for its roots and rejects the path if it is outside them.
2. Emits four logs and four progress updates as it works.
3. Computes the arithmetic locally, then **asks the client's model** to write
   the analysis — because "is this person overspending on surge?" is judgement,
   not arithmetic.

---

## Try these

```
> what folders can you see?
> price a ride from Home to Airport T2
> book the cheapest one
> what's the status of that booking?
> save the receipt to the data folder
> analyse my spending using data/trips.json      <- triggers a sampling approval prompt
> read C:/Windows                                <- roots denies this
> /plan_trip Home "Office Park"                  <- an MCP prompt
> who are the drivers? @drivers                  <- an MCP resource
```

---

## Full lifecycle

### Startup

```
uv run main.py ./data
  │
  ├─ load_dotenv() → assert CLAUDE_MODEL / ANTHROPIC_API_KEY
  ├─ WindowsProactorEventLoopPolicy        (default Windows loop can't spawn subprocesses)
  ├─ Claude(model)                         LLM access lives on the CLIENT
  ├─ SamplingHandler(claude)               needs Claude, so built second
  │
  └─ AsyncExitStack
       └─ MCPClient(roots=["./data"], sampling_handler=…, on_log=…, on_progress=…)
            ├─ _create_roots()   → [Root(file:///…/data)]   (resolve() first!)
            ├─ stdio_client()    → spawns `uv run mcp_server.py`
            ├─ ClientSession(list_roots_callback=…, sampling_callback=…, logging_callback=…)
            │       ▲ THIS LINE decides which capabilities we advertise
            └─ initialize()
                 client ──initialize {capabilities:{roots, sampling}}──► server
                 client ◄──{capabilities:{tools, resources, prompts}}── server
                 client ──notifications/initialized─────────────────────► server
       └─ CliApp.initialize()   → prompts/list + resources/list → tab-completion
       └─ CliApp.run()          → REPL
```

### One turn: "analyse my spending using data/trips.json"

```
CliApp.run()  ── prompt_async("> ")
 └─ CliChat._process_query()          expands /slash and @mentions
 └─ Chat.run()  ─ ITERATION 1
     ├─ tools/list → 8 tools, inputSchema → input_schema
     ├─ chat_stream(messages, system, tools, on_event)
     │     content_block_start(tool_use)   → remember the tool name
     │     content_block_delta(input_json) → buffer JSON fragments
     │     content_block_stop              → render the blue "Tool Call" box
     ├─ stop_reason == "tool_use"
     └─ ToolManager.execute_tool_requests()
          └─ call_tool("summarize_spending", …, progress_callback=render_progress)
                 ▲ passing this is what puts a progressToken in _meta

             ══════════════ SERVER: summarize_spending ══════════════

             (a) ROOTS
                 server ──roots/list──────────────────────► CLIENT
                 server ◄──[file:///…/data]────────────── _handle_list_roots
                 file_url_to_path() strips the leading "/" from "/C:/…"
                 path.resolve().relative_to(root) → OK

             (b) NOTIFICATIONS
                 server ──notifications/message  "Reading trip history…"──► render_server_log
                 server ──notifications/progress 20/100 "reading history"─► render_progress
                 server ──notifications/message  "Found 10 trips…"────────► render_server_log
                 server ──notifications/progress 45/100 "computing totals"─► render_progress

             (c) SAMPLING                        ◄── server becomes the requester
                 server ──sampling/createMessage {messages, maxTokens:600,
                                                  systemPrompt, temperature:0.3}──► CLIENT
                     ┌─ SamplingHandler.handle()
                     │    1. render_sampling_request()  → shows the user the prompt
                     │    2. "Allow this inference? [y/N]"   (asyncio.to_thread)
                     │       └─ declined → return ErrorData(-32001)
                     │    3. SamplingMessage → [{"role","content"}]
                     │    4. claude.chat(system=params.systemPrompt,
                     │                   max_tokens=params.maxTokens,
                     │                   temperature=params.temperature)
                     │           ──────────► Anthropic API
                     │           ◄────────── Message
                     └─ CreateMessageResult(model=…, stopReason=…, content=TextContent)
                 server ◄────────────────────────────────────────────────────
                 (summarize_spending was SUSPENDED this whole time; the
                  original tools/call is still open on the wire)

                 server ──notifications/progress 100/100 "done"──► render_progress
             ══════════════════════════════════════════════════════════

          └─ CallToolResult → tool_result block (tool_use_id must match!)
     ├─ add_user_message(tool_results)      results re-enter as a USER turn
     │
     └─ ITERATION 2
         ├─ chat_stream(...) → model narrates the analysis, no tool calls
         ├─ stop_reason == "end_turn" → break
 └─ back to "> "   (self.messages retained, so follow-ups have context)
```

### Shutdown

```
Ctrl-C → KeyboardInterrupt → CliApp.run() breaks
       → main() returns → AsyncExitStack.__aexit__
       → MCPClient.cleanup() → aclose()
       → session closed, pipes closed, mcp_server.py subprocess terminated
```

---

## Exam notes

**MCP is bidirectional.** Tools/resources/prompts go client→server. Roots,
sampling, and notifications go **server→client**. Notice in the trace above
that `roots/list` and `sampling/createMessage` travel *backwards* while the
`tools/call` request is still open — two requests in flight in opposite
directions on one pipe. That is why MCP needs full duplex JSON-RPC and why
every handler is `async`.

**Capabilities are negotiated at `initialize()`, and the client's callbacks are
what declare them.** In [mcp_client.py](mcp_client.py), `list_roots_callback=None` means
no `roots` capability, which means the server's `ctx.session.list_roots()`
fails. Same for `sampling_callback`. Registering the handler *is* the opt-in.

**Session-scoped vs per-call.**
- `logging_callback` → on `ClientSession`, one handler for every call.
- `progress_callback` → on `call_tool`, **per call**. It makes the SDK attach a
  `progressToken`, and without that token `ctx.report_progress()` is a silent
  no-op. Progress is opt-in by the client on each request; the server cannot
  force it.

**Roots are advisory, not enforced.** The protocol sandboxes nothing. The
sandbox is `is_path_allowed()` in [mcp_server.py](mcp_server.py), and it only works because
the server author remembers to call it before every filesystem touch. Two
details are load-bearing:
- `Path.resolve()` **before** the containment check, or `root/../..` escapes.
- `file_url_to_path()` stripping the leading slash from `/C:/data`, or every
  check fails on Windows.

**Sampling inverts who owns the model.** The server contributes the *prompt*;
the client contributes the *inference, the API key, the model choice and the
bill*. `mcp_server.py` imports no LLM SDK and names no model — it learns which
model ran only from `result.model` in the response.

**Sampling needs consent.** The server is spending the user's tokens on a
prompt the user never wrote. [core/sampling.py](core/sampling.py) shows the prompt and asks
before running, and returns `ErrorData` on refusal rather than raising — so the
server gets a clean JSON-RPC error it can handle.

**Who initiates what:**
| Primitive | Initiated by |
|---|---|
| Tools | the **model** decides to call them |
| Prompts | the **user** invokes them (`/plan_trip`) |
| Resources | the **user or client** attaches them (`@drivers`) |
| Roots / Sampling / Notifications | the **server** asks the client |

**Tool results come back as a `user` turn.** Counter-intuitive but required by
the Anthropic API: the assistant's `tool_use` blocks must be preserved verbatim
in history, and each one paired with a `tool_result` block carrying the same
`tool_use_id`.

**A tool returning `list[dict]` produces one `TextContent` block per element**,
not one block containing a JSON array. `ToolManager` collects them all, so the
model sees everything, but it surprises you the first time you index
`result.content[0]` expecting the whole list.

**`mcp` 2.x is a different API.** `pyproject.toml` pins `mcp[cli]>=1.9.3,<2`
deliberately. In 2.x, `mcp.shared.context.RequestContext` no longer exists
(it is `BaseContext` now) and the `Context` surface differs. Everything in this
repo and the tutorial folders beside it is 1.x.

---

## Differences from the tutorial folders

Three bugs from the originals are fixed here, and worth knowing as traps:

1. **`ToolManager` error status.** The original computes
   `"error" if tool_output and tool_output.isError else "success"` inside the
   `except` block — but `tool_output` is `None` on that path, so genuine
   exceptions were reported to the model with `is_error: False`. Fixed in
   [core/tools.py](core/tools.py).
2. **Sampling dropped `systemPrompt` and `maxTokens`.** The sampling demo's
   callback ignores `params.systemPrompt` entirely, so the server's
   instructions had no effect. [core/sampling.py](core/sampling.py) forwards
   `systemPrompt`, `maxTokens`, `temperature` and `stopSequences`.
3. **No sampling consent.** The original auto-approves silently.

And two additions: an iteration cap on the agentic loop
(`MAX_TOOL_ITERATIONS`), and `CliApp.initialize()` actually doing discovery
instead of being a no-op.
