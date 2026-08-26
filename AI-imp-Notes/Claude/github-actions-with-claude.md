-> https://codingnomads.com/claude-github-actions-automate-pr-review

## Claude Code + GitHub Actions

How Claude Code plugs into GitHub Actions, and how it connects to the `/code-review` command.

## Two Ways to Set It Up

### 1. Quick Setup (from inside a Claude Code session)

Run `/install-github-app`. When you install the GitHub App, you're granted several permissions, and Claude Code then asks whether to continue with GitHub Actions setup — you can choose "Skip for now" to stop with just the app installed, or continue to finish the workflow and secrets steps.

Quick setup works with both the **Claude API** and **Claude subscriptions**.

### 2. Manual Setup

Add `ANTHROPIC_API_KEY` to your repository secrets (never hardcode it in a workflow file), then copy a workflow YAML file into `.github/workflows/`.

Either path ends the same way — a workflow file lives in your repo and Claude responds to triggers.

## What Triggers It

Claude integrates with GitHub Actions through event triggers — the core ones being:

| Trigger | Fires On |
|---|---|
| `issue_comment` | A comment on an issue or PR |
| `pull_request_review_comment` | Inline PR review comments |
| `issues` | Issue opened or assigned |

The `issues` trigger enables the "walk away, come back to a draft PR" workflow: when someone opens a new issue containing `@claude`, Claude can immediately start working on it and open a PR.

## What It Actually Does Under the Hood

This is where it connects back to **headless mode**: the action runs Claude Code in non-interactive (headless) mode — it pipes the prompt along with the PR diff context to Claude, collects the output, and uses the GitHub API to post structured review comments.

Claude sees the full diff and can post inline suggestions using GitHub's native suggestion syntax, referencing specific files and line numbers.

**So:**
- **GitHub Actions** = trigger/orchestration layer
- **Headless Claude Code** = the engine doing the actual reasoning underneath it

Same headless primitive as scheduled/cron use cases — just invoked by a GitHub event instead.

## What the Automated Review Actually Checks

A typical setup gives every PR a **5-axis review** — design, readability, performance, security, and testability — automatically, before a human reviewer even opens the PR.




