# 4 Breakpoints — The Ceiling

> **4 is the hard maximum per request.** A fifth `cache_control` is a 400.
> Use all four only when you genuinely have four different change frequencies.
> Spending a slot on a boundary that never moves independently is a wasted slot.

---

## Why split tools away from system

Previous files put ① on the last system block, which caches `tools` + `system`
together. That is fine until the system prompt itself changes — a prompt-version
rollout, an A/B test, a per-tenant preamble.

The API has three cache tiers, and a change only invalidates its own tier and
below. Read this as **"does this cache survive the change?"**

| Change | Tools cache | System cache | Messages cache |
|---|:---:|:---:|:---:|
| Tool definitions (add/remove/reorder) | ✗ | ✗ | ✗ |
| Model switch | ✗ | ✗ | ✗ |
| `speed`, web-search, citations toggle | **survives** | ✗ | ✗ |
| **System prompt content** | **survives** | ✗ | ✗ |
| `tool_choice`, images | **survives** | **survives** | ✗ |
| Message content | **survives** | **survives** | ✗ |

So a system-prompt change leaves the tools cache intact — but **a read can only
land where an earlier request wrote a breakpoint**. Without a marker at the end
of the tool list, that surviving tier has no read point and you re-process the
tools at full price anyway. Marker ① is how you collect on it.

---

## Block layout

```
╔═══════════════════════════════════════════════════════════╗
║ ① tools[-1]                 1,500 tok   changes: monthly  ║
║                                            ephemeral 1h   ║
╠═══════════════════════════════════════════════════════════╣
║ ② system[-1]                6,000 tok   changes: weekly   ║
║                                            ephemeral 1h   ║
╠═══════════════════════════════════════════════════════════╣
║ ③ messages[0] context      25,000 tok   changes: daily    ║
║    policy docs, schema, retrieved corpus   ephemeral 1h   ║
╠═══════════════════════════════════════════════════════════╣
║ ④ messages[-1].content[-1]    grows     changes: per turn ║
║    conversation + tool results             ephemeral 5m   ║
║                                              ◄── MOVES    ║
╚═══════════════════════════════════════════════════════════╝
   1h ────────────────────────────────────► 5m
   (longer TTLs must appear before shorter ones)
```

---

## Code

```python
TOOLS = sorted(MY_TOOLS, key=lambda t: t["name"])
TOOLS[-1] = {**TOOLS[-1], "cache_control": {"type": "ephemeral", "ttl": "1h"}}  # ①

SYSTEM = [
    {"type": "text", "text": PERSONA},
    {"type": "text", "text": RULES,
     "cache_control": {"type": "ephemeral", "ttl": "1h"}},                     # ②
]

CONTEXT_MSG = {"role": "user", "content": [
    {"type": "text", "text": POLICY_DOCS,
     "cache_control": {"type": "ephemeral", "ttl": "1h"}},                     # ③
]}

def step(history):
    msgs = place_moving_marker(history)          # ④ — see 03-three-breakpoints.md
    return client.messages.create(
        model="claude-opus-5",
        max_tokens=64000,
        thinking={"type": "adaptive"},
        tools=TOOLS,
        system=SYSTEM,
        messages=[CONTEXT_MSG] + msgs,
    )
```

---

## What each tier earns you

```
NORMAL TURN                    ① READ   ② READ   ③ READ   ④ READ + small write
SYSTEM PROMPT ROLLOUT          ① READ   ② write  ③ write  ④ write
DAILY CONTEXT REFRESH          ① READ   ② READ   ③ write  ④ write
TOOL ADDED / MODEL SWITCHED    ① write  ② write  ③ write  ④ write
```

Row 2 is what slot ① paid for: 1,500 tokens read instead of re-processed on
every request for the rest of the rollout. Row 4 has no escape — tool-definition
changes and model switches force a full rebuild (caches are model-scoped).

| Turn | creation | read | input |
|---|---:|---:|---:|
| 1 | 32,800 | 0 | 0 |
| 2 | 1,400 | 32,800 | 0 |
| 3 | 1,600 | 34,200 | 0 |
| after system-prompt rollout | 31,300 | **1,500** | 0 |

---

## Alternative use of the 4th slot: leapfrog the tail

If your tiers are only three deep but turns are long (sequential tool loops),
spend the 4th slot on a **second rolling marker** one turn behind:

```
turn N request:   [①tools][②system][③ctx][ ...history... ]◄④a  ◄④b
                                            previous turn ┘      └ current turn
```

④a guarantees a read point that survives even if ④b's placement lands more than
20 positions past the previous entry. This is the standard defence for agent
loops with long tool runs.

---

## When you have more than four tiers

- **Merge the two least-independent tiers.** If context and system almost always
  change together, give them one marker.
- **Top-level automatic caching consumes a slot.** `cache_control` on
  `messages.create()` auto-places on the last cacheable block and moves forward
  as the conversation grows. Two documented 400s: all four slots already taken
  by explicit markers, and an explicit marker on the last block with a *different*
  TTL than the top-level field. The robust agent-loop combination is **one
  explicit marker on the static system prefix + top-level automatic caching for
  the tail** — the expensive shared part gets a guaranteed read point, and you
  do no marker bookkeeping for the conversation.
- **Fork operations must reuse the parent's exact prefix.** Summarizers,
  compactors, and sub-agents that rebuild `system` / `tools` / `model` with any
  difference miss the parent's cache entirely. Copy all three verbatim and append
  fork-specific content at the end.

---

## Verifying it works — the only thing that actually proves it

```python
r1 = step(history); r2 = step(history)
assert r2.usage.cache_read_input_tokens > 0
print(r2.usage.cache_creation)   # {ephemeral_5m_input_tokens, ephemeral_1h_input_tokens}
```

Make that a standing integration-test assertion, not a one-time check. The
costliest caching failure is silent: requests keep succeeding, the bill is just
higher. The typical shape is a **regression** — caching worked when written,
then a new dynamic field in the system prompt or a tool list that stopped being
deterministic broke it, and nobody noticed for months.

**Localising a break.** The `usage` fields tell you *that* the prefix broke, not
where. Log several consecutive full request bodies and diff adjacent pairs:
strip `cache_control` markers first (the moving marker always differs and is not
an invalidator), then the first divergence *inside the overlapping region* is
the invalidation point. On the Claude API, cache diagnostics does this
server-side — send beta header `cache-diagnosis-2026-04-07` on **every** request
(fingerprints are only stored for requests that carried it, so a retrofit fails
with `previous_message_not_found`), pass the prior response's `id` as
`diagnostics.previous_message_id`, and `response.diagnostics` names which of
model / system / tools / message history diverged.

**Expected writes you did not ask for:** server tools such as web search insert
a 5-minute cache write after tool results when the request already uses caching.
Not an invalidator.

---

## Parallel requests never read each other's writes

A cache entry becomes readable only once the first response **begins streaming**.
N concurrent requests with identical prefixes all pay full price.

```
✗  fire 20 requests at once        → 20 writes, 0 reads
✓  fire 1 → await first token      → then fire 19  → 1 write, 19 reads
```

Same arithmetic for multi-agent fan-out: N workers each assembling a slightly
different prompt over the same context write N entries and read none of each
other's. When input cost dominates, fewer lanes over a byte-identical shared
prefix — or one worker making N sequential passes — turns those writes into reads.

Back to: [1](01-one-breakpoint.md) · [2](02-two-breakpoints.md) · [3](03-three-breakpoints.md)
