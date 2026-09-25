## Images, PDFs, and Batch Processing for Claude Developer Certification

### Why This Topic Matters

When working with Claude, there are two important scaling challenges:

1. Multimodal inputs (images and PDFs) consume context tokens before Claude reads your prompt.
2. Large-scale workloads (thousands of requests) require batch processing instead of normal synchronous API calls.

A Claude-certified developer should understand both context consumption and high-volume processing patterns.

---

## What is Multimodal?

A multimodal AI model can understand and work with multiple types (modes) of input, not just text.

Instead of only reading text, a multimodal model can process:

- Text
- Images
- PDFs
- Charts
- Screenshots
- Diagrams
- Documents

and sometimes can generate outputs using one or more of these formats.

## Image Token Cost Explained Simply

Claude does not view an image as a human does.

Instead, it divides the image into small 28 × 28 pixel patches.

Each patch = 1 visual token.

Formula:

```text
Visual Tokens =
⌈Width / 28⌉ × ⌈Height / 28⌉
```

Example:

```text
Image Size = 1000 × 1000 pixels

⌈1000 / 28⌉ = 36
⌈1000 / 28⌉ = 36

36 × 36 = 1296 visual tokens
```

Result:

```text
1000 × 1000 image ≈ 1296 visual tokens
```

If you send:

```text
10 screenshots
```

Then:

```text
1296 × 10 = 12,960 visual tokens
```

This can consume a significant portion of the model's context window before the prompt is even processed.

---

## Important Design Lesson

Always calculate image token cost before building an image-processing pipeline.

Bad approach:

```text
Build pipeline first
Discover token limit issues later
Rewrite entire system
```

Good approach:

```text
Measure typical production image size
Calculate visual token usage
Resize images if necessary
Build pipeline
```

A simple image resize step can save thousands of tokens.

---

## Image Size Limits

Every Claude model has:

- Maximum image resolution
- Maximum visual token limit

If an image exceeds either limit:

```text
Claude automatically downsizes it
```

Token calculations are performed on the resized image.

Certification Tip:

```text
Always verify current image limits from Claude Vision documentation because limits may change across model versions.
```

---

## Three Ways to Send Images

### Option 1: Base64 Inline

How it works:

```text
Convert image to Base64
Embed image directly in the request
```

Advantages:

```text
Simple
No upload step
Good for one-time images
```

Disadvantages:

```text
Large request payload
Higher latency
Must resend image every time
```

Best for:

```text
Single-use images
Quick prototypes
```

---

### Option 2: Public URL

How it works:

```text
Provide image URL
Claude fetches image from the internet
```

Advantages:

```text
Small request payload
No Base64 encoding
```

Disadvantages:

```text
URL must be public
URL must remain accessible
Failures occur if URL expires
```

Best for:

```text
Images already hosted publicly
Stable URLs
```

Avoid for:

```text
Authenticated images
Temporary signed URLs
Private content
```

---

### Option 3: Files API

How it works:

```text
Upload image once
Receive file_id
Reuse file_id in future requests
```

Advantages:

```text
One-time upload
Small future requests
Reusable assets
Better conversation scalability
```

Disadvantages:

```text
Requires separate upload process
Currently platform-dependent availability
```

Best for:

```text
Large images
Frequently reused assets
Multi-turn conversations
Image classification pipelines
```

Certification Tip:

```text
Files API is usually the best choice when the same asset will be referenced multiple times.
```

---

## Sending PDFs

PDFs use:

```json
{
  "type": "document",
  "source": {
    "type": "base64",
    "media_type": "application/pdf",
    "data": "<base64-pdf>"
  },
  "title": "contract_review.pdf"
}
```

Key points:

- Use `document` block type.
- Title is optional.
- Context metadata is optional.
- Source can be:
  - Base64
  - URL
  - Files API file_id

The same optimization principles used for images apply to PDFs.

---

## Prompting for Images and PDFs

Poor prompt:

```text
Describe this image
```

Problem:

```text
Too vague
Output may be inconsistent
```

Better prompt:

```text
Identify all visible objects.
If objects overlap, describe each separately.
Explain spatial relationships.
Mention partially hidden objects.
Produce output in JSON format.
```

Why?

Images contain ambiguity:

- Overlapping objects
- Occlusion
- Distance
- Depth
- Multiple interpretations

Clear instructions reduce ambiguity and improve accuracy.

---

## Message Batches API

### What Problem Does It Solve?

Suppose you need to process:

```text
5,000 images
10,000 PDFs
20,000 customer records
```

Making one synchronous request per item is inefficient.

The Message Batches API is designed specifically for this scenario.

---

## Core Workflow

Step 1:

```text
Submit batch
```

Step 2:

```text
Receive batch_id
```

Step 3:

```text
Poll batch status periodically
```

Step 4:

```text
Download completed results
```

---

## Batch Limits

A single batch supports:

```text
Up to 100,000 requests
OR
256 MB total size
```

(whichever limit is reached first)

---

## Synchronous API vs Batch API

### Synchronous API

Behavior:

```text
Send request
Wait for response
Continue
```

Best for:

```text
Chatbots
Interactive tools
Customer-facing applications
Real-time image analysis
```

Reason:

```text
User is waiting
```

---

### Batch API

Behavior:

```text
Send large batch
Process asynchronously
Collect results later
```

Best for:

```text
Nightly jobs
Large-scale document processing
Prompt evaluations
Offline analytics
Image classification pipelines
```

Reason:

```text
No human waiting for immediate output
```

---

## Main Advantage of Batch API

Benefits:

```text
Lower cost per token
No need for thousands of open connections
Handles large-scale workloads efficiently
```

Tradeoff:

```text
Latency is unpredictable
Can take minutes or even hours
```

Therefore:

```text
Batch API = Offline tasks
Synchronous API = Real-time tasks
```

---

## When Multimodal + Batch Works Well

Excellent use case:

```text
Nightly image classification system
```

Workflow:

```text
Upload images via Files API
Reuse file_ids
Submit Batch job
Receive structured JSON results
```

Benefits:

```text
Minimal payload overhead
Lower cost
Scalable processing
```

---

## Two Common Mistakes

### Mistake 1: Using Batch for User-Facing Features

Bad example:

```text
User uploads photo
Application submits Batch request
User waits hours
```

Problem:

```text
Terrible user experience
```

Solution:

```text
Use Synchronous API
```

---

### Mistake 2: Ignoring Context Costs

Bad example:

```text
Send multiple large images
Add large PDF
Add long prompt
```

Result:

```text
Context window exhausted
High costs
Possible failures
```

Solution:

```text
Measure production inputs before deployment
Resize assets when possible
Calculate token costs
```

---

## Certification Scenario: The Batch Job That Was Not Actually a Batch

Developer says:

```text
I split my 5,000-item job into chunks.
Why do I still hit rate limits?
```

Actual implementation:

```text
for item in items:
    call_synchronous_api(item)
```

Problem:

```text
Still making thousands of API calls
Chunking changed nothing
```

Important Certification Concept:

```text
Chunking ≠ Batching
```

Chunking only changes:

```text
How your code organizes data
```

It does NOT change:

```text
How the API sees requests
```

---

## Real Batch Processing

Correct approach:

```text
Create batch
Submit once
Receive batch_id
Poll status
Download results
```

Now the API sees:

```text
One batch submission
```

instead of:

```text
Thousands of synchronous requests
```

---

## Result Ordering

Batch results may return:

```text
Out of order
```

Example:

```text
Input:
A
B
C

Output:
C
A
B
```

Therefore use:

```text
custom_id
```

Example:

```json
{
  "custom_id": "customer_123"
}
```

This allows you to match results back to the original input.




