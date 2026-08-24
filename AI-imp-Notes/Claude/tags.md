## Claude Tag — Quick Reference

**Availability:** Slack only (live). Microsoft Teams — "coming soon" (waitlist stage, not live yet).

## What It Is

A new way for teams to work with Claude — Claude joins as a **team member** in Slack. You grant it access to specific channels and connect it to chosen tools, data, or codebases. Anyone in the channel can tag `@Claude` in and delegate tasks while continuing other work.

## What Makes It Different from a Normal Claude Chat

| Feature | Description |
|---|---|
| **Multiplayer** | One Claude per channel, shared by everyone — not a 1:1 chat. Anyone can see what it's doing and pick up where the last person left off. |
| **Accumulates context** | Builds context over time from following the channel — no need to re-explain from scratch. Can learn from other Slack channels if granted permission (never pulls from private channels it lacks access to). |
| **Proactive (ambient mode)** | If enabled, Claude proactively updates the team — flagging stalled threads, posting when a deploy finishes — without being tagged first. |

## How It Handles Tasks

- When tagged with a task, Claude **breaks it into stages** and works through them independently.
- Delivers the final result back in Slack.
- Has its own **agent identity** — acts under its own account in connected systems (not borrowing anyone's login), so admins can audit exactly what Claude did and who requested it.
