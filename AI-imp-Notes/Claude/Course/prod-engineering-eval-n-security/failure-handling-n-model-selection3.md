## Model Selection in Production (Claude Developer Certification)

### What is Model Selection?

Model selection is the process of choosing the most appropriate Claude model for a specific workload.

This decision affects:

- Cost
- Latency
- Response quality
- Scalability

A common misunderstanding is:

```text
Cost optimization starts after choosing a model.
```

Reality:

```text
Model selection determines the baseline cost.
Cost optimization happens afterward.
```

Therefore, choosing the right model is one of the most important production decisions.

---

### The Claude Model Family

Claude models exist in capability tiers.

Moving up a tier generally provides:

- Better reasoning
- Better coding
- Better agent behavior
- Better problem solving

Moving down a tier generally provides:

- Lower cost
- Lower latency
- Faster responses

The model family can be viewed as:

```text
Haiku
   ↓
Sonnet
   ↓
Opus
   ↓
Fable
```

---

#### Haiku

Characteristics:

- Fastest model
- Lowest cost
- Best for high-volume traffic
- Suitable for simple tasks

Common use cases:

- Classification
- Summarization
- FAQ responses
- Data extraction
- Simple transformations

Goal:

```text
Maximum speed
Minimum cost
```

---

#### Sonnet

Characteristics:

- Balanced model
- Strong reasoning
- Good coding performance
- Moderate latency
- Moderate cost

Common use cases:

- Most production applications
- Business assistants
- General chat
- Standard coding workflows
- Knowledge retrieval systems

Goal:

```text
Balance cost, speed, and quality
```

This is the recommended default model.

---

#### Opus

Characteristics:

- More capable than Sonnet
- Handles more difficult reasoning
- Better at complex workflows
- Higher cost

Common use cases:

- Advanced coding
- Complex reasoning
- Multi-step decision making
- Difficult agent workflows

Goal:

```text
Higher quality on challenging tasks
```

---

#### Fable

Characteristics:

- Most capable Claude model
- Highest reasoning ability
- Designed for demanding tasks

Common use cases:

- Advanced agents
- Deep reasoning
- Complex code generation
- Research-intensive workflows

Goal:

```text
Maximum capability
```

---

## The Cost, Latency, and Quality Trade-off

Model selection is fundamentally a trade-off between three factors:

```text
Quality
Cost
Latency
```

Improving one often affects the others.

---

### Moving Up a Model Tier

Example:

```text
Sonnet → Opus
```

Benefits:

✅ Better answers

✅ Stronger reasoning

✅ Better code generation

Costs:

❌ Higher token costs

❌ Potentially higher latency

---

### Moving Down a Model Tier

Example:

```text
Sonnet → Haiku
```

Benefits:

✅ Lower cost

✅ Faster responses

✅ Better scalability

Risks:

❌ Lower reasoning quality

❌ More mistakes

❌ Reduced capability

---

### Important Certification Insight

Many developers assume:

```text
Most capable model = Best choice
```

This is usually wrong.

A production system should use:

```text
Cheapest model
that still meets
the required quality bar.
```

Not:

```text
Most powerful model available.
```

This is one of the most common and expensive mistakes in production systems.

---

## Quality Has a Cost Too

Lower model costs can sometimes create larger business costs.

Example:

```text
Haiku saves $20/day
```

But if it causes:

```text
Wrong financial advice
Incorrect code
Customer support errors
```

The indirect cost may be much higher.

Therefore:

```text
Model price
+
Cost of mistakes
=
Real cost
```

Always evaluate both.

---

## Default Model Strategy

The recommended production approach is:

```text
Start with Sonnet
```

Then use evaluations to decide if a change is needed.

Decision flow:

```text
Start
   ↓
Sonnet
   ↓
Evaluate
   ↓
Quality Good?
   ↓
Yes → Keep Sonnet

No
   ↓
Move to Opus
```

Or:

```text
Start
   ↓
Sonnet
   ↓
Evaluate
   ↓
Quality Still Acceptable?
   ↓
Yes
   ↓
Try Haiku
```

---

### Certification Rule

Always remember:

```text
Start with Sonnet.
Move up only when evaluation proves it is needed.
Move down only when evaluation proves quality remains acceptable.
```

---

## Routing Models in Production

A production application does not have to use a single model for every request.

A common pattern is:

```text
Default Model
+
Override Rules
```

This is called:

```text
Model Routing
```

---

### How Routing Works

Most requests go to a default model.

Example:

```text
Default = Sonnet
```

Special requests are routed elsewhere.

Example:

```text
Simple task
    ↓
Haiku

Normal task
    ↓
Sonnet

Complex task
    ↓
Opus
```

---

### Routing Signals

Routing decisions are usually based on inexpensive signals.

Examples:

#### Task Type

```text
Customer FAQ
    ↓
Haiku

Code Review
    ↓
Opus
```

---

#### Input Length

```text
Short Input
    ↓
Haiku

Large Document
    ↓
Sonnet or Opus
```

---

#### Difficulty Classification

```text
Easy Question
    ↓
Haiku

Medium Question
    ↓
Sonnet

Hard Question
    ↓
Opus
```

---

### Why Routing Saves Money

Without routing:

```text
100% of requests
→ Opus
```

High quality but expensive.

With routing:

```text
70% → Haiku
25% → Sonnet
5%  → Opus
```

Quality remains high while costs decrease significantly.

---

## When to Skip Routing

Routing introduces:

- Additional logic
- Classification code
- Maintenance overhead

If all traffic looks similar:

```text
Use one model.
```

Example:

```text
All requests are customer support tickets.
All require the same quality level.
```

Then:

```text
Pin a single model.
```

No router is necessary.

---

## When to Move Up a Model

Upgrade to a stronger model when:

```text
Evaluations show failures
on important cases.
```

Examples:

- Poor reasoning
- Incorrect coding output
- Bad agent decisions
- High business impact mistakes

Decision:

```text
Current model misses quality bar
        ↓
Move Up
```

Examples:

```text
Haiku → Sonnet
Sonnet → Opus
Opus → Fable
```

---

## When to Move Down a Model

Downgrade when:

```text
Evaluation shows
quality remains acceptable.
```

Benefits:

- Lower cost
- Lower latency
- Higher throughput

Decision:

```text
Current model exceeds quality needs
        ↓
Move Down
```

Example:

```text
Sonnet → Haiku
```

---

## Role of Evaluations (Evals)

Evals are the decision-making tool for model selection.

Never choose models based on:

```text
Gut feeling
Personal preference
Assumptions
```

Choose models based on:

```text
Measured performance
```

Evaluation provides:

- Accuracy scores
- Success rates
- Failure rates
- Quality comparisons

---

### Certification Principle

```text
Model changes must be justified by eval results.
```

Not by intuition.

---

## Example Production Architecture

```text
Incoming Request
        ↓
Task Classifier
        ↓

Simple Task?
        ↓ Yes
      Haiku

No
        ↓
Normal Task?
        ↓ Yes
      Sonnet

No
        ↓
Complex Task
        ↓
       Opus
```

This architecture provides:

✅ Controlled cost

✅ Controlled latency

✅ High quality

✅ Scalable production performance

