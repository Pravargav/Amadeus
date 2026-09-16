## Tool Schemas Claude Selects Correctly: Definition, Loop, and Calling Patterns

Tool use is different from normal prompting.

In a standard prompt, Claude generates the answer itself.

With tool use, Claude does **not** execute functions, APIs, databases, or external systems. Instead, Claude:

1. Reads the available tool schemas.
2. Decides which tool matches the user's request.
3. Returns a tool call with the required inputs.
4. Your application executes the tool.
5. Your application sends the result back to Claude.
6. Claude uses that result to continue the conversation.

The quality of Claude's tool selection depends heavily on the schema, especially the tool description.

---

### The Tool Use Loop

Think of tool use as a collaboration between:

- Claude → decides what tool should be called.
- Your Application → actually runs the tool.

Flow:

```text
User Request
      ↓
Claude Reads Tool Schemas
      ↓
Claude Chooses Tool
      ↓
Returns tool_use Block
      ↓
Your Code Executes Tool
      ↓
Your Code Sends tool_result
      ↓
Claude Continues Response
```

Important:

Claude does **not** wait for your code.

After generating a `tool_use` block, Claude's turn ends.

Your code must:

1. Run the tool.
2. Create a new API request.
3. Include the tool result.
4. Send the conversation back to Claude.

If this step is missed, Claude never receives the data and cannot continue.

---

### Step-by-Step Example

#### Step 1: Define Tool Schema

You provide Claude with:

- Tool name
- Tool description
- Input schema

Example:

```json
{
  "name": "get_account_balance",
  "description": "Use this to retrieve the current balance for a specific account ID. Do not use this for transaction history requests.",
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

Claude studies this definition before making any tooling decision.

---

#### Step 2: Send User Message

Example:

```text
What is the balance of account 12345?
```

Tool definitions are included in the request.

---

#### Step 3: Claude Generates a tool_use Block

Instead of answering directly, Claude decides the tool is needed.

```json
{
  "type": "tool_use",
  "id": "toolu_01",
  "name": "get_account_balance",
  "input": {
    "account_id": "12345"
  }
}
```

At this point:

```text
stop_reason = tool_use
```

Claude's turn is finished.

---

#### Step 4: Your Application Executes the Tool

Your code receives:

```json
{
  "account_id": "12345"
}
```

Then calls:

```text
get_account_balance(12345)
```

Example result:

```json
{
  "balance": "$500"
}
```

---

#### Step 5: Return tool_result

Your code sends the result back using the same tool ID.

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01",
  "content": "$500"
}
```

The ID must match exactly.

---

#### Step 6: Claude Continues

Claude now has the tool output.

Response:

```text
The current balance for account 12345 is $500.
```

---

### Message Block Structure

A tool conversation is made of structured blocks.

There are four important block types.

---

### 1. text Block

Purpose:

Claude's normal text response.

Example:

```json
{
  "type": "text",
  "text": "Let me check that balance for you."
}
```

Important Rule:

Claude may return:

```text
text block
+
tool_use block
```

in the same response.

Do not drop the text block when saving conversation history.

Always preserve the entire content array.

---

### 2. tool_use Block

Purpose:

Requests a tool call.

Contains:

- Tool name
- Unique ID
- Input arguments

Example:

```json
{
  "type": "tool_use",
  "id": "toolu_01",
  "name": "get_account_balance",
  "input": {
    "account_id": "12345"
  }
}
```

Important Rule:

Every `tool_use` block must be followed by a matching `tool_result`.

---

### 3. tool_result Block

Purpose:

Returns the tool output.

Example:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01",
  "content": "$500"
}
```

Optional error format:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01",
  "content": "Database unavailable",
  "is_error": true
}
```

Important Rule:

`tool_use_id` must exactly match the original tool call ID.

This is especially important when multiple tools are called.

---

### 4. thinking Block

Purpose:

Contains Claude's internal reasoning when Extended Thinking is enabled.

Example:

```json
{
  "type": "thinking",
  "thinking": "..."
}
```

Important Rule:

Never alter it.

Pass it back exactly as received.

Even redacted thinking blocks must remain unchanged.

Otherwise signature validation fails.

---

### Critical Validation Rule

Always maintain this sequence:

```text
Assistant:
  tool_use

User:
  tool_result

Assistant:
  continues response
```

Correct:

```text
Assistant → tool_use
User      → tool_result
Assistant → answer
```

Incorrect:

```text
Assistant → tool_use
User      → normal text
User      → tool_result
Assistant → answer
```

The API rejects invalid ordering.

---

## Schema Anatomy

A tool schema contains three important components.

```text
1. Name
2. Description
3. Input Schema
```

Among these, the **description** has the biggest impact on tool selection.

---

### 1. Name

The name should clearly communicate purpose.

Good:

```text
get_account_balance
search_customer_orders
create_support_ticket
```

Bad:

```text
get_data
fetch_info
tool1
```

Specific names help Claude quickly identify the correct tool.

---

### 2. Description (Most Important Part)

Claude relies heavily on descriptions when deciding:

- When to use a tool.
- When NOT to use a tool.

A good description contains:

#### What the Tool Does

```text
Use this to retrieve the current balance for a specific account.
```

#### What the Tool Does NOT Do

```text
Do not use this for transaction history requests.
```

This creates clear boundaries.

---

### Weak Description Example

```text
Use this to find information.
```

Problem:

Claude cannot distinguish it from dozens of other tools.

---

### Strong Description Example

```text
Use this to retrieve the current balance for a specific account ID.

Do not use this for:
- transaction history
- account updates
- customer profile information
```

Benefit:

Claude has explicit inclusion and exclusion rules.

This significantly improves tool selection accuracy.

---

### Best Practice for Descriptions

Always answer two questions:

#### When should Claude use this tool?

```text
Use this tool to retrieve the current balance for an account.
```

#### When should Claude NOT use this tool?

```text
Do not use this tool for transaction history or account modification requests.
```

Formula:

```text
Use this tool for [specific purpose].

Do not use this tool for [related but different tasks].
```

---

### 3. Input Schema

Defines the parameters Claude must provide.

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

Claude uses this schema to construct arguments.

---

### Required vs Optional Parameters

Required:

```json
{
  "required": ["account_id"]
}
```

Meaning:

Claude must provide it.

Without it, the tool call is invalid.

---

Optional:

```json
{
  "properties": {
    "currency": {
      "type": "string"
    }
  }
}
```

Meaning:

The tool can still execute even if the value is missing.

---

### Common Cause of Wrong Tool Selection

One of the most common tool-use mistakes is having multiple tools with:

- Similar descriptions
- Similar parameter structures
- Overlapping responsibilities

Example:

Tool A:

```text
Retrieve customer account information.
```

Tool B:

```text
Retrieve customer profile information.
```

Claude may confuse them.

Instead:

Tool A:

```text
Retrieve account balance and account status.
Do not use for customer profile details.
```

Tool B:

```text
Retrieve customer profile data such as name, email, and address.
Do not use for account balances.
```

The clearer the boundary, the better the tool selection.

