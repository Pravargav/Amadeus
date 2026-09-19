# Code Modernization: Applying the Full Module to Legacy Code Changes

Code modernization is a good example of why the tools and practices in this module exist.

Modernizing a large legacy codebase is risky because:

- The code is often unfamiliar.
- Many systems may depend on it.
- A small mistake can affect multiple downstream applications.
- Changes can be difficult to reverse.

The module's tools help reduce these risks before any code is changed.

---

# Core Workflow: Explore → Plan → Code

## 1. Explore

First, understand the codebase without making changes.

Goals:

- Understand dependencies
- Identify affected files
- Discover potential risks
- Learn existing patterns

At this stage, the agent only gathers information.

```text
Explore
   ↓
Understand the codebase
```

---

## 2. Plan

Use **Plan Mode** to create a detailed change plan.

Plan Mode keeps the agent in a **read-only state**.

This allows you to:

- Review proposed changes
- Verify impacted files
- Identify unexpected modifications
- Provide feedback before any edits happen

```text
Explore
   ↓
Plan (Read-Only)
   ↓
Human Review
```

### Benefit

You gain confidence in the proposed changes before touching the code.

---

## 3. Code

Only after approval does the agent modify files.

```text
Explore
   ↓
Plan
   ↓
Approve
   ↓
Code Changes
```

This reduces the risk of unintended modifications.

---

# Additional Safety Controls

## Hooks

Hooks enforce guardrails during development.

Example:

```text
Protected Folder
      ↓
Edit Blocked by Hook
```

A hook can prevent:

- Editing sensitive files
- Modifying production configurations
- Changing critical system paths

### Benefit

Even if the agent proposes an unsafe change, the hook can stop it.

---

## CLAUDE.md

`CLAUDE.md` provides instructions and coding conventions.

Example:

```text
Legacy Pattern → Avoid
Modern Pattern → Use
```

The file helps ensure:

- Consistent refactoring
- Standardized modernization patterns
- Fewer regressions
- Better code quality

### Benefit

The agent follows the desired modern architecture instead of copying old legacy patterns.

---

# Questions to Answer Before Starting

For high-risk work, define these items before the modernization project begins.

---

## 1. What Is the Blast Radius?

Ask:

> If something breaks, what systems are affected?

Consider:

- Downstream applications
- APIs
- Databases
- Customer-facing systems
- Dependent services

```text
Code Change
      ↓
Service A
      ↓
Service B
      ↓
Service C
```

Understanding dependencies helps assess risk before making changes.

---

## 2. How Are Changes Audited?

Ask:

> Can we prove what the agent changed?

A `PostToolUse` hook can record:

- Tool usage
- Modified files
- Commands executed
- Timestamps

```text
Agent Action
      ↓
Audit Log
```

### Benefit

Reviewers and auditors can verify exactly what happened during the modernization effort.

---

## 3. Who Approves Each Phase?

Ask:

> Who is responsible for approving the next step?

Example process:

```text
Explore
   ↓
Architect Approval
   ↓
Plan
   ↓
Team Lead Approval
   ↓
Implementation
```

Plan Mode creates a clear separation between:

- Investigation
- Planning
- Execution

However, organizations must still define who grants approval.

---

# Why This Matters

These questions are not unique to code modernization.

They apply to any high-risk agentic task involving:

- Large-scale code changes
- Infrastructure updates
- Security-sensitive modifications
- Enterprise systems

Code modernization simply makes the risks more obvious because:

- The codebase is large
- The code may be poorly documented
- Dependencies are often unclear
- Mistakes can be expensive

---

# Summary

A safe code modernization process uses:

## Explore → Plan → Code

- Explore the codebase
- Create a read-only plan
- Review and approve changes
- Execute modifications

## Safety Controls

- **Plan Mode** prevents premature edits
- **Hooks** enforce restrictions and guardrails
- **CLAUDE.md** ensures consistent modernization practices
- **Audit logs** track all actions

## Key Takeaway

Before modernizing a legacy system, answer:

1. **What is the blast radius if something fails?**
2. **How will changes be audited?**
3. **Who approves each phase?**

By defining these before work begins, code modernization becomes safer, more controlled, and more suitable for enterprise environments.
