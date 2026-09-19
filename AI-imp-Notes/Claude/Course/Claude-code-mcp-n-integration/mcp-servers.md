## Building and Configuring an MCP Server (Claude Developer Certification Notes)

### What is an MCP Server?

MCP (Model Context Protocol) is a standard way to provide tools, resources, and prompts to AI applications like Claude.

Without MCP:

- Every application builds its own integration.
- Tool definitions and implementation are tightly coupled to the application.
- Multiple applications must re-implement the same integration.

With MCP:

- You create one MCP server.
- The server exposes capabilities.
- Any MCP client (such as Claude Code) can connect and use them.
- Integration is built once and reused everywhere.

Think of an MCP Server as:

> A reusable service that exposes tools, resources, and prompts to AI clients.

---

### Why Use an MCP Server Instead of Direct Tool Wiring?

Direct Tool Integration:

```text
App A → GitHub Integration
App B → GitHub Integration
App C → GitHub Integration
```

Problems:

- Duplicate code
- Separate maintenance
- Inconsistent implementations

MCP Approach:

```text
           ┌─────────────┐
App A ───► │ MCP Server  │
App B ───► │  (GitHub)   │
App C ───► │             │
           └─────────────┘
```

Benefits:

- Build once
- Reuse everywhere
- Easier maintenance
- Standardized interface

---

### Three Things an MCP Server Can Expose

An MCP server can expose:

1. Tools
2. Resources
3. Prompts

---

### 1. Tools

Tools are actions Claude can execute.

Examples:

- Create GitHub issue
- Search repository
- Review pull request
- Query database

Example:

```text
User: Create a bug issue in GitHub

Claude
  ↓
GitHub MCP Tool
  ↓
Issue Created
```

Use tools when:

- An action must be performed.
- Data must be retrieved dynamically.
- Something changes in an external system.

---

### 2. Resources

Resources are read-only data.

Instead of Claude calling a tool every time, the client can fetch data directly and place it into context.

Examples:

```text
Available Documents
Company Policies
API Documentation
Knowledge Base Articles
```

Two Types:

#### Direct Resource

Fixed address.

Example:

```text
/company/policies
```

Returns the same data every time.

#### Templated Resource

Contains parameters.

Example:

```text
/document/{id}
```

Examples:

```text
/document/100
/document/200
```

Use resources when:

- Data is predictable.
- Read-only access is enough.
- Bringing data into context is cheaper than calling a tool.

---

### 3. Prompts

Prompts are reusable instruction templates hosted on the server.

Instead of users writing instructions repeatedly:

```text
Analyze this pull request and provide review feedback
```

The server provides:

```text
prompt: review_pr
```

Benefits:

- Consistent outputs
- Central maintenance
- Better quality instructions

Use prompts when:

- Precise wording matters.
- You want standardized behavior across users.

---

## MCP Transport: How Claude Talks to the Server

Transport is the communication method between:

```text
Claude Client ↔ MCP Server
```

There are three transport types.

---

### 1. stdio (Most Common for Local Development)

How it works:

```text
Claude
   ↓
Launches Process
   ↓
MCP Server
```

Communication occurs through:

```text
stdin
stdout
```

Use for:

- Personal tools
- Local scripts
- Development environments

Example:

```json
{
  "command": "node",
  "args": ["server.js"]
}
```

Advantages:

- Easy setup
- No networking required
- Fast local communication

Limitation:

- Cannot be shared remotely.

Exam Tip:

> stdio = Local machine only.

---

### 2. HTTP (Recommended)

How it works:

```text
Claude
   ↓ HTTP
Remote MCP Server
```

Use for:

- Team-wide services
- Cloud-hosted servers
- Enterprise systems

Example:

```text
https://mcp.company.com
```

Advantages:

- Shared access
- Remote hosting
- Recommended transport

Exam Tip:

> For remotely hosted MCP servers, choose HTTP.

---

### 3. SSE (Server-Sent Events)

Older transport mechanism.

```text
Claude
   ↓ SSE
Server
```

Important:

- Legacy approach
- Superseded by HTTP
- Not recommended for new implementations

Exam Tip:

> SSE is supported mainly for backward compatibility.

---

## Context Cost and MCP Servers

Every MCP server introduces:

- Tool definitions
- Metadata
- Context overhead

Loading all tools immediately would consume context window space.

Claude solves this by using:

### Tool Discovery

Instead of loading everything:

```text
100 Tools Available
```

Claude loads only:

```text
Tools Needed For Current Task
```

This reduces:

- Context usage
- Cost
- Token consumption

Exam Tip:

> Claude performs tool discovery and loads tools on demand.

---

## Prompt Caching

### Problem

Every request normally re-processes:

```text
System Prompt
Tool Definitions
Documents
Instructions
```

This costs tokens every time.

---

### Solution

Prompt caching stores processed content and reuses it.

Example:

Request 1:

```text
Large Prompt
Large Tool Definitions
```

Cache created.

Request 2:

```text
Same Prefix
```

Claude reuses cache.

Result:

- Faster processing
- Lower cost
- Less repeated work

---

### Cache Breakpoint

Caching is enabled by:

```json
{
  "cache_control": {
    "type": "ephemeral"
  }
}
```

You mark where the cache should end.

Everything before that point is cached.

---

### Cache Lifetimes

Default:

```text
5 Minutes
```

Optional:

```text
1 Hour
```

```json
{
  "ttl": "1h"
}
```

---

### Important Rules

Caching works best for:

- Tool definitions
- Long system prompts
- Reference documents

Cache becomes invalid if:

- Content before breakpoint changes

Exam Tip:

> Even a single character change before the breakpoint invalidates the cache.

---

## Retrieval-Augmented Generation (RAG)

### Why RAG Exists

Imagine:

```text
10,000 Documents
```

Loading all documents into context is impossible.

RAG solves this by:

1. Storing documents externally.
2. Finding relevant content.
3. Sending only relevant pieces to Claude.

---

### Classical RAG

Work done beforehand.

Process:

```text
Documents
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Database
```

When a question arrives:

```text
Question
   ↓
Embedding
   ↓
Similarity Search
   ↓
Relevant Chunks
```

Think of it as:

> A librarian who created an index before the library opened.

---

### Agentic Search

No pre-built index.

Process:

```text
Question
   ↓
Claude Searches
   ↓
Reads Sources
   ↓
Retrieves Information
```

Think of it as:

> A researcher finding information live.

---

### Claude Examples of Agentic Search

#### MCP Tool Discovery

Claude searches tools when needed.

#### Claude Projects

Claude retrieves only relevant document sections.

---

### Advantages of RAG

#### Scales Well

Even if documents grow:

```text
100 docs → retrieve small set
1000 docs → retrieve small set
10000 docs → retrieve small set
```

Request cost remains relatively stable.

---

#### Retrieval Quality Matters

Claude only reasons over retrieved content.

Bad organization:

```text
notes_final_v3.pdf
```

Better organization:

```text
Q3 Refund Policy Updated Aug 2024.pdf
```

Exam Tip:

> Retrieval quality depends heavily on how information is organized.

---

## MCP Configuration Scope

Scope determines:

```text
Who gets access to the server?
```

Four scopes exist.

---

### 1. Local Scope

Stored in:

```text
~/.claude.json
```

Characteristics:

- Current project only
- Personal
- Not shared

Use when:

- Testing
- Project-specific tools
- Temporary integrations

Exam Tip:

> Local scope = Only this project on your machine.

---

### 2. User Scope

Characteristics:

- Available across all projects
- Personal
- Not shared with teammates

Examples:

- Database tool
- Personal utilities
- Favorite automation tools

Exam Tip:

> User scope = Available everywhere for you.

---

### 3. Project Scope

Stored in:

```text
.mcp.json
```

at repository root.

Characteristics:

- Commit to Git
- Shared with team
- Travels with repository

Use when:

- Entire team uses same server

Example:

```text
GitHub MCP
Jira MCP
Internal API MCP
```

Important:

Every teammate runs their own server process.

Exam Tip:

> Project scope = Shared through version control.

---

### 4. Enterprise Scope

Managed centrally by administrators.

Characteristics:

- Organization-wide
- Automatically deployed
- Central governance

Use when:

- Security tools
- Internal company services
- Compliance systems

Exam Tip:

> Enterprise scope = Admin-managed deployment.

---

## MCP Tool Permissions

Permissions can target individual tools.

Format:

```text
mcp__server__tool
```

Example:

```text
mcp__github__create_issue
```

---

### Allow Rule

```text
Allow:
mcp__github__create_issue
```

Only issue creation runs automatically.

Other GitHub tools may still require approval.

---

### Deny Rule

```text
Deny:
mcp__github__delete_repository
```

Repository deletion becomes unavailable.

Even if the server itself is allowed.

Important:

```text
Deny > Allow
```

Deny rules always win.

---

## Enabled Tools vs Permissions

Two separate controls exist.

### Enabled Flag

Controls:

```text
Can Claude See It?
```

Example:

```text
Tool Hidden
```

Claude cannot use it.

---

### Permission Rule

Controls:

```text
Can Claude Run It?
```

Example:

```text
Tool Visible
But Needs Approval
```

Think of it like:

```text
Enabled = Visibility
Permission = Execution Rights
```

---

## GitHub MCP Server Example

### What It Provides

Tools for:

- Managing repositories
- Reviewing pull requests
- Creating issues
- Searching code
- Repository operations

---

### Transport

GitHub MCP is hosted remotely.

Therefore:

```text
HTTP Transport
```

is used.

Exam Question:

> Which transport should GitHub MCP use?

Answer:

```text
HTTP
```

---

### Scope Choice

#### Local Scope

Use when:

```text
Only you need GitHub access.
```

#### Project Scope

Use when:

```text
Entire team needs GitHub tooling.
```

---

### Authentication

GitHub uses:

```text
Personal Access Token (PAT)
```

Process:

1. Generate PAT in GitHub.
2. Store token securely.
3. Put token in environment variable.
4. Reference environment variable in MCP config.

Example:

```text
GITHUB_TOKEN=xxxx
```

Never do this:

```json
{
  "token": "ghp_abc123"
}
```

inside:

```text
.mcp.json
```

Reason:

- Gets committed to Git
- Stays in repository history
- Security risk

Exam Tip:

> Store GitHub PAT in environment variables, never directly in `.mcp.json`.

---

## GitHub vs Linear Authentication

### GitHub

Authentication Type:

```text
Personal Access Token
```

You:

- Create token manually.
- Store credential manually.

---

### Linear

Authentication Type:

```text
OAuth
```

Process:

```text
Sign In
   ↓
Authorize Access
   ↓
Token Automatically Issued
```

You do not manually manage credentials.

