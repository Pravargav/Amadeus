## Claude Code Agent Loop, Permission Modes, Settings, and Human Review Gate

### Big Picture

Claude Code works like an AI software engineer that follows a cycle:

1. Explore the codebase
2. Build a plan
3. Make changes
4. Run commands/tools if needed
5. Review results
6. Continue until the task is finished

The important part is that Claude Code does **not immediately start coding**. It first tries to understand the project before making changes.

---

### How Claude Code Handles a Task

#### Phase 1: Explore

Claude Code first investigates the codebase:

- Reads files
- Understands project structure
- Traces functions and dependencies
- Identifies where changes are needed

Goal: Understand before modifying.

Example:

You ask:

> "Add JWT authentication to this Node.js API."

Claude Code will first inspect:

- Authentication files
- Middleware
- Routes
- Database logic
- Existing security patterns

before writing any code.

---

#### Phase 2: Plan

After understanding the project, Claude Code creates a plan.

A plan typically includes:

- Files to modify
- New files to create
- Commands to run
- Possible risks
- Expected outcomes

Example:

```text
Plan:
1. Create auth middleware.
2. Install jsonwebtoken package.
3. Update login route.
4. Protect API endpoints.
5. Add unit tests.
```

The plan gives humans visibility before changes happen.

---

#### Phase 3: Code

Once approved, Claude Code:

- Edits files
- Creates new files
- Executes commands
- Runs tests
- Fixes discovered issues

This is the execution phase.

---

### Why Permission Modes Exist

Without controls, an AI agent could:

- Modify sensitive files
- Delete data
- Run dangerous commands
- Change production configurations

Permission modes define:

> "How much can Claude Code do without asking a human?"

Every mode is a balance between:

- Speed
- Convenience
- Safety
- Human oversight

---

## Permission Modes Explained Simply

### 1. Default Mode

#### What is auto-approved?

✅ File reading only

#### What requires approval?

❌ File edits

❌ Shell commands

❌ Tool actions

#### Best for

- New projects
- Unknown repositories
- Sensitive environments

#### Pros

- Safest option
- Maximum human control

#### Cons

- Slowest workflow
- Frequent prompts

Think of it as:

> "Look around, but ask before touching anything."

---

### 2. acceptEdits Mode

#### What is auto-approved?

✅ Reading files

✅ Editing files

✅ Common filesystem operations inside project

Examples:

- mkdir
- touch
- rm
- rmdir
- mv
- cp
- sed

#### What still requires approval?

❌ Shell scripts

❌ External commands

❌ Protected paths

❌ Changes outside project

#### Best for

- Trusted repositories
- Local development work

#### Pros

- Faster than default
- Less interruption

#### Cons

- Cannot freely execute scripts

Think of it as:

> "You may edit project files, but ask before running anything powerful."

---

### 3. Plan Mode

#### What is auto-approved?

✅ Reading files

✅ Research

✅ Analysis

✅ Planning

#### What is blocked?

❌ All edits

❌ All shell commands

#### Best for

- Architecture reviews
- Security reviews
- Understanding unfamiliar codebases

#### Pros

- Zero modification risk
- Great for discovery

#### Cons

- Cannot produce actual code changes

Think of it as:

> "Investigate and propose. Do not touch anything."

---

### 4. auto Mode

#### What is auto-approved?

✅ Most actions

✅ File changes

✅ Commands

✅ Tool usage

A safety classifier evaluates actions before execution.

#### Still blocked by default

❌ Production deployments

❌ Database migrations

❌ Credential theft

❌ Mass deletion

❌ Force push to main branch

#### Best for

- Productivity-focused workflows
- Routine development

#### Pros

- Very fast
- Few interruptions

#### Cons

- Still needs human oversight

Think of it as:

> "Proceed automatically unless the action appears risky."

---

### 5. dontAsk Mode

#### What is auto-approved?

✅ Read-only commands

✅ Explicitly allowed tools

#### What happens to everything else?

❌ Automatically denied

No approval prompt appears.

No approval queue exists.

#### Best for

- CI/CD
- Automation
- Locked-down environments

#### Pros

- Predictable behavior
- Strong restrictions

#### Cons

- Inflexible

Think of it as:

> "Only do exactly what has already been approved."

---

### 6. bypassPermissions Mode

#### What is auto-approved?

✅ Everything

- File edits
- Commands
- Scripts
- Tool calls

#### What is blocked?

Almost nothing.

Only catastrophic commands may trigger a last-resort warning.

Examples:

```bash
rm -rf /
rm -rf ~
```

#### Best for

- Disposable containers
- Sandboxes
- Temporary testing VMs

#### Never use on

- Developer laptops
- Production machines
- Real customer systems

#### Pros

- Fastest possible execution

#### Cons

- Highest risk

Think of it as:

> "No guardrails."

---

## Settings Hierarchy

Claude Code settings can exist at multiple levels.

### 1. User Level

Location:

```text
~/.claude/settings.json
```

Applies to:

- All projects on your machine

Use for:

- Personal preferences
- Preferred default mode

Example:

```json
{
  "permissionMode": "plan"
}
```

---

### 2. Project Level

Location:

```text
.claude/settings.json
```

Applies to:

- Everyone using the repository

Use for:

- Team standards
- Shared allow rules
- Shared deny rules

Example:

```json
{
  "deny": [
    ".env",
    "secrets/*"
  ]
}
```

---

### 3. Local Project Level

Location:

```text
.claude/settings.local.json
```

Applies to:

- Only you
- Only that project

Usually:

- Git ignored
- Not shared with team

Use for:

- Personal overrides

---

### 4. Enterprise Level

Location:

```text
managed-settings.json
```

Configured by:

- Security teams
- Administrators

Applies to:

- Entire organization

Cannot be overridden by:

- Users
- Repositories
- Local settings

Use for:

- Organization-wide restrictions

Example:

```json
{
  "deny": [
    "*.env",
    "kubectl delete"
  ]
}
```

---

## Rule Precedence

Important Certification Concept:

### Deny Always Wins

Even if a mode allows something:

```text
Allow Rule + Deny Rule
= Deny
```

Example:

Project allows:

```text
Edit all files
```

Enterprise denies:

```text
Edit .env files
```

Result:

```text
.env cannot be edited
```

The deny rule overrides the allow rule.

---

## Human Review Gate

### Key Question

Before deciding whether Claude Code can act automatically, ask:

> "What is the worst thing that could happen if this runs without human review?"

This is the core decision-making principle.

---

### Low-Risk Actions

Examples:

- Formatting
- Renaming variables
- Updating comments
- Refactoring inside project

Characteristics:

- Easy to undo
- Limited impact

Human review:

✅ Usually unnecessary before execution

Good mode:

```text
acceptEdits
```

---

### Medium-Risk Actions

Examples:

- Running scripts
- Modifying build files
- Changing deployment configuration

Characteristics:

- Can affect multiple systems

Human review:

✅ Recommended before execution

Good modes:

```text
default
plan
```

---

### High-Risk Actions

Examples:

- Production deployment
- Security configuration
- Database migration
- Secret management
- Customer data access

Characteristics:

- Hard to reverse
- Expensive if wrong

Human review:

✅ Mandatory

Agent should never be the only decision maker.

---
