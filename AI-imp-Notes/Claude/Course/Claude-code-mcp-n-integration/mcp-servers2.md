## MCP Setup Reference (Certification-Friendly Notes)

### Quick Idea

When configuring an MCP server, always think about 4 decisions:

1. Transport (How Claude communicates with the server)
2. Scope (Who can use the server)
3. Configuration Location (Where settings are stored)
4. Secrets Handling (Where credentials are stored)

A simple memory trick:

```text
Transport = How to connect
Scope = Who gets access
Config = Where settings live
Secrets = Where credentials live
```

---

## MCP Deployment Scenarios

### Personal Local Tool

Situation:

```text
Tool runs only on your machine.
```

Configuration:

```text
Transport : stdio
Scope     : Local
Config    : ~/.claude.json
Secrets   : Environment Variables
```

Example:

```text
Local SQLite MCP
Personal Script MCP
Local Testing Tool
```

Important:

```text
Never place API keys directly in configuration files.
```

---

### Shared Team Server

Situation:

```text
Entire team uses same server.
```

Configuration:

```text
Transport : HTTP
Scope     : Project
Config    : .mcp.json
Secrets   : OAuth or Environment Variables
```

Example:

```text
GitHub MCP
Jira MCP
Internal Company MCP
```

Important:

```text
.mcp.json can be committed.
Secrets must NOT be committed.
```

---

### Personal Experiment

Situation:

```text
Testing an MCP server before sharing.
```

Configuration:

```text
Transport : stdio or HTTP
Scope     : Local
Config    : Personal Claude Settings
Secrets   : Environment Variables
```

Example:

```text
Prototype MCP
Experimental Integration
```

---

### Enterprise Deployment

Situation:

```text
Entire organization needs access.
```

Configuration:

```text
Transport : HTTP
Scope     : Enterprise
Config    : Admin Managed
Secrets   : Managed by Administrators
```

Example:

```text
Security Tools
Compliance Systems
Internal Enterprise Services
```

Important:

```text
Users cannot freely modify enterprise-controlled configurations.
```

---

## Cost, Complexity, and Risk

### Cost

Every connected MCP server contributes:

```text
Tool Definitions
Metadata
Context Usage
```

More servers:

```text
More Tokens
More Cost
More Context Consumption
```

Example:

```text
5 MCP Servers
=
More Context Usage

1 MCP Server
=
Less Context Usage
```

Best Practice:

```text
Connect only the servers needed for the current work.
```

Certification Tip:

> More MCP servers = Higher context cost.

---

### Complexity

Transport and Scope are separate decisions.

However:

```text
They influence each other.
```

Example:

A stdio server runs only on one machine.

Therefore:

```text
Cannot truly be shared with the entire team.
```

Wrong Thinking:

```text
stdio + Team Sharing
```

Correct Thinking:

```text
HTTP + Project Scope
```

Memory Rule:

```text
Choose Transport first.
Choose Scope second.
```

---

### Risk

Biggest mistake in MCP setup:

```text
Committing API Keys
```

Example:

```text
API Key inside .mcp.json
```

Consequences:

- Credential exposure
- Security incident
- Key rotation required
- Service disruptions

Certification Tip:

> Secrets belong in environment variables, not configuration files.

---

## When MCP Is a Good Choice

### Handles Well

Use MCP when:

```text
Capability is reusable
```

and

```text
Multiple users or projects need it
```

Examples:

- GitHub MCP
- Jira MCP
- Internal Knowledge Base MCP
- Database MCP

Benefits:

- One implementation
- Reusable everywhere
- Easy maintenance

Think:

```text
Build Once → Use Many Times
```

---

## When MCP Adds Complexity

MCP may create extra management work when:

```text
Many servers exist
```

and

```text
Many secrets must be managed
```

Risks increase because:

```text
More servers
=
More credentials
=
More chances for mistakes
```

Special Attention:

```text
.mcp.json
```

because it is often committed to source control.

---

## When You Should Use Another Approach

Situation:

```text
One developer
One project
One simple integration
```

Instead of:

```text
Building a full MCP Server
```

You can:

```text
Integrate tool directly into application code.
```

Reason:

```text
Less setup
Less maintenance
Less complexity
```

Certification Tip:

> Not every integration needs an MCP server.

---

## Case Study: API Key Committed to Repository

### Setup

A developer connected to a:

```text
Data Warehouse MCP Server
```

using:

```text
Service Account API Key
```

To save time:

```text
API key was placed directly into .mcp.json
```

The plan was:

```text
Move it to environment variable later.
```

Unfortunately:

```text
The file was committed first.
```

---

### What Happened

Developer committed:

```text
.mcp.json
```

containing:

```text
Real API Key
```

Repository was shared.

Within 48 hours:

- 3 teammates cloned repository
- CI pipeline cloned repository
- Repository history stored credential

The key now existed in:

```text
Developer Machine
Repository History
3 Teammate Machines
CI Runner
```

Result:

```text
Credential Exposure
```

---

### Attempted Fix

Developer later:

1. Removed API key.
2. Added environment variable.
3. Committed new version.

Problem:

```text
Old Commit Still Exists
```

The secret was still available in:

```text
Git History
```

Therefore:

```text
Credential considered compromised.
```

---

### Additional Impact

The service account key was used elsewhere.

When security team rotated the key:

```text
Other Systems Broke
```

Result:

```text
Hours of Emergency Work
```

Lesson:

> Once a secret enters Git history, removing it from the latest file version is not enough.

---

## Wrong Configuration (Never Use)

Inline credential:

```json
{
  "type": "http",
  "url": "https://warehouse.internal/mcp",
  "headers": {
    "Authorization": "Bearer sk-abc123..."
  }
}
```

Problem:

```text
Secret stored directly in file.
```

If committed:

```text
Secret enters repository history.
```

---

## Correct Configuration

Environment variable reference:

```json
{
  "type": "http",
  "url": "https://warehouse.internal/mcp",
  "headers": {
    "Authorization": "Bearer ${WAREHOUSE_MCP_TOKEN}"
  }
}
```

Actual secret stored in:

```text
WAREHOUSE_MCP_TOKEN
```

Benefits:

- Safer
- Rotatable
- Not committed to Git
- Follows security best practices

Certification Tip:

> Configuration file stores references, not actual secrets.

---

## What To Watch Out For

### Common Misunderstanding

Developers often think:

```text
I removed the key in a later commit.
```

Problem:

```text
Old commits still contain the key.
```

Meaning:

```text
The credential is exposed forever in history
until history is rewritten.
```

Therefore:

```text
Treat as compromised.
Rotate immediately.
```

---

## Best Practice for Secret Protection

Use Two Layers of Protection.

### Layer 1: CLAUDE.md Instruction

Add rule:

```text
Never write credentials directly
inside .mcp.json.
```

Purpose:

```text
Guides Claude.
```

However:

```text
Instructions can be missed.
```

---

### Layer 2: PreToolUse Hook

Create hook that checks:

```text
File Writes
File Edits
.mcp.json Changes
```

The hook searches for:

```text
API Keys
Tokens
Credentials
```

If detected:

```text
Block Operation
```

Example:

```text
Inline Secret Found
       ↓
Hook Triggered
       ↓
Action Blocked
```

Purpose:

```text
Enforcement
```

Unlike instructions:

```text
Hooks execute every time.
```

---

## Instruction vs Hook

### CLAUDE.md Instruction

Role:

```text
Communicate Intent
```

Example:

```text
Do not place secrets in .mcp.json
```

Weakness:

```text
Can be ignored accidentally.
```

---

### Hook

Role:

```text
Enforce Rule
```

Example:

```text
Block commits containing API keys
```

Strength:

```text
Runs automatically
Every time
Without exception
```



