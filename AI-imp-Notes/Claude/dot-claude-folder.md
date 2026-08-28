## Can You Build a Full-Stack Production App Inside `.claude/`?

**No** — and this is a common misunderstanding.

`.claude/` is **metadata about your project**, not a place to put your project. Your actual codebase — your Next.js app, your API routes, your database migrations, your `src/` folder — all lives at the **project root**, next to `.claude/`, not inside it.

## The `.git/` Analogy

Think of it like `.git/`: nobody builds their app inside `.git/`. Git's folder holds version-control metadata about the code sitting next to it.

`.claude/` follows the same pattern — it holds Claude Code's **operational metadata** (instructions, permissions, workflows) about a project that lives right next to it.

## Folder Structure

```
your-project/
├── .claude/          ← config: CLAUDE.md instructions live outside here actually
├── CLAUDE.md          ← project instructions, read every session
├── src/               ← your actual app code
├── package.json
└── ...
```
