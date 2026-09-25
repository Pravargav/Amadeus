
# Bug Fixes

## Bug 1: Schema Layer

### Problem
The tool description is too vague:

```python
"description": "Gets data."
```

This does not clearly communicate when the tool should or should not be used, increasing the risk of incorrect tool selection.

### Fix

Replace the description with one that specifies both intent and exclusions:

```python
"description": "Use this to retrieve full account and contact details for a customer by customer ID. Do not use this for order history or transaction records."
```

---

## Bug 2: Streaming Layer

### Problem
The implementation removes thinking blocks and appends a partial assistant turn even when streaming is interrupted.

```python
assistant_content = [b for b in assemble(blocks) if b["type"] != "thinking"]
messages.append({"role": "assistant", "content": assistant_content})
```

This can lead to incomplete conversation state and broken tool-use sequences.

### Fix

Keep all blocks, including thinking blocks, and only commit the assistant turn if `message_stop` was received.

```python
assistant_content = assemble(blocks)  # keep all blocks including thinking

if stop_seen:
    messages.append({
        "role": "assistant",
        "content": assistant_content
    })
else:
    raise StreamInterruptedError(
        "Discarding partial turn; retry from last complete turn."
    )
```

### Benefits

- Preserves the complete assistant response
- Prevents saving partial turns
- Ensures conversation state remains valid after interruptions

---

## Bug 3: Context Layer

### Problem
Tool-result messages may be added without the corresponding assistant `tool_use` message being safely committed first, violating the expected tool-use/tool-result pairing.

### Fix

No separate code change is required.

Once Bug 2 is fixed, the complete assistant message (including the `tool_use` block) is appended before any `tool_result` message is added.

### Outcome

The required message sequence becomes:

```text
assistant(tool_use)
↓
user(tool_result)
```

This satisfies the tool-calling protocol and maintains valid conversation history.

---

## Bug 4: Memory Layer

### Problem

The current implementation concatenates all previous session transcripts into the prompt:

```python
def build_session_history(prior_sessions):
    full_history = []
    for session in prior_sessions:
        full_history.extend(session["messages"])
    return full_history
```

Issues:

- Context window grows indefinitely
- Token costs increase over time
- Retrieval becomes inefficient
- Older content may crowd out relevant context

### Fix

Store session history externally and inject only a summary of the most recent session.

```python
def build_session_history(prior_sessions):
    if not prior_sessions:
        return []

    summary = load_session_summary(
        prior_sessions[-1]["id"]
    )  # from external store

    return [{
        "role": "user",
        "content": f"Session context: {summary}"
    }]
```

### Benefits

- Prevents unbounded context growth
- Reduces token usage
- Improves scalability
- Maintains relevant historical context through summaries

