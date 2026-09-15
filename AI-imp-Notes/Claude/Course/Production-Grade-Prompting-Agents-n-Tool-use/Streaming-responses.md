## Streaming Responses Explained Simply (Claude Developer Certification Notes)

Streaming is a way to receive the model's response piece by piece instead of waiting for the entire response to be generated.

Without streaming:

- Send request
- Wait
- Receive complete response
- Process it

With streaming:

- Send request
- Receive small events continuously
- Build the response yourself
- Use the final assembled message after completion

The final message is exactly the same as a non-streamed response. The only difference is that your application has to assemble it from multiple events.

---

## Why Streaming Exists

Streaming improves user experience because users can immediately see content appearing on the screen instead of staring at a blank page.

Benefits:

- Faster perceived response time
- Better user experience
- Useful for long answers
- Useful for chat interfaces

Trade-offs:

- More implementation complexity
- Must manage partial state
- Must handle interruptions properly

---

## Important Concept

The model is not giving you a live message object.

Instead, it sends a sequence of events.

Each event represents a small update such as:

- Message started
- New block started
- More text added
- Tool input added
- Block completed
- Message completed

Your application listens to these events and continuously updates its local state.

---

## Event Flow

Typical stream:

```text
message_start
content_block_start
content_block_delta
content_block_delta
content_block_delta
content_block_stop
message_delta
message_stop
```

Only after `message_stop` should the message be considered complete.

---

## Event Breakdown

### 1. message_start

Meaning:

A new assistant message is beginning.

What to do:

```text
Create an empty message structure.
Create an empty content array.
Prepare state tracking.
```

Example:

```json
{
  "type": "message_start",
  "message": {
    "content": []
  }
}
```

---

### 2. content_block_start

Meaning:

A new content block is opening.

Block types can be:

- text
- tool_use
- thinking

What to do:

```text
Create a slot for that block.
Store its index and type.
```

Example:

```json
{
  "type": "content_block_start",
  "index": 0,
  "content_block": {
    "type": "text"
  }
}
```

---

### 3. content_block_delta

Meaning:

New content is being added to the block.

Examples:

Text block:

```text
Hello
```

then

```text
 world
```

Tool use block:

```text
{
```

then

```text
"city":
```

then

```text
"London"
```

What to do:

```text
Append each fragment to the existing block.
Do NOT process yet.
Simply collect.
```

---

### 4. content_block_stop

Meaning:

The block is finished.

What to do:

```text
Finalize the block.
```

For text:

```text
Text is complete.
```

For tool_use:

```text
Now parse the JSON.
Now execute the tool.
```

This is the first safe moment to use tool inputs.

---

### 5. message_delta

Meaning:

Updates top-level message information.

Usually contains:

- stop_reason
- final token usage

Example:

```json
{
  "stop_reason": "tool_use"
}
```

Store it for later decision making.

---

### 6. message_stop

Meaning:

The entire message is complete.

What to do:

```text
Mark stream complete.
Save assistant message to history.
Treat it as a normal response.
```

This is the most important event.

Without this event, the message is NOT complete.

---

## Golden Rule: Never Act on a Partial Block

This is the most common streaming mistake.

Consider a tool call.

You receive:

```text
{
```

Then:

```text
"city":
```

Then:

```text
"London"
```

Then:

```text
}
```

Until all pieces arrive, this is not valid JSON.

Bad:

```text
Receive first fragment
Try parsing immediately
JSON parse error
```

Also bad:

```text
Run tool before all arguments arrive
```

Correct:

```text
Collect all fragments
Wait for content_block_stop
Parse JSON
Run tool
```

Simple rule:

> Never process a block before its `content_block_stop`.

---

## When Should You Save to Conversation History?

Wrong approach:

```text
Read loop ended
Save message
```

Correct approach:

```text
Received message_stop
Save message
```

The conversation history must contain only complete messages.

---

## What Happens If a Stream Stops Early?

Common causes:

- Network disconnect
- Timeout
- Client crash
- Dropped connection

Example:

```text
message_start
content_block_start
content_block_delta
content_block_delta
```

Connection dies here.

Missing:

```text
content_block_stop
message_stop
```

Result:

```text
Incomplete message
```

---

## What Should You Do?

If `message_stop` was NOT received:

```text
Discard partial assistant turn
Do not save to history
Retry the request
```

Treat the data as temporary.

---

## Why Partial Text Is Usually Not a Big Problem

Example:

User sees:

```text
The capital of France is Par
```

instead of

```text
The capital of France is Paris.
```

This is mostly a UI issue.

Annoying?

Yes.

Dangerous?

Usually not.

---

## Why Partial Tool Calls Are Dangerous

Example:

Expected:

```json
{
  "city": "London",
  "days": 5
}
```

Received before disconnect:

```json
{
  "city": "London"
```

Problems:

- Invalid JSON
- Missing parameters
- Tool cannot run safely
- Conversation history becomes corrupted

This can break all future requests.

---

## Understanding stop_reason

Always inspect `stop_reason`.

Common values:

### stop_reason = "tool_use"

Meaning:

```text
Tool calls are ready.
Execute tools.
Continue agent loop.
```

---

### stop_reason = "end_turn"

Meaning:

```text
Assistant finished speaking.
No tool execution required.
```

---

### Other stop reasons

Handle according to your application's logic.

Never assume every response leads to tool execution.

---

## Real Production Failure Example

Scenario:

An agent uses streaming.

Everything works during local testing.

Process:

1. Tool use starts.
2. JSON input is streaming.
3. Network disconnect occurs.
4. Stream ends unexpectedly.
5. Application assumes message is finished.
6. Partial tool call is stored in history.

Stored history:

```json
{
  "type": "tool_use",
  "input": {
    "city":
  }
}
```

Later:

User retries.

New request includes corrupted history.

API validation fails.

Team investigates:

- Schema
- Tool logic
- Retry code

But the actual bug happened earlier.

Root Cause:

```text
Handler assumed:
    "stream ended"
means
    "message completed"
```

Those are not the same thing.

Only:

```text
message_stop
```

guarantees completion.

---

## Best Practices for Claude Developer Certification

### Rule 1

Only treat the message as complete after:

```text
message_stop
```

---

### Rule 2

Never execute tool calls before:

```text
content_block_stop
```

---

### Rule 3

Never parse partial tool input JSON.

Collect first.

Parse later.

---

### Rule 4

Only save assistant turns that received:

```text
message_stop
```

---

### Rule 5

If streaming is interrupted:

```text
Discard partial turn
Retry request
```

---

### Rule 6

Check `stop_reason` before deciding next action.

Example:

```text
tool_use → run tools
end_turn → finish conversation
```
---
