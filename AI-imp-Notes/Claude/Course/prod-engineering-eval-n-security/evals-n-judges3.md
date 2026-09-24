## Coverage Matters More Than Perfection

Many developers spend too much time trying to create the perfect rubric while testing only a few examples.

The real goal of an eval is:

```text
Catch regressions and edge cases before users do.
```
Coverage is what makes that possible.

---

## Why Coverage Is More Important

Imagine two evaluation sets:

### Eval A

```text
3 hand-picked cases
Perfect grading
```

### Eval B

```text
20 diverse cases
Slightly noisy automated grading
```

Most of the time:

```text
Eval B is better.
```

Why?

Because it tests more situations.

A model can easily pass a few carefully selected examples while still failing real-world inputs.

---

## What Coverage Means

Coverage means your eval includes:

- Common inputs
- Rare inputs
- Edge cases
- Unexpected variations

Example:

For a date extraction system:

Common case:

```text
My order was placed on March 3.
```

Edge cases:

```text
I ordered on March 3 and received it April 12.
```

```text
I ordered it last Tuesday.
```

```text
I do not remember the date.
```

```text
Order placed: 03/03/2026
```

Testing only the common case provides poor coverage.

Testing all variations provides strong coverage.

---

## More Cases = Better Regression Detection

A regression means:

```text
A change breaks behavior that previously worked.
```

Without enough test cases:

```text
Regression stays hidden.
```

With broad coverage:

```text
Regression becomes obvious.
```



## Generating Additional Eval Cases

You do not always need to manually write every test case.

Claude can help generate additional examples.

Process:

### Step 1

Create a small set of high-quality labeled examples.

Example:

```text
10 human-verified cases
```

### Step 2

Ask Claude to generate similar cases and edge cases.

Example:

```text
Generate examples with:
- Missing dates
- Multiple dates
- Relative dates
- Ambiguous wording
```

### Step 3

Human reviewers spot-check the generated cases.

This keeps quality high while increasing coverage.

---

## The Eval Improvement Loop

The production workflow is a continuous loop.

### Step 1

Set a goal.

Example:

```text
Extract the correct order date.
```

---

### Step 2

Write an initial prompt.

---

### Step 3

Run the eval.

---

### Step 4

Identify failures.

---

### Step 5

Make a single improvement.

---

### Step 6

Run the eval again.

---



## Change Only One Thing at a Time

One of the most important certification concepts:

```text
Change one variable per iteration.
```

Good approach:

```text
Change prompt
Run eval
Measure score
```

or

```text
Change model
Run eval
Measure score
```

or

```text
Add examples
Run eval
Measure score
```

---

### Bad Approach

```text
Change prompt
+
Add examples
+
Switch model
+
Add tools
```

all at once.

Problem:

```text
If the score changes,
you do not know why.
```

You learn nothing.

---

## Why Per-Case Results Matter

Many developers focus only on average score.

Example:

### Before

```text
Case A ✅
Case B ✅
Case C ❌
Case D ❌

Average = 50%
```

### After

```text
Case A ❌
Case B ❌
Case C ✅
Case D ✅

Average = 50%
```

Same average.

But behavior changed completely.

---

## Treat Low Scores as Information

A failing case is valuable.

Do not ask:

```text
Did it fail?
```

Ask:

```text
Why did it fail?
```

The reason often points directly to the fix.

---

### Formatting Failure

Example:

```text
Output should be JSON.
Returned plain text.
```

Likely problem:

```text
Prompt instructions
```

Fix:

```text
Strengthen formatting instructions.
```

---

### Factual Failure

Example:

```text
Retrieved data is incorrect.
```

Likely problem:

```text
Retrieval system
```

Fix:

```text
Improve retrieval quality.
```

---

### Long Context Failure

Example:

```text
Works on short inputs.
Fails on long documents.
```

Likely problem:

```text
Context handling
```

Fix:

```text
Improve chunking or context strategy.
```

---

## Cost of Evals

Evals are extremely valuable, but they are not free.

You must invest time in:

### Creating Test Cases

Defining examples and expected outputs.

---

### Building Graders

Using:

- Exact Match
- Code Grading
- LLM Judges

---

### Calibrating Judges

Comparing judge results with human ratings.

---

### Maintaining Eval Sets

Adding new cases as failures are discovered.


## Case Study: The Demo That Passed but Production Failed

### Scenario

A team built a feature that extracted dates from customer messages.

They manually tested about:

```text
12 example messages
```

Everything looked correct.

The feature was shipped.

---

### Validation That Existed

The system verified:

✅ Message was not empty

✅ Date field existed

✅ Date format was valid

✅ Date value was parseable

Everything seemed safe.

---

### Real Customer Input

Customer message:

```text
I placed my order on March 3
but did not receive it until April 12.
```

Expected extraction:

```text
March 3
```

Actual extraction:

```text
April 12
```

Wrong answer.

---

### Why Validation Didn't Catch It

All validation checks passed.

Because:

```text
April 12 is a valid date.
```

Validation confirms:

```text
Is the value well-formed?
```

Validation does NOT confirm:

```text
Is the value correct?
```

