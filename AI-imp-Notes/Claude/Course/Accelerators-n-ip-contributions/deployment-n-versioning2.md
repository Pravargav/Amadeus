## Accelerator & IP Contribution: The Deployment That Broke When the Model Alias Moved

### Scenario Overview

This example demonstrates one of the most important deployment and versioning lessons in the Claude Developer Certification:

> Never deploy production workloads using a moving model alias when a pinned version is available.

The application was deployed successfully using an alias such as:

```python
model = "opus"
```

Initially, everything worked correctly.

Later, the alias automatically pointed to a newer model version. Although the application code never changed, the model behavior changed because the alias now resolved to a different model snapshot.

This caused a production incident.

---

### Production Log Analysis

Log:

```text
-- deploy: model="opus" status=ok

-- alias advanced -> new opus version (no app change)

-- parser: KeyError "summary" in response payload

-- Error: output shape changed; downstream parse failed

-- rollback attempted -> no pinned prior version retained

-- incident: hotfix parser; root cause = unpinned deployment
```

Let's examine each event.

---

### Step 1: Initial Deployment

```text
deploy: model="opus"
status=ok
```

The application was deployed using a model alias.

The alias pointed to the recommended model version at that time.

Everything functioned correctly.

Problem:

The deployment was tied to a moving alias rather than a fixed model version.

---

### Step 2: Alias Automatically Advanced

```text
alias advanced -> new opus version
(no app change)
```

A newer model version became available.

The alias was updated to reference that newer version.

Important:

- No code was modified.
- No deployment occurred.
- No developer action was taken.

Yet production behavior changed.

This is the primary risk of aliases.

---

### Step 3: Output Format Changed

```text
parser: KeyError "summary"
```

The application expected a field called:

```json
{
  "summary": "..."
}
```

However, the newer model returned a different structure.

Example:

Expected:

```json
{
  "summary": "Customer issue resolved"
}
```

Received:

```json
{
  "result": "Customer issue resolved"
}
```

The parser searched for:

```python
response["summary"]
```

Since the field no longer existed:

```python
KeyError
```

was raised.

---

### Step 4: Downstream Failure

```text
Error: output shape changed
downstream parse failed
```

The model itself was not necessarily defective.

The issue was that the application relied on a specific output structure.

When the structure changed:

- Parsing failed.
- Workflow execution failed.
- Production users were affected.

This is called a regression.

---

### Step 5: Rollback Failure

```text
rollback attempted
```

The team attempted rollback.

Normally rollback means:

```text
New Version
↓
Failure Detected
↓
Restore Previous Version
```

Unfortunately:

```text
no pinned prior version retained
```

There was no fixed version available.

The team never saved the previously working snapshot.

As a result:

- Rollback became impossible.
- Recovery took longer.
- Risk increased.

---

### Step 6: Hotfix

```text
hotfix parser
```

The team modified the parser to handle the new output format.

Example:

Instead of:

```python
response["summary"]
```

they may have changed logic to support multiple formats.

While this restored functionality, it did not solve the underlying issue.

The deployment remained unpinned.

Future alias updates could cause similar incidents again.

---

### Root Cause

Log Entry:

```text
root cause = unpinned deployment
```

This is the most important lesson.

The failure was not caused by:

- Network issues
- Infrastructure failure
- Security problems
- Bad application code

The root cause was:

> The production system relied on a moving alias instead of a pinned model version.

---

## What Is a Moving Alias?

Alias Example:

```python
model = "opus"
```

or

```python
model = "claude-sonnet"
```

An alias is a convenience name.

Advantages:

- Simple to use
- Automatically receives updates

Disadvantages:

- Behavior can change unexpectedly
- Difficult to reproduce results
- Harder to troubleshoot
- Risk of production regressions

Think of an alias as:

> "Always use the newest version."

---

## What Is a Pinned Version?

Pinned Example:

```python
model = "claude-opus-4-8"
```

or

```python
model = "claude-haiku-4-5-20251001"
```

A pinned version corresponds to a specific model snapshot.

Benefits:

- Stable behavior
- Predictable outputs
- Easier debugging
- Easy rollback
- Better auditability

Think of a pinned version as:

> "Use exactly this version until I explicitly change it."

---

## Proper Production Deployment Process

### Step 1: Pin the Model Version

Instead of:

```python
model = "opus"
```

Use:

```python
model = "claude-opus-4-8"
```

This prevents unexpected changes.

---

### Step 2: Keep Previous Versions

Retain:

- Previous model version
- Previous prompt version
- Previous application release

Example:

```text
Production
├── Version A
└── Version B
```

If Version B fails:

```text
Rollback
↓
Version A
```

Recovery becomes fast and predictable.

---

### Step 3: Run Evaluations

Before promotion:

- Accuracy testing
- Safety testing
- Functional testing
- Integration testing

This detects issues before users see them.

---

### Step 4: Promote Gradually

Example:

```text
10% Traffic
↓
25% Traffic
↓
50% Traffic
↓
100% Traffic
```

Monitor results at each stage.

This limits risk.

---

### Step 5: Roll Back if Necessary

If regressions appear:

```text
New Version
↓
Failure Detected
↓
Restore Prior Pinned Version
```

A rollback should take minutes, not days.

---

## Exam Concepts Being Tested

### Moving Alias

A moving alias can change without warning.

Example:

```python
model = "opus"
```

Risk:

Production behavior changes automatically.

---

### Pinned Model Version

A pinned version remains stable.

Example:

```python
model = "claude-opus-4-8"
```

Benefit:

Predictable outputs.

---

### Rollback

A prior working version must always be retained.

Purpose:

Quick recovery from regressions.

---

### Evaluation Gate

A model should pass evaluations before promotion.

Purpose:

Catch issues before production deployment.

---

### Production Stability

The goal of version pinning is:

- Reliability
- Traceability
- Auditability
- Safe deployment

