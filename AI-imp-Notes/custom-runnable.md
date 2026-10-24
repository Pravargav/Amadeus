### Custom Runnables in LangChain (LCEL)

Custom Runnables are one of the most important concepts in modern LangChain, especially when working with **LCEL (LangChain Expression Language)**.

Think of a **Runnable** as:

> Anything that can participate in a LangChain pipeline and supports methods like `.invoke()`, `.batch()`, `.stream()`, `.ainvoke()`, etc.

Examples of built-in runnables:

```text
Prompt Templates
Chat Models (LLMs)
Retrievers
Output Parsers
Chains
```

A **Custom Runnable** is simply your own code wrapped so it behaves like any other LangChain component.

---

### Why Do Custom Runnables Exist?

Consider a simple chain:

```text
Prompt
   ↓
LLM
   ↓
Output
```

In real-world applications, you often need additional logic:

- Preprocess input
- Validate requests
- Fetch external data
- Call APIs
- Transform outputs
- Apply business rules
- Format retrieved documents

Instead of writing standalone Python code outside the chain, you can package that logic as a runnable.

Result:

```text
Input
   ↓
Custom Runnable
   ↓
Prompt
   ↓
LLM
   ↓
Output
```

Everything becomes a composable LangChain component.

---

### Simplest Custom Runnable: `RunnableLambda`

The easiest way to create a custom runnable is with `RunnableLambda`.

```python
from langchain_core.runnables import RunnableLambda

def uppercase(text):
    return text.upper()

upper = RunnableLambda(uppercase)

print(
    upper.invoke("hello")
)
```

Output:

```text
HELLO
```

Observe the transformation:

```python
uppercase("hello")
```

becomes:

```python
upper.invoke("hello")
```

Now it's compatible with LCEL.

---

### Chaining a Custom Runnable with an LLM

```python
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

clean_text = RunnableLambda(
    lambda x: x.strip().lower()
)

chain = clean_text | llm

response = chain.invoke(
    "   WHAT IS LANGCHAIN?   "
)

print(response.content)
```

Flow:

```text
Input
   ↓
Custom Runnable
   ↓
LLM
   ↓
Output
```

The runnable cleans the text before the model sees it.

---

### Adding Business Rules

Imagine your company has a rule:

> Inputs longer than 100 characters must be truncated.

```python
from langchain_core.runnables import RunnableLambda

def truncate(text):
    return text[:100]

truncate_runnable = RunnableLambda(
    truncate
)
```

Chain:

```python
chain = (
    truncate_runnable
    | prompt
    | llm
)
```

Result:

```text
User Input
      ↓
Truncate Runnable
      ↓
Prompt
      ↓
LLM
```

The LLM never receives oversized input.

---

### Working with Dictionaries

Many LCEL chains pass dictionaries instead of plain strings.

Example:

```python
def enrich(data):
    data["country"] = "Singapore"
    return data
```

```python
enrich_runnable = RunnableLambda(
    enrich
)

result = enrich_runnable.invoke(
    {"name": "John"}
)

print(result)
```

Output:

```python
{
    "name": "John",
    "country": "Singapore"
}
```

Useful for:

- Enriching context
- Adding metadata
- Preprocessing chain inputs

---

### Runnable Parallel

Multiple runnables can execute simultaneously.

```python
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel
)

parallel = RunnableParallel(
    uppercase=RunnableLambda(
        lambda x: x.upper()
    ),
    count=RunnableLambda(
        lambda x: len(x)
    )
)

print(
    parallel.invoke("langchain")
)
```

Output:

```python
{
    "uppercase": "LANGCHAIN",
    "count": 9
}
```

Flow:

```text
           Input
             |
    ------------------
    |                |
Uppercase        Count
    |                |
    ------------------
             |
          Output
```

This is useful when several independent computations can run together.

---

### Class-Based Custom Runnable

For more advanced logic, create your own runnable class.

```python
from langchain_core.runnables import Runnable

class WordCounter(Runnable):

    def invoke(
        self,
        text,
        config=None
    ):
        return len(
            text.split()
        )
```

Usage:

```python
counter = WordCounter()

print(
    counter.invoke(
        "hello world from langchain"
    )
)
```

Output:

```text
4
```

This approach is often used when:

- Logic becomes complex
- Internal state is required
- Multiple methods must be implemented

---

### Real RAG Example

Retrieved documents are often messy.

Before passing them to the LLM, we format them.

```python
def format_docs(docs):
    return "\n\n".join(
        doc.page_content
        for doc in docs
    )
```

```python
formatter = RunnableLambda(
    format_docs
)
```

Typical RAG chain:

```python
rag_chain = (
    retriever
    | formatter
    | prompt
    | llm
)
```

Flow:

```text
Question
    ↓
Retriever
    ↓
Documents
    ↓
Custom Formatter Runnable
    ↓
Prompt
    ↓
LLM
```

The formatter is a custom runnable.

---

### Custom Runnable vs Normal Function

Normal function:

```python
def clean(text):
    return text.lower()
```

Usage:

```python
clean("HELLO")
```

It cannot participate directly in LCEL.

---

Runnable version:

```python
clean_runnable = RunnableLambda(
    clean
)
```

Usage:

```python
clean_runnable.invoke(
    "HELLO"
)
```

or

```python
clean_runnable | prompt | llm
```

Additional capabilities:

```python
.invoke()
.batch()
.stream()
.ainvoke()
```

---

### Custom Runnable vs Tool

These are commonly confused.

---

#### Tool

```python
from langchain_core.tools import tool

@tool
def add(a, b):
    return a + b
```

Purpose:

```text
Used by Agents

Agent decides:
- Whether to use it
- When to use it
- Which arguments to provide
```

Flow:

```text
User
  ↓
Agent
  ↓
Tool (Optional)
```

---

#### Runnable

```python
from langchain_core.runnables import RunnableLambda

add_runnable = RunnableLambda(
    lambda x: x + 5
)
```

Purpose:

```text
Part of the workflow itself
```

Flow:

```text
Input
  ↓
Runnable
  ↓
Next Step
```

It always executes when the chain runs.

---

### Tool vs Runnable Summary

#### Tool

```text
Exposed Capability
For Agents
Agent Chooses Whether To Execute
```

#### Runnable

```text
Workflow Component
For Chains
Always Executes As Part Of Pipeline
```

---

### Mental Model

```text
Tool
    = Capability exposed to an Agent

Runnable
    = Building Block in a Chain

Custom Runnable
    = Your Own Building Block
```

---

### Where Custom Runnables Are Commonly Used

#### Input Validation

```text
Validate
    ↓
Prompt
    ↓
LLM
```

---

#### Data Enrichment

```text
Fetch Customer Data
        ↓
Add Context
        ↓
Prompt
```

---

#### API Integration

```text
Input
   ↓
Weather API Runnable
   ↓
Prompt
   ↓
LLM
```

---

#### RAG Document Formatting

```text
Retriever
    ↓
Formatter Runnable
    ↓
Prompt
    ↓
LLM
```

---

#### Output Transformation

```text
LLM Output
      ↓
Parser Runnable
      ↓
Final Result
```

---

### LCEL Perspective

Everything in LCEL follows the same idea:

```text
Input
  ↓
Runnable
  ↓
Runnable
  ↓
Runnable
  ↓
Output
```

Examples:

```python
prompt
llm
retriever
parser
custom_logic
```

All can be chained together using:

```python
|
```

Operator.

Example:

```python
custom_runnable \
| prompt \
| llm \
| parser
```

