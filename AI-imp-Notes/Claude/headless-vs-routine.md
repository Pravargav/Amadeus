## Headless Mode vs. Routines — Why Both Exist

Worth separating what's documented fact from reasonable inference — Anthropic hasn't published an explicit "here's why we built both" statement.

## The Documented Reason: Different Trust/Control Needs

**Headless mode isn't a new feature built for scheduling — it's the underlying primitive.** It's the mode where Claude Code runs unattended inside a guardrail — restricted tools, a non-interactive permission mode, deterministic hooks — with a pipeline parsing structured output and only then acting. It existed for CI/CD and scripting long before scheduling was a use case at all. Scheduling-via-cron is just *one thing you can bolt onto it*.

**Routines came later, specifically to remove the hosting burden** for the common case of "I just want this to run on a schedule." The guidance: compare Routines against headless-in-a-VM-with-cron, GitHub Actions, or a platform like Trigger.dev — Routines abstract away the hosting entirely. That phrase — "abstracts away the hosting" — is the actual reason: a huge fraction of people who wanted scheduled Claude Code runs didn't want to manage a VM, weren't going to build CI pipelines, and just wanted to type a sentence and have it work.

## Why Not Just Make Headless "Good Enough" and Skip Routines?

Concrete gaps headless leaves open that Routines close:

1. **Always-on requirement.** Headless via cron needs *something* staying powered on 24/7. Close your laptop and everything stops — a fundamental ceiling on automation for anyone without their own server infrastructure. Not every developer has a VM lying around; Routines removes that prerequisite entirely.

2. **Safety rails for people who aren't ops engineers.** Headless gives you raw power — `--dangerously-skip-permissions`, arbitrary tool access, whatever you configure. Appropriate for a CI engineer deliberately building guardrails; dangerous for someone who just wants "scan my repo nightly" without thinking through blast radius. Routines bake in defaults for that: a fresh clone every run, and pushes restricted to `claude/`-prefixed branches unless explicitly loosened — training-wheels safety a casual user gets for free, without writing their own permission config.

3. **Conversational setup vs. infrastructure setup.** `/schedule` lets you describe intent in plain English from inside a session you're already in. Headless requires you to already know cron syntax, flag names, and where you're going to host it. Different skill floors — Routines is aimed at making scheduling accessible to people who'd never touch a crontab.

## Why Not Just Make Routines the Only Option?

Because power users and pipelines need things Routines explicitly can't do yet:

- Routines only run **hourly at most** — anything more frequent isn't a fit.
- Routines run in Anthropic's **sandboxed cloud environment** — no access to your specific VM, private network, custom CI secrets, or exact local dependency setup.
- Routines are a **research preview** — behavior and limits are still moving, so anything mission-critical or requiring guaranteed behavior needs the maturity and configurability of headless/CI instead.

## The Likely Underlying Logic

This mirrors a pattern seen across a lot of dev tooling: **a low-level primitive (headless) for people who want full control and already have infrastructure, plus a high-level managed wrapper (Routines) for people who just want the outcome without the ops work.**

It's the same relationship as raw AWS EC2 vs. a managed service like Vercel — same underlying compute, different amount of infrastructure you're forced to own.

## Caveat

This reasoning is inference stitched from how the two features behave and are positioned — not a quote from an Anthropic strategy document. For the official framing, check the Claude Code changelog or Anthropic's blog post announcing Routines, since product-launch posts sometimes spell out the intended audience split directly.
