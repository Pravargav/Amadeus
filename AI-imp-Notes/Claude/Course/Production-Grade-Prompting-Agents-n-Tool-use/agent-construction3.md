# These are three increasingly higher-level ways to build with Claude:

## 1. Raw Messages API Loop

You directly manage the conversation loop, tool execution, retries, context, and state.

### Flow

```
User
  ↓
Messages API
  ↓
Claude requests tool
  ↓
Your code executes tool
  ↓
Tool result sent back
  ↓
Claude responds
```

### Example

```python
from anthropic import Anthropic

client = Anthropic()

messages = [
    {
        "role": "user",
        "content": "What's the weather in Bangalore?"
    }
]

tools = [
    {
        "name": "get_weather",
        "description": "Get current weather",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    }
]

while True:
    response = client.messages.create(
        model="claude-sonnet-4",
        max_tokens=1000,
        messages=messages,
        tools=tools
    )

    assistant_content = response.content

    tool_use = next(
        (block for block in assistant_content
         if block.type == "tool_use"),
        None
    )

    if not tool_use:
        print(response.content[0].text)
        break

    city = tool_use.input["city"]

    # Execute tool yourself
    weather = f"28°C and sunny in {city}"

    messages.append({
        "role": "assistant",
        "content": assistant_content
    })

    messages.append({
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": tool_use.id,
            "content": weather
        }]
    })
```

### Responsibility

✅ Full control  
✅ Lowest abstraction  
❌ Must write tool loop yourself  
❌ Must manage context, retries, memory

---

## 2. Agent SDK

The SDK manages the agent loop automatically, but you still provide tools.

### Flow

```
User
  ↓
Agent SDK
  ↓
Claude
  ↓
Tool calls handled automatically
  ↓
Final answer
```

### Example

```python
from anthropic import Agent, tool

@tool
def get_weather(city: str) -> str:
    return f"28°C and sunny in {city}"

agent = Agent(
    model="claude-sonnet-4",
    tools=[get_weather]
)

result = agent.run(
    "What's the weather in Bangalore?"
)

print(result.output)
```

### Multi-step Example

```python
from anthropic import Agent, tool

@tool
def search_flights(destination: str):
    return f"Flight to {destination}: ₹6,500"

@tool
def search_hotels(destination: str):
    return f"Hotel in {destination}: ₹3,000/night"

agent = Agent(
    model="claude-sonnet-4",
    tools=[search_flights, search_hotels]
)

response = agent.run(
    "Plan a weekend trip to Goa"
)

print(response.output)
```

### The SDK automatically:

- Calls tools
- Feeds results back
- Handles multi-step reasoning
- Returns final answer

### Responsibility

✅ Less boilerplate  
✅ Automatic tool loop  
✅ Easier development  
❌ Less low-level control

---

## 3. Claude Managed Agents

Anthropic hosts and manages the entire agentic workflow.

### Flow

```
User
  ↓
Managed Agent
  ↓
Claude
  ↓
Built-in memory
  ↓
Built-in tool orchestration
  ↓
Long-running tasks
```

### Create an Agent Once

```python
agent = client.beta.agents.create(
    name="Travel Planner",
    model="claude-sonnet-4",
    instructions="""
    Plan trips and compare travel options.
    """
)
```

### Then Use It

```python
response = client.beta.agents.run(
    agent_id=agent.id,
    input="Plan a 3-day Goa vacation"
)

print(response.output)
```

### Example with MCP Tools

```python
agent = client.beta.agents.create(
    name="Support Agent",
    tools=[
        {
            "type": "mcp",
            "server_url": "https://company-mcp-server.com"
        }
    ]
)

response = client.beta.agents.run(
    agent_id=agent.id,
    input="Check ticket INC12345 status"
)
```

### The managed agent can:

- Maintain agent configuration
- Use MCP tools
- Store state/memory
- Handle orchestration
- Run complex workflows

### Responsibility

✅ Lowest engineering effort  
✅ Managed memory/state  
✅ Built-in orchestration  
✅ Best for production agents  
❌ Least control  
❌ Platform-managed behavior
