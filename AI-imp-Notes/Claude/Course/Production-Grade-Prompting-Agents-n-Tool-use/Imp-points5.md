-----------------
# Cumulative Production-Hardening Task: Corrected Version

The application contains defects in three different layers:

1. **Security/Guardrail Layer** → Prevent path traversal and unauthorized writes.
2. **Error-Handling/Cost Layer** → Add proper retry behavior with exponential backoff.
3. **Eval/Test Layer** → Ensure the function is covered by automated evaluation on a graded holdout set.

---

# Corrected Application

```python
def answer(question, page_url):
    page = fetch(page_url)  # still untrusted

    # Security fix:
    # Never allow untrusted content to control filesystem paths.
    notes = read_file("/workspace/input/notes")

    write_file(
        "/workspace/output/summary.txt",
        summarize(page)
    )
    # PreToolUse/guardrail hook enforces:
    # - writes only under /workspace/output
    # - audit logging of write operations

    # Error-handling fix:
    # Use a hardened retry helper with:
    # - Retry-After support
    # - exponential backoff + jitter
    # - fail-fast on terminal errors
    resp = call_with_retry(
        lambda: client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=msg(question)
        )
    )

    return resp.content[0].text
```

---

# Fix 1: Security / Guardrail Layer

### Original Defect

```python
write_file(page.suggested_path, summarize(page))
```

### Problem

`page.suggested_path` originates from untrusted fetched content. A malicious page could supply a path such as:

```text
../../../etc/passwd
```

or

```text
/workspace/secrets/api_key.txt
```

causing unauthorized file writes.

### Fix

```python
write_file(
    "/workspace/output/summary.txt",
    summarize(page)
)
```

Additionally:

```python
# Guardrail
allow_write_only("/workspace/output")
```

### Runtime Impact

- Prevents path traversal.
- Enforces a strict write boundary.
- Ensures external content cannot choose write destinations.

---

# Fix 2: Error-Handling / Cost Layer

### Original Defect

```python
for i in range(5):
    try:
        resp = client.messages.create(...)
        break
    except Exception:
        time.sleep(0)
```

### Problems

- Retries every exception.
- No distinction between retriable and terminal errors.
- `time.sleep(0)` causes immediate retries.
- Can worsen rate limits and increase costs.

### Fix

```python
def call_with_retry(make_call, max_attempts=5, cap=30):
    for attempt in range(max_attempts):
        try:
            return make_call()

        except anthropic.RateLimitError as e:
            wait = e.response.headers.get("retry-after")

            if wait is None:
                wait = min(cap, 2 ** attempt) + random.uniform(0, 1)

            time.sleep(float(wait))

        except anthropic.APIStatusError as e:
            if not is_retriable(e.status_code):
                raise

            time.sleep(
                min(cap, 2 ** attempt) + random.uniform(0, 1)
            )

    raise RetryBudgetExhausted()
```

Used as:

```python
resp = call_with_retry(
    lambda: client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=msg(question)
    )
)
```

### Runtime Impact

- Honors `Retry-After`.
- Uses exponential backoff.
- Adds jitter to avoid retry storms.
- Fails fast on unrecoverable errors.
- Reduces waste and rate-limit amplification.

---

# Fix 3: Eval / Test Layer

### Original Defect

No automated evaluation exists.

### Problem

The application can regress without detection when:

- prompts change,
- model versions change,
- retry behavior changes,
- security logic changes.

### Fix

Create a graded holdout evaluation suite and run it on every change.

Example:

```python
EVAL_CASES = [
    {
        "question": "What is the return policy?",
        "expected": "30 days"
    },
    {
        "question": "Summarize the article",
        "expected_contains": "key findings"
    }
]

score = run_eval(answer, EVAL_CASES)

assert score >= 0.95
```

### Runtime Impact

- Detects regressions before deployment.
- Provides an objective quality baseline.
- Ensures future changes do not silently degrade behavior.
