## Defining Done Before You Ship: Evals and a Calibrated Judge

For the Claude Developer Certification, this topic is about moving from "it seems to work" to "we can prove it works." Production systems need measurable success criteria, not intuition. The key idea is that before building an AI feature, you must define what success looks like, how failures are handled, what costs are acceptable, and what security boundaries exist.

### Why This Matters

When testing manually, you might ask a few questions and get correct answers. However, that does not guarantee the system will continue working correctly after:

- Prompt changes
- Model upgrades
- Tool modifications
- New feature additions

An evaluation (eval) provides a measurable score that tells you whether the system is improving or getting worse.

Think of an eval like a thermometer:

- It does not improve the system.
- It measures the system.
- It provides a number you can track over time.

Without evals, "done" is a feeling.

With evals, "done" is a score.

---

## Design Document: Define Success Before Building

Before writing production code, create a short design document.

This document defines:

1. Success Criteria
2. Failure Handling
3. Cost and Latency Budget
4. Trust Boundary

The purpose is to establish expectations before implementation so you do not later justify poor model behavior.

---

### 1. Success Criteria

Success criteria specify exactly what the feature must produce.

Bad example:

```text
Summarize the email thread.
```

Why bad?

- Too vague
- Difficult to grade
- No measurable outcome

Good example:

```text
Generate a two-sentence summary that includes:
- Every action item
- The owner of each action item
```

Why good?

- Specific
- Measurable
- Easy to evaluate

These criteria become the foundation of your eval dataset.

Key certification point:

```text
If success cannot be measured,
it cannot be evaluated.
```

---

### 2. Failure Handling

Production systems will fail.

Common failures include:

- API timeout
- Model unavailability
- Rate limiting
- Tool failure
- Invalid input

Each failure should be classified as:

#### Retriable Failure

The system should try again.

Examples:

- Temporary network problem
- Rate limit exceeded
- Timeout

#### Terminal Failure

Retrying will not help.

Examples:

- Missing permissions
- Invalid request
- Corrupted input

For every terminal failure, define:

```text
What should the user see?
```

Example:

```text
"We couldn't process this document.
Please upload a supported file type."
```

This prevents discovering missing error handling after deployment.

---

### 3. Cost and Latency Budget

Every system has limits.

The design document should define:

#### Cost Budget

Example:

```text
Maximum cost per request: $0.05
Monthly budget: $500
```

#### Latency Target

Example:

```text
Responses must complete within 3 seconds.
```

#### Reliability Floor

Example:

```text
At least 95% successful completion rate.
```

Important principle:

```text
Do not optimize speed or cost
by sacrificing required reliability.
```

The architecture must stay within these limits.

---

### 4. Trust Boundary

A trust boundary defines:

```text
What inputs are untrusted?
What actions is the system allowed to perform?
```

Examples of untrusted inputs:

- User prompts
- Uploaded files
- External web content
- Third-party documents

Examples of allowed actions:

- Read a database
- Create a file
- Send a message

Examples of disallowed actions:

- Arbitrary shell commands
- Unapproved data access
- System administration actions

Principle:

```text
Grant the smallest amount of access
required for the task.
```

This follows the idea of least privilege.

---

## What Is an Eval?

An eval is a structured test that determines whether a feature performs correctly.

An eval contains:

1. Test cases
2. Expected outcomes
3. Grading logic
4. Final score

Basic process:

```text
Input Cases
      ↓
Run Feature
      ↓
Grade Output
      ↓
Calculate Score
```

Instead of saying:

```text
The model seems good.
```

You can say:

```text
The model scored 87%.
```

That score is objective and repeatable.

---

## Eval Workflow

### Step 1: Create Test Cases

Example:

```json
{
  "input": "Summarize this email thread"
}
```

Collect many representative examples.

---

### Step 2: Define Expected Behavior

Example:

```text
Must include:
- Action items
- Owners
- Deadlines
```

The more precise the expectation, the easier grading becomes.

---

### Step 3: Run the Feature

Example function:

```python
def run_test_case(test_case):
    output = run_prompt(test_case)
    score = grade(test_case, output)

    return {
        "output": output,
        "test_case": test_case,
        "score": score
    }
```

This executes the feature on one test case.

---

### Step 4: Grade the Result

The grading function checks:

```text
Did the output satisfy the expected criteria?
```

Possible grading methods:

- Pass/Fail
- Numeric score (0-10)
- Percentage score

Example:

```python
score = grade(test_case, output)
```

---

### Step 5: Compute Overall Performance

Example:

```python
def run_eval(dataset):
    results = [run_test_case(c) for c in dataset]

    average = (
        sum(r["score"] for r in results)
        / len(results)
    )

    print(f"Average score: {average}")

    return results
```

This produces an overall evaluation score.

---

## Understanding the Score

A low initial score is normal.

Example:

```text
Version 1 → 25%
Version 2 → 48%
Version 3 → 76%
Version 4 → 89%
```

The goal is not perfection immediately.

The goal is measurable improvement.

---

## Best Practice for Claude Developer Certification

When improving a system:

Change only one thing at a time.

Examples:

```text
Change prompt only
      OR
Change model only
      OR
Change tool only
```

Avoid:

```text
New prompt
+ New model
+ New tools
at the same time
```

Otherwise, you will not know which change improved the score.

---

## Agentic Coding Tool Requirement

For coding agents, the process should be:

```text
1. Write design document
2. Define success criteria
3. Define constraints
4. Create eval dataset
5. Implement solution
6. Run evals
7. Measure score
8. Deploy only after passing
```

The design document becomes the contract that the generated code must satisfy.

---

## Certification Exam Cheat Sheet

### Design Document Contains

✅ Success Criteria  
✅ Failure Handling  
✅ Cost & Latency Budget  
✅ Trust Boundary

---

### Success Criteria

- Specific
- Measurable
- Testable

Example:

```text
Two-sentence summary containing
all action items and owners.
```

---

### Failure Handling

Classify failures as:

- Retriable
- Terminal

Define user-facing error behavior.

---

### Cost & Latency Budget

Specify:

- Per-request cost
- Monthly budget
- Response time target
- Reliability floor

---

### Trust Boundary

Define:

- Untrusted inputs
- Allowed actions
- Least privilege access

---

### Eval Definition

An eval contains:

```text
Test Cases
+
Expected Results
+
Grading Logic
+
Score
```

---

### Eval Pipeline

```text
Dataset
   ↓
Run Feature
   ↓
Grade Outputs
   ↓
Calculate Average Score
```

---
