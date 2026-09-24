## The Pieces Passed and the Seam Broke

This scenario is a classic example of an **integration failure**. The individual components worked correctly on their own, but the connection between them failed.

---

## Scenario Overview

You have two components:

### Retrieval Component

Returns:

```python
[
    {"content": "Refunds are processed within 7 days"},
    {"content": "Customers receive email confirmation"}
]
```

### Prompt Builder

Expected:

```python
"Refunds are processed within 7 days"
```

The retrieval system returned a **list of dictionaries**, while the prompt builder expected a **plain string**.

Because of this mismatch, the context was inserted incorrectly into the prompt.

Result:

```text
Malformed Context
        ↓
Model ignores retrieved data
        ↓
Model answers from memory
        ↓
End-to-End test fails
```

---

## What the Trace Shows

Trace output:

```text
PASS  test_parser_unit

PASS  test_extract_shape_functional

FAIL  test_full_flow_e2e
```

At first glance:

```text
Parser → Working
Model Call → Working
System → Failing
```

---

### Step 1: Retrieval

```text
retrieve(q)

OK

→ 3 chunks (list of dicts)
```

Output:

```python
[
    {"content": "..."},
    {"content": "..."},
    {"content": "..."}
]
```

Retrieval behaved correctly.

---

### Step 2: Prompt Builder

```text
build_prompt(ctx)

OK

→ ctx inserted as raw list
```

Instead of converting chunks into text:

```python
"policy text ..."
```

The prompt builder inserted:

```python
[
    {"content": "..."},
    {"content": "..."}
]
```

No exception occurred, so the step appears successful.

However, the context format was wrong.

---

### Step 3: Model Call

```text
model.call(prompt)

OK

→ answer ignores context
```

The Claude call succeeded technically.

The model received malformed context and could not properly use the retrieved information.

Therefore it responded using its pretrained knowledge instead.

Important:

```text
The model call succeeded.
The answer was wrong.
```

---

### Step 4: Assertion

```text
assert answer...

FAIL
```

The final answer did not match expectations.

The E2E test detects the failure.

---

## Why Unit Tests Passed

Unit test:

```text
test_parser_unit
```

Checks only:

```text
Parser Input
      ↓
Parser Output
```

Example:

```python
parse("2025-01-01")
```

Output:

```python
date(2025, 1, 1)
```

Everything works.

The parser never sees retrieval results.

Therefore the handoff problem remains hidden.

---

## Why Functional Tests Passed

Functional test:

```text
test_extract_shape_functional
```

Checks:

```text
Prompt
    ↓
Claude
    ↓
Structured Output
```

Example:

```json
{
  "primary_date": "2025-01-01",
  "issue": "refund"
}
```

The model returned the expected format.

Since the functional test used a well-formed prompt, the retrieval mismatch never appeared.

Result:

```text
Functional Test = PASS
```

---

## Why the End-to-End Test Failed

The E2E test executed:

```text
Retrieve
   ↓
Build Prompt
   ↓
Claude
   ↓
Parser
   ↓
Result
```

This was the first test that exercised the entire workflow.

During execution:

```text
Retrieval Output
        ↓
Prompt Builder Input
```

The formats did not match.

This broke the system.

Result:

```text
End-to-End Test = FAIL
```

---

## The Real Root Cause

The issue was not:

```text
❌ Retrieval Logic
❌ Prompt Logic
❌ Parser Logic
❌ Claude Call
```

The issue was:

```text
✅ Component Handoff
```

Specifically:

```text
Missing Format Contract
```

Retriever:

```python
List[Dict]
```

Prompt Builder:

```python
String
```

Expected and actual formats were different.

---

## What Is a Format Contract?

A format contract defines exactly what data one component sends and another component receives.

Example:

### Agreed Contract

```python
{
    "content": str
}
```

or

```python
str
```

Every component must follow the same structure.

Without a contract:

```text
Component A assumes one format
Component B assumes another format
```

Eventually:

```text
Integration Failure
```

---

## How Integration Testing Prevents This

Integration tests connect real components together.

Example:

```python
retrieved_chunks = retrieve(query)

prompt = build_prompt(retrieved_chunks)

assert "Refunds" in prompt
```

This test verifies:

```text
Retrieve
      ↓
Prompt Builder
```

works correctly.

If formats differ:

```text
Test Fails Immediately
```

before production deployment.

