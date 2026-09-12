# 3 Breakpoints — Static + Session + Moving Tail

> **Use when:** tiers 1 and 2 from the previous file, *plus* a conversation that
> grows turn over turn. The third marker is not fixed to a position — it **moves
> forward** with the conversation on every request.

---

## The new idea: a moving breakpoint

Markers ① and ② stay pinned. Marker ③ is re-placed on the last content block of
the most-recently-appended turn each request. Because the previous request's ③
already wrote an entry at the previous turn's end, hits accrue incrementally as
the conversation grows.

```
turn 1 request:  [①system][②docs][ u1 ]◄③
turn 2 request:  [①system][②docs][ u1   a1   u2 ]◄③
                                  └── read ──┘└ write ┘
turn 3 request:  [①system][②docs][ u1 a1 u2   a2 u3 ]◄③
                                  └─── read ───┘└ write┘
```

Moving the marker is **not** an invalidator. A block that was marked on a
previous request is still a cache hit even though the marker has moved past it.

---

## Block layout

```
╔═══════════════════════════════════════════════════════════╗
║ tools[]  +  system[0].text                    ~5,000 tok  ║
║                                   ◄── ① ephemeral, ttl=1h ║
╠═══════════════════════════════════════════════════════════╣
║ messages[0]  retrieved docs / knowledge base ~30,000 tok  ║
║                                   ◄── ② ephemeral, ttl=1h ║
╠═══════════════════════════════════════════════════════════╣
║ messages[1..n]  conversation history                      ║
║   u1 / a1 / u2 / a2 / ... / u_n           grows each turn ║
║                                 ◄── ③ ephemeral 5m, MOVES ║
╚═══════════════════════════════════════════════════════════╝
                    (nothing after ③ — the new turn IS the tail)
```

Ordering rule still holds: the two 1-hour entries sit ahead of the 5-minute one.

---

## Code

```python
import copy

def turn(history: list, user_text: str):
    """history: list of Anthropic.MessageParam, mutated in place."""
    history.append({"role": "user", "content": [{"type": "text", "text": user_text}]})

    # ③ — strip any previous marker, re-place on the current last block.
    msgs = copy.deepcopy(history)
    for m in msgs:
        if isinstance(m["content"], list):
            for b in m["content"]:
                b.pop("cache_control", None)
    msgs[-1]["content"][-1]["cache_control"] = {"type": "ephemeral"}

    resp = client.messages.create(
        model="claude-opus-5",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        tools=TOOLS,
        system=[{"type": "text", "text": SYSTEM_PROMPT,
                 "cache_control": {"type": "ephemeral", "ttl": "1h"}}],   # ①
        messages=[KB_MESSAGE_WITH_MARKER_2] + msgs,                       # ②
    )
    history.append({"role": "assistant", "content": resp.content})
    return resp
```

Append `resp.content` — the block list, not `resp.content[0].text`. Dropping
thinking blocks or tool_use blocks rewrites the history and breaks ③.

---

## Request-by-request

```
TURN 1
  ① system ......... WRITE   5,000
  ② knowledge base . WRITE  30,000
  ③ u1 ............. WRITE     300

TURN 2
  ①+② ............. READ   35,000
  ③ u1+a1 .......... READ      300   ← written by turn 1's ③
      a1 + u2 ...... WRITE     900   ← only the delta
  (nothing at full price)

TURN 3
  ①+②+③ ........... READ   36,200
      a2 + u3 ...... WRITE   1,100
```

| Turn | creation | read | input |
|---|---:|---:|---:|
| 1 | 35,300 | 0 | 0 |
| 2 | 900 | 35,300 | 0 |
| 3 | 1,100 | 36,200 | 0 |
| 4 | 1,000 | 37,300 | 0 |

**This is the healthy-loop signature:** `read` grows monotonically and covers
the whole prior prefix; `creation` stays small — roughly the previous assistant
output plus the newly appended input; `input_tokens` is just whatever tail sits
after the last marker (zero here, since ③ is on the last block).

If instead `creation` is near the **full conversation size every turn**, the
prefix is being rewritten upstream. See the failure modes below.

---

## Three ways this layout silently breaks

**1 — Editing an earlier turn.** Any history rewrite (trimming old turns,
re-summarizing turn 2, deleting an injected reminder) changes bytes inside the
overlap and kills ③ from that point on. Keep history **append-only**. To add an
operator instruction mid-conversation, append a `role: "system"` message instead
of editing top-level `system`:

```python
messages=[..., {"role": "user", "content": "..."},
          {"role": "system", "content": "Terse mode — under 40 words."}]
```
Available on Claude Opus 5, Opus 4.8, Fable 5, Fable 5.1, Mythos 5/5.1 — **not
on Sonnet 5**, which returns 400 `role 'system' is not supported on this model`.
Editing top-level `system` instead would invalidate ① and everything after it.

**2 — The 20-block lookback.** Each breakpoint walks back at most **20
positions** to find a prior entry. A run of consecutive `tool_use` blocks counts
as one position, and so does a run of consecutive `tool_result` blocks — so
parallel tool calls are safe. A long *sequential* tool loop in one turn is not:
once a turn appends more than 20 positions, ③ can't see turn N-1's entry and
silently rewrites the entire conversation with byte-identical payloads. Fix by
placing an intermediate marker every ~15 positions.

**3 — Thinking-block stripping (model-specific).** On Fable 5/5.1, Mythos 5/5.1,
Opus 4.5+, and Sonnet 4.6+, prior-turn thinking blocks are preserved, so ③ holds.
On earlier Opus/Sonnet models and all Haiku through 4.5, a plain user message
following tool use strips previously-cached thinking blocks server-side, and
everything after the first stripped block falls out of cache — a `creation`
spike that no payload diff can explain. Rule this out from the model before
hunting for a bug.

Also: toggling `thinking` or changing `output_config.effort` between requests
invalidates the messages cache on **every** model. Pin both per route.

Next: [4 breakpoints](04-four-breakpoints.md) — the full agent loop, and what to
do when you have more stability tiers than slots.
