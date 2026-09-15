## Claude Developer Certification Notes
### Zero-Shot, One-Shot, and Multi-Shot Prompting

---

### The Three Prompting Modes

Prompting modes define how many examples you provide inside the prompt.

They are separate from:

- Model choice (Haiku, Sonnet, Opus, Fable)
- Reasoning mode

The difference is simply:

```text
How many examples do I show the model?
```

---

### Zero-Shot Prompting

#### What Is Zero-Shot?

You provide:

- Instructions only
- No examples

The model must understand the task directly from your description.

---

#### Example

Prompt:

```text
Classify the sentiment of this review as Positive or Negative.

Review:
"The product arrived quickly and works perfectly."
```

Output:

```text
Positive
```

---

#### When To Use

Use when:

- Task is simple
- Output format is obvious
- Instructions are clear

Examples:

- Summarization
- Basic Q&A
- Simple classification
- Translation

---

#### Benefits

- Lowest cost
- Fastest execution
- Uses fewer tokens

---

#### Certification Tip

> Start with zero-shot whenever possible.

---

### One-Shot Prompting

#### What Is One-Shot?

You provide:

- Instructions
- One example input
- One example output

The example teaches the model the desired format.

---

#### Example

Prompt:

```text
Convert product names to lowercase.

Example:

Input: iPhone
Output: iphone

Input: MacBook Pro
```

Output:

```text
macbook pro
```

---

#### When To Use

Use when:

- Format matters
- Instructions alone aren't enough
- You need a specific response style

Examples:

- Structured outputs
- Formatting rules
- Labeling tasks

---

#### Benefits

- More reliable than zero-shot
- Small token increase
- Easy to maintain

---

#### Certification Tip

> One good example often works better than a long explanation.

---

### Multi-Shot (Few-Shot) Prompting

#### What Is Multi-Shot?

You provide:

- Instructions
- Multiple examples

The model learns the pattern from several demonstrations.

---

#### Example

Prompt:

```text
Convert text sentiment to labels.

Example 1:
Input: I love this product.
Output: Positive

Example 2:
Input: This is terrible.
Output: Negative

Example 3:
Input: It works fine.
Output: Neutral

Input:
The service was excellent.
```

Output:

```text
Positive
```

---

#### When To Use

Use when:

- Output format is complex
- Edge cases exist
- Consistency is critical
- Zero-shot keeps failing

Examples:

- Classification
- Extraction
- Structured JSON generation
- Domain-specific tasks

---

#### Benefits

- Highest reliability
- Better consistency
- Handles edge cases well

---

#### Drawback

More examples mean:

```text
More Tokens
=
Higher Cost
=
Less Context Available
```

---

### Important Concept

Examples Are Not Training

The model is **not being retrained**.

Examples exist only inside the current prompt.

Think of them as:

```text
Temporary demonstrations
```

for the current request.

---

### Cost vs Quality Trade-Off

#### Why Examples Cost More

Every example consumes tokens.

Example:

```text
Instruction = 100 tokens
```

With:

```text
Zero-Shot
```

Total:

```text
100 tokens
```

Add examples:

```text
Example 1 = 200 tokens
Example 2 = 200 tokens
```

Now:

```text
100 + 200 + 200
= 500 tokens
```

Every API call now costs more.

---

### Quality vs Cost

#### Zero-Shot

```text
Lowest Cost
Lowest Context Usage
```

Quality:

```text
Good for simple tasks
```

---

#### One-Shot

```text
Slightly Higher Cost
```

Quality:

```text
Usually more reliable
```

---

#### Multi-Shot

```text
Highest Cost
Highest Context Usage
```

Quality:

```text
Usually most consistent
```

---

### Practical Rule

Start with:

```text
Zero-Shot
```

If results are unreliable:

```text
Move to One-Shot
```

If problems still exist:

```text
Move to Multi-Shot
```

---

### Certification Tip

Remember:

> Add the smallest number of examples needed to achieve reliable results.

---

### Examples vs More Instructions

Suppose the model keeps producing incorrect formatting.

Instead of writing:

```text
Long paragraph of instructions
```

Often better:

```text
One correct example
```

The model learns the pattern much faster.

---

#### Example

Less Effective:

```text
Return JSON.
Use lowercase keys.
Keep values as strings.
Do not add extra fields.
```

More Effective:

```json
{
  "name": "john",
  "city": "london"
}
```

A single example clearly shows the desired structure.

---

### How Prompting Mode and Model Choice Work Together

Prompting mode and model choice are two separate levers.

---

#### Lever 1: Model Capability

```text
Haiku
↓
Sonnet
↓
Opus
↓
Fable
```

Capability increases as you move up.

---

#### Lever 2: Number of Examples

```text
Zero-Shot
↓
One-Shot
↓
Multi-Shot
```

Guidance increases as you add examples.

---

### Example Scenario

Task:

```text
Generate structured JSON.
```

#### Option A

```text
Sonnet
+
Zero-Shot
```

May already succeed.

---

#### Option B

```text
Haiku
+
Few Examples
```

Might produce results similar to Sonnet.

This can reduce cost.

---

### Important Insight

A stronger model often needs:

```text
Fewer Examples
```

A smaller model often needs:

```text
More Examples
```

to achieve the same quality.

---

### Recommended Strategy

Try:

```text
Cheapest Appropriate Model
+
Fewest Possible Examples
```

Evaluate the results.

If quality is insufficient:

```text
1. Add examples
2. Increase model capability
3. Re-evaluate
```

---

### Quick Exam Revision

#### Zero-Shot

```text
Instruction Only
No Examples
Lowest Cost
```

---

#### One-Shot

```text
Instruction + One Example
Better Reliability
```

---

#### Multi-Shot (Few-Shot)

```text
Instruction + Multiple Examples
Highest Consistency
Highest Cost
```

---

#### Cost vs Quality

```text
More Examples
=
More Tokens
=
Higher Cost
=
Better Guidance
```

---

#### Model Interaction

```text
Stronger Model
→ Fewer Examples Needed

Smaller Model
→ More Examples Needed
```

---
