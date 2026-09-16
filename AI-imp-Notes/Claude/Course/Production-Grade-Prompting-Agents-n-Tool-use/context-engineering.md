## Model Selection and Context Engineering for Claude Developer Certification

### The Big Idea

When building Claude-powered applications, two things decide whether your system stays fast, cheap, and reliable:

1. Choosing the right model
2. Managing the context window

Most production failures are not caused by bad prompts. They happen because developers do not manage context growth properly.

---

## 1. Model Selection: Start with Sonnet

Think of Claude models as different vehicle types:

| Model | Best For | Cost | Speed | Capability |
|---------|---------|---------|---------|---------|
| Haiku | Simple tasks, classification, extraction | Lowest | Fastest | Basic |
| Sonnet | Most production applications | Medium | Fast | Strong |
| Opus | Complex reasoning and coding | High | Slower | Very Strong |
| Fable | Most advanced reasoning and agent systems | Highest | Slowest | Maximum |

### Recommended Approach

Start with **Sonnet** because it provides the best balance of:

- Cost
- Speed
- Intelligence

Only move to:

- **Opus** if evaluation results prove Sonnet is not good enough.
- **Haiku** if evaluation results prove quality remains acceptable.
- **Fable** for the most demanding reasoning and agentic workloads.

Never choose a model based only on cost.

Use evaluation results to justify model changes.

---

## 2. Understanding the Context Window

The context window is Claude's working memory.

It contains:

- System prompt
- User messages
- Assistant responses
- Tool calls
- Tool results
- Retrieved documents

Everything consumes tokens.

Example:

```text
System Prompt
     +
Conversation History
     +
Tool Results
     +
Current User Message
     =
Context Window Usage
```

A common mistake is believing only prompts consume context.

In reality, tool outputs often become the biggest consumer.

---

## 3. Why Agent Workflows Run Out of Context

Single-turn prompts rarely hit limits.

Agentic workflows are different.

Example:

```text
Turn 1 → Tool Output
Turn 2 → Tool Output
Turn 3 → Tool Output
Turn 4 → Tool Output
...
Turn 10 → Tool Output
```

Every tool output remains inside the conversation.

If each output is large:

```text
10 Tool Calls × Large Results
=
Huge Context Consumption
```

Eventually:

- Context fills up
- Costs increase
- Latency increases
- Quality decreases

The model may begin:

- Missing instructions
- Choosing incorrect tools
- Producing incomplete answers

---

## 4. What Is Context Engineering?

Context Engineering means deciding:

### What goes into context

Examples:

- Relevant instructions
- Needed documents
- Critical history

### What gets summarized

Examples:

- Old discussions
- Completed work

### What never enters context

Examples:

- Large irrelevant logs
- Redundant tool data
- Internal debugging information

In simple words:

> Context Engineering = Managing Claude's memory budget.

---

## 5. Four Main Context Management Strategies

### Strategy 1: Pruning

Pruning removes unnecessary conversation history.

Example:

```text
Turn 1
Turn 2
Turn 3
Turn 4
Turn 5
```

Suppose Turns 3-5 were debugging attempts that were not useful.

You can rewind to Turn 2.

Result:

```text
Turn 1
Turn 2
(New Path Starts Here)
```

#### Use When

- Claude went down the wrong path
- Old discussion is no longer useful

#### Downside

Everything after the rewind point is lost.

---

### Strategy 2: Compaction

Compaction summarizes older conversation history.

Instead of storing:

```text
50 messages
```

Store:

```text
1 summary message
```

Example:

Before:

```text
20,000 tokens
```

After:

```text
2,000-token summary
```

#### Use When

- The same task continues
- Context is approaching its limit

#### Downside

Poor summaries lose important details.

---

### Good Summarizer Example

Bad instruction:

```text
Summarize the conversation.
```

Risk:

- File names lost
- Decisions lost
- Errors lost

Better instruction:

```text
Summarize the conversation.
Preserve:
- File paths
- Decisions made
- Errors encountered
- Resolutions applied
```

Better summaries create better future performance.

---

### Strategy 3: Clearing

Clearing starts a completely new session.

Example:

Current task:

```text
Build an API
```

Next task:

```text
Write a marketing report
```

The old context is unnecessary.

Start fresh.

#### Use When

Tasks are unrelated.

#### Downside

Nothing is remembered.

Anything important must be stored elsewhere.

---

### Strategy 4: Subagent Handoffs

Instead of one agent doing everything:

```text
Main Agent
```

Create:

```text
Main Agent
   |
   +-- Research Agent
   |
   +-- Analysis Agent
   |
   +-- Report Writer Agent
```

Each subagent gets:

- Small context
- Specific task
- Required tools only

Then returns a short summary.

#### Benefits

- Lower token usage
- Better scalability
- Easier long-term tasks

#### Downside

Intermediate reasoning is discarded.

Only the final summary remains.

---

## 6. Prompt Caching

Prompt caching reduces repeated costs.

Imagine every request contains:

```text
50-page System Prompt
Tool Definitions
Company Handbook
```

Without caching:

Claude processes everything every time.

With caching:

Claude reuses previously processed content.

Benefits:

- Lower cost
- Faster responses
- Better efficiency

Best candidates for caching:

- System prompts
- Tool schemas
- Reference documents

Anything that rarely changes.

---

## 7. Token Counting

Token counting helps estimate cost before sending a request.

Instead of discovering:

```text
Oops!
Window exceeded.
```

You can measure first.

Benefits:

- Predicts context usage
- Prevents failures
- Supports production monitoring

Think of it as:

```text
Fuel Gauge
for
Claude Context
```

Always test using real production-sized data.

---

## 8. RAG: Three Places Where Retrieval Can Fail

### A. Chunking Failure

Chunk too small:

```text
Fact gets split apart
```

Chunk too large:

```text
Too much unrelated content
```

Best practice:

- Section-based chunks
- Small overlap between chunks

---

### B. Retrieval Failure

Embedding search finds:

```text
Semantically similar content
```

It may miss:

```text
Exact ID
Exact number
Exact keyword
```

Solution:

Combine:

- Semantic search
- Keyword search

---

### C. Prompt Assembly Failure

Even when correct chunks are retrieved:

```text
Chunks Retrieved ✅

Chunks Inserted Poorly ❌
```

The model may ignore them.

Always structure retrieved content clearly.

---

## 9. Real Production Failure Example

### Development

Assumed budget:

```text
40k tokens
```

Each tool output:

```text
~800 tokens
```

Twenty turns completed successfully.

Total usage:

```text
~18k tokens
```

Everything looked fine.

---

### Production

Real receipts included:

- Transactions
- Supporting records
- Correspondence

Tool output grew to:

```text
~3200 tokens per call
```

After 8 turns:

```text
8 × 3200
=
25,600 tokens
```

Adding:

- System prompt
- Messages
- Responses

Result:

```text
40k budget reached
```

---

### Symptoms

The team observed:

- Wrong tool selection
- Partial analyses
- Lower quality outputs

Initially they blamed:

```text
Tool schema problems
```

Actual cause:

```text
Context budget exhausted
```

The model lost visibility into important instructions because old tool outputs consumed too much context.

---

### Fix

1. Remove unused tool outputs.
2. Compact conversations before reaching limits.
3. Measure token consumption using real production data.
4. Monitor context growth continuously.

