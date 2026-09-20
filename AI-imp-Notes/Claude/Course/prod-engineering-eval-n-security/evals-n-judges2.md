## Matching the Grading Method to the Output

For the Claude Developer Certification, one of the most important concepts is choosing the correct grading method for an eval. A grader converts model output into a measurable score, usually from 1 to 10.

Using the wrong grader creates misleading results, increases cost, and wastes evaluation effort.

There are three primary grading methods:

1. Exact/String Match
2. Code-Graded Checks
3. LLM-as-Judge

The grading method should always match the structure of the output.

---

## 1. Exact or String Match

Use when there is exactly one correct answer.

Examples:

- Classification labels
- Boolean outputs
- Fixed values
- Known identifiers

Example:

Expected output:

```text
Positive
```

Model output:

```text
Positive
```

Result:

```text
Pass
```

Model output:

```text
positive
```

Result:

```text
Fail
```

because the strings do not exactly match.

### Advantages

- Extremely cheap
- Fast
- Deterministic
- Easy to implement

### Disadvantages

- Very brittle
- Rejects valid paraphrases
- Rejects harmless formatting differences
- Not suitable for natural language generation

### Certification Rule

Use Exact Match when:

```text
Only one valid answer exists.
```

Avoid it when:

```text
Multiple correct phrasings are possible.
```

---

## 2. Code-Graded Checks

Use when correctness can be validated with rules or code.

Instead of comparing exact text, verify whether the output satisfies specific requirements.

Examples:

- Valid JSON
- Valid Python code
- Required fields exist
- Numerical value within range
- Correct schema

### JSON Validation Example

```python
import json

def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0
```

If parsing succeeds:

```text
Score = 10
```

If parsing fails:

```text
Score = 0
```

---

### Python Validation Example

```python
import ast

def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0
```

If the code is syntactically valid:

```text
Pass
```

Otherwise:

```text
Fail
```

---

### Advantages

- Cheap
- Fast
- Reliable
- Catches structural errors
- Easy to automate

### Disadvantages

- Cannot measure quality
- Cannot evaluate reasoning
- Cannot determine usefulness

It can tell you:

```text
The JSON is valid.
```

It cannot tell you:

```text
The JSON contains good information.
```

### Certification Rule

Use Code-Graded Checks when:

```text
A programmatic rule can determine correctness.
```

---

## Exact Match vs Code-Graded Example

Suppose the task is:

```text
Return the capitals as a JSON array.
```

Reference answer:

```json
["Paris", "Berlin", "Rome"]
```

Model output:

```json
["Rome", "Paris", "Berlin"]
```

### Exact Match Result

```text
Fail
```

The strings differ.

### Code-Graded Result

```text
Pass
```

Because:

- JSON is valid
- All cities are present
- Structure is correct

This demonstrates why Code-Graded Checks are often superior for structured outputs.

---

## 3. LLM-as-Judge

Use when evaluating open-ended content.

Examples:

- Summaries
- Explanations
- Recommendations
- Essays
- Rationales
- Customer support responses

These outputs cannot be fairly graded using exact matching.

---

### Example Problem

Task:

```text
Write a one-paragraph rationale for a recommendation.
```

Why Exact Match Fails:

```text
There are countless valid answers.
```

Why Code Check Fails:

```text
It can only verify that text exists.
```

Therefore:

```text
Use an LLM Judge.
```

---

## What Is LLM-as-Judge?

An LLM Judge is a second model call that evaluates the first model's output using a rubric.

The judge reviews:

- Task
- Solution
- Evaluation Criteria

and then produces:

- Strengths
- Weaknesses
- Reasoning
- Score

---

### Judge Example

```python
def grade_by_model(task, solution):

    eval_prompt = f"""
    You are an expert reviewer.

    Evaluate the solution.

    Task: {task}

    Solution: {solution}

    Return JSON with:

    strengths
    weaknesses
    reasoning
    score
    """

    result = chat([{
        "role": "user",
        "content": eval_prompt
    }])

    return json.loads(result)
```

Expected output:

```json
{
  "strengths": [
    "Clear explanation",
    "Complete answer"
  ],
  "weaknesses": [
    "Slightly verbose"
  ],
  "reasoning": "The answer addresses all requirements.",
  "score": 8
}
```

---

## Why Ask for Reasoning?

A common mistake is asking the judge for only a score.

Bad:

```json
{
  "score": 6
}
```

Problem:

```text
Why 6?
Nobody knows.
```

Models often drift toward middle scores when no justification is required.

Better:

```json
{
  "strengths": [...],
  "weaknesses": [...],
  "reasoning": "...",
  "score": 6
}
```

The reasoning anchors the score to specific observations.

### Certification Tip

Always request:

- Strengths
- Weaknesses
- Reasoning
- Score

not just the score.

---

## Strengths of LLM-as-Judge

Can evaluate:

### Faithfulness

```text
Did the summary accurately reflect the source?
```

### Instruction Following

```text
Did the model obey the prompt?
```

### Completeness

```text
Did it include all required information?
```

### Tone

```text
Was the response professional and appropriate?
```

### Overall Quality

```text
Is the answer genuinely useful?
```

---

## Weaknesses of LLM-as-Judge

### Expensive

Each evaluation requires another model call.

Example:

```text
1000 test cases
=
1000 additional API calls
```

---

### Noisy

The same answer may receive slightly different scores across runs.

---

### Subjective

Quality judgments are harder to standardize than format checks.

---

## Judge Calibration

A judge is not trustworthy until it is calibrated.

Calibration means:

```text
Compare judge scores
against human-labeled scores.
```

---

### Calibration Process

#### Step 1

Create a gold-standard dataset.

Example:

```text
Human reviewers score answers.
```

---

#### Step 2

Run the judge on the same dataset.

---

#### Step 3

Compare results.

Example:

```text
Human Score = 9
Judge Score = 9
```

Agreement:

```text
Good
```

Example:

```text
Human Score = 9
Judge Score = 3
```

Agreement:

```text
Poor
```

---

#### Step 4

Measure agreement rate.

Example:

```text
Judge agrees with humans 90% of the time.
```

This judge is reasonably reliable.

Example:

```text
Judge agrees with humans 50% of the time.
```

This judge is unreliable.

---

## Improving a Poor Judge

If calibration results are weak:

### Tighten the Rubric

Bad rubric:

```text
Score quality from 1-10.
```

Too vague.

---

Better rubric:

```text
10 = Complete, accurate, concise

7-9 = Mostly complete, minor issues

4-6 = Significant omissions

1-3 = Incorrect or unusable
```

---

### Add Examples

Include:

```text
Example of a high-quality answer
```

and

```text
Example of a poor-quality answer
```

This helps the judge apply scores consistently.

---

## Cost Strategy Used by Many Teams

Because judges are expensive:

### Every Commit

Run:

- Exact Match
- Code-Graded Checks

These are nearly free.

---

### Scheduled Evaluations

Run:

- LLM Judge

Examples:

```text
Nightly
Weekly
Before Release
```

This balances quality and cost.

---

## Grader Selection Cheat Sheet

### Exact Match

Use For:

```text
Single correct value
```

Examples:

- Labels
- IDs
- Fixed answers

Pros:

- Cheap
- Fast
- Reliable

Cons:

- Extremely brittle

---

### Code-Graded Checks

Use For:

```text
Structured outputs
```

Examples:

- JSON
- SQL
- Python
- Numeric ranges

Pros:

- Cheap
- Automated
- Flexible

Cons:

- Cannot evaluate quality

---

### LLM-as-Judge

Use For:

```text
Open-ended outputs
```

Examples:

- Summaries
- Essays
- Recommendations
- Explanations

Pros:

- Evaluates quality
- Evaluates faithfulness
- Evaluates completeness

Cons:

- Expensive
- Noisy
- Requires calibration

---

## Certification Exam Cheat Sheet

### Choose Exact Match When

```text
There is only one correct answer.
```

---

### Choose Code-Graded Check When

```text
Correctness can be verified using rules or parsing.
```

---

### Choose LLM-as-Judge When

```text
Quality matters more than format.
```

---

### Judge Best Practices

✅ Ask for strengths

✅ Ask for weaknesses

✅ Ask for reasoning

✅ Ask for a score

✅ Calibrate against human labels

✅ Improve rubric when agreement is low

