## Claude Code — Shift+Tab Permission Modes

`Shift+Tab` cycles through **permission modes** while at the input prompt — the shortcut for controlling how much Claude can do without asking first.

## What It Cycles Through

Pressing it repeatedly moves through: **Manual (default) → acceptEdits → auto → plan**

Depending on version, you may see three or four modes listed, but these are the core ones:

| Mode | Behavior |
|---|---|
| **Manual / default** | Claude asks before each non-trivial action. |
| **acceptEdits** | File edits go through automatically; other actions still prompt. |
| **auto** | Hands-off mode — most actions auto-approve. |
| **plan** | Claude proposes a step-by-step plan before touching any files. Press `Enter` to approve and execute, or `Esc` to reject and keep iterating on the plan. |

