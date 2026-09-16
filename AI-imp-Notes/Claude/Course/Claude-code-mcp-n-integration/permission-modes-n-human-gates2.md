## The Bypass Mode That Removed the One Prompt That Mattered

### Scenario

A developer switched to `bypassPermissions` because the task looked safe:

> Rename old API endpoint references.

The agent had been working correctly for several days, so the developer removed permission prompts to speed things up.

---

### What Happened?

Claude Code:

1. Scanned files containing `/v1/legacy/`
2. Updated references
3. Ran a cleanup script
4. Deleted matching files

The problem was that the pattern matched files in:

```text
/src/
```

and also:

```text
/deploy/config/prod/
```

As a result, production configuration files were deleted accidentally.

---

### Why Did This Happen?

The developer expected work only inside:

```text
/src/
```

But the search pattern was broader than expected:

```text
/v1/legacy/
```

The cleanup script found matches in production deployment files as well.

Because `bypassPermissions` was enabled:

- No confirmation prompt appeared
- No protected-path warning appeared
- The script executed immediately

---

### The Important Certification Point

The critical safety gate was:

```text
Running the cleanup script
```

not

```text
The individual rm deletions
```

This is an important distinction.

---

### What Would Happen in Other Modes?

#### default

✅ Prompts before commands

✅ Prompts before edits

✅ Developer could stop the script

Safe outcome.

---

#### acceptEdits

✅ File edits auto-approved

✅ Common filesystem actions auto-approved

❌ Script execution still prompts

Developer could review and stop the command.

Safe outcome.

---

#### bypassPermissions

✅ Everything auto-approved

✅ No confirmation prompts

✅ No protected-path checks

Result:

```text
Script ran immediately
Files were deleted
```

---

### Key Lesson

`bypassPermissions` removes the prompt that might catch a mistake before it happens.

A small error such as:

```text
Broad file pattern
```

can become:

```text
Unintended production changes
```

because no human checkpoint exists.

---

### What to Watch Out For

Before using `bypassPermissions`:

#### Add deny rules for sensitive paths

Example:

```text
/deploy/
/prod/
/secrets/
/.env
```

#### Verify search patterns

Make sure matches only include intended files.

#### Use auto mode if possible

```text
auto
```

provides fewer prompts while still keeping safety checks.

