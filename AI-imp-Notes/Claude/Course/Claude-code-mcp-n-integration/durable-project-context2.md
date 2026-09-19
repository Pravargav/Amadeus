## Durable Context Mechanisms - Certification Notes

Think of Claude Code as having 4 different ways to remember information or enforce behavior:

```text
CLAUDE.md     = Permanent project instructions
Rules Files   = Instructions for specific files/folders
Hooks         = Automatic enforcement
Subagents     = Isolated helper assistants
```

Each serves a different purpose.

---

## CLAUDE.md

### What it loads

The entire file is automatically added to Claude's context when a session starts.

```text
Project Start
      ↓
Read CLAUDE.md
      ↓
Load into Context
      ↓
Process User Prompt
```

### When it runs

Every session.

Always loaded.

No conditions.

### Context Cost

High because it stays in context throughout the session.

The larger it gets, the less attention Claude can effectively give to any single rule.

### What belongs here

Project-wide instructions such as:

- Framework preferences
- Build commands
- Testing commands
- Code review expectations
- Global restrictions
- Architecture decisions that apply everywhere

Example:

```md
Always run:

npm test

before completing work.

Do not modify:

/database/schema
```

### Remember

CLAUDE.md should contain:

```text
Universal project rules
```

not

```text
Project history
```

---

## Rules Files

### What it loads

Contents of the rule file.

Usually loaded only when matching files are involved.

### Location

```text
.claude/rules/
```

### How Scoping Works

A rule becomes file-specific through YAML frontmatter.

Example:

```yaml
---
paths:
  - "src/db/**/*.sql"
---
```

Now the rule loads only when Claude works with SQL files inside that path.

### When it runs

For scoped rules:

```text
Only when matching files are accessed
```

For unscoped rules:

```text
Loads like CLAUDE.md
```

at session start.

### Context Cost

Much lower than CLAUDE.md because the rule loads only when needed.

### What belongs here

File-specific guidance.

Example:

```text
Database rules
React component rules
Security module requirements
Infrastructure conventions
```

### Certification Shortcut

Ask:

```text
Does this apply everywhere?
```

If yes:

```text
CLAUDE.md
```

If no:

```text
Rules File
```

---

## Hooks

### What they load

Hooks do not load instructions into Claude's context.

Instead, they execute scripts automatically.

### Why They Matter

Instructions can be forgotten.

Hooks cannot.

Example:

Instruction:

```md
Run prettier after every edit.
```

Claude may forget.

Hook:

```text
PostToolUse → Run Prettier
```

Runs automatically every time.

### When they run

At specific lifecycle events.

### Common Events

#### PreToolUse

Runs before a tool executes.

Used for:

- Validation
- Security
- Restrictions

Can block actions.

Example:

```text
Prevent editing production files
```

---

#### PostToolUse

Runs after the action completes.

Used for:

- Formatting
- Testing
- Logging

Example:

```text
Run lint after file edit
```

---

#### UserPromptSubmit

Runs before Claude processes the prompt.

Used for:

- Request validation
- Context injection

---

#### Stop

Runs after Claude finishes responding.

Used for:

- Notifications
- Cleanup tasks

---

#### Notification

Runs when Claude:

- Requests permissions
- Is idle

Used for:

- Alert systems
- Monitoring

---

#### SessionStart

Runs when the session begins.

Used for:

- Environment checks
- Initialization

---

#### SessionEnd

Runs when the session finishes.

Used for:

- Cleanup
- Audit logging

### Context Cost

Very small.

Only script output might be sent back to Claude.

### What belongs here

Things that:

```text
Must happen every time
```

Examples:

- Format code
- Run tests
- Block restricted paths
- Audit logging

### Important Certification Concept

```text
Convention = Instruction
Guardrail  = Hook
```

A hook is stronger than a written rule.

---

## Subagents

### What they load

Only task-specific context.

They do not inherit the entire main conversation.

### How They Work

```text
Main Agent
     ↓
Delegate Task
     ↓
Subagent
     ↓
Performs Work
     ↓
Returns Result
```

### Key Characteristic

Subagents operate in isolation.

They do not automatically inherit:

- Conversation history
- Session memory
- Loaded files
- Current context

### When They Run

Only when the main session delegates a task.

### Context Cost

Low.

Instead of returning the full history, they return only the final result or summary.

### What belongs here

Large tasks such as:

- Research
- Investigation
- Exploration
- Planning
- Parallel work

### Why They Are Useful

Without subagents:

```text
Research output fills your context
```

With subagents:

```text
Only final findings return
```

This keeps the main context clean.

---

## Built-in Subagents

### Explore Agent

Purpose:

```text
Fast research and discovery
```

Loads:

```text
Minimal context
```

Does NOT load:

```text
CLAUDE.md
Git Status
```

Advantage:

```text
Fast and cheap
```

Risk:

```text
Project rules may not apply
```

---

### Plan Agent

Purpose:

```text
Architecture and planning
```

Also skips:

```text
CLAUDE.md
Git Status
```

Best for:

```text
Design discussions
High-level plans
```

---

### General-Purpose Agent

Loads:

```text
CLAUDE.md
Git Status
```

Best when project constraints matter.

---

## Custom Subagents

Location:

```text
.claude/agents/
```

You can create specialized agents.

Examples:

```text
security-agent
frontend-agent
backend-agent
database-agent
```

### Important Rule

Custom subagents do NOT automatically receive skills.

You must explicitly configure them.

Example:

```yaml
skills:
  - code-review
  - security-audit
```

Without this configuration:

```text
Skill unavailable to that agent
```

---

## Comparison

### CLAUDE.md

Loads:

```text
Entire file
```

Runs:

```text
Every session
```

Best For:

```text
Universal project rules
```

Context Cost:

```text
High and persistent
```

---

### Rules Files

Loads:

```text
Matching scoped rules
```

Runs:

```text
When relevant files are used
```

Best For:

```text
Area-specific instructions
```

Context Cost:

```text
Lower and targeted
```

---

### Hooks

Loads:

```text
No instruction context
```

Runs:

```text
Lifecycle events
```

Best For:

```text
Enforcement and automation
```

Context Cost:

```text
Minimal
```

---

### Subagents

Loads:

```text
Task-specific context
```

Runs:

```text
When delegated
```

Best For:

```text
Research and isolated work
```

Context Cost:

```text
Returns summary only
```

---

## Certification Scenario: Growing CLAUDE.md

### The Problem

A team keeps adding rules to CLAUDE.md.

After several months:

```text
CLAUDE.md = 847 lines
```

Contents:

```text
Framework rules
Testing rules
Style guide
Historical decisions
Old notes
Archived content
```

Everything is loaded into every session.

### What Happened?

User says:

```text
Do not modify /legacy/tokens/
```

The same restriction already exists in CLAUDE.md.

Claude still edits:

```text
/legacy/tokens/store.ts
```

### Why?

Not because the rule was missing.

The rule existed.

The problem was:

```text
Instruction Dilution
```

One important rule was competing with hundreds of less important lines.

### Lesson

CLAUDE.md is not a knowledge archive.

It is a:

```text
Behavior-control document
```

### Move These Out

Historical decisions:

```text
Reference document
```

Archived notes:

```text
Reference document
```

Path-specific rules:

```text
Rules files
```

Critical restrictions:

```text
Hooks whenever possible
```

