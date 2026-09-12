## what's current production ready projects trend GET or POST

**POST only.** Same story as sessions — GET was removed in 2026-07-28, and it was optional even before that.

## GET was never load-bearing

GET had exactly one job: the standalone SSE stream for server-initiated messages. It was never used for calling tools or reading resources. And it was always optional — a server with nothing to push answered `405 Method Not Allowed` and was fully compliant. Plenty of servers never implemented it at all.

It's also gone in the current spec, replaced by `subscriptions/listen` — a POST whose response stream stays open and carries the notifications the client opted into. Push survived; the second HTTP verb didn't.

## GET and stateful were the same decision

This is why the question mostly answers itself: a standalone GET stream has to *belong* to something. It needs a session to correlate with, and it pins that client to one process for the life of the connection. GET was the stateful model's push channel.

So when you chose `stateless_http=True`, you already chose POST-only. They were never independent knobs.

DELETE goes the same way — it existed solely to tear down a session, so no sessions means nothing to delete.

## The misconception worth naming

If you're thinking "reads should be GET, writes should be POST" — that's REST, and **MCP is not REST**. It's JSON-RPC that happens to use HTTP as a carrier. Every message is a POST regardless of semantics:

```http
POST /mcp    {"method":"resources/read", ...}   ← a read. Still POST.
POST /mcp    {"method":"tools/list", ...}       ← a read. Still POST.
POST /mcp    {"method":"tools/call", ...}       ← maybe a write. Still POST.
```

`resources/read` is a pure read and it's a POST, because the method name lives in the JSON body, not in the HTTP verb. One endpoint, one verb, everything in the body. That's also why 2026-07-28 mirrors `Mcp-Method` and `Mcp-Name` into headers — so a gateway can route or rate-limit on "this is a `tools/call` for `find_rides`" without parsing bodies. The verb carries no routing information, so the headers had to.

## For your server

Nothing to do beyond what you'd already do. Run `transport="streamable-http"` with `stateless_http=True`, expose `/mcp` accepting POST, and let GET and DELETE return `405` — which is what the current spec says a modern-only server *should* do when an older client tries them.
