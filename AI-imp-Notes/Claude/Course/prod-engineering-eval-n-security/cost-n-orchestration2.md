## Prompt Caching: Reusing Previously Processed Prompt Work

---

## How Prompt Caching Works

With caching:

### First Request

```text
Long System Prompt
       ↓
Processed
       ↓
Stored in Cache
```

This is called a **cache write**.

### Later Requests

```text
Same Prefix
      ↓
Read Cached Processing
      ↓
Skip Reprocessing
      ↓
Generate Response
```

This is called a **cache read**.

---

## Cache Economics

Prompt caching only saves money when reads significantly outnumber writes.

### Cache Write Cost

Processing is stored in cache.

### Cache Read Cost

Reading from cache costs:

```text
0.1× Input Cost
```

Therefore:

```text
Few Reads  → Not Worth It

Many Reads → Significant Savings
```

---

## Automatic Caching

Recommended for most applications.

Enable caching through a top-level cache flag.

```text
Application
      ↓
Cache Enabled
      ↓
Claude Manages Breakpoints Automatically
```

---

## Explicit Caching

Developers manually define cache boundaries.

A `cache_control` marker is added to a content block.

```text
System Prompt
Tool Definitions
Cache Breakpoint
----------------
User Message
```

Everything before and including the breakpoint is cached.

Everything after:

```text
Processed Normally
```

---

## Best Candidates for Caching

Cache content that stays unchanged across requests.

### Long System Prompts

Example:

```text
Company policies
Brand voice
Safety instructions
Workflow rules
```

These rarely change.

Ideal cache target.

---

### Tool Schemas

Example:

```text
Search Tool
Calendar Tool
CRM Tool
Database Tool
```

Tool definitions often stay identical for long periods.

Also excellent cache candidates.

---

### Poor Candidates

Content that frequently changes.

Examples:

```text
User Messages

Conversation State

Live Data

Current Metrics
```

Frequent changes prevent cache hits.

---

## Conditions Required for Effective Caching

Three requirements determine whether caching provides value.

---

### 1. Cached Content Must Be Identical

Cache matching works on an exact prefix.

Example:

Cached:

```text
You are an AI assistant.
```

Later request:

```text
Please, you are an AI assistant.
```

Even one additional word:

```text
"Please"
```

breaks the match.

Result:

```text
Cache Miss
```

Rule:

```text
Any change before the breakpoint invalidates the cache.
```

---

### 2. Reuse Must Occur Within TTL

Default cache lifetime:

```text
5 Minutes
```

Extended option:

```text
1 Hour
```

Example:

```text
Request 1
↓
Cache Created

Request 2 (3 minutes later)
↓
Cache Hit
```

Good.

But:

```text
Request 1
↓
Cache Created

Request 2 (20 minutes later)
↓
Cache Expired
```

Bad under 5-minute TTL.

Rule:

```text
Frequently reused content benefits most.
```

---

### 3. Cached Prefix Must Be Large Enough

Caching requires a minimum size threshold.

Very small prompts provide little reusable computation.

Example:

```text
Small Prompt
↓
No Meaningful Benefit
```

Versus:

```text
5,000-token System Prompt
↓
Huge Benefit
```

Rule:

```text
Long + Stable = Ideal Cache Candidate
```

---

## Cache Staleness Tradeoff

Caching assumes the stored content remains correct.

Potential issue:

```text
Cached Data
      ↓
Real Data Changes
      ↓
Cache Still Used
```

Result:

```text
Stale Information
```

This is called the **consistency window**.

---

### Safe Cache Targets

```text
System Prompts

Safety Rules

Tool Schemas

Static Instructions
```

Nothing changes.

No staleness risk.

---

### Risky Cache Targets

```text
Inventory Counts

Stock Prices

Live User Status

Real-Time Metrics
```

Can become outdated.

Use carefully.

---


## When To Use Batches

Good Examples:

```text
Nightly Reporting

Document Classification

Large Data Processing

Scheduled Workflows
```

Bad Examples:

```text
Customer Chat

Interactive Search

Live Support

Copilot Interface
```

Users should never wait for batch completion.


## Prompt Caching + Batching

The strongest savings often come from combining both.

Example:

```text
Scheduled Classification Job
        ↓
Large Fixed System Prompt
        ↓
Thousands of Requests
```



## Multi-Agent Orchestration

Multi-agent orchestration uses multiple agents working together.

Structure:

```text
Lead Agent
    ↓
Plans Task
    ↓
Delegates Work
    ↓
Subagents Execute
    ↓
Lead Synthesizes Results
```

---

## Orchestrator-Worker Pattern

Example:

```python
async def orchestrate(task):

    plan = await lead.plan(task)

    results = await gather(
        *[
            worker.run(subtask)
            for subtask in plan.subtasks
        ]
    )

    return await lead.synthesize(results)
```

Workflow:

```text
Planning
   ↓
Parallel Work
   ↓
Synthesis
```

---

## Why Multi-Agent Helps

Large research tasks often contain independent work.

Example:

```text
Research Topic
     ↓
Source A
Source B
Source C
Source D
```

Instead of:

```text
One Agent
Reading Sequentially
```

Use:

```text
Four Agents
Reading Simultaneously
```

Benefits:

- Parallel exploration
- Better coverage
- Faster completion

---

## Hiring Analogy

Think of agents as employees.

Single Agent:

```text
One Researcher
```

Multi-Agent:

```text
Five Researchers
```

Five researchers finish faster.

But:

```text
Five Salaries
```

Cost increases substantially.

---

## Anthropic Findings

Anthropic observed that:

```text
Lead Agent
+
Multiple Subagents
```

often performs better than a single agent on complex research tasks.

However:

```text
Cost ≈ 15× Normal Chat
```

because:

- Every subagent has its own context
- Every subagent spends tokens
- Lead agent performs synthesis

---

## Cost Example

Single Agent:

```text
10,000 Tokens
```

Multi-Agent:

```text
Lead + 4 Workers
```

Approximate usage:

```text
150,000 Tokens
```

(15× multiplier)

---

## When Multi-Agent Is Worth It

Good Use Cases:

```text
Research

Information Gathering

Document Analysis

Independent Investigations
```

Tasks can be explored in parallel.

---

## When It Is NOT Worth It

Coding is a common example.

Most coding tasks are:

```text
Step 1
   ↓
Step 2
   ↓
Step 3
```

Each step depends on previous work.

Parallelization provides limited benefit.

A single well-contextualized agent is often cheaper and equally effective.

---

## Failure Handling in Multi-Agent Systems

More agents create more failure points.

Example:

```text
Lead Agent
      ↓
 ┌────┼────┐
 ↓    ↓    ↓
A     B     C
```

If Worker B fails:

```text
Lead Cannot Finish Synthesis
```

Therefore every worker needs:

- Retry logic
- Exponential backoff
- Fallback strategies
- Error handling

The reliability work multiplies with the number of agents.

---

## Cost Optimization Strategy

A common pattern:

### Lead Agent

Use:

```text
More Capable Model
```

Responsibilities:

- Planning
- Coordination
- Synthesis

---

### Subagents

Use:

```text
Cheaper Models
```

Responsibilities:

- Data collection
- Research
- Parallel exploration

Benefits:

```text
Maintains Quality
+
Reduces Cost
```

