## Extended Thinking (Claude Developer Certification Notes)

### What is Extended Thinking?

Extended Thinking is a feature that lets Claude spend extra time reasoning before giving the final answer.

When enabled, Claude performs an internal reasoning process first and then provides the final response.

Think of it like:

- Normal mode = Answer immediately.
- Extended Thinking = "Think first, answer later."

This is useful when problems require multiple reasoning steps, careful planning, or managing many constraints.

---

### How Extended Thinking Works

When Extended Thinking is enabled:

1. Claude performs a reasoning phase.
2. A thinking block is created.
3. The final answer is generated after the reasoning.
4. In API responses, the thinking block appears before the answer block.

Example flow:

```text
User Question
      ↓
Thinking Block (Reasoning)
      ↓
Final Answer
```

Important:

- On newer Claude models, reasoning content is hidden by default.
- To view a readable reasoning summary, you must enable the appropriate display setting.
- The actual answer is always separate from the thinking block.

---

### Adaptive Reasoning

Modern Claude models use adaptive reasoning.

Instead of specifying exactly how many reasoning tokens to use, you tell Claude how much effort to spend.

Available concept:

```text
Low Effort
Medium Effort
High Effort
```

Claude then decides how much reasoning is needed.

---

### Deprecated Setting

Older versions used:

```text
budget_tokens
```

This is now deprecated.

For newer model generations:

```text
budget_tokens → Returns 400 Error
```

Use:

```text
thinking
effort
```

instead.

---

### Why Not Enable It All the Time?

Extended Thinking costs more because reasoning tokens are billed the same way as output tokens.

Example:

- Simple classification task
  - Normal mode: cheap and fast
  - Extended Thinking: unnecessary extra cost

- Complex planning task
  - Normal mode: may miss important reasoning steps
  - Extended Thinking: higher accuracy

Rule:

```text
More reasoning = More cost
```

Only use it when the extra reasoning provides value.

---

### When Should You Use Extended Thinking?

#### 1. Multi-Step Reasoning Problems

Examples:

- Mathematical derivations
- Logic puzzles
- Complex decision making
- Problems with multiple constraints

Recommendation:

```text
Enable Extended Thinking
```

Reason:

Claude can work through dependencies and intermediate steps before answering.

---

#### 2. Mechanical Tasks

Examples:

- Data extraction
- Classification
- Format conversion
- Simple factual lookups

Recommendation:

```text
Do NOT use Extended Thinking
```

Reason:

Additional reasoning provides little or no benefit.

Example:

```text
Extract email from text
Convert JSON to YAML
Classify sentiment
```

A well-written prompt is usually enough.

---

#### 3. Agentic Workflows

Examples:

- Tool calling
- Multi-step agents
- Workflow planning
- Research agents

Recommendation:

```text
Enable Extended Thinking
```

Reason:

Better planning typically leads to better tool selection and fewer mistakes later.

---

### The Most Important Rule: Carry-Back Rule

When using tools with Extended Thinking:

Every thinking block returned by Claude must be sent back unchanged on the next API request.

Why?

Each thinking block contains a signature that proves it has not been modified.

---

### What Must Be Returned?

Return:

```text
Thinking Block
+
Tool Results
+
User Messages
```

Exactly as received.

---

### What Must NOT Be Done?

Do NOT:

- Edit the thinking block
- Summarize the thinking block
- Remove the thinking block
- Modify the signature
- Replace the block with your own version

Any of these actions can cause the API request to fail.

---

### Why Does This Matter?

Claude validates that the reasoning history has not been tampered with.

If the signature no longer matches:

```text
Request Rejected
```

This is an API requirement, not a prompting preference.

---

### What About Redacted Thinking Blocks?

Sometimes Claude returns redacted reasoning.

Characteristics:

- Encrypted
- Not human-readable
- Cannot be inspected

Even then:

```text
Return them unchanged
```

The same carry-back rule applies.

---

### Common Developer Mistake

Problem:

```text
"Let's remove old thinking blocks to save context."
```

Result:

```text
Signature mismatch
API error
```

Incorrect:

```text
Previous Message
Tool Result
```

Correct:

```text
Previous Message
Thinking Block
Tool Result
```

---

### Effort Calibration Guide

#### Low Effort

Use for:

- Simple reasoning
- Light planning
- Basic comparisons

Example:

```text
Compare two products
Rank a short list
```

---

#### Medium Effort

Use for:

- Multi-step analysis
- Moderate planning
- Decision making

Example:

```text
Create project plan
Analyze tradeoffs
Debug an issue
```

---

#### High Effort

Use for:

- Difficult reasoning
- Complex problem solving
- Long dependency chains

Example:

```text
Advanced math
Complex architecture design
Multi-stage strategic planning
```

---
