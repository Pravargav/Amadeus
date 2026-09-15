## Claude Developer Certification Notes
### SDK vs REST, Sync vs Streaming, and Async Patterns

---

### How Developers Reach Claude

There are two main ways to call Claude:

1. REST API
2. SDK

Both connect to the same Claude API.

The difference is convenience.

---

### REST API

#### What Is REST?

REST means your application communicates with Claude using HTTP requests.

Your application:

```text
Send HTTP Request
→ Claude API
→ Receive JSON Response
```

You manually handle:

- Authentication
- Headers
- Request body
- Response parsing
- Error handling

---

#### REST Flow

```text
Your App
      ↓
HTTP Request
      ↓
Claude API
      ↓
JSON Response
      ↓
Your App
```

---

#### Benefits

- Full control
- Works in any language
- No SDK dependency

---

#### Drawbacks

- More boilerplate code
- More manual setup
- More error handling

---

### SDK (Software Development Kit)

#### What Is an SDK?

An SDK is a convenience layer built on top of the REST API.

Instead of manually building HTTP requests, you use library functions.

Available for:

- Python
- TypeScript
- Other supported languages

---

#### SDK Handles

Automatically:

- Authentication
- Request creation
- Response parsing
- Retries
- Error handling

---

#### SDK Flow

```text
Your Code
      ↓
SDK
      ↓
Claude API
      ↓
SDK
      ↓
Your Code
```

---

#### Benefits

- Less code
- Faster development
- Easier debugging
- Recommended for most developers

---

#### Important Certification Point

Remember:

> SDK and REST use the same Claude API and the same models.

The SDK is simply a more convenient way to access the API.

---

### SDK vs REST Quick Comparison

#### REST

```text
More Control
More Boilerplate
More Setup
```

---

#### SDK

```text
Less Code
Easier Development
Same API
```

---

### Synchronous Responses

#### What Is Synchronous?

The simplest request pattern.

Your application:

1. Sends request
2. Waits
3. Receives complete response

Only then does execution continue.

---

#### Flow

```text
Send Request
      ↓
Wait
      ↓
Full Response Arrives
      ↓
Continue
```

---

#### Example Use Cases

- Backend jobs
- Short responses
- Internal automation
- Scripts

---

#### Benefits

- Simple implementation
- Easy to understand

---

#### Drawback

Users see nothing while waiting.

```text
Blank Screen
...
Response Appears
```

---

### Streaming Responses

#### What Is Streaming?

Instead of waiting for the entire response, Claude sends output in small pieces as it generates them.

Users see text appear immediately.

---

#### Flow

```text
Send Request
      ↓
Token Chunk
      ↓
Token Chunk
      ↓
Token Chunk
      ↓
Final Response
```

---

#### User Experience

Without Streaming:

```text
Wait 10 Seconds
↓
Entire Response Appears
```

With Streaming:

```text
Response starts immediately
and grows in real time.
```

---

#### When To Use

Use streaming when:

- Responses are long
- Users are watching the output
- Chat applications
- Coding assistants

---

#### Benefits

- Better user experience
- Faster perceived performance
- Immediate feedback

---

#### Under The Hood

Claude streams using:

```text
Server-Sent Events (SSE)
```

The application receives messages incrementally and reassembles the final response.

---

### Certification Tip

Remember:

> Streaming improves user experience by delivering output as it is generated rather than waiting for the entire response.

---

### Async API Calls

#### What Is Async?

Async means:

```text
Don't block while waiting.
```

The request still takes time to complete.

However, your application can perform other work while waiting.

---

#### Traditional Blocking Call

```text
Send Request
↓
Wait
↓
Wait
↓
Wait
↓
Response
```

Nothing else happens during the wait.

---

#### Async Call

```text
Send Request
↓
Continue Other Work
↓
Response Arrives Later
↓
Process Response
```

---

### Why Async Matters

Useful when processing:

- Many users
- Multiple requests
- Concurrent workloads

---

#### Python SDK

Uses:

```text
AsyncAnthropic
```

with:

```text
async / await
```

---

#### TypeScript SDK

Uses:

```text
Promises
```

with:

```text
await
```

No separate async client is needed.

---

### Important Certification Point

Remember:

> Async does not make Claude answer faster. It allows your application to do other work while waiting.

---

### Async Use Cases

Good for:

- Web applications
- APIs
- Concurrent workloads
- Multi-user systems

---

### Message Batches API

#### What Is Message Batches?

A completely different pattern from async.

Instead of sending one request at a time:

```text
Request 1
Request 2
Request 3
...
```

You submit a large collection of requests together.

---

#### Batch Workflow

```text
Submit Batch
        ↓
Receive Batch ID
        ↓
Wait
        ↓
Poll Status
        ↓
Retrieve Results
```

---

### Key Characteristic

Batch jobs are:

```text
Offline Workloads
```

not real-time workloads.

---

### Completion Time

Batch jobs may take:

```text
Up to 24 Hours
```

to complete.

---

### Why Use Batches?

Benefits:

- Lower cost
- Large-scale processing
- Massive job execution

Trade-off:

```text
Lower Cost
=
Higher Latency
```

---

### Good Batch Use Cases

- Dataset processing
- Large evaluations
- Reporting pipelines
- Bulk classification
- Offline analytics

---

### Bad Batch Use Cases

Avoid for:

- Chatbots
- User interactions
- Real-time systems
- Live applications

Users should not wait hours for responses.

---

### Async vs Batch

#### Async

```text
Real-Time
Response arrives immediately when ready
Application remains responsive
```

Best for:

```text
Concurrent user applications
```

---

#### Message Batches

```text
Offline Processing
Can take up to 24 hours
Lower per-token cost
```

Best for:

```text
Large bulk workloads
```

---

### Common Exam Trap

Many learners confuse:

```text
Async API Calls
```

with

```text
Message Batches API
```

They solve different problems.

---

#### Async

Question:

```text
How can I handle many requests without blocking my app?
```

Answer:

```text
Async
```

---

#### Batch

Question:

```text
How can I process thousands of requests cheaply when no user is waiting?
```

Answer:

```text
Message Batches API
```

---

### Quick Exam Revision

#### REST API

```text
Direct HTTP Calls
More Control
More Boilerplate
```

---

#### SDK

```text
Convenience Layer
Handles Authentication
Handles Parsing
Same Claude API
```

---

#### Synchronous

```text
Send Request
Wait
Get Complete Response
```

---

#### Streaming

```text
Response Arrives In Pieces
Better User Experience
```

---

#### Async

```text
Non-Blocking
Real-Time Responses
Concurrency Friendly
```

---

#### Message Batches

```text
Bulk Offline Workloads
Lower Cost
Can Take Up To 24 Hours
```

---
