## what's current production ready projects trend stateful or stateless

**Stateless** — and this isn't really a trend question anymore, it's settled. The 2026-07-28 spec removed protocol-level sessions outright. Stateless stopped being one of two valid architectures and became the only one the standard defines.

Worth separating two things that get conflated, though, because "stateless" sounds scarier than it is.

## Protocol-stateless ≠ your server can't have state

Stateless means **no MCP session** — no `Mcp-Session-Id`, no server-side object that has to survive between POSTs, no requirement that request 2 reach the same process as request 1.

It does not mean your server is amnesiac. A production remote MCP server still has a database, a cache, and a user identity — the identity just arrives as a **bearer token on every request** (OAuth 2.1 resource-server flow) rather than being remembered from an earlier handshake. Each POST is independently authenticated and independently routable. Per-user state lives in Postgres or Redis, keyed by the subject in the token, exactly like any REST API. That's the whole model: stateless transport, stateful backend.

For your server specifically, `find_rides` taking arguments and returning results is the *canonical* stateless shape. Nothing to give up.

## Why production got there before the spec did

Sticky sessions are an operational tax that buys nothing most servers wanted:

- Every hosting target that's actually convenient — Lambda, Cloudflare Workers, Cloud Run, anything autoscaling — either can't hold in-process state between invocations or will happily kill the instance holding it.
- Horizontal scaling needs either affinity config or a shared session store. Both are real work, and the session store reintroduces a stateful dependency to avoid statefulness.
- A dropped TCP connection shouldn't destroy a session. With per-request POSTs, a retry is just a retry.

The spec followed the deployments, not the other way around. Notice that each removed feature got a stateless replacement rather than being abandoned: sampling and elicitation became MRTR (re-POST the original request with the answers attached), server-push became `subscriptions/listen` (a request whose response stream stays open). Only `Last-Event-ID` resumability was dropped without replacement.

## Where stateful genuinely persists

Two honest cases:

1. **Interoperating with older clients.** Plenty of deployed clients speak 2025-03-26 through 2025-11-25 and expect to negotiate a session. If you must serve them, you implement that revision's behavior alongside the modern one — that's compatibility work, not an architecture choice.
2. **Long-lived interactive sessions** where a single logical unit of work spans many calls and holds expensive in-memory context. Even here the pattern is usually to externalize that context and key it by an application-level ID passed as a tool argument — which is stateless transport again, with the state made explicit.

## The gotcha in your SDK

`mcp` 1.29.1 still defaults to **stateful** — `stateless_http: bool = False`. The SDK default is not the direction the spec went, so you have to opt in:

```python
mcp = FastMCP("rideshare-mcp", stateless_http=True, json_response=True)
```

Add `json_response=True` too unless your tools stream progress mid-call; a plain JSON response is simpler for gateways and clients to handle than SSE.

One caveat on the "settled" framing: the spec revision is unambiguous, but ecosystem migration lags standards, so you'll still encounter session-based servers and clients in the wild for a good while. Build stateless; expect to *meet* stateful.
