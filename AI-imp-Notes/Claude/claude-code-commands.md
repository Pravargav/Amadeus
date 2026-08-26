## Claude Code Session Commands & Worktrees

## `/compact`

Instead of wiping history, `/compact` **compresses conversation history into a summary**. You can pass optional focus instructions to tell Claude what's most important to preserve — e.g.:

```
/compact keep the migration plan, drop the debugging
```

**Key distinction:** `/compact` keeps Claude oriented on what happened, while `/clear` starts fresh with no memory of the session at all.

**Use when:** a long session is filling up your context window but you still need continuity.

## `/rewind`

Rolls the code and/or conversation back to an earlier checkpoint. Every user prompt creates a new checkpoint, and you can choose to restore **code only, conversation only, or both**.

**Two important caveats:**
- Bash-command changes (`rm`, `mv`, `cp`) aren't tracked and can't be undone this way.
- Manual edits made outside Claude Code aren't captured either.

This is a **session-recovery tool**, not a replacement for real version control.

> Shortcut: double-tapping `Esc` opens the same rewind menu.

## `/goal`

Keeps Claude working toward a defined outcome across many turns. Set it once (e.g. `/goal tests pass`) and Claude keeps that objective anchored even as the conversation wanders through debugging detours — so it doesn't lose the thread of what "done" looks like.

## `/loop`

Runs a scheduled, recurring check inside the session — e.g.:

```
/loop 5m check CI
```

Tells Claude to re-check something (like CI status) every 5 minutes without you having to re-prompt it manually each time.

## Worktrees (not a slash command)

This one is a **Git-level feature** Claude Code builds on top of, not a slash command.

A **git worktree** is a linked working directory attached to an existing repository — normally a repo has exactly one working directory, but worktrees let you add more, each with a different branch checked out, all sharing the same `.git` folder and object store.

**Worktrees vs. cloning:**

| Clone | Worktree |
|---|---|
| Separate histories that can diverge | Same repository — commits in one worktree show up in the shared history |
| Fully independent | Working files stay separate, history is shared |

### Claude Code + Worktrees

Using the `-w` flag (or `--worktree`), Claude Code creates isolated worktrees so you can run **multiple parallel Claude sessions** without them stepping on each other — each task gets its own branch, its own file state, and its own Claude context.

**Classic use case:** You're mid-feature when a production bug appears. Instead of stashing your work, you create a hotfix worktree from `main`, run a separate Claude session there, fix the bug, and merge — while your feature branch and its Claude session stay completely untouched.

---

## Exam-Relevant Distinction

| | `/compact`, `/rewind`, `/goal`, `/loop` | Worktrees |
|---|---|---|
| **Type** | In-session slash commands (typed with `/`) | Repo/filesystem-level Git mechanism |
| **Invoked via** | Chat input | CLI flag when launching Claude Code |
| **Layer** | Conversation-level | Process/filesystem-level |**
