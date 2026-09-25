## Failure Handling: The Call That Never Failed in Development

### Core Lesson

One of the biggest mistakes developers make is assuming that because an API call never failed during development, it will never fail in production.


---

### What Happened in the Story?

A developer created a feature that called the Anthropic API for every item in a batch.

The implementation was simple:

```python
results = []

for item in batch:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=msg(item)
    )

    results.append(resp.content)
```

The code assumed:

```text
Every API call succeeds.
Every response returns HTTP 200.
No errors occur.
```

Since development traffic was very small, this assumption appeared correct.

The feature worked perfectly during testing.

---

### What Happened After Deployment?

When the feature reached production, user traffic increased.

Eventually the application encountered:

```text
429 Rate Limit Exceeded
```

Instead of handling the error, the application:

```text
Raised an unhandled exception.
```

This caused:

```text
Single API call failure
        ↓
Unhandled exception
        ↓
Entire request fails
        ↓
User sees broken feature
```

From the user's perspective:

```text
The application simply stopped working.
```

---

### Why Development Did Not Reveal the Problem

The API was called only a few times during testing.

Example:

```text
10 requests
20 requests
50 requests
```

This volume was nowhere near the rate limit.

Therefore:

```text
Failure path never executed.
```

The developer never saw:

- 429 responses
- Timeout errors
- Transient network failures

As a result:

```text
No error handling code was written.
```

The real test happened only after release.

---

### The Wrong Fix

The developer's first reaction was:

```text
Retry immediately.
```

Example:

```python
while True:
    try:
        return api_call()
    except Exception:
        continue
```

This is extremely dangerous.

---

### Why Immediate Retries Make Things Worse

Suppose the API returns:

```text
429 Rate Limit
```

This means:

```text
Too many requests currently.
```

Immediate retries generate:

```text
Request
→ 429

Instant retry
→ 429

Instant retry
→ 429

Instant retry
→ 429
```

Now the application is sending even more requests against the same limit.

The result:

```text
Rate limit becomes worse.
```

This is often called a:

```text
Retry Storm
```

Where retries create additional load, generating even more failures.

---

### Correct Solution

The failure must first be classified.

Ask:

```text
Would the same request succeed later?
```

For a 429:

```text
Yes
```

Therefore:

```text
429 = Retriable
```

Since it is retriable, the system should:

1. Wait
2. Retry later
3. Limit the number of attempts
4. Respect Retry-After when provided

---

### Proper Recovery Flow

```text
API Call
    ↓
429 Rate Limit
    ↓
Check Retry-After Header
    ↓
Wait Required Time
    ↓
Retry
    ↓
Success
```

If there is no Retry-After header:

```text
Use exponential backoff
```

---

### Exponential Backoff

Instead of retrying immediately:

```text
Retry 1 → Wait 1s
Retry 2 → Wait 2s
Retry 3 → Wait 4s
Retry 4 → Wait 8s
```

A cap is usually applied:

```text
Maximum 3–5 attempts
```

Benefits:

- Reduces pressure on the API
- Gives the service time to recover
- Prevents retry storms

---

### Add Jitter

Many systems retry at the same time.

Without jitter:

```text
1000 clients wait 4 seconds
1000 clients retry simultaneously
```

This creates another spike.

With jitter:

```text
Client A waits 4.2s
Client B waits 3.7s
Client C waits 5.1s
```

Requests become distributed across time.

This reduces load concentration.

---

### Better Production-Safe Example

```python
import time
import random

MAX_RETRIES = 5

for attempt in range(MAX_RETRIES):
    try:
        return client.messages.create(...)
    
    except RateLimitError:
        delay = (2 ** attempt) + random.random()
        time.sleep(delay)

raise Exception("Retry limit exceeded")
```

This implementation:

✅ Uses retries

✅ Uses exponential backoff

✅ Includes jitter

✅ Caps retry attempts

✅ Avoids infinite loops

---


### Why Did the Immediate Retry Fail?

Because:

```text
Every retry counted as another request.
```

The application increased the load instead of reducing it.

---

### Correct Handling Pattern

```text
1. Detect failure
2. Classify as retriable or terminal
3. If retriable:
       - Honor Retry-After
       - Apply exponential backoff
       - Add jitter
       - Limit retries
4. If terminal:
       - Fail fast
       - Surface the error
```

If a scenario describes:

```text
429 Rate Limit
529 Overloaded
500 Internal Error
502 Bad Gateway
503 Service Unavailable
504 Timeout
```

Your answer should immediately include:

```text
Retriable Failure
+
Exponential Backoff
+
Jitter
+
Retry-After Header
+
Capped Retry Attempts
```

If the scenario describes:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
```

Your answer should be:

```text
Terminal Failure
+
Fail Fast
+
No Retry
```

