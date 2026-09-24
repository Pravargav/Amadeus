## Cost & Orchestration: Keeping Cost, Latency, and Reliability in Budget

A production-ready Claude application must continuously monitor:

- Token usage (input and output tokens)
- Latency (response time)
- Error rate (failure percentage)

These three metrics provide visibility into system performance and spending.

---

## Why Cost and Latency Matter in Production

During development:

- Only a few API calls are made.

During production:

- Thousands or millions of requests may occur.


Without observability, teams only see a large monthly bill and cannot easily identify the cause.

With observability, teams can determine.

---

## Instrumenting Every API Call

Every Claude API call should be wrapped with monitoring logic.

Example:

```python
import time

def instrumented_call(make_call, step_name):
    start = time.perf_counter()

    resp = make_call()

    latency_ms = (time.perf_counter() - start) * 1000

    log_metric(
        step=step_name,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
        latency_ms=latency_ms
    )

    return resp
```

This wrapper records:

1. Input token count
2. Output token count
3. Request latency

As a result, each model interaction becomes measurable.

---

## Benefits of Per-Call Instrumentation

Without instrumentation:

Question:
- Why is the bill so high?

Difficult to answer because only total spending is visible.

With instrumentation:

Questions become:

- Which workflow increased spending?
- Which step consumes the most tokens?
- Which operation is slowest?
- Which request types generate the highest costs?

Optimization should target those high-impact components first.

---

## Major Cost and Latency Levers

Most cost and performance issues come from a few controllable factors.

### Model Selection

---

### Prompt and Context Size

Every token included in the prompt increases cost.

Large context windows often include:

- Unnecessary conversation history
- Excessive tool output
- Redundant instructions
- 
---

### Number of Tool Calls

Each tool invocation introduces:

- Additional API costs
- Extra processing time
- More potential failure points

Example:

Bad flow:

```text
Agent
 ├─ Tool Call 1
 ├─ Tool Call 2
 ├─ Tool Call 3
 ├─ Tool Call 4
 └─ Response
```

Optimized flow:

```text
Agent
 ├─ Combined Tool Call
 └─ Response
```

Best Practice:

- Eliminate unnecessary tool usage.
- Combine related actions when practical.

---

### Streamed vs Batched Responses

#### Batched Response

```text
Request
   ↓
Model Generates Entire Output
   ↓
User Receives Response
```

#### Streaming Response

```text
Request
   ↓
Model Starts Generating
   ↓
User Immediately Sees Tokens
```
---

### Prompt Caching

Prompt caching stores repeated prompt content.

When identical context is reused:

- Previously processed tokens can be reused.
- Cost decreases.
- Response speed improves.
---

## Streaming with Tool Use

Streaming becomes more complex when tools are involved.

### Non-Streaming Behavior

In a standard request:

```text
Response arrives completely
↓
Tool blocks are fully available
↓
Execute tools
```

Safe and straightforward.

---

### Streaming Behavior

During streaming:

```text
Response arrives in pieces
↓
Tool input arrives across multiple events
↓
Tool input must be reconstructed
↓
Tool executed after completion
```

Tool data may arrive gradually rather than all at once.

Therefore:

```text
Never execute a tool from partial streamed data.
```

## Correct Streaming Tool Pattern
Example pattern:

```python
tool_blocks = {}
text_chunks = []

for event in stream:

    if event.type == "content_block_start":
        # initialize block

    elif event.type == "content_block_delta":
        # accumulate JSON fragments

    elif event.type == "message_stop":
        break

# after stream ends
# reconstruct full tool calls
```

After reconstruction:

```python
tool_calls.append({
    "id": block["id"],
    "name": block["name"],
    "input": json.loads(block["input_json"])
})
```

---

## Why Partial Tool Execution Is Dangerous

Example:

Partial stream received:

```json
{
  "city": "New Yor
```

and not yet:

```json
{
  "city": "New York",
  "units": "metric"
}
```

If execution starts immediately:

- JSON is invalid.
- Required fields are missing.
- Tool fails.

Therefore:

```text
Wait until stream closes.
Then reconstruct tool calls.
Then execute tools.
```

---

## Failure Handling in Streaming

Streams can fail midway because of:

- Network interruptions
- Temporary service issues
- Connection drops

Example:

```text
Stream Started
↓
50% Response Received
↓
Network Failure
```

This is a transient failure.

Correct action:

```text
Retry entire request
```

Incorrect action:

```text
Send partial tool input downstream
```

Partial outputs should never be treated as valid tool inputs.

---

## Multi-Agent Cost Explosion

Cost grows rapidly when multiple agents coordinate.

Example:

```text
Coordinator Agent
      ↓
 ┌────┼────┐
 ↓    ↓    ↓
Agent A
Agent B
Agent C
```

If each agent:

- Reads large context
- Calls tools
- Produces long outputs

Then cost multiplies across all agents.

Best Practices:

- Minimize context passed between agents.
- Use smaller models where possible.
- Limit unnecessary coordination.
- Instrument every agent separately.
- Track token usage per agent.

