## Plugin Pitfalls, Cost, Complexity, and Risk (Certification Notes)

### Core Idea

A plugin makes setup easier because the workflow is packaged once and installed by everyone.

Without a plugin:

```text
Developer A manually configures everything
Developer B manually configures everything
Developer C manually configures everything
```

With a plugin:

```text
Create once
Install everywhere
```

The challenge is making sure the plugin works on every machine, not just the author's machine.

---

## Cost Consideration

### Skills Have Context Cost

A skill is loaded only when needed.

When activated:

```text
Instructions are added to context
```

This creates additional token/context usage.

However:

```text
No installation required
```

---

### Plugins Have Setup Cost

A plugin introduces:

- Packaging effort
- Version management
- Testing effort
- Ongoing maintenance

You pay this cost once during creation.

---

### Certification Tip

Ask:

```text
Do I want to pay setup cost once
or many times?
```

Manual setup:

```text
Every developer repeats the work
```

Plugin:

```text
Author packages once
Everyone installs
```

For teams, plugins are usually the better long-term choice.

---

## Complexity Consideration

### The Most Common Plugin Mistake

A plugin works perfectly on the author's computer.

After installation:

```text
Everyone else's plugin fails
```

Reason:

```text
Machine-specific assumptions
```

were built into the plugin.

---

### Example of a Bad Absolute Path

Bad:

```bash
/Users/alexmorgan/projects/deploy-utils/validate.sh
```

This path exists only on:

```text
Alex Morgan's computer
```

After installation on a teammate's machine:

```text
Path not found
```

The plugin installs successfully but execution fails.

---

### Why Installation Succeeds

Installation only does:

```text
Copy files
```

It does not verify that every referenced path exists.

So:

```text
Plugin Installed ✅

Plugin Executes ❌
```

---

### Certification Principle

Always remember:

```text
Installation success
≠
Execution success
```

---

## The Deployment Plugin Failure Example

### Scenario

A developer created:

```text
Deployment Workflow Skill
```

The skill was packaged into a plugin.

Testing:

```text
Author's machine ✅
```

Marketplace release:

```text
Plugin installed everywhere ✅
```

Execution:

```text
Team machines ❌
```

---

### Root Cause #1

Inside SKILL.md:

```bash
/Users/alexmorgan/projects/deploy-utils/validate.sh
```

Only the author's machine had that file.

Result:

```text
Every teammate's execution failed.
```

---

### Root Cause #2

Another skill expected:

```bash
DEPLOY_TOKEN
```

The author already had it configured in:

```text
Shell profile
```

Example:

```bash
export DEPLOY_TOKEN=xxxx
```

Other developers did not.

Result:

```text
Missing environment variable
```

The plugin failed again.

---

## Why Environment Variables Are Tricky

Paths are easy to spot.

Example:

```bash
/Users/alexmorgan/
```

A reviewer immediately notices the issue.

Environment variables are harder.

Example:

```bash
$DEPLOY_TOKEN
```

The skill appears valid.

The failure only happens when:

```text
The command actually runs
```

This makes troubleshooting harder.

---

## Risk Consideration

### Guardrails Are Not Automatically Included

Many developers assume:

```text
My skill is safe because I use hooks and deny rules.
```

Not necessarily.

A plugin only contains what is explicitly bundled.

---

### Example

Author's local setup:

```text
Skill
+
Hook
+
Deny Rule
```

Plugin bundle:

```text
Skill only
```

Result:

```text
Teammates get the skill
Teammates do not get the protection
```

The intended guardrail disappears.

---

### Certification Rule

If a component is important:

```text
Explicitly include it in the plugin.
```

Do not assume:

```text
Local configuration travels automatically.
```

---

## Best Practice: Use Portable Paths

### Never Use

```bash
/Users/name/project
```

or

```bash
C:\Users\name\project
```

These are machine-specific.

---

### Use Project-Relative Paths

Claude provides:

```bash
$CLAUDE_PROJECT_DIR
```

Example:

```bash
$CLAUDE_PROJECT_DIR/scripts/deploy.sh
```

Benefits:

- Works for every developer
- Independent of install location
- Independent of operating system path layout

---

### Use Plugin-Relative Paths

For files bundled inside a plugin:

```bash
${CLAUDE_PLUGIN_ROOT}
```

Example:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh
```

Benefits:

- Plugin remains portable
- No dependency on author's filesystem

---

## Bundle Required Assets

A plugin should include all required resources.

Examples:

```text
Scripts
Configuration Files
Templates
Utilities
Helper Files
```

Bad:

```text
Skill references a script
Script is not included
```

Good:

```text
Skill references a script
Script is bundled with plugin
```

---

## Document Environment Variables

If a plugin requires:

```bash
DEPLOY_TOKEN
API_KEY
DATABASE_URL
```

Document them clearly.

Example:

```text
Required Variables:

DEPLOY_TOKEN
DATABASE_URL
API_KEY
```

A user should know every dependency before running the skill.

---

## Validate Environment Variables Early

Bad:

```text
Plugin installs
Skill runs
Fails midway
```

Good:

```text
Plugin installs
Validation runs
Missing variable detected immediately
```

Early failure saves debugging time.

---

## Test on a Clean Machine

The author's machine often hides problems because:

- Extra tools already installed
- Environment variables already configured
- Local scripts already available
- Personal settings already present

Therefore:

```text
Test on a fresh machine
```

or

```text
Test in a clean environment
```

before publishing.

This exposes hidden dependencies.

