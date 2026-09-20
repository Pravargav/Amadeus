## Choosing the Right Memory Scope for Claude Agents

Memory scope decides **what your agent remembers when a new session starts**.

A simple way to think about it:

- Context Window = Agent's short-term memory
- Database/Storage = Agent's long-term memory
- Summary = Agent's condensed notes
- Stateless = Agent starts fresh every time

The biggest design mistake is choosing the wrong memory scope at the beginning. This can lead to either:

1. Too much memory being passed every time → high token cost and slow responses.
2. Too little memory being stored → agent forgets everything after a session ends.

---

## Memory Options Explained

### In-Context Memory

The agent remembers information because the conversation history is included in every API call.

Example:

- User: "My project name is Apollo."
- Later in same session: "What is my project name?"
- Agent answers: "Apollo."

Why?

Because the earlier conversation is still in the context window.

#### Best For

- Short conversations
- Single-session tasks
- Prototypes and demos

#### Advantages

- Very easy to implement
- No database required
- No retrieval logic

#### Disadvantages

- Token usage grows every turn
- More expensive over time
- Eventually reaches context window limit
- Memory disappears when session ends

#### What You Lose

When the conversation ends, all memory is gone.

---

### External Storage Memory

The agent saves information into a database and retrieves it later.

Example:

Session 1:

- User: "My favorite programming language is Python."
- Agent stores this in a database.

Session 2 (next day):

- Agent reads database.
- Agent remembers user's preference.

#### Best For

- Multi-day conversations
- Customer support agents
- CRM agents
- Team collaboration agents
- Multiple agent instances sharing state

#### Advantages

- Memory survives across sessions
- Scales well
- Can be shared between users and systems

#### Disadvantages

- Requires database design
- Read/write logic needed
- Adds retrieval latency

#### What You Lose

Nothing from memory itself.

The cost is additional engineering complexity.

---

### Summarized Memory

Instead of storing the entire conversation, the agent stores a summary.

Example:

Original conversation:

- 500 messages

Stored summary:

- User works on Project Apollo
- Prefers Python
- Ticket #123 still open
- Waiting for customer response

Next session starts using the summary instead of all 500 messages.

#### Best For

- Long-running chat assistants
- Personal AI assistants
- Ongoing conversations where history becomes very large

#### Advantages

- Much cheaper than replaying full history
- Keeps context window manageable
- Prevents window overflow

#### Disadvantages

- Summary may miss details
- Quality depends on summarization prompt

#### What You Lose

Any detail that was not included in the summary.

---

### No Persistent Memory (Stateless)

The agent stores nothing.

Every session starts completely fresh.

Example:

A text translation service.

User submits text → gets translation → session ends.

No memory needed.

#### Best For

- One-time tasks
- Automation pipelines
- Request/response systems
- Independent jobs

#### Advantages

- Cheapest approach
- Simplest architecture
- No storage required

#### Disadvantages

- Cannot remember previous interactions

#### What You Lose

All previous context.

---

## Quick Comparison

| Memory Type | Persists Across Sessions? | Cost | Best For |
|------------|--------------------------|------|----------|
| In-Context | No | Token cost grows | Short conversations |
| External Storage | Yes | Retrieval + engineering cost | Long-term memory |
| Summarized Memory | Yes | Summary generation cost | Long-running chats |
| Stateless | No | Almost none | Independent tasks |

---

## How to Choose During Design

Ask these questions:

### Question 1

Will the user come back later and expect the agent to remember something?

If **Yes** → Use External Storage or Summarized Memory.

If **No** → Stateless or In-Context is enough.

---

### Question 2

Will conversations become very long?

If **Yes** → Use Summaries or External Storage.

If **No** → In-Context may be sufficient.

---

### Question 3

Do multiple agents or users need access to the same information?

If **Yes** → Use External Storage.

If **No** → Simpler options may work.

---

## Common Mistake

### The Prototype Trap

Many developers start with:

```text
messages = full conversation history
```

Everything works during development.

Why?

Because testing sessions are short.

Later in production:

```text
Session 1 = 5,000 tokens
Session 2 = 10,000 tokens
Session 3 = 20,000 tokens
Session 4 = 40,000+ tokens
```

Now every API call must process all of that history.

Problems appear:

- Higher cost
- Larger latency
- Context window exhaustion
- Incomplete responses

The agent starts failing even though tools are working correctly.

The real issue is memory architecture.

---

## The Session Four Failure Story (Certification View)

### What Happened?

Support agent stored all history inside conversation context.

Development:

- 10–15 turns
- No issues

Production:

- Multiple sessions
- More history
- More tool calls

By Session 4:

- History exceeded 40,000 tokens
- System prompt + tools consumed more tokens
- Context window nearly exhausted

Result:

- Agent returned incomplete answers
- Looked like a tool problem
- Actually a memory problem

---

### Fix

Move conversation history into external storage.

Instead of injecting everything:

```text
Load relevant records only
```

Benefits:

- Smaller prompts
- Lower cost
- Faster responses
- Better scalability

---

## Skills: A Different Concept From Memory

Memory answers:

```text
"What should the agent remember?"
```

Skills answer:

```text
"What instructions should the agent know?"
```

Do not confuse the two.

---

### What Is a Skill?

A Skill is a reusable instruction set stored in a `SKILL.md` file.

Example:

```text
Code Review Skill
Security Audit Skill
Legal Contract Review Skill
Financial Analysis Skill
```

When a user request matches the skill description:

```text
User Request
    ↓
Skill Match
    ↓
Load Skill Instructions
    ↓
Execute Task
```

---

### Why Skills Are Efficient

Without Skills:

```text
System Prompt
+ Review Instructions
+ Security Rules
+ Formatting Rules
+ Domain Knowledge
```

Loaded every session.

With Skills:

```text
System Prompt
+ Skill Names
```

Only the matching skill loads.

Result:

- Lower context usage
- Lower token cost
- Cleaner architecture

---

## Skill vs CLAUDE.md vs In-Context Instructions

| Pattern | When Loaded | Best For |
|----------|------------|----------|
| Skill (SKILL.md) | Only when needed | Task-specific expertise |
| CLAUDE.md | Every session | Project-wide rules |
| In-Context Instructions | Current session only | Temporary instructions |

---

### Use Skills When

The instructions are needed only for specific tasks.

Examples:

- Compliance review
- Security audit
- Contract analysis
- Custom output formatting

---

### Use CLAUDE.md When

Rules apply to every task.

Examples:

- Coding standards
- Team conventions
- Project-wide formatting requirements

---

### Use In-Context Instructions When

Instructions are temporary.

Example:

```text
For this conversation,
respond in bullet points only.
```

---

## Important Certification Takeaway

Remember this simple decision flow:

```text
Need memory across sessions?
        |
       Yes
        |
External Storage
or
Summarized Memory
        |
       No
        |
Short Session?
   /         \
 Yes         No
  |           |
In-Context  Stateless
```

---

-> Note: Overhead means extra work, cost, time, or resources required to perform something.
