## Testing and Tracing for Claude Developer Certification

Testing and tracing are critical parts of production-grade AI systems. An evaluation (eval) score tells you whether the system is performing well overall, but it does not identify where failures occur. To build reliable Claude applications, you need both:

- Testing → Detects failures
- Tracing → Locates failures

### Why Evals Alone Are Not Enough

An eval provides a numerical measure of quality.

Example:

- Eval Score = 92/100

A system can even pass an eval while hiding failures in intermediate workflow steps. Therefore, testing and tracing must be implemented underneath the evaluation layer.

---

## Four Levels of Testing

Each testing level catches a different kind of failure.

### Unit Testing

Tests an individual function or component in isolation.

Examples:

- Parser function
- Tool wrapper
- Data formatter
- Validation logic

Goal:

- Verify a single piece of functionality works correctly.

What it catches:

- Logic bugs inside a component
- Incorrect handling of inputs
- Formatting issues

What it cannot catch:

- Problems caused by interactions with other components

Example:

```python
def parse_amount(text):
    return float(text)

assert parse_amount("100") == 100.0
```

Think of unit tests as checking one building block at a time.

---

### Functional Testing

Tests a single Claude API call.

Goal:

- Validate that the model returns the expected output structure.

Checks:

- Required fields exist
- Correct data types
- JSON is parseable
- Output follows schema

Example:

Input:

```text
Extract:
Order ID: 12345
```

Expected:

```json
{
  "order_id": "12345"
}
```

What it catches:

- Prompt design issues
- Invalid responses
- Schema violations

What it cannot catch:

- Problems elsewhere in the system

Functional testing validates the model call itself rather than the workflow around it.

---

### Integration Testing

Tests how multiple components work together.

Goal:

- Verify successful handoff between system components.

Example Workflow:

```text
Retriever
    ↓
Prompt Builder
    ↓
Claude Model
    ↓
Parser
```

Common integration points:

- Retrieval → Model
- Model → Parser
- Tool → Agent
- Database → Retrieval

What it catches:

- Data mismatches
- Missing fields
- Broken handoffs
- Incorrect assumptions between components

Why this matters:

Most silent production failures happen here.

Each component may pass its own tests, but the data exchanged between them may be incorrect.

Example:

Retriever returns:

```json
{
  "customer_id": "123"
}
```

Model expects:

```json
{
  "user_id": "123"
}
```

Both components work individually, yet the workflow fails.

---

### End-to-End (E2E) Testing

Tests the complete system exactly as a user experiences it.

Goal:

- Validate the entire workflow from input to final output.

Example:

```text
User Question
     ↓
Retrieval
     ↓
Prompt Creation
     ↓
Claude Call
     ↓
Parsing
     ↓
Final Response
```

What it catches:

- Real-world failures
- Cross-system errors
- Workflow-level issues

Advantages:

- Highest confidence
- Closest to production behavior

Disadvantages:

- Slowest test type
- Hardest to diagnose failures

Example:

```text
User: Where is my refund?
```

Expected:

```text
Refund issued on September 15.
```

If output is wrong, E2E identifies a failure but does not reveal which step caused it.

---

## Tracing

Tests identify that something failed.

Tracing identifies where it failed.

### What Is a Trace?

A trace records:

- Inputs
- Prompts
- Tool calls
- Intermediate outputs
- Execution times
- Final result

Think of a trace as a detailed timeline of system execution.

---

### Example Trace

```text
[trace run_id=8f21c]

case: "Where is my refund?"

step 1
retrieve(query)
OK
42 ms
→ 3 chunks

step 2
build_prompt(chunks)
OK
1 ms
→ 1240-token prompt

step 3
model.call(prompt)
OK
980 ms
→ answer generated

step 4
parse(answer)
FAIL
2 ms
→ KeyError: amount

Final Score: 0
```

---



## Testing vs Tracing


Best Practice:

Use both together.

```text
Tests detect problems.
Traces explain problems.
```

---

## Routing: Choosing the Right Retrieval Strategy

Not every query requires expensive agentic search.

A routing step can decide the best execution path.

### Router Architecture

```text
User Query
      ↓
   Router
   /    \
Lookup   Multi-Step
  ↓          ↓
Fetch Once  Agentic Search
```

---

### Example

```python
def route(query):
    kind = classify(query)

    if kind == "lookup":
        return fetch_once(query)

    return agentic_search(query)
```

---

### Lookup Path

Used for:

- Single-fact questions
- Stable knowledge bases
- Direct information retrieval

Examples:

```text
What is the refund policy?
```

```text
What is Claude's context window?
```

Advantages:

- Faster
- Cheaper
- Lower latency

---

### Multi-Step Path

Used for:

- Complex questions
- Reasoning tasks
- Multi-document synthesis
- Iterative searching

Examples:

```text
Compare customer complaints from the last quarter and identify trends.
```

Advantages:

- Better depth
- Higher reasoning capability

Trade-off:

- Increased cost
- Increased latency

---

### Why Routing Matters

Without router:

```text
Every query uses agentic search.
```

Result:

- Unnecessary expense
- Increased response time

With router:

```text
Simple queries → Cheap path
Complex queries → Expensive path
```

