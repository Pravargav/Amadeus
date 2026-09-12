# 2 Breakpoints — Two Change Frequencies

> **Use when:** the prompt has two distinct stability tiers — something that
> *never* changes (system + tools) and something that changes *per session*
> (an uploaded document, a retrieved corpus, a customer record).

---

## Why a second marker buys anything

**A read can only land on a position where some earlier request wrote a
breakpoint.** With one marker at the very end of the document, a new session
with a different document has no read point at all — it re-processes the system
prompt at full price too.

A second marker splits the prefix into two independently-readable segments:

```
one marker:     [ system ][ document ]◄①        new doc → 0 reads
two markers:    [ system ]◄① [ document ]◄②     new doc → system still reads
```

Earlier breakpoints stay valid read points forever. That is the whole trick.

---

## Block layout

```
╔═══════════════════════════════════════════════════════════╗
║ tools[]                                       ~1,000 tok  ║
╠═══════════════════════════════════════════════════════════╣
║ system[0].text   frozen core prompt           ~4,000 tok  ║
║                                   ◄── ① ephemeral, ttl=1h ║
╚═══════════════════════════════════════════════════════════╝
        ── TIER 1: changes never · 5,000 tok · 1-hour TTL ──
╔═══════════════════════════════════════════════════════════╗
║ messages[0].content[0]  document / retrieved  ~30,000 tok ║
║                                        ◄── ② ephemeral 5m ║
╚═══════════════════════════════════════════════════════════╝
        ── TIER 2: changes per session · 30,000 tok ────────
╭───────────────────────────────────────────────────────────╮
│ messages[0].content[1]  "the varying question"   ~200 tok │
│ NO marker — this is the part that must stay outside       │
╰───────────────────────────────────────────────────────────╯
```

**Longer TTLs must come first.** A 1-hour entry has to appear *before* any
5-minute entry in the prefix. `① 1h → ② 5m` is legal; the reverse is not.

---

## Code

```python
def ask_about(doc_text: str, question: str):
    return client.messages.create(
        model="claude-opus-5",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        tools=TOOLS,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral", "ttl": "1h"},   # ①
        }],
        messages=[{"role": "user", "content": [
            {"type": "text", "text": doc_text,
             "cache_control": {"type": "ephemeral"}},              # ② 5m
            {"type": "text", "text": question},                    # bare
        ]}],
    )
```

---

## Request-by-request

```
SESSION A ─────────────────────────────────────────────────────
REQUEST 1   doc A, question 1
  ① system ........ WRITE   5,000  (1h, 2.0×)
  ② doc A ......... WRITE  30,000  (5m, 1.25×)
  question ........ FULL      200

REQUEST 2   doc A, question 2
  ①+② ............. READ   35,000  (0.1×)
  question ........ FULL      200        ← only the question is new

SESSION B ───────── different document, same system prompt ────
REQUEST 3   doc B, question 1
  ① system ........ READ    5,000  ◄ still a valid read point!
  ② doc B ......... WRITE  30,000
  question ........ FULL      200
```

| Request | creation | read | input |
|---|---:|---:|---:|
| 1 (doc A, q1) | 35,000 | 0 | 200 |
| 2 (doc A, q2) | 0 | 35,000 | 200 |
| 3 (doc B, q1) | 30,000 | **5,000** | 200 |
| 4 (doc B, q2) | 0 | 35,000 | 200 |

Row 3 is the payoff. With a single breakpoint it would read **0**.

---

## The mistake this layout prevents

```
✗ WRONG — marker after the varying question
  messages[0].content = [
      {doc_text},
      {question, cache_control: ephemeral}     ← writes a unique entry
  ]                                              every single request
```

Signature in `usage`: `cache_creation_input_tokens` non-zero on **every**
request while `cache_read_input_tokens` never covers the full shared prefix.
You are paying the 1.25× write premium on 30,000 tokens that are never read
back — a pure surcharge over not caching.

Put the marker at the end of the **shared** portion, not the end of the prompt.

---

## Choosing the TTL per tier

A read refreshes the entry's timer for free, and the lifetime is measured from
the **start** of the request that touches it — so a 4-minute generation leaves
only ~1 minute for the next request to start.

| Start-to-start gap between requests sharing the prefix | TTL |
|---|---|
| Under 5 min (continuous traffic, fast agent turns) | 5-minute — strictly cheaper, every request refreshes it |
| 5–60 min (a user who replies after 20 min) | 1-hour — the only window where the 2× write pays off |
| Over an hour | Neither; re-warm on a schedule or accept the miss |

Here tier 1 is shared across *all* sessions and users, so it survives idle gaps
worth paying 2× for. Tier 2 lives and dies with one session, so 5-minute is right.

Next: [3 breakpoints](03-three-breakpoints.md) — adding a growing conversation.
