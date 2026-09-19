## Packaging a Workflow as a Plugin (Claude Developer Certification Notes)

### The Big Picture

When you build useful workflows in Claude Code using:

- Skills
- Hooks
- Subagents
- Settings
- MCP Servers

they usually live inside the `.claude` directory of a project.

The problem: every teammate would need to manually recreate the same setup.

The solution: package everything into a **Plugin** so it can be installed in one step.

Think of it like:

- Skill = reusable procedure
- Custom Command = shortcut to run a procedure
- Plugin = installable package containing multiple Claude components

---

## Skills: Reusable Workflows Loaded On Demand

A **Skill** is a portable `SKILL.md` file stored in:

```text
.claude/skills/
```

A skill contains:

1. Frontmatter
   - Skill name
   - Description
   - Metadata

2. Instructions
   - Actual workflow steps
   - Best practices
   - Procedures

The model checks the skill description and loads it when the task matches.

Example:

```text
Review pull requests for:
- Security issues
- Performance concerns
- Missing tests
```

If the user asks:

```text
Review this PR
```

Claude can automatically load that skill.

---

### Why Skills Are Useful

Skills keep large instructions out of the active context until needed.

Instead of always loading:

```text
100 lines of deployment instructions
```

the instructions stay dormant until a deployment-related task appears.

Benefits:

- Smaller context
- Better focus
- Reusable workflows
- Easier maintenance

---

## How Skills Work in Different Runtimes

### Claude Code

How it loads:

```text
Automatically discovers skills from .claude/skills
```

Where it runs:

```text
Local machine
```

Access:

- Local files
- Local tools
- Terminal commands

Key point:

A skill can interact with your project files because it runs inside your local Claude Code environment.

---

### Messages API

How it loads:

```text
Skill is sent with the API request
```

Where it runs:

```text
Anthropic code execution container
```

Access:

- Container files only
- Container tools only

Key point:

A skill that expects:

```bash
npm test
```

on your computer may fail because it is running inside a remote container instead.

---

### Agent SDK

How it loads:

```text
Loaded through settingSources
```

Important:

```text
Always configure settingSources explicitly.
```

Common mistake:

```text
Skill exists but never loads because settingSources
was not configured.
```

Where it runs:

```text
Your application's environment
```

---

### Claude Managed Agents

How it loads:

```text
Attached to the Managed Agent definition
```

Where it runs:

```text
Anthropic-managed sandbox
```

Important points:

- No filesystem discovery
- Skills are configured server-side
- Sessions are stored by Anthropic
- Skills are attached during agent definition

---

## Three Skill Portability Rules

### 1. Write a Clear Description

The description controls skill matching.

Bad:

```text
General helper skill
```

Good:

```text
Review pull requests for code quality,
security vulnerabilities, and test coverage.
```

The clearer the description, the easier it is for Claude to load it correctly.

---

### 2. Do Not Assume Local Files Exist

Bad assumption:

```bash
./deploy.sh
```

This may work in Claude Code but fail in:

- Messages API
- Managed Agents

because those environments may not contain that file.

Always design skills to be portable unless they explicitly require local dependencies.

---

### 3. Subagents Do Not Inherit Skills

A subagent starts with a clean environment.

If:

```text
Parent Agent
    -> Uses Skill A
```

then:

```text
Subagent
```

does NOT automatically get Skill A.

You must explicitly provide required skills to every subagent.

---

## When to Use a Skill

Use a skill when:

- The workflow is reusable
- The instructions are large
- The task occurs occasionally
- You want on-demand loading

Examples:

- PR review
- Release checklist
- Security audit
- Deployment validation

---

## Custom Commands: Explicit Workflow Entry Points

A custom command provides a predictable way to launch a workflow.

Instead of waiting for Claude to detect the skill automatically, you call it directly.

Example:

```text
/run-tests
```

or

```text
/review-pr
```

Think of custom commands as shortcuts.

---

### Current Recommendation

Modern Claude Code recommends:

```text
Skills
```

for both:

- Automatic invocation
- Explicit invocation

You can directly run:

```text
/skill-name
```

to execute a skill.

---

### Disable Automatic Invocation

If you only want manual execution:

```yaml
disable-model-invocation: true
```

Now the skill runs only when explicitly called.

Example:

```text
/deployment-checklist
```

---

## Legacy Commands

Older Claude Code versions used:

```text
.claude/commands/
```

These still work but are considered legacy.

Preferred approach:

```text
Skills
```

---

## Plugin Commands Are Namespaced

Plugin commands automatically receive a namespace.

Example plugin:

```text
payments
```

Command:

```text
run-tests
```

User executes:

```text
/payments:run-tests
```

Advantages:

- No command collisions
- Multiple plugins can use similar command names

Example:

```text
/payments:run-tests

/frontend:run-tests

/backend:run-tests
```

All can coexist safely.

---

## Plugins: Packaging Everything Together

A **Plugin** is a versioned bundle containing Claude components.

A plugin can contain:

- Skills
- Hooks
- Subagents
- Settings
- MCP Servers

Goal:

```text
One installation
Many configured features
```

Instead of giving teammates a setup guide with 20 steps:

```text
1. Create skills
2. Add hooks
3. Configure MCP
4. Add settings
5. Create subagents
...
```

they simply install the plugin.

---

## Plugin Structure

Typical contents:

```text
plugin
│
├── skills/
├── hooks/
├── subagents/
├── settings/
└── manifest
```

The manifest describes:

- Plugin name
- Version
- Components included

---

## Marketplace

Plugins can be distributed through a marketplace.

Sources:

### Official Marketplace

Built into Claude Code.

Users can browse and install plugins directly.

---

### Third-Party Marketplace

Can be added manually.

Example:

```text
/plugin marketplace add owner/repo
```

After adding it, users can install plugins hosted in that repository.

---

## Enterprise Plugin Deployment

Organizations can deploy plugins centrally.

Benefits:

- Standardized tooling
- Security controls
- Consistent team environments

Administrators can:

- Approve marketplaces
- Restrict marketplace sources
- Deploy plugins organization-wide

Because managed settings have higher precedence:

```text
Managed Settings
    >
User Settings
    >
Project Settings
```

users cannot override enterprise-controlled plugin configurations.

---

## Choosing Between Skill, Custom Command, and Plugin

### Skill

What it is:

```text
Reusable workflow loaded when needed.
```

Use when:

- Procedure is reusable
- Should stay out of context until needed
- Can be triggered automatically

Examples:

- PR review
- Security audit
- Code cleanup

---

### Custom Command

What it is:

```text
Explicit shortcut to start a workflow.
```

Use when:

- Workflow has a clear name
- Users should invoke it directly
- Predictability is important

Examples:

```text
/run-tests
/release
/deploy
```

---

### Plugin

What it is:

```text
Installable package of Claude components.
```

Use when:

- Multiple people need the setup
- Versioning is important
- Installation should be simple
- Team consistency matters

Examples:

- Team development toolkit
- Security review toolkit
- Deployment automation toolkit

