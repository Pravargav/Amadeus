

# Broken Code Shown to the Learner

```python
def call_with_retry(make_call, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            return make_call()
        except Exception:
            time.sleep(0)
    raise RetryBudgetExhausted()
```

---

# Defect Analysis

The implementation has several problems:

1. **No backoff between retries**
   - `time.sleep(0)` causes retries to happen immediately.
   - This can quickly exhaust retry budgets and worsen rate-limiting situations.

2. **Retries all exceptions**
   - The code catches every exception using `except Exception`.
   - Some errors (such as invalid requests or authentication failures) are terminal and should not be retried.

3. **Makes rate limits worse**
   - When a rate limit is hit, each immediate retry counts as another request.
   - This can deepen the rate limit instead of allowing time for it to reset.

---

# Corrected Version

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
                raise  # Fail fast on terminal errors

            time.sleep(
                min(cap, 2 ** attempt) + random.uniform(0, 1)
            )

    raise RetryBudgetExhausted()
```

---

# Key Fixes

### 1. Honor the `Retry-After` Header

When a rate limit response includes a `Retry-After` header, the client waits for the specified duration before retrying.

```python
wait = e.response.headers.get("retry-after")
```

If the header is not available, the code falls back to exponential backoff with jitter.

---

### 2. Use Exponential Backoff

The delay grows with each retry attempt:

```python
min(cap, 2 ** attempt)
```

Examples:

| Attempt | Delay (before jitter) |
|----------|----------------------|
| 1 | 1 second |
| 2 | 2 seconds |
| 3 | 4 seconds |
| 4 | 8 seconds |
| 5 | 16 seconds |

The `cap` prevents delays from growing indefinitely.

---

### 3. Add Jitter

A small random delay is added:

```python
random.uniform(0, 1)
```

This prevents many clients from retrying at exactly the same moment and creating another spike in traffic.

---

### 4. Fail Fast on Terminal Errors

Some HTTP status codes are not recoverable through retries:

- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

For these cases:

```python
if not is_retriable(e.status_code):
    raise
```

The exception is re-raised immediately instead of wasting retry attempts.

