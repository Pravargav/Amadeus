# bookstore-agent — tool schemas vs tool functions

A ~250-line bookstore assistant that exists to make one distinction concrete: the
**schema** is data you send to Claude, the **function** is code that runs in your
process, and they are wired together only by a matching name string.

Three tools over a seeded SQLite catalog:

| Tool | Kind | Why it's here |
|---|---|---|
| `search_books` | read-only | optional parameter with a default |
| `check_stock` | read-only | raises on bad input → `is_error` tool_result |
| `place_order` | **mutates stock** | the approval gate, and an `enum`-constrained arg |

## Layout

The split is the point, so the two halves live in separate files:

```
inventory.py       plain SQLite logic. Knows nothing about Claude.
tool_functions.py  THE FUNCTION HALF -- runs locally. Claude never sees it.
tool_schemas.py    THE SCHEMA HALF   -- pure data. The only part Claude sees.

agent_manual.py    approach A: hand-written schemas + explicit agentic loop
agent_runner.py    approach B: @beta_tool, schema derived from the signature

show_schemas.py    prints both schemas side by side   (no API key needed)
test_contract.py   asserts the two halves agree       (no API key needed)
```

## Run it

```bash
pip install -r requirements.txt
python inventory.py        # seed bookstore.db
```

These two need no API key and no network — start here:

```bash
python show_schemas.py
```

```bash
python test_contract.py
```

These two call the API (`export ANTHROPIC_API_KEY=...`, or `ant auth login`):

```bash
python agent_manual.py "do you have anything by Orwell?"
```

```bash
python agent_runner.py "I'd like 2 copies of 1984"
```

Both print each tool call as it happens. The second will stop and ask you to
approve the order at the terminal.

## What `show_schemas.py` demonstrates

For each tool it prints the hand-written schema, the schema `@beta_tool` derived
from the same function, and then **the function's actual return value, called
directly with no model in the loop**. That last part is the whole lesson: the
functions work fine on their own. Claude is a caller, not a runtime.

The two schemas come out nearly identical. The differences:

- `"strict": true` only appears in the hand-written one. It's a top-level field
  on the tool (not inside `input_schema`, and not on `tool_choice`), so there's
  nothing in a function signature for the decorator to read it from.
- `"title"` per property only appears in the derived one. The API ignores it;
  you just pay a few input tokens for it on every request.
- `"enum": [1,2,3,4,5]` appears in **both**, because `agent_runner.place_order`
  is annotated `quantity: Literal[1, 2, 3, 4, 5]`. A plain `int` would have
  produced an unbounded integer and pushed that check out to runtime.

## Things worth noticing in the code

**The docstring is not documentation.** In `agent_runner.py` it *becomes* the
`description` Claude reads, and the `Args:` entries become the per-property
descriptions. Write it for the model: each one says *when* to call the tool, not
just what it does. Recent Opus models reach for tools conservatively, so explicit
trigger conditions measurably raise the should-call rate. Keep the summary on one
line — a multi-line summary paragraph comes through with a stray `\n\n` in it.

**The approval gate is in the function, not the schema.**
`tool_functions.place_order` calls `APPROVAL_HOOK` before touching the database.
A schema description saying "confirm with the user first" is a suggestion to a
language model, not access control. This is also why it's safe to let the Tool
Runner execute tools automatically — the gate is somewhere Claude can't talk its
way past. Declining returns a normal result rather than raising, which tells
Claude the call was understood and refused, so it reports back instead of
retrying.

**Failures go back as `tool_result` with `is_error: true`.** See
`execute_tool` in `agent_manual.py`. Every `tool_use` block needs a matching
`tool_result` with the same `tool_use_id` — dropping one because the tool threw
breaks the conversation.

**`tool_input` is parsed before you get it.** Never string-match the serialized
JSON; escaping of unicode and forward slashes varies between models.

**All tool results go back in one user message.** Claude can request several
tools at once. Splitting the results across multiple messages quietly teaches it
to stop making parallel calls.

## The failure mode this split creates

Nothing checks that a schema matches the function it describes. Rename a
parameter in `tool_functions.py` and `tool_schemas.py` keeps advertising the old
name; Claude then sends a perfectly well-formed `tool_use` your code can't
service, and it isn't Claude's mistake. `test_contract.py` checks the seam —
name dispatchable, no schema property the function won't accept, no required
parameter hidden from Claude, `required` agreeing with the defaults,
`strict: true` having its prerequisites, and nothing implemented but unpublished.

Verified: injecting a renamed property, a wrongly-required parameter, and an
unpublished function makes it report all three and exit 1.

`agent_runner.py` needs none of that — a generated schema can't drift from the
signature it was generated from. Which is the practical argument for the Tool
Runner over hand-written dicts, more than the saved lines of loop code.

## Which approach to use

Ship `agent_runner.py`. Read `agent_manual.py` once to see what the runner is
doing, then don't hand-write the loop unless you need something it can't express
— the runner yields each assistant message *before* the tools run, so approval
gates, logging, retries, and rewriting results are all still available to you.

Notes on the API calls themselves: model is `claude-opus-5` with
`thinking: {"type": "adaptive"}`; `agent_manual.py` also passes the server-side
refusal `fallbacks` so a declined request retries on another model instead of
returning an unusable turn, and both bound their loops (`range(10)` /
`max_iterations=10`) rather than looping unbounded against a model.

Written against `anthropic` 1.5.0 and Python 3.14. `@beta_tool` and
`tool_runner` are beta surfaces (`client.beta.messages.*`).
