## Schema Design & MCP for Claude Developer Certification

Tool selection is not magic.

Claude decides which tool to call by reading the tool schema. If the schema is unclear, Claude may:

- Choose the wrong tool
- Provide incorrect arguments
- Make unnecessary tool calls
- Create inefficient tool-use loops

For certification, remember:

```text
Claude chooses tools based primarily on:
1. Tool Name
2. Tool Description
3. Input Schema
```

The description is the most important factor.

---

### Schema Anatomy

A tool schema contains three parts:

```text
1. Name
2. Description
3. Input Schema
```

Example:

```json
{
  "name": "get_account_balance",
  "description": "Use this to retrieve the current balance for a specific account ID. Do not use this for transaction history.",
  "input_schema": {
    "type": "object",
    "properties": {
      "account_id": {
        "type": "string"
      }
    },
    "required": ["account_id"]
  }
}
```

---

### 1. Name

The name is a short identifier.

Claude uses it as a signal during tool selection.

Good names:

```text
get_account_balance
create_support_ticket
search_customer_orders
```

Bad names:

```text
get_data
fetch_info
tool1
```

Why?

Because specific names communicate intent.

---

### 2. Description (Most Important)

Claude relies heavily on descriptions to determine:

```text
When should I use this tool?
When should I avoid this tool?
```

A strong description always contains:

#### What The Tool Does

Example:

```text
Use this tool to retrieve the current balance for a specific account.
```

#### What The Tool Does NOT Do

Example:

```text
Do not use this tool for transaction history requests.
```

These are called exclusion conditions.

---

### Weak Description

```text
Use this tool to find information.
```

Problem:

Many tools can find information.

Claude cannot distinguish between them.

This causes wrong-tool selection.

---

### Strong Description

```text
Use this tool to retrieve the current balance for a specific account ID.

Do not use this for:
- transaction history
- customer profile data
- account updates
```

Benefit:

Claude now understands the tool boundaries.

---

### Description Formula

For certification, use this pattern:

```text
Use this tool for [specific task].

Do not use this tool for [similar but different tasks].
```

Example:

```text
Use this tool to retrieve account balances.

Do not use it for transaction history or account modification requests.
```

---

### 3. Input Schema

The input schema defines what data Claude must provide.

Example:

```json
{
  "type": "object",
  "properties": {
    "account_id": {
      "type": "string"
    }
  },
  "required": ["account_id"]
}
```

Claude reads this to build tool arguments.

---

## Required Fields

A field should be required only when the tool cannot work without it.

Example:

```json
{
  "required": ["account_id"]
}
```

Meaning:

```text
Claude must provide account_id.
```

Without it, the tool call is invalid.

---

### Why Overusing Required Fields Is Dangerous

Suppose:

```json
{
  "required": [
    "account_id",
    "currency",
    "region",
    "branch"
  ]
}
```

If the user only provided the account ID:

```text
Check balance for account 12345
```

Claude may invent values for:

```text
currency
region
branch
```

This creates incorrect tool inputs.

---



## Optional Fields

Optional fields should be used when:

- Defaults exist
- Missing values are acceptable
- The tool can still function

Example:

```json
{
  "properties": {
    "currency": {
      "type": "string"
    }
  }
}
```

Not included in:

```json
required
```

Therefore Claude can omit it.

---

### Why Optional Fields Help

If Claude doesn't know a value:

Good:

```text
Leave it empty.
```

Bad:

```text
Guess the value.
```

Optional fields reduce hallucinated inputs.

---

## Decision Table: Important Schema Design Choices

### 1. Subtask Dependency

Ask:

```text
Does Tool B need Tool A's result?
```

If YES:

```text
Tool A
    ↓
Result
    ↓
Tool B
```

Use sequential tool calls.

Example:

```text
Find Customer ID
      ↓
Get Customer Balance
```

The second tool cannot run until the first result arrives.

---

### Independent Tasks

If tools do not depend on each other:

```text
Tool A
Tool B
Tool C
```

Claude can call them together.

This is called parallel tool use.

Example:

```text
Check weather
Check stock price
Check exchange rate
```

All can run simultaneously.

---

### Sequential vs Parallel

Sequential:

```text
Tool A
 ↓
Result
 ↓
Tool B
```

Parallel:

```text
Tool A
Tool B
Tool C
```

Current Claude models prefer parallel execution when tasks are independent.

---

## Description Length

A common mistake is making descriptions too short or too long.

---

### Too Short

```text
Use this tool to search.
```

Problem:

Not enough information.

Claude guesses.

---

### Too Long

```text
Use this tool to...
(15 paragraphs)
```

Problem:

Important routing instructions become hidden inside unnecessary details.

---

### Recommended Length

Use:

```text
3-4 concise sentences
```

Cover:

1. What it does
2. When to use it
3. When not to use it
4. Input examples if format matters

---

## Overlapping Parameter Types

This is a major certification topic.

Suppose:

Tool A

```text
Accepts:
query:string
```

Tool B

```text
Accepts:
query:string
```

The parameter shapes are identical.

Claude can no longer rely on parameter structure.

It must rely on descriptions.

---

### Bad Example

Tool A:

```text
Use this to find information.
```

Tool B:

```text
Use this to locate data.
```

To Claude:

```text
They look nearly identical.
```

Wrong tool selection becomes common.

---

### Better Example

Tool A:

```text
Retrieve customer profile information.

Do not use for account balances.
```

Tool B:

```text
Retrieve account balances.

Do not use for customer profile information.
```

Now Claude has a clear routing rule.

---

## Worked Example: Wrong Tool Selection

Imagine two tools.

---

### Tool 1

```text
search_knowledge_base
```

Description:

```text
Use this to find information.
```

---

### Tool 2

```text
get_cached_result
```

Description:

```text
Use this to find information.
```

Problem:

Both look identical.

Claude doesn't know which one to use.

---

### Fixed Version

#### search_knowledge_base

```text
Use this to search the knowledge base when the user needs current information.

Do not use if previous search results in this session already answer the question.
```

---

#### get_cached_result

```text
Use this to retrieve information already fetched during this conversation.

Only use if search_knowledge_base was previously called for the same query.
```

Now Claude has:

```text
Inclusion conditions
+
Exclusion conditions
```

Selection becomes reliable.

---

## Important Dependency: Conversation History

The previous example works only if conversation history is preserved.

Claude must be able to see:

```text
Previous tool calls
Previous tool results
Previous messages
```

If history is removed:

```text
Claude cannot determine
whether a previous search occurred.
```

The routing logic fails.

---

## When To Merge Tools Instead

Sometimes developers create many similar tools.

Example:

```text
search_books
search_articles
search_documents
search_pdfs
```

Each description becomes longer and longer.

At some point:

```text
Claude struggles to distinguish them.
```

Better solution:

```text
search_content
```

with:

```json
{
  "type": "book"
}
```

or

```json
{
  "type": "article"
}
```

Rule:

```text
If two tools do almost the same thing,
merge them and use a parameter.
```

---

## MCP (Model Context Protocol)

MCP is a standardized way to connect Claude to external services.

Instead of manually creating:

- Tool names
- Descriptions
- Schemas
- Execution functions

you can use an MCP server that already provides them.

---

### Example: GitHub

Without MCP:

You build:

```text
get_repository
create_issue
close_issue
list_pull_requests
create_pr
merge_pr
```

Plus schemas and execution code.

Lots of work.

---

### With MCP

GitHub MCP Server already provides these tools.

Your application simply connects to the server.

Claude receives the available tools automatically.

---

## MCP Does NOT Change The Tool Loop

The tool loop remains exactly the same.

```text
Claude
   ↓
tool_use
   ↓
Application
   ↓
Execute Tool
   ↓
tool_result
   ↓
Claude Continues
```

Only the source of the tool definitions changes.

---

## How MCP Loads Tools

Before chatting:

```text
Application
      ↓
ListToolsRequest
      ↓
MCP Server
      ↓
Tool Definitions Returned
      ↓
Claude Receives Tools
```

Claude then selects tools normally.

To Claude:

```text
Manual Tool
and
MCP Tool
```

look the same.

---

## MCP Context Window Cost

Important certification concept.

Every tool definition consumes context.

Example:

```text
Server A = 20 tools
Server B = 30 tools
Server C = 50 tools
```

Total:

```text
100 tool definitions
```

Even before the user sends a message.

This consumes valuable context window space.

---

## Two MCP Optimization Settings

### defer_loading

Purpose:

```text
Load a tool only when Claude needs it.
```

Benefit:

Lower initial context cost.

---

### enabled

Purpose:

```text
Turn specific tools on or off.
```

Benefit:

Claude only sees relevant tools.

Fewer tools = better routing accuracy.

---

## MCP Transport Types

There are two transports.

### 1. stdio

Used for local servers.

Communication:

```text
Application
     ↔
Local MCP Server
```

via standard input/output.

---

### 2. Streamable HTTP

Used for remote servers.

Communication:

```text
Application
      ↔
Remote MCP Server
```

over HTTP.

This is the preferred modern approach.

---

## When Should You Use MCP?

### Use MCP When

```text
A reliable MCP server already exists.
```

Example:

```text
GitHub
Atlassian
Database services
Enterprise systems
```

No need to recreate tool schemas.

---

### Use Manual Schemas When

```text
No MCP server exists.
```

Or:

```text
You need complete control
over descriptions and behavior.
```

---

### Use Both Together

Best practice:

```text
MCP for broad functionality
+
Custom schema tuning for precision
```

This gives:

```text
Maximum Coverage
+
Maximum Accuracy
```

