## Defining Done Before You Ship: Evals and a Calibrated Judge

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

Good example:

```text
Generate a two-sentence summary that includes:
- Every action item
- The owner of each action item
```

These criteria become the foundation of your eval dataset.

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


---

## What Is an Eval?

An eval is a structured test that determines whether a feature performs correctly.

An eval contains:

1. Test cases
2. Expected outcomes
3. Grading logic
4. Final score

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

## Best Practice 

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

