## Claude Developer Certification Notes
### The Model Family, Reasoning Modes, and How They Work Together

---

### The Claude Model Family

Claude is not a single model.

It is a family of models designed for different tradeoffs between:

- Cost
- Speed (latency)
- Capability

Current tiers:

- Fable
- Opus
- Sonnet
- Haiku

---

### Understanding Each Model

#### Fable

Most capable model.

Best for:

- Advanced reasoning
- Complex coding
- Agentic workflows
- Difficult problem solving

Characteristics:

- Highest intelligence
- Highest cost
- Higher latency

Use when:

```text
Maximum quality matters more than cost or speed.
```

---

#### Opus

Very powerful model.

Best for:

- Complex analysis
- Strong reasoning
- Difficult coding tasks

Characteristics:

- More capable than Sonnet
- Less expensive than Fable
- Slower than Sonnet

Use when:

```text
Sonnet is not meeting your quality requirements.
```

---

#### Sonnet

Balanced model.

Best for:

- Most production applications
- Chatbots
- Coding assistants
- Content generation
- General business workflows

Characteristics:

- Strong quality
- Good speed
- Reasonable cost

Use when:

```text
You need a balance of quality, speed, and cost.
```

---

#### Haiku

Fastest and cheapest model.

Best for:

- Simple tasks
- Classification
- Quick responses
- Lightweight automation

Characteristics:

- Lowest cost
- Lowest latency
- Lowest capability

Use when:

```text
Speed and cost matter more than maximum quality.
```

---

### Recommended Model Selection Strategy

Start with:

```text
Sonnet
```

Then evaluate results.

If quality is insufficient:

```text
Sonnet → Opus → Fable
```

If quality remains acceptable and cost matters:

```text
Sonnet → Haiku
```

---

### Certification Tip

Remember:

> Start with Sonnet and move up or down only after evaluating performance.

---

### Reasoning Modes

#### What Is Reasoning?

Reasoning means the model spends extra effort thinking through a problem before producing an answer.

Instead of immediately responding, the model performs additional internal reasoning.

---

#### Model Choice vs Reasoning Mode

These are two separate decisions.

##### Decision 1: Which Model?

Choose:

```text
Haiku
Sonnet
Opus
Fable
```

##### Decision 2: How Much Reasoning?

Choose:

```text
Reasoning Off
or
Reasoning On (Adaptive Thinking)
```

---

### Adaptive Thinking

Modern Claude models use:

```text
Adaptive Thinking
```

The model decides:

- Whether thinking is needed
- How much thinking is needed

You control the depth using:

```text
Effort Setting
```

instead of manually assigning reasoning tokens.

---

### Effort Levels

Higher effort means:

- More reasoning
- More thinking time
- Higher token usage
- Better performance on complex tasks

Lower effort means:

- Faster responses
- Lower cost
- Less reasoning

---

### When Reasoning Helps

Reasoning is useful for:

- Multi-step problems
- Math
- Complex coding
- Planning
- Deep analysis
- Agent workflows

Example:

```text
Design a scalable microservices architecture.
```

Reasoning helps significantly.

---

### When Reasoning Is Unnecessary

Reasoning is usually wasted on:

- Simple lookups
- Basic classification
- Short factual questions
- Straightforward extraction

Example:

```text
What is the capital of Japan?
```

Reasoning adds little value.

---

### Thinking Content

On newer Claude models:

- Thinking is not shown by default
- Internal reasoning remains hidden

If needed:

```text
Request summarized thinking.
```

---

### Certification Tip

Remember:

> Use reasoning for difficult, multi-step tasks, not simple retrieval tasks.

---

### How Model Choice and Reasoning Work Together

Model selection and reasoning settings are independent.

You configure both separately.

---

#### Example 1

```text
Sonnet
+
Reasoning Off
```

Result:

- Fast
- Direct
- Lower cost

Good for:

- General chat
- Most production tasks

---

#### Example 2

```text
Sonnet
+
Reasoning On
```

Result:

- Better analysis
- More thoughtful responses
- Slightly higher cost

Good for:

- Problem solving
- Planning
- Technical work

---

#### Example 3

```text
Haiku
+
Reasoning On
```

Result:

- Small model
- Extra thinking

Can sometimes outperform:

```text
Haiku + Reasoning Off
```

on harder tasks.

---

#### Example 4

```text
Fable
+
High Effort Reasoning
```

Result:

- Maximum intelligence
- Highest quality
- Highest cost

Ideal for:

- Advanced coding
- Research
- Agentic systems
- Complex reasoning

---

### Practical Mental Model

Think of these as two separate knobs:

#### Knob 1: Model Size

```text
Haiku → Sonnet → Opus → Fable
```

Increasing:

- Capability
- Cost

---

#### Knob 2: Reasoning Effort

```text
Low → Medium → High
```

Increasing:

- Thinking depth
- Token usage
- Response quality on hard tasks

---

### Key Takeaway

Model choice answers:

```text
Which Claude should I use?
```

Reasoning mode answers:

```text
How much should it think before answering?
```

---

### Quick Exam Revision

#### Claude Models

```text
Haiku  = Fastest & Cheapest
Sonnet = Balanced Default
Opus   = Higher Capability
Fable  = Most Capable
```

---

#### Reasoning Modes

```text
Separate from model choice
Uses adaptive thinking
Controlled by effort settings
Best for complex problems
```

---

#### When To Use Reasoning

Use:

- Coding
- Planning
- Analysis
- Math
- Multi-step tasks

Avoid for:

- Lookups
- Simple classification
- Basic retrieval

---

#### Model + Reasoning Examples

```text
Sonnet + Off
= Fast production default

Sonnet + On
= Better reasoning

Haiku + On
= Cheap but thoughtful

Fable + High Effort
= Maximum intelligence
```

---
