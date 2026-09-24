## Reliability First, Cost Second

## Why Reliability Comes First

The cheapest system is rarely the most reliable.

Example:

```text
No Retries
Small Model
Aggressive Timeouts
```

This minimizes spending.

But it can also increase:

- Failed requests
- User frustration
- Production incidents

A slightly higher bill is often acceptable.

A system that silently fails is not.

Therefore:

```text
Reliability First
Cost Second
```

---

## Defining a Reliability Floor

Before optimizing cost, define measurable reliability requirements.

Example:

```text
Maximum Response Time:
4 Seconds

Maximum Retries:
3 Attempts

Acceptable Error Rate:
Defined Baseline
```

These become fixed constraints.

---

## Example Reliability Floor

Suppose a user-facing application requires:

```text
Latency Ceiling = 4 seconds

Retry Budget = 3 retries
```

These rules define the minimum acceptable service quality.

Any cost optimization must preserve them.

---

### Acceptable Cost Optimization

### Unacceptable Cost Optimization

### Reliability Floor Prevents Bad Tradeoffs

Without a reliability floor:

```text
Lower Cost
↓
More Failures
↓
Production Problems
```

With a reliability floor:

```text
Cost Change
      ↓
Verify Reliability
      ↓
Deploy Only If Reliability Holds
```

This keeps optimization honest.

---

## Why Order Matters

Cost and reliability create competing pressures.

### Cost Pressure

Very visible.

Example:

```text
Monthly Bill
Dashboard Spend
Leadership Reviews
```

Everyone notices rising costs.

---

### Reliability Pressure

Less visible initially.

Example:

```text
Occasional Timeout

Random Failure

Missed Request
```

Easy to ignore.

But eventually:

```text
Minor Failures
      ↓
Accumulation
      ↓
Major Incident
```

---

## Correct Optimization Order

### Wrong Approach

```text
1. Cut Costs

2. Observe Failures

3. Fix Reliability Later
```

By the time failures appear:

```text
Reliability Floor Already Crossed
```

---

### Correct Approach

```text
1. Define Reliability Floor

2. Measure Reliability

3. Optimize Cost Inside Constraints
```

This ensures:

```text
Reliable System
+
Controlled Cost
```

---

## Relationship with Evaluations (Evals)

Earlier modules introduced evaluation baselines.

Example:

```text
Baseline Reliability Score
```

This score acts as a protection mechanism.

Process:

```text
Cost Optimization
        ↓
Run Eval
        ↓
Compare Baseline
```

If score falls below baseline:

```text
Reject Change
```

If score remains acceptable:

```text
Approve Change
```

Thus:

```text
Eval = Reliability Guardrail
```

---

## Observability Reference

Every Claude system should monitor three primary metrics.

### Token Cost

Purpose:

```text
Identify Expensive Components
```

---

### Latency

Purpose:

```text
Identify Performance Bottlenecks
```

---

### Error Rate

Purpose:

```text
Identify Reliability Problems
```

---

## Single-Agent vs Orchestrator-Worker

### Single-Agent

Structure:

```text
User
 ↓
Agent
 ↓
Answer
```



---

### Orchestrator-Worker

Structure:

```text
Lead Agent
      ↓
 ┌────┼────┐
 ↓    ↓    ↓
A     B     C
      ↓
Lead Synthesis
```



---

## Token Cost Impact

Single Agent:
Cost:

```text
Normal Token Usage
```

---

Multi-Agent:
Result:

```text
Token Usage Multiplies
```

Anthropic reports examples around:

```text
15× Token Consumption
```

compared with a standard chat workflow.

---

## Latency Impact

### Benefit

All explored in parallel.

This can reduce wall-clock completion time.

---

### Cost

Additional orchestration steps:

```text
Planning

Coordination

Result Compilation
```

These add their own latency.

---

## Reliability Impact

Single Agent:

```text
One Execution Path
```

Limited failure surface.

---

Multi-Agent:

```text
Lead
Worker A
Worker B
Worker C
Worker D
```

More components mean:

```text
More Possible Failures
```

Every worker requires:

- Retry handling
- Backoff strategy
- Fallback behavior

The complexity multiplies.

---

## What Orchestrator-Worker Handles Well

Great for:

```text
Independent Research

Multiple Data Sources

Document Exploration

Parallel Investigation
```

These tasks naturally decompose into separate pieces.

---

## What Orchestrator-Worker Handles Poorly

Poor fit for:

```text
Coding

Sequential Reasoning

Dependency-Heavy Workflows
```

Example:

```text
Step 2 Depends On Step 1

Step 3 Depends On Step 2
```

Parallel workers gain little.

---

## Case Study: The Parallel Fan-Out That Tripled the Bill

### Situation

A developer had a slow task.

Solution attempted:

```text
Add Multiple Subagents
```

Expectation:

```text
More Agents
=
Better Performance
```

Latency improved slightly.

However:

```text
Bill Tripled

Quality Barely Improved
```

---

## What Happened?

Each subagent:

```text
Reads Context

Consumes Tokens

Produces Output
```

Example:

```text
Lead Agent

+ Worker A

+ Worker B

+ Worker C

+ Worker D
```

All spend tokens independently.

The cost rapidly increases.

---

## Why Quality Didn't Improve

The task did not naturally split into independent parts.

Reality:

```text
Step B Needed Step A

Step C Needed Step B

Step D Needed Step C
```

The workers were not truly parallel.

They were mostly dependent on each other.

As a result:

```text
Large Cost Increase

Minimal Quality Gain
```

---

## Developer's Fix

The task returned to:

```text
Single Agent
+
Good Context
```

This confirmed that orchestration was unnecessary.
