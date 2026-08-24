## Agent vs Subagent 
(Context Windows)

## Quick Answer

**Not like git branches.** Git branches share full history and are designed to merge back together with everything intact. Subagent context windows are **isolated, not branched** — nothing merges back except a final result.

## Better Analogy: Manager Delegating to a Specialist Consultant

- **Main agent (manager)** — has its own running context: all the back-and-forth, decisions made, files read, etc.
- **Spinning up a subagent** — like calling in a consultant and handing them a task brief, not your entire meeting history. Just what's relevant to the task.
- **Subagent** — works independently in its own workspace: its own context window, own tool calls, own reasoning. Completely separate from the main agent's context.
- **Subagent finishes** — it doesn't hand back its whole notebook, just a summary/result — the output the manager needs.
- **Main agent** — never sees the subagent's intermediate steps, tool calls, or reasoning. Only the final digest.

## Concrete Walkthrough (Function-Call Analogy)

### The Setup

Main conversation (main agent context) so far:

```
- You: "Refactor the auth module and also check if there are
  any unused dependencies in package.json"
- Claude: [20 turns discussing auth refactor, read 8 files,
  made edits...]
```

Main agent decides: checking unused dependencies is a self-contained side-task → delegate it instead of doing it inline and cluttering its own context.

### The "Function Call"

```python
result = check_unused_dependencies(project_path="/repo")
```

**Input to subagent (like function arguments):**
```
Task: "Scan package.json and the codebase. Identify which
dependencies listed in package.json are never imported
anywhere in the source files. Return a list."

Files given: package.json, /src directory access
```

Note: the subagent does **not** receive the 20 turns of auth-refactor discussion. It has no idea that's even happening — it only gets this one clean task brief.

### Inside the Subagent (its own local stack)

```
1. Reads package.json → sees 34 dependencies listed
2. Runs grep/search across /src for each dependency name
3. Finds: "moment" never imported, "lodash.debounce"
   never imported, "axios" used in 12 files, etc.
4. Internal reasoning: "moment and lodash.debounce appear
   in package.json but 0 matches in source"
```

Every tool call, every intermediate grep result, every dead-end stays **inside the subagent** — like local variables inside a function that disappear once it returns.

### The Return Value (output back to main agent)

```
"Found 2 unused dependencies: 'moment' and 'lodash.debounce'.
Safe to remove from package.json."
```

One clean string comes back — not the grep logs, not the file-by-file scan trail.

### Main Agent's Context After

```
- [...all 20 turns of auth refactor still here...]
- Subagent result: "Found 2 unused dependencies: 'moment'
  and 'lodash.debounce'. Safe to remove."
- Claude: "I've refactored the auth module. Also, 'moment'
  and 'lodash.debounce' are unused — want me to remove them?"
```

The main agent's context grew by **one summary line**, not by the entire scanning investigation. Doing it inline would've burned thousands of tokens the way excessive `console.log` debugging clutters a function before you extract it — same idea, applied to context budget instead of code readability.

## Key Takeaways

| Git Branches | Subagent Context |
|---|---|
| Share full history | Isolated — no shared history |
| Designed to merge back with everything intact | Only a final summary returns, not the process |
| Same repo, same commit graph | Separate workspace, separate context window entirely |

**Exam-relevant point:** Anthropic's docs describe subagents as ideal for tasks that are **self-contained and context-heavy** — isolation is the feature, not a limitation. If a task needs constant back-and-forth with the main conversation's context, it's a poor fit for a subagent.
