```json
System: You are a support ticket processor.

Return ONLY valid JSON.

Schema:
{
  "category": "BILLING | TECHNICAL | ESCALATION",
  "urgency": "LOW | MEDIUM | HIGH",
  "summary": "string"
}

Example:

Input:
My credit card was charged twice.

Output:
{
  "category": "BILLING",
  "urgency": "MEDIUM",
  "summary": "Customer reports duplicate credit card charge."
}
```

-------------------------

# MCP Connector: Controlling Tool Loading Cost

When using the **API MCP Connector**, tool loading behavior is controlled through the `mcp_toolset` object in the `tools` array.

## Key Configuration

### `default_config`
Applies settings to **all tools** on the MCP server.

### `configs`
Allows **per-tool overrides** using the tool name as the key.

---

## Cost Optimization Settings

### 1. `defer_loading`

```json
{
  "defer_loading": true
}
```

- Delays loading a tool's definition until the model actually needs it.
- Reduces initial context size and token usage.
- Useful when an MCP server exposes many tools.

### 2. `enabled`

```json
{
  "enabled": false
}
```

- Enables or disables specific tools.
- Lets you register an MCP server while exposing only selected tools to the model.
- Helps reduce unnecessary context and improve efficiency.

---

## Example

```json
{
  "mcp_toolset": {
    "default_config": {
      "defer_loading": true
    },
    "configs": {
      "search_tool": {
        "enabled": true
      },
      "admin_tool": {
        "enabled": false
      }
    }
  }
}
```

### Result

- All tools use lazy loading (`defer_loading: true`).
- `search_tool` is available to the model.
- `admin_tool` is hidden from the model.

---

## Required Header

When using the MCP Connector, include the beta header:

```http
mcp-client-2025-11-20
```

This header is required for MCP Connector requests.

-----------------

```js
blocks = {}
stop_seen = False
with client.messages.stream(model=model, max_tokens=4096, messages=messages, tools=tools) as stream:
	for event in stream:
    	if event.type == "content_block_start":
        	blocks[event.index] = init_block(event)
    	elif event.type == "content_block_delta":
        	apply_delta(blocks[event.index], event.delta)
    	elif event.type == "message_stop":
        	stop_seen = True
if stop_seen:
	messages.append({"role": "assistant", "content": assemble(blocks)})
else:
	raise StreamInterruptedError(
    	"Stream ended before message_stop; discarding partial turn. Retry from the last complete turn."
	)

```
------------------

# Gap 1: Description for `update_record`

```python
"Use this to update a specific field on a customer record. Only call this tool after a read_record call has confirmed the current value and the proposed change has been reviewed. Do not use this for bulk updates or schema changes."
```

### Why this works

- Specifies the tool's intended purpose.
- Requires a `read_record` call before any modification.
- Instructs the model that the change must be reviewed before execution.
- Explicitly prohibits unsupported actions such as bulk updates and schema modifications.
- Reduces the likelihood of unsafe or unintended tool usage.

---

# Gap 2: HITL (Human-in-the-Loop) Checkpoint Code

Insert the following code immediately before executing `update_record`:

```python
if block.type == "tool_use":

    if block.name == "update_record":
        print(
            f"Proposed update, customer_id: {block.input['customer_id']}, "
            f"field: {block.input['field']}, "
            f"new_value: {block.input['new_value']}"
        )

        approval = input("Approve this update? (yes/no): ").strip().lower()

        if approval != "yes":
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": "Update rejected by operator."
            })
            continue

    result = execute_tool(block.name, block.input)

    tool_results.append({
        "type": "tool_result",
        "tool_use_id": block.id,
        "content": result
    })
```

### Why this works

- Applies approval only to the sensitive `update_record` tool.
- Allows read-only tools such as `read_record` to run without interruption.
- Displays the exact record change before execution.
- Requires explicit operator approval.
- Prevents execution when approval is denied.
- Ensures authorization occurs **before** the update is performed, avoiding irreversible changes prior to review.

---

# Complete Filled Version

```python
tools = [
  {
    "name": "read_record",
    "description": "Use this to read a customer record by customer_id.",
    "input_schema": {
      "type": "object",
      "properties": {
        "customer_id": {"type": "string"}
      },
      "required": ["customer_id"]
    }
  },
  {
    "name": "update_record",
    "description": "Use this to update a specific field on a customer record. Only call this tool after a read_record call has confirmed the current value and the proposed change has been reviewed. Do not use this for bulk updates or schema changes.",
    "input_schema": {
      "type": "object",
      "properties": {
        "customer_id": {"type": "string"},
        "field": {"type": "string"},
        "new_value": {"type": "string"}
      },
      "required": ["customer_id", "field", "new_value"]
    }
  }
]

def run_agent_loop(user_request):
    messages = [{"role": "user", "content": user_request}]

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            return response

        if response.stop_reason == "tool_use":
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results = []

            for block in response.content:
                if block.type == "tool_use":

                    if block.name == "update_record":
                        print(
                            f"Proposed update, customer_id: {block.input['customer_id']}, "
                            f"field: {block.input['field']}, "
                            f"new_value: {block.input['new_value']}"
                        )

                        approval = input(
                            "Approve this update? (yes/no): "
                        ).strip().lower()

                        if approval != "yes":
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Update rejected by operator."
                            })
                            continue

                    result = execute_tool(block.name, block.input)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({
                "role": "user",
                "content": tool_results
            })
```
---------------------
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

-------------------

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

