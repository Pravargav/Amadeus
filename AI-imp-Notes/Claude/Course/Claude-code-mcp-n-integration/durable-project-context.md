## Durable Project Context in Claude Code (Claude Developer Certification Notes)

### Big Picture

Claude Code gives you multiple ways to make behavior persist across sessions. Think of them as different layers:

1. `CLAUDE.md` → Project-wide memory and instructions
2. `Rules Files` → Instructions for specific parts of the codebase
3. `Hooks` → Automatic enforcement and automation
4. `Subagents` → Specialized assistants with isolated contexts

A simple way to remember:

- CLAUDE.md = "What Claude should always know"
- Rules Files = "What Claude should know only in certain folders/files"
- Hooks = "What Claude must automatically do or must never do"
- Subagents = "Extra assistants that work independently"

---

## 1. CLAUDE.md

### What is it?

`CLAUDE.md` is a project-level instruction file.

Whenever Claude Code starts in a project, it automatically reads this file before processing any user prompt.

Everything inside becomes part of Claude's context from the beginning of every session.

### Why use it?

You don't need to repeatedly tell Claude:

- Coding standards
- Project conventions
- Test commands
- Protected directories
- Preferred frameworks
- Review requirements

### Example

```md
Always run:

npm test

Before committing changes.

Do not modify:

/database/schema

Use:

npm run lint
```

### How to create it?

Run:

```bash
/init
```

Claude scans the project and generates an initial `CLAUDE.md`.

### Best Practice

Keep it small and important.

Good content:

- Project rules
- Coding standards
- Required commands
- Critical restrictions

Avoid:

- Huge documentation
- Rarely used instructions
- Long implementation details

### Certification Tip

Think of `CLAUDE.md` as:

> Permanent project memory loaded into every session.

---

## 2. Rules Files

### Why do we need them?

Not every instruction applies to the entire repository.

Example:

A SQL rule should only apply to database files.

Instead of placing everything in `CLAUDE.md`, create scoped rules.

### Location

```text
.claude/rules/
```

### Example Structure

```text
.claude/
└── rules/
    ├── database.md
    ├── frontend.md
    └── backend.md
```

### Path-Based Loading

Rules use YAML frontmatter:

```yaml
---
paths:
  - "src/db/**/*.sql"
---
```

Now the rule loads only when Claude works with SQL files.

### Example Rule

```md
---
paths:
  - "src/db/**/*.sql"
---

Every SQL statement must include
an explicit transaction boundary.
```

### Important Exam Point

Folder placement does NOT control loading.

This:

```text
.claude/rules/database/example.md
```

does not become database-specific automatically.

Only the `paths` field determines scope.

### Best Practice

Put:

- Global rules → `CLAUDE.md`

Put:

- File-specific guidance → Rules Files

### Certification Shortcut

Ask yourself:

"Does this apply to the entire repository?"

- Yes → CLAUDE.md
- No → Rules File

---

## 3. Hooks

### What are Hooks?

Hooks run scripts automatically at specific lifecycle events.

Unlike instructions, hooks do not depend on the model remembering to do something.

### Why are Hooks Powerful?

Compare:

Rule:

```md
Run Prettier after every edit.
```

Claude might forget.

Hook:

```text
PostToolUse → Run Prettier
```

Runs every time.

No exceptions.

---

### Main Hook Events

#### PreToolUse

Runs before a tool executes.

Used for:

- Validation
- Security
- Access control

Can block actions.

Exit code:

```text
2
```

means:

```text
Tool call denied
```

Example:

```text
Prevent changes to production configs
```

---

#### PostToolUse

Runs after a tool completes.

Used for:

- Formatting
- Testing
- Logging

Example:

```text
After file edit:
Run prettier
```

---

#### UserPromptSubmit

Runs before Claude processes a prompt.

Used for:

- Request validation
- Context injection

Example:

```text
Check issue ticket exists before work begins
```

---

#### Stop

Runs after Claude finishes responding.

Used for:

- Notifications
- Cleanup
- Logging

---

#### Notification

Runs when:

- Claude requests permission
- Claude is idle

Used for:

- Slack notifications
- Audit systems

---

#### SessionStart

Runs when a session starts.

Used for:

- Environment validation
- Service availability checks
- Initialization

---

#### SessionEnd

Runs when a session ends.

Used for:

- Cleanup
- Final logging
- Notifications

---

### Certification Tip

A hook is stronger than an instruction.

Instruction:

> Please don't edit production files.

Hook:

> Editing production files is technically impossible.

---

## 4. Subagents

### What are Subagents?

Subagents are separate assistants that Claude can delegate work to.

Each subagent:

- Starts with a fresh context
- Performs a task
- Returns only the result

### Important Concept

Subagents do NOT automatically inherit:

- Current conversation
- Loaded files
- Session state
- Existing context

Think of them as:

> Temporary independent workers.

---

## Built-in Subagents

### Explore Agent

Purpose:

- Fast investigation
- Research
- Discovery

Loads:

- Minimal context

Does NOT load:

- CLAUDE.md
- Git status

Advantage:

- Faster
- Cheaper

Risk:

- Project rules may not apply

---

### Plan Agent

Purpose:

- Planning
- Architecture suggestions

Also skips:

- CLAUDE.md
- Git status

Best for:

- High-level planning

---

### General-Purpose Agent

Purpose:

- Regular development tasks

Loads:

- CLAUDE.md
- Git status

Best choice when project rules must be respected.

---

## Custom Subagents

Location:

```text
.claude/agents/
```

You can create specialized agents.

Example:

```text
backend-agent
frontend-agent
security-agent
```

### Skills and Custom Subagents

Custom subagents do not automatically get skills.

If a skill is required, explicitly include it in the agent configuration.

### Example

```yaml
skills:
  - security-review
  - code-analysis
```

Without this:

```text
Subagent cannot use those skills.
```

### Certification Tip

Need project rules?

Use:

```text
General-Purpose Agent
```

Need speed?

Use:

```text
Explore or Plan Agent
```

Need specialized behavior?

Use:

```text
Custom Subagent
```

---

## Quick Comparison

### CLAUDE.md

Purpose:

```text
Global project memory
```

Loads:

```text
Every session
```

Use for:

```text
Project-wide rules
```

---

### Rules Files

Purpose:

```text
Scoped instructions
```

Loads:

```text
Only for matching files
```

Use for:

```text
Folder/file-specific guidance
```

---

### Hooks

Purpose:

```text
Automatic enforcement
```

Runs:

```text
Lifecycle events
```

Use for:

```text
Validation, automation, security
```

---

### Subagents

Purpose:

```text
Task delegation
```

Runs:

```text
Isolated context
```

Use for:

```text
Research, planning, specialized work
```

---
