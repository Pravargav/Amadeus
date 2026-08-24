## Plugins vs Skills in Claude Code

Plugins and skills are related but distinct — **plugins are the mechanism for sharing skills at scale.**

## What a Plugin Is

A plugin is a reusable package that extends Claude Code with extra capabilities — think of it as a **portable workflow kit**. Instead of manually setting up a custom skill here, a hook there, an MCP server somewhere else, and project rules scattered in `.claude/`, a plugin bundles all of that into one shareable package.

A plugin directory typically looks like this:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata (required) — name, description, version
├── .mcp.json             # MCP server configuration (optional)
├── commands/             # Slash commands (optional)
├── agents/                # Subagent definitions (optional)
├── skills/                # Agent Skills (optional)
├── hooks/                 # Event handlers (optional)
└── README.md
```

**Mental model:** plugins don't introduce new capabilities — they *package* existing ones. Everything a plugin can ship (a skill, a subagent, a hook, an MCP server connection) can already be configured standalone in a `.claude/` directory. The plugin is just the shareable wrapper.

## How Skills Get Shared Through Plugins

This is the key mechanic: Claude Code supports two ways to add custom skills, agents, and hooks —

1. Start with **standalone configuration** in `.claude/` for quick iteration.
2. **Convert to a plugin** when you're ready to share.

### The Flow

1. Build a skill locally in your own `.claude/skills/` folder, testing it on your own work.
2. Once it's solid, move it into a plugin's `skills/` directory alongside a `plugin.json` manifest.
3. Publish that plugin to a **marketplace** — a directory of plugins that can be installed directly via Claude Code's plugin system, e.g.:
   ```
   /plugin install {plugin-name}@marketplace-name
   ```
4. Anyone with access to that marketplace (a team's internal one, or a public one like Anthropic's official directory) can now install the plugin — and the skill comes along with it, ready to use, no manual copy-pasting of `SKILL.md` files.

## The Relationship, Summarized

| Concept | Role |
|---|---|
| **Skill** | One ingredient — instructions/knowledge for a specific task (`SKILL.md`) |
| **Plugin** | The packaged, distributable container that can carry one or more skills (plus agents, hooks, MCP configs) to other people or projects |

You don't "share a skill" directly — you **package it into a plugin and share the plugin**.

## Mapping to Certification Modules

- **"Introduction to Agent Skills"** → the skill itself: what `SKILL.md` is, how Claude discovers/loads it.
- **Distribution/packaging side** → shows up more under **Claude Code** topics (plugins, marketplaces).

## Authoritative Source

For the exact `plugin.json` schema and marketplace-hosting steps, refer to Claude Code's plugin docs at **code.claude.com** — worth a skim since field names can shift between doc revisions.
