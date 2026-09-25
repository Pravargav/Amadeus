## Failure Handling: Surviving Production Failure (Claude Developer Certification)

### Why Failure Handling Matters

In development, most workflows run under ideal conditions. In production, however, systems encounter rate limits, network interruptions, overloaded services, malformed requests, authentication failures, and tool execution errors.

A resilient Claude application is not one that never fails. It is one that knows exactly how to react when failure occurs.

The first and most important decision is:

> Is the failure retriable or terminal?

Everything else depends on this classification.

---

### Retriable vs Terminal Errors

Ask a simple question:

> "Would sending the exact same request again later reasonably succeed?"

If the answer is **yes**, the error is retriable.

If the answer is **no**, the error is terminal.

#### Retriable Errors

These failures are temporary and often resolve with time.

Examples:

- Rate limit reached (429)
- Service overloaded (529)
- Internal server error (500)
- Bad gateway (502)
- Service unavailable (503)
- Gateway timeout (504)
- Temporary network interruption
- Connection reset

Because these conditions are temporary, retrying later may succeed.

```python
RETRIABLE = {429, 529, 500, 502, 503, 504}

def is_retriable(status):
    return status in RETRIABLE
```

---

#### Terminal Errors

These failures are caused by the request itself and will continue failing until the request is fixed.

Examples:

- Bad request (400)
- Authentication failure (401)
- Permission denied (403)
- Resource not found (404)

Retrying these errors wastes:

- Time
- API budget
- Retry attempts
- User latency

```python
TERMINAL = {400, 401, 403, 404}
```

---

### Why Correct Classification Is Critical

#### Correctly Retrying a Retriable Error

Example:

```text
429 Rate Limit Exceeded
```

The service is temporarily restricting requests.

Waiting and retrying later is likely to work.

Result:

✅ Request eventually succeeds.

---

#### Incorrectly Retrying a Terminal Error

Example:

```text
400 Bad Request
```

The request body is malformed.

Retrying the same request gives:

```text
400
400
400
400
```

Nothing improves.

Result:

❌ Wasted time  
❌ Higher latency  
❌ Unnecessary API usage

---

#### Incorrectly Treating a Retriable Error as Terminal

Example:

```text
503 Service Unavailable
```

If you immediately fail instead of retrying:

```text
User request fails
```

Even though the service may have recovered seconds later.

Result:

❌ Lost availability

---

### Important HTTP Status Classifications

| Status | Meaning | Action |
|----------|----------|----------|
| 429 | Rate Limited | Retry |
| 529 | Service Overloaded | Retry |
| 500 | Internal Error | Retry |
| 502 | Bad Gateway | Retry |
| 503 | Service Unavailable | Retry |
| 504 | Gateway Timeout | Retry |
| 400 | Bad Request | Fail Fast |
| 401 | Unauthorized | Fail Fast |
| 403 | Forbidden | Fail Fast |
| 404 | Not Found | Fail Fast |

---

### Timeouts Need Special Attention

A timeout is generally considered retriable.

Example:

```text
Request took too long.
Client stopped waiting.
```

The request may actually complete successfully on a second attempt.

Because of this:

```text
504 Gateway Timeout
```

should usually be retried.

However:

Repeated timeouts may indicate:

- Prompt too large
- Tool workload too heavy
- Poor system design

At that point, fixing the request is better than endlessly retrying.

---

### Safe Default Rule

When unsure:

```text
Treat the error as terminal.
Raise it immediately.
```

Why?

A wrongly classified terminal error:

```text
Fails loudly.
Gets fixed quickly.
```

A wrongly classified retriable error:

```text
Creates retry storms.
Consumes resources.
Hides root causes.
```

Failing loudly is generally safer.

---

## SDK Retries: Know What Already Exists

Many developers accidentally create:

```text
Application Retry
        +
SDK Retry
```

This causes retry multiplication.

Example:

```text
Application retries: 3

SDK retries: 3
```

Total attempts:

```text
3 × 3 = 9 requests
```

A single failure can generate nine API calls.

This is especially dangerous during rate limiting.

---

### Recommended Approach

Use one retry strategy.

Option A:

```text
Let SDK handle retries.
```

Use your code only for:

- Fallback logic
- Business-specific recovery

---

Option B:

```text
Disable/minimize SDK retries.
```

Implement all retry behavior yourself.

---

Avoid:

```text
SDK retries
+
Application retries
```

unless intentionally coordinated.

---

## Respect Retry-After Headers

For rate limits and overload situations, the API may return:

```text
Retry-After
```

This tells you exactly how long to wait.

Example:

```http
Retry-After: 30
```

Meaning:

```text
Wait 30 seconds before retrying.
```

This is better than guessing.

Preferred order:

```text
1. Retry-After header
2. Exponential backoff
```

Pseudo-flow:

```python
if retry_after_exists:
    wait(retry_after)
else:
    exponential_backoff()
```

---

## Tool Errors Must Be Returned to Claude

One of the most tested Claude certification topics is tool failure handling.

When a tool fails:

✅ Return the failure to Claude.

❌ Do not silently swallow the error.

---

### Incorrect Approach

```python
try:
    result = execute_tool()
except Exception:
    return ""
```

Problem:

Claude sees:

```text
Empty result
```

Claude may assume:

```text
Tool succeeded but found nothing.
```

The model then continues reasoning with incorrect assumptions.

This can produce confident but incorrect answers.

---

### Correct Approach

Return a tool result with:

```python
{
    "type": "tool_result",
    "tool_use_id": tool_use.id,
    "is_error": True,
    "content": "Tool failed: timeout"
}
```

Example:

```python
def run_tool(tool_use):
    try:
        result = execute(tool_use)

        return {
            "type": "tool_result",
            "tool_use_id": tool_use.id,
            "content": result
        }

    except Exception as e:
        return {
            "type": "tool_result",
            "tool_use_id": tool_use.id,
            "is_error": True,
            "content": f"Tool failed: {e}"
        }
```

---

### Why is_error Matters

Without:

```text
is_error = True
```

Claude assumes:

```text
Valid tool result
```

With:

```text
is_error = True
```

Claude understands:

```text
Tool failed.
```

It can then:

- Try another tool
- Change strategy
- Ask for clarification
- Explain failure to the user

This makes reasoning significantly more reliable.

---

## Refusals Are Not Retriable

A common certification trick question:

> Is a refusal retriable?

Answer:

**No.**

A refusal is not a system failure.

It is a model decision.

Example:

```python
if response.stop_reason == "refusal":
    raise ValueError(
        "Model refused the request."
    )
```

Even though the HTTP status is:

```text
200 OK
```

the model intentionally declined the request.

Retrying the same prompt usually produces the same refusal.

Treat it as:

```text
Terminal Failure
```

---

## Error Handling Decision Table

| Error Type | Retry? | Strategy | Fallback |
|------------|---------|-----------|----------|
| 429 Rate Limit | Yes | Exponential backoff + jitter + Retry-After | Cached/simpler response |
| 529 Overloaded | Yes | Backoff | Graceful fallback |
| 500/502/503/504 | Yes | Retry with capped attempts | Fallback path |
| 400 Bad Request | No | Fail fast | Fix request |
| 401 Unauthorized | No | Fail fast | Fix credentials |
| 403 Forbidden | No | Fail fast | Fix permissions |
| 404 Not Found | No | Fail fast | Fix resource path |
| Tool Failure | Depends | Retry only if transient | Return `is_error=True` |
| Model Refusal | No | Fail fast | Surface refusal |

## Note: Exponential Backoff
# Exponential Backoff

**Exponential backoff** is a retry strategy used when an application call fails temporarily, such as due to:

- Network issues
- API rate limits
- Service overload
- Timeouts

Instead of retrying immediately and repeatedly, the application waits for progressively longer intervals between retries.

## Example

If the initial delay is **1 second**, the retries happen as follows:

| Retry Attempt | Wait Time |
|--------------|------------|
| 1st retry | 1 second |
| 2nd retry | 2 seconds |
| 3rd retry | 4 seconds |
| 4th retry | 8 seconds |
| 5th retry | 16 seconds |

The delay grows exponentially, typically doubling after each failed attempt.

## Why Use Exponential Backoff?

Without exponential backoff:

```text
Request fails
↓
Retry immediately
↓
Fails again
↓
Retry immediately
↓
Thousands of clients do the same
↓
Service becomes even more overloaded
```

With exponential backoff:

```text
Request fails
↓
Wait 1s
↓
Retry
↓
Wait 2s
↓
Retry
↓
Wait 4s
↓
Retry
```

This gives the failing service time to recover and reduces traffic spikes.

## Example Code

```python
import time

delay = 1

for attempt in range(5):
    try:
        response = call_api()
        break
    except TemporaryError:
        time.sleep(delay)
        delay *= 2
```

If the API is temporarily unavailable, the client waits 1 second, then 2 seconds, then 4 seconds, and so on before retrying.

## Exponential Backoff with Jitter

Many systems add a random delay (**jitter**) to prevent large numbers of clients from retrying at exactly the same moment.

Example:

```text
Retry 1: 1.3s
Retry 2: 2.7s
Retry 3: 4.4s
Retry 4: 8.9s
```
