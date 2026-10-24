### Normal Functions vs LangChain Tools

Yes, Python agents can call normal functions, but **LLM-powered LangChain agents cannot effectively use arbitrary normal functions unless they are exposed as tools**.

Think of it from the agent's perspective.

#### Normal Function

```python
def add(a, b):
    return a + b
```

A Python program can call it:

```python
result = add(5, 10)
```

But an LLM sees only text. It doesn't know:

- The function exists
- What arguments it accepts
- When to call it
- What the return type is

---

#### What `@tool` Adds

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

LangChain converts this into a **Tool object** with metadata:

```python
print(add.name)
# add

print(add.description)
# Add two numbers.

print(add.args)
# schema showing a and b
```

The agent can now see:

```json
{
  "name": "add",
  "description": "Add two numbers",
  "parameters": {
    "a": "integer",
    "b": "integer"
  }
}
```

---

#### Why Normal Functions Don't Work Directly

Consider:

```python
def calculate_salary(emp_id):
    ...
```

If you do:

```python
tools = [calculate_salary]
```

Most agent constructors expect **Tool objects**, not raw Python callables.

The agent needs:

- Function name
- Description
- Argument schema
- Validation rules

A plain function typically provides none of these.

---

#### What `@tool` Internally Does

```python
@tool
def get_weather(city: str):
    """Get weather."""
    return "Sunny"
```

becomes roughly:

```python
StructuredTool(
    name="get_weather",
    description="Get weather.",
    func=get_weather,
    args_schema=...
)
```

The original function still exists. The decorator simply wraps it with metadata.

---

#### Without `@tool`

Using `StructuredTool`:

```python
from langchain_core.tools import StructuredTool

def add(a: int, b: int):
    return a + b

tool = StructuredTool.from_function(add)
```

Using `Tool`:

```python
from langchain.tools import Tool

tool = Tool(
    name="add",
    description="Add two numbers",
    func=add
)
```

So `@tool` is mainly a convenience wrapper.

---

#### Can an Agent Call a Normal Function?

##### Case 1: Inside Python Code

```python
def add(a, b):
    return a + b

result = add(1, 2)
```

No tool required.

##### Case 2: LangChain Agent

```python
agent = create_tool_calling_agent(
    llm,
    [add],
    prompt
)
```

Usually this won't work because the LLM cannot see enough metadata.

Instead:

```python
@tool
def add(a: int, b: int):
    ...
```

or

```python
StructuredTool.from_function(add)
```

---

#### Real-World Analogy

A normal function is like hiding a calculator in a drawer:

```python
def add(a, b):
    return a + b
```

The employee doesn't know:

- The drawer exists
- What's inside
- How to use it

A tool is like giving the employee a catalog:

```text
Tool Name: add
Purpose: Add two numbers

Inputs:
 
