## Building a Production Agent (Claude Developer Certification Notes)

### Simple Definition: What is an Agent?

An **agent** is an AI system that:

- Has a goal
- Can use tools
- Maintains context
- Decides what to do next
- Repeats actions until the goal is achieved

Think of it as:

User Request → Agent Thinks → Uses Tool → Gets Result → Thinks Again → Uses Another Tool → Final Answer

A normal chatbot usually responds once.

An agent works in a **loop** until the task is completed.

---

## First Question: Do You Really Need an Agent?

This is one of the most important certification concepts.

Many developers build agents when a simple workflow is enough.

### Use a Workflow When

- Steps are known in advance.
- Process is predictable.
- Inputs are structured.
- Every execution follows the same sequence.
- You need strict control over execution.

Example:

Customer enters order number

1. Validate order
2. Fetch shipment data
3. Return tracking info

The path never changes.

Use a workflow.

---

### Use an Agent When

- Goal is known, but path is unknown.
- User requests are unpredictable.
- Multiple tools may be needed.
- Tool sequence changes per request.
- Creative decision-making is required.

Example:

"Analyze our sales performance, find issues, compare with last quarter, and recommend actions."

The agent must decide:

- Which data to pull
- Which tools to use
- What order to use them in

Use an agent.

---

## Easy Memory Trick

### Workflow

"I know every step."

### Agent

"I know the goal, but not the steps."

---

## The Agent Loop

Every agent follows the same loop.

```text
User Request
      ↓
Agent Reasoning
      ↓
Tool Call
      ↓
Tool Result
      ↓
Update Context
      ↓
Goal Complete?
      ↓
No → Repeat Loop
Yes → Final Answer
```

This loop is the heart of every agent.

---

## Three Ways to Build an Agent

### 1. Raw Messages API Loop

You build everything yourself.

#### You Handle

- Tool registration
- Tool execution
- Context management
- Retry logic
- Exit conditions
- Loop iterations

#### Advantages

- Maximum control
- Full customization

#### Disadvantages

- Most code
- Highest maintenance

Think:

"I own everything."

---

### 2. Agent SDK

The SDK runs the loop for you.

You still execute tools.

#### SDK Handles

- Agent loop
- Iteration
- Context management
- Tool registration structure

#### You Handle

- Tool implementation
- Application logic

#### Advantages

- Faster development
- Less boilerplate

#### Disadvantages

- Less control than raw API

Think:

"Claude manages the framework, I manage the tools."

---

### 3. Claude Managed Agents

Anthropic runs everything.

#### Anthropic Handles

- Agent loop
- Sandbox
- Execution environment
- Session management
- Infrastructure

#### You Handle

- Agent definition
- Application integration

#### Advantages

- Simplest deployment
- Supports long-running agents

#### Disadvantages

- Server-side state
- Compliance limitations
- Less control

Think:

"Anthropic runs the agent."

---

## Quick Comparison

| Feature | Raw API | Agent SDK | Managed Agents |
|----------|----------|------------|----------------|
| Runs Loop | You | SDK | Anthropic |
| Context Management | You | SDK | Anthropic |
| Tool Execution | You | You | Managed Runtime |
| Infrastructure | You | You | Anthropic |
| Control | Highest | Medium | Lowest |
| Development Speed | Slowest | Faster | Fastest |

---

## The Four Parts of Every Agent

Regardless of the wiring path, every agent needs four things.

### 1. Register Tools

Tell Claude which tools are available.

Example:

```text
search_customer
create_ticket
send_email
query_database
```

Claude cannot use tools that are not registered.

---

### 2. Define System Prompt

The system prompt tells the agent:

- What its job is
- What tools it can use
- What success looks like

#### Bad Prompt

```text
Help users with anything.
```

Too broad.

#### Good Prompt

```text
You are a customer support agent.
Use search_customer, create_ticket,
and send_email tools to resolve requests.
```

Specific prompts improve tool selection.

---

### 3. Handle Tool Loop

Whenever Claude requests a tool:

```text
Tool Request
      ↓
Execute Tool
      ↓
Return Result
      ↓
Claude Continues
```

Important certification point:

**All tool calls from one assistant turn must be resolved before moving forward.**

---

### 4. Define Exit Conditions

Without exit conditions, the agent may continue using tools unnecessarily.

Examples:

- Goal completed
- Required information collected
- Maximum iterations reached
- Human approval denied

Always define "done".

---

## Agent Wiring Checklist

Before deployment verify:

### Tool Registration

✅ All required tools exist

✅ No missing tools

✅ No unused tool references

---

### System Prompt

✅ Scope is clear

✅ Available tools are described

✅ Agent role is well-defined

---

### Tool Loop

✅ Every tool request is handled

✅ Tool results returned correctly

✅ Multiple calls resolved together

---

### Human Review

✅ HITL checkpoint exists

---

### Exit Conditions

✅ Clear stopping criteria

---

## Human-in-the-Loop (HITL)

Human-in-the-Loop means:

The agent pauses and asks a human to approve or review something.

Purpose:

Reduce risk.

---

## HITL Placement 1: Before Destructive Actions

Agent wants to:

- Delete data
- Send emails
- Transfer money
- Modify records

### Flow

```text
Agent Plans Action
       ↓
Human Approval
       ↓
Execute Action
```

Risk Level:

High

This is the most common HITL checkpoint.

---

## HITL Placement 2: After Planning

The agent creates a plan.

Before executing it:

A human reviews the plan.

### Example

```text
Migration Plan Created
       ↓
Human Review
       ↓
Execution Starts
```

Risk Level:

Medium

Useful for long tasks.

---

## HITL Placement 3: Unexpected Results

Pause when:

- Error returned
- Empty data returned
- Result looks suspicious
- Values outside expected range

### Example

```text
Database Returned Zero Records
       ↓
Human Review
       ↓
Continue or Stop
```

Risk Level:

Variable

Great for catching hidden failures.

---

## Tool Orchestration

Tool orchestration means:

Deciding which tools an agent gets.

This strongly affects performance.

---

### Under-Tooling

Too few tools.

Problem:

Agent cannot complete tasks.

Example:

Need:

```text
Search Tool
Database Tool
Email Tool
```

But only:

```text
Search Tool
```

Result:

Incomplete answers.

---

### Over-Tooling

Too many tools.

Problem:

Confuses routing decisions.

Example:

```text
search_customer
find_customer
lookup_customer
customer_search_v2
advanced_customer_search
```

All do nearly the same thing.

Claude may choose inefficiently.

Certification Tip:

**Start with the minimum tool set and add tools only when necessary.**

---

## When Agents Are the Right Choice

Use agents when:

- Inputs vary heavily
- Path cannot be predetermined
- Goal is known
- Multiple tools may be required
- Dynamic decision-making is needed

Examples:

- Research assistants
- Customer support agents
- Incident response agents
- Financial analysis agents
- Software debugging agents

---

## When Workflows Are Better

Use workflows when:

- Steps are fixed
- Inputs are predictable
- Compliance requires strict execution
- High determinism is required

Examples:

- Invoice processing
- Password reset flow
- User onboarding
- Order status lookup

Certification Shortcut:

```text
Known Steps = Workflow

Unknown Path = Agent
```

---

## Regulated Data Determines Architecture

Often compliance rules decide the architecture before technical preferences.

### Attorney-Client Privilege

Usually requires:

- Auditable systems
- Controlled logging
- Approved enterprise environment

Avoid:

- Consumer-grade deployments

---

### HIPAA (PHI)

Requires:

- BAA-covered environments
- Approved storage paths
- Approved logging

Avoid:

- Non-covered endpoints

---

### GDPR / Data Residency

Requires:

- Region-specific deployment
- Geographic control of data

Avoid:

- Global endpoints without residency guarantees

---

### FedRAMP / Government

Requires:

- Authorized government environments
- Approved cloud infrastructure

Avoid:

- Non-authorized deployments

---

### Internal Corporate Policies

Requires:

- Approved cloud providers
- Approved regions
- Approved logging systems

Even if another solution is technically better, internal policy usually wins.

---

=
