## The Description That Sent Claude to the Wrong Tool

### Key Idea

A tool schema can be technically correct but still fail if Claude cannot clearly distinguish between tools.

The most common reason:

```text
Two tools have similar descriptions.
```

Claude then has no clear rule for choosing the correct one.

---

### Example Problem

Tool 1:

```text
search_docs

Use this to find information about the product.
```

Tool 2:

```text
get_context_summary

Use this to retrieve relevant information from the current session.
```

From a developer's perspective they seem different.

From Claude's perspective:

```text
Both are trying to find information.
```

So Claude may choose the wrong tool.

---

### The Fix

Add a boundary to each description.

#### search_docs

```text
Use this when the user asks for information not already present in the conversation.

Do not use this if the answer is available in the current session context.
```

#### get_context_summary

```text
Use this when the answer already exists in the current session.

Do not use this to look up new information.
```

Now Claude knows:

```text
New information  → search_docs

Existing session information → get_context_summary
```

---

### Certification Lesson

A good tool description needs **two parts**:

#### When To Use It

```text
Use this tool for...
```

#### When NOT To Use It

```text
Do not use this tool for...
```

This is called an **exclusion condition**.

---

### What To Watch Out For

If two tools:

- Do similar things
- Have similar descriptions
- Accept similar inputs

Claude may select the wrong tool.

Fix:

```text
Add clear exclusion conditions.
```

If the tools still cannot be clearly separated:

```text
Merge them into one tool
and use a type parameter.
```

Example:

```text
search_information(type="docs")
search_information(type="context")
```

