# Understanding Polling and Offline Workloads in the Message Batches API

## What Does "Poll" Mean?

In this context, **polling** means repeatedly checking the status of a batch job after you have submitted it.

### How It Works

1. You send a batch job request.
2. The API returns a **Job ID** (or **Batch ID**).
3. Instead of waiting for the final results immediately, your application periodically sends another request to check whether the job has finished.

### Example

Submit a batch:

```http
POST /batches
```

Response:

```json
{
  "batch_id": "12345"
}
```

Check status periodically:

```http
GET /batches/12345
```

While processing:

```json
{
  "status": "running"
}
```

After completion:

```json
{
  "status": "completed",
  "output_file": "results.json"
}
```

The repeated status checks using `GET /batches/12345` are called **polling**.

---

## Why Is It Called an "Offline" Workload?

Here, **offline** does **not** mean "without internet."

Instead, it means the work is **not interactive** and does not require an immediate response.

---

## Online (Real-Time) Processing

In online processing, a user is actively waiting for the result.

```text
User → API → Response in seconds
```

### Examples

- ChatGPT conversations
- Customer support chatbots
- Website search
- Microsoft Copilot queries

Since a user is waiting, the response must be returned quickly.

---

## Offline Processing

In offline processing, no user is waiting for each individual result.

```text
Upload 1,000,000 requests
          ↓
 Batch processing system
          ↓
 Results available later
```

### Examples

- Generating embeddings for millions of documents
- Bulk translation jobs
- AI model evaluation runs
- Processing historical records
- Overnight analytics jobs

Because immediate responses are not required, the provider can process these requests more slowly and efficiently.

---

## Does Offline Processing Still Need the Internet?

**Yes.**

The internet is still required to:

- Submit the batch job
- Check (poll) the job status
- Download the final results

The term **offline** refers to the processing pattern, not network connectivity.

### Think of It This Way

| Type | User Waiting? | Internet Required? | Response Time |
|--------|--------------|-------------------|---------------|
| Online | Yes | Yes | Seconds |
| Offline | No | Yes | Minutes to Hours |

---

## Why Is Batch Processing Cheaper?

For normal API requests, providers must keep resources available to serve users immediately.

For batch jobs:

- Requests can be queued.
- Work can run during low-demand periods.
- No low-latency guarantees are needed.
- Infrastructure can be utilized more efficiently.

Because of this, providers often offer a **lower cost per token** for batch processing.

