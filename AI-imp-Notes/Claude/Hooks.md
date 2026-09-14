## Claude Code Hooks

## What Hooks Are

Claude Code hooks are **user-defined shell commands** that execute at various points in Claude Code's lifecycle. They provide **deterministic control** over Claude Code's behavior, ensuring certain actions always happen rather than relying on the LLM to choose to run them.

### The Problem They Solve

`CLAUDE.md` files and prompt-based rules help guide Claude's behavior, but they're ultimately **suggestions** the model can choose to ignore — Claude might cheerfully reformat a file you didn't want touched, or decide it's "done" when it isn't.

A hook removes that ambiguity. Anthropic's documentation is explicit that hooks introduce **deterministic control at specific points in the lifecycle**, rather than relying on the model to remember or prioritize the right behavior.

## Common Hook Events

| Event | Fires |
|---|---|
| **PreToolUse** | Before tool calls — can block them |
| **PostToolUse** | After tool calls complete |
| **UserPromptSubmit** | When you submit a prompt, before Claude processes it |
| **Notification** | — |
| **Stop** | — |
| **SubagentStop** | — |
| **SessionStart** | — |
| **SessionEnd** | — |
| **PreCompact** | — |
| Newer events | `TeammateIdle`, `TaskCompleted`, `PostToolBatch` |

## Common Use Cases

- Custom notifications
- Automatic formatting (e.g. running `prettier` on `.ts` files, `gofmt` on `.go` files after edits)
- Logging
- Feedback on convention violations
- Custom permissions — e.g. blocking modifications to production files

## How a Handler Responds

- **Exit code 2 is the key control:**
  - A `PreToolUse` hook that exits 2 → **stops the tool**
  - A `Stop` hook that exits 2 → **forces Claude to keep working** instead of ending its turn
- Handler types go beyond shell commands — **HTTP hooks** send the event's JSON as a POST body and expect the same JSON response format back.

## Security Note

Hooks run automatically during the agent loop using your **current environment's credentials**, so a malicious hook could exfiltrate data. **Always review a hook's implementation before registering it.**

---

## "Nested Hooks" — Is That a Real Concept?

Not as a named feature. It shows up in two different, legitimate senses:

### 1. Config Nesting (more common meaning)

The hook configuration has **three levels of nesting**:

```
Event (e.g. PreToolUse, Stop)
  └── Matcher group (e.g. "only for the Bash tool")
        └── Handler(s) — one or more commands to run when matched
```

Both `PreToolUse` and `PostToolUse` nest under the `hooks` key of:
- `.claude/settings.json` (project scope)
- `~/.claude/settings.json` (user scope)

Scopes combine across files. So "nested hooks" here just means the JSON structure: **event → matcher → handler array**, all nested inside each other.

### 2. Hooks Tied to Nested/Hierarchical Operations

Hooks that fire around **subagents**, which are themselves "nested" inside the main agent's task.

- `SubagentStop` runs when a Claude Code subagent (a `Task` tool call) finishes responding.
- Documented use case: **"hierarchical logging of nested operations"** — tracking what happened inside a subagent's sub-task relative to the parent session.
