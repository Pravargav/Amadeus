# 1 Breakpoint — Cache the Static Prefix

> **Use when:** you have one big chunk of content that is byte-identical on every
> request (system prompt + tool definitions), and everything else varies.
> This covers the majority of real applications.

---

## The invariant behind all four files

Prompt caching is a **prefix match**. The cache key is the exact bytes of the
rendered prompt up to each `cache_control` marker. One changed byte at position
N invalidates every breakpoint at position >= N.

Render order is fixed:

```
      ┌──────────┐     ┌──────────┐     ┌────────────┐
      │  tools   │ ──► │  system  │ ──► │  messages  │
      └──────────┘     └──────────┘     └────────────┘
        position 0                          position N
      <──────────────── stable ────── volatile ──────►
```

A marker on the **last system block** therefore caches `tools` + `system`
together — you do not need a separate marker on the tools.

---

## Block layout

```
╔═══════════════════════════════════════════════════════════╗
║ BLOCK 1   tools[]                             ~1,000 tok  ║
║           (deterministic, sorted by name)                 ║
╠═══════════════════════════════════════════════════════════╣
║ BLOCK 2   system[0].text                      ~4,000 tok  ║
║           persona, rules, few-shot examples               ║
║                                        ◄── ① cache_control ║
╚═══════════════════════════════════════════════════════════╝
            ─────────── CACHED PREFIX: 5,000 tok ───────────
╭───────────────────────────────────────────────────────────╮
│ BLOCK 3   messages[0]  "the user's question"     ~200 tok │
│           differs every request → NO marker               │
╰───────────────────────────────────────────────────────────╯
```

---

## Code

```python
import anthropic

client = anthropic.Anthropic()

TOOLS = sorted(MY_TOOLS, key=lambda t: t["name"])   # deterministic order

def ask(question: str):
    return client.messages.create(
        model="claude-opus-5",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        tools=TOOLS,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,                       # frozen — no f-strings
            "cache_control": {"type": "ephemeral"},      # ① 5-minute TTL
        }],
        messages=[{"role": "user", "content": question}],
    )
```

---

## Request-by-request

```
REQUEST 1  (cold)
  tools + system ......... WRITE  5,000 tok   ← paid 1.25×
  question ............... FULL     200 tok

REQUEST 2  (warm)
  tools + system ......... READ   5,000 tok   ← paid 0.1×
  question ............... FULL     200 tok

REQUEST 3..N  (warm)
  identical to request 2 — each read refreshes the 5-min timer
```

| Request | `cache_creation_input_tokens` | `cache_read_input_tokens` | `input_tokens` |
|---|---:|---:|---:|
| 1 | 5,000 | 0 | 200 |
| 2 | 0 | 5,000 | 200 |
| 3 | 0 | 5,000 | 200 |

Total prompt size is always `input + creation + read`. `input_tokens` alone is
only the uncached remainder — never read it as "my prompt size".

---

## Cost (Claude Opus 5: $5.00/MTok input, write 1.25× = $6.25, read 0.1× = $0.50)

| | Request 1 | Request 2+ |
|---|---:|---:|
| Cached | $0.0323 | $0.0035 |
| Uncached | $0.0260 | $0.0260 |

Request 1 costs **24% more** than not caching at all. Request 2 costs **7.4×
less**. Break-even at the 5-minute TTL is **two requests** (1.25× + 0.1× = 1.35×
vs 2.0× uncached); at the 1-hour TTL it is **three** (2× + 0.2× = 2.2× vs 3×).

---

## Gotchas at 1 breakpoint

- **Minimum cacheable prefix is model-dependent and not monotonic.** 512 tokens
  on Claude Opus 5 / Fable 5 / Fable 5.1; 1,024 on Opus 4.8 / Sonnet 5 / Sonnet 4.6;
  2,048 on Opus 4.7; **4,096 on Opus 4.6, Opus 4.5, and Haiku 4.5.** Below the
  minimum there is no error — just `cache_creation_input_tokens: 0`.
- **Never interpolate into the system prompt.** `f"Today is {date.today()}"`,
  a session ID, or a `if flag:` branch sits at the front of the prefix and makes
  everything after it uncacheable. Put dynamic context in `messages` instead.
- **Serialize tools deterministically.** `json.dumps(d, sort_keys=True)`,
  no iteration over a `set`. Tools render at position 0; a reordered tool list
  rebuilds the whole cache.
- **The simpler alternative:** top-level `cache_control` on `messages.create()`
  auto-places the marker on the last cacheable block. Good for plain multi-turn
  chat — but it lands *after* your varying question here, writing a fresh entry
  every request that is never read back. For this layout, place it explicitly.

Next: [2 breakpoints](02-two-breakpoints.md) — when the prompt has two different
change frequencies.
