## Claude Developer Certification Notes: System Prompts, XML Tags, Few-Shot Examples, and Output Constraints

### The Main Idea

When a prompt works during testing but fails in production, the problem is usually **not that the prompt is too short**.

Most developers keep adding more instructions, but the real issue is that a specific **prompting technique is missing**.

Instead of adding more words:

1. Identify the failure.
2. Find the missing technique.
3. Add only that technique.

This approach creates reliable and scalable prompts.

---

## The Four Techniques

### 1. System Prompt

A **System Prompt** defines Claude's permanent behavior throughout the conversation.

It acts like a contract that tells Claude:

- What role it should play
- What rules must always be followed
- What scope it should stay within
- What output expectations remain constant

Example:

```text
You are a support classifier.
Classify each ticket into exactly one category:
BILLING, TECHNICAL, or ESCALATION.
```

Use a System Prompt when:

- Claude changes tone unexpectedly
- Claude starts answering a broader question
- Claude drifts from its role
- Responses become inconsistent across multiple turns

Symptom:

```text
Correct format
Wrong scope or behavior
```

Fix:

```text
Strengthen the System Prompt.
```

---

### 2. XML Tags

XML tags create clear boundaries between:

- Instructions
- Examples
- User input
- Reference data

Example:

```xml
<sample_input>
My account shows two charges.
</sample_input>

<ideal_output>
BILLING
</ideal_output>
```

Why use XML tags?

Without boundaries, Claude may mix:

- Instructions
- Examples
- User data

XML tags help Claude understand:

```text
This is instruction.
This is example.
This is actual input.
```

Use XML when:

- Prompt contains multiple sections
- You have examples
- You want strong separation of content

---

### 3. Few-Shot Examples

Few-shot examples teach by showing patterns.

Instead of describing the format:

```text
Return a category label.
```

Show the format:

```text
Input: My account shows two charges.
Output: BILLING

Input: API returns 429 errors.
Output: TECHNICAL
```

Claude learns the exact pattern from examples.

Benefits:

- Consistent structure
- Correct casing
- Better handling of ambiguity
- Reduced hallucinated formats

Use Few-Shot Examples when:

- Claude understands the task but invents its own structure
- Output shape varies
- Written instructions are not enough

Symptom:

```text
Right answer
Wrong structure
```

Fix:

```text
Add Few-Shot Examples.
```

---

### 4. Output Constraints

Output Constraints specify exactly what Claude can return.

Example:

```text
Return exactly one label:
BILLING
TECHNICAL
ESCALATION

Return only the label.
No explanation.
No extra text.
```

Without constraints:

Possible outputs:

```text
Billing

billing

This appears to be a billing issue.

The category is BILLING.
```

All are correct logically, but may break a parser.

With constraints:

```text
BILLING
```

every time.

Use Output Constraints when:

- Output format changes
- JSON becomes invalid
- Extra explanations appear
- Parser failures occur

Symptom:

```text
Correct content
Wrong format
```

Fix:

```text
Add Output Constraints.
```

---

## Failure Diagnosis Cheat Sheet

### Problem: Output Format Is Wrong

Example:

```text
Expected: BILLING

Received:
This looks like a billing issue.
```

Missing Technique:

```text
Output Constraint
```

---

### Problem: Scope or Behavior Changes

Example:

```text
Claude starts giving advice instead of classification.
```

Missing Technique:

```text
System Prompt
```

---

### Problem: Structure Is Invented

Example:

```json
{
  "type": "billing"
}
```

when you expected:

```text
BILLING
```

Missing Technique:

```text
Few-Shot Examples
```

---

### Problem: Works On Simple Cases But Fails On Edge Cases

Example:

```text
Ticket contains both billing and technical issues.
```

Missing Technique:

```text
Constraint covering the edge case
```

or

```text
Few-shot example showing the edge case
```

---

## Classification Example: Bad Prompt

```text
System:
You are a support classifier.
Classify the ticket.

User:
I was charged twice for the same month.
```

Possible Outputs:

```text
Billing
```

```text
billing
```

```text
This appears to be a billing issue.
```

Problem:

```text
No output constraint.
```

The router or parser may fail.

---

## Classification Example: Good Prompt

```text
System:
You are a support classifier.

Classify each ticket into exactly one category:

BILLING
TECHNICAL
ESCALATION

Return only the label.
No other text.

<sample_input>
My account shows two charges for April.
</sample_input>

<ideal_output>
BILLING
</ideal_output>

<sample_input>
The API keeps returning 429 errors.
</sample_input>

<ideal_output>
TECHNICAL
</ideal_output>

User:
<ticket>
I was charged twice for the same month.
</ticket>
```

Expected Output:

```text
BILLING
```

Why it works:

- System Prompt defines behavior
- XML Tags separate content
- Few-Shot Examples teach format
- Output Constraint locks output shape

All four techniques work together.

---

## The Biggest Mistake Developers Make

Many developers follow this cycle:

Pass 1:

```text
Add more instructions
```

Pass 2:

```text
Add more explanations
```

Pass 3:

```text
Add edge-case descriptions
```

Pass 4:

```text
Add even more paragraphs
```

Result:

- Longer prompts
- Higher latency
- More tokens
- Same failures

The prompt becomes bigger, not better.

---

## The Correct Iteration Process

When output fails:

### Step 1

Identify the failure.

Ask:

```text
Is the format wrong?
Is the content wrong?
Is the structure wrong?
Does it fail on edge cases?
```

### Step 2

Map failure to technique.

| Failure | Missing Technique |
|----------|------------------|
| Wrong format | Output Constraint |
| Scope drift | System Prompt |
| Invented structure | Few-Shot Example |
| Edge case failure | Constraint or Example |

### Step 3

Add only the missing technique.

### Step 4

Retest.

---

## Structured Outputs (Production-Grade Reliability)

Prompt instructions are only requests.

Claude may still generate:

- Invalid JSON
- Wrong field names
- Extra text

For production systems, use:

### JSON Schema Structured Outputs

Instead of saying:

```text
Return valid JSON.
```

Provide:

```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string"
    }
  }
}
```

Claude becomes constrained to that schema.

Benefits:

- Always valid JSON
- No parser retries
- Reliable automation

---

### Strict Tool Use

When Claude calls a tool:

```text
strict = true
```

ensures the tool arguments conform to the schema.

Benefits:

- Prevents malformed tool calls
- Reduces runtime errors
- Safer agent workflows

---

## Limitations of Structured Outputs

### First Request Is Slower

Schema must be compiled first.

---

### Slightly Higher Token Usage

The API injects formatting instructions.

---

### Not 100% Success Cases

Still possible:

```text
Refusal
```

or

```text
max_tokens truncation
```

Always check:

```text
stop_reason
```

---

## Assistant Prefill vs Structured Outputs

### Assistant Prefill

You start the assistant's response and Claude completes it.

Example:

```json
User: Classify this ticket

Assistant:
{"category": "
```

Claude continues:

```json
{"category": "BILLING"}
```

Think:

```text
Prefill = "I decide how the response starts."
```

---

### Structured Outputs

You provide a JSON Schema.

Example:

```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "enum": ["BILLING", "TECHNICAL", "ESCALATION"]
    }
  }
}
```

Claude must generate valid JSON matching the schema:

```json
{
  "category": "BILLING"
}
```

Think:

```text
Structured Outputs = "The schema controls the response."
```

---

### Why They Can't Be Used Together

Both try to control output generation.

Prefill:

```text
Start the response like this...
```

Structured Outputs:

```text
Only generate tokens that match the schema...
```

Conflict:

```text
Prefill controls the beginning.
Schema controls everything.
```

Therefore:

```text
❌ Prefill + Structured Outputs
✅ Prefill only
✅ Structured Outputs only
```



