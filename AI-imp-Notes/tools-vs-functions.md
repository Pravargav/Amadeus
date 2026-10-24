Yes, Python agents can call normal functions, but LLM-powered LangChain agents cannot effectively use arbitrary normal functions unless they are exposed as tools.

Think of it from the agent's perspective.

Normal Function
def add(a, b):
    return a + b


A Python program can call it:

result = add(5, 10)


But an LLM sees only text. It doesn't know:

The function exists
What arguments it accepts
When to call it
What the return type is
What @tool Adds
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


LangChain converts this into a Tool object with metadata:

print(add.name)
# add

print(add.description)
# Add two numbers.

print(add.args)
# schema showing a and b


The agent can now see:

{
  "name": "add",
  "description": "Add two numbers",
  "parameters": {
    "a": "integer",
    "b": "integer"
  }
}


This schema is sent to the model.

The model can reason:

User asked "What is 25 + 18?"
 I should call tool "add" with arguments:

{"a": 25, "b": 18}

Why Normal Functions Don't Work Directly

Consider:

def calculate_salary(emp_id):
    ...


If you do:

tools = [calculate_salary]


Most agent constructors will fail because they expect Tool objects, not raw Python callables.

The agent needs metadata:

function name
description
argument schema
validation

A plain function typically provides none of these.

What @tool Internally Does

Roughly:

@tool
def get_weather(city: str):
    """Get weather."""
    return "Sunny"


becomes something like:

StructuredTool(
    name="get_weather",
    description="Get weather.",
    func=get_weather,
    args_schema=...
)


The original function is still there.

The decorator simply wraps it with agent-friendly metadata.

Without @tool

You can manually create a tool:

from langchain_core.tools import StructuredTool

def add(a: int, b: int):
    return a + b

tool = StructuredTool.from_function(add)


or

from langchain.tools import Tool

tool = Tool(
    name="add",
    description="Add two numbers",
    func=add
)


So @tool is mostly convenience.

Can an Agent Call a Normal Function?
Case 1: Inside your Python code

Absolutely.

def add(a, b):
    return a + b

result = add(1, 2)


No tool required.

Case 2: LangChain Agent

Not directly.

agent = create_tool_calling_agent(
    llm,
    [add],   # raw function
    prompt
)


Usually this won't work correctly because the agent cannot derive enough tool metadata.

You must expose it as:

@tool
def add(a: int, b: int):
    ...


or

StructuredTool.from_function(add)

Real Analogy

Imagine the agent is a new employee.

A normal function is like hiding a calculator inside a drawer:

def add(a,b):
    return a+b


The employee doesn't know:

the drawer exists
what is inside
how to use it

A tool is like giving the employee a catalog:

Tool Name: add
Purpose: Add two numbers
Inputs:
  a : int
  b : int


Now the employee knows when and how to use it.

Modern OpenAI Tool Calling Perspective

Under the hood, LangChain tools map to the LLM's function/tool calling API.

The model receives something like:

{
  "name": "add",
  "description": "Add two numbers",
  "parameters": {
    "type": "object",
    "properties": {
      "a": {"type": "integer"},
      "b": {"type": "integer"}
    }
  }
}


A plain Python function cannot automatically be sent to the model in this structured format.

That's the main reason tools exist.

In one sentence

A normal function is for Python code to call; a LangChain tool is a normal function plus metadata/schema that allows an LLM agent to discover, select, and invoke it intelligently.
