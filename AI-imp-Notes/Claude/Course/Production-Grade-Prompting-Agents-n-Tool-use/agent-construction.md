## Building a Production Agent (Claude Developer Certification Notes)

### What is an Agent?

An agent is a system that:

- Has a goal to achieve.
- Uses tools when needed.
- Maintains context across multiple steps.
- Repeats actions in a loop until the goal is completed.

Think of an agent as:

User Request → Reason → Use Tool → Analyze Result → Decide Next Step → Repeat Until Done

Unlike a single LLM call, an agent can perform multiple actions and adapt based on intermediate results.

---

### First Question: Do You Really Need an Agent?

Before writing any code, determine whether the problem requires:

- A Workflow
- An Agent

Using an agent unnecessarily increases:

- Complexity
- Cost
- Context size
- Failure possibilities

---

### Choose a Workflow When

A workflow is best when the process is predictable.

Examples:

- Employee onboarding process
- Invoice approval flow
- Data validation pipeline
- Report generation with fixed steps

Characteristics:

- Exact steps are known beforehand.
- Same sequence runs every time.
- Inputs are restricted and predictable.
- Strong step-by-step control is required.
- Easier debugging and monitoring.

Mental Model:

Step 1 → Step 2 → Step 3 → Done

---

### Choose an Agent When

An agent is best when the path cannot be predefined.

Examples:

- Research assistants
- Customer support agents
- Travel planners
- Coding assistants
- Multi-step troubleshooting systems

Characteristics:

- Goal is known, but path is unknown.
- Inputs vary significantly.
- Tool selection changes dynamically.
- Creative decision making is needed.
- Different executions may follow different routes.

Mental Model:

Goal → Figure Out Steps → Use Tools → Adapt → Reach Goal

---

### Important Principle

Do not start with an agent.

Progression should be:

1. Single API Call
2. Workflow
3. Agent

Move to the next level only if the simpler approach cannot handle the problem.

---

## The Agent Loop

Every agent follows the same fundamental loop:

### Step 1: Receive Goal

Example:

User: "Find top competitors of Company X and summarize them."

---

### Step 2: Reason

The model decides:

- What information is needed
- Which tool to call
- What order to follow

---

### Step 3: Use Tools

Examples:

- Search Tool
- Database Tool
- CRM Tool
- File System Tool
- API Tool

---

### Step 4: Analyze Results

The model evaluates:

- Did the tool return useful data?
- Is more information needed?
- Is another tool required?

---

### Step 5: Repeat if Necessary

Continue until:

- Goal achieved
- Error encountered
- Human approval required

---

### Step 6: Exit

Return final answer and stop.

---

## Wiring Paths

Once you decide to build an agent, there are three ways to implement the loop.

### Option 1: Raw Messages API Loop

You write everything yourself.

You handle:

- Iteration loop
- Tool execution
- Context management
- Retries
- Stopping conditions

Flow:

User -> Claude API -> Tool Call -> Your Code Executes Tool-> Tool Result -> Claude API -> Repeat

Advantages:

- Maximum control
- Custom behavior
- Complete transparency

Disadvantages:

- Most engineering effort
- Highest maintenance cost

Best For:

- Advanced teams
- Custom runtime requirements
- Learning how agents work internally

---

### Option 2: Agent SDK

The SDK manages most of the loop.

You provide:

- Tools
- Agent configuration
- Application logic

The SDK provides:

- Tool registration
- Context handling
- Iteration structure
- Agent orchestration

Advantages:

- Faster development
- Less boilerplate
- Runs in your infrastructure

Disadvantages:

- Less control than raw implementation

Best For:

- Most production applications
- Teams wanting balance between control and simplicity

---

### Option 3: Claude Managed Agents

Anthropic runs:

- The loop
- The sandbox
- Session management
- Long-running execution

You only define:

- Model
- System prompt
- Tools
- MCP servers
- Skills

Advantages:

- Minimal infrastructure work
- Long-running agents supported
- Managed execution environment

Disadvantages:

- Stateful sessions stored server-side
- Less infrastructure control
- Beta features may change

Best For:

- Long-running tasks
- Rapid deployment
- Teams avoiding infrastructure management

---

## How to Choose a Wiring Path

### Use Raw Messages API When

- You need full control.
- Custom compliance requirements exist.
- You want to understand agent internals.

---

### Use Agent SDK When

- You want easier development.
- The agent must run in your environment.
- You need production-ready orchestration quickly.

---

### Use Managed Agents When

- Long execution time is common.
- You want Anthropic-managed infrastructure.
- Building sandbox and orchestration is not desired.

---

## The Four Core Steps of Agent Wiring

Regardless of implementation path, every agent needs four components.

### 1. Register Tools

The agent only knows about registered tools.

Example:

- Search Tool
- Database Tool
- CRM Tool

If a tool is not registered:

- Agent cannot use it.

---

### 2. Define System Prompt

The prompt should be specific.

Bad:

"Help the user."

Good:

"You are a customer support agent. Use CRM and Order tools to resolve customer issues."

Why?

Specific prompts improve tool routing accuracy.

---

### 3. Implement Tool Loop

Every tool call must receive a result.

Process:

Tool Call
↓
Execute Tool
↓
Return Tool Result
↓
Continue Agent

Never leave tool calls unresolved.

---

### 4. Define Exit Conditions

Without exit criteria, agents may continue unnecessarily.

Examples:

- Goal completed
- Maximum iteration reached
- Human approval needed
- Error threshold exceeded

Always define "Done."

---

## Production Checklist

Before deployment verify:

### Tool Registration

✅ All required tools available

✅ No missing tools referenced in prompts

---

### Prompt Scope

✅ Clear responsibility

✅ Appropriate tool guidance

✅ No references to unavailable tools

---

### Tool Loop

✅ Agent handles every tool request

✅ Every tool request receives a result

✅ Multiple tool calls handled properly

---

### Human Review

✅ Human checkpoint exists

✅ Critical actions require approval

---

### Exit Conditions

✅ Clear stopping logic

✅ Agent cannot run forever

---

## Human-in-the-Loop (HITL)

### What is HITL?

Human-in-the-Loop means pausing agent execution for human review before continuing.

Purpose:

Prevent costly mistakes.

---

### HITL Point 1: Before Destructive Actions

Trigger:

Agent is about to:

- Delete data
- Send email
- Modify records
- Execute transactions

Risk:

High

Example:

"Are you sure you want to delete 5,000 customer records?"

Human approval required.

---

### HITL Point 2: After Planning

Trigger:

Agent creates a plan.

Risk:

Medium

Example:

Research Agent:

1. Search competitors
2. Collect reports
3. Produce summary

Human verifies plan before execution.

---

### HITL Point 3: Unexpected Results

Trigger:

Tool returns:

- Error
- Empty result
- Invalid value
- Out-of-range numbers

Risk:

Variable

Example:

Expected revenue: $1M - $10M

Returned value: $500B

Pause for review.

---

## Tool Orchestration

Tool orchestration means deciding:

- Which tools exist
- How many tools exist
- How tools are described

Poor orchestration creates routing problems.

---

### Under-Tooling

Too few tools.

Problem:

Agent cannot complete task.

Example:

Research agent without web search capability.

Result:

Incomplete answers.

---

### Over-Tooling

Too many tools.

Problem:

Agent becomes confused.

Example:

10 tools performing nearly identical searches.

Result:

Poor tool selection.

---

### Best Practice

Start small.

Add tools only when a genuine capability gap exists.

Rule:

Minimum Tools Required > Large Tool Collection

---

## Common Production Failures

### Context Explosion

Problem:

Conversation history grows too large.

Result:

- Higher cost
- Slower responses
- Context loss

Solution:

- Summarize old context
- Prune unnecessary history

---

### Incorrect Tool Input

Problem:

Tool receives malformed data from previous step.

Result:

Chain failure

Solution:

- Validate tool inputs
- Use structured schemas

---

### Tool Routing Errors

Problem:

Agent chooses wrong tool.

Solution:

- Improve tool descriptions
- Remove overlapping tools
- Narrow system prompt

---

### Infinite Loops

Problem:

Agent keeps calling tools.

Solution:

- Maximum iteration limits
- Explicit exit conditions

