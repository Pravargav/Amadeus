"""Protocol walkthrough with NO API key and NO tokens spent.

Connects to mcp_server.py with a stub sampling callback and exercises every
capability in order, printing the notifications as they arrive. Use this to
watch the wire behaviour without the model in the loop.

    uv run smoke_test.py
"""
import asyncio, json, sys
from pathlib import Path

from mcp.types import CreateMessageResult, TextContent
from mcp_client import MCPClient

DATA = str(Path("data").resolve())


async def on_log(params):
    print(f"    LOG[{params.level}] {params.data}")


async def on_progress(progress, total, message):
    print(f"    PROGRESS {progress}/{total} {message or ''}")


async def fake_sampling(context, params):
    print(f"    SAMPLING system={params.systemPrompt[:40]!r} max_tokens={params.maxTokens} temp={params.temperature}")
    print(f"    SAMPLING messages={len(params.messages)} first_len={len(params.messages[0].content.text)}")
    return CreateMessageResult(
        role="assistant", model="stub-model", stopReason="end_turn",
        content=TextContent(type="text", text="STUB ANALYSIS: you overspend on surge."),
    )


def show(label, result):
    # NOTE: a tool returning list[dict] comes back as one TextContent block
    # PER ELEMENT, not one block containing a JSON array.
    texts = [c.text for c in result.content if c.type == "text"]
    joined = " | ".join(t.replace("\n", "") for t in texts)
    print(f"  {label} isError={result.isError} blocks={len(texts)} -> {joined[:220]}")
    return texts


async def main():
    async with MCPClient(
        command="uv", args=["run", "mcp_server.py"], roots=[DATA],
        sampling_handler=fake_sampling, on_log=on_log, on_progress=on_progress,
    ) as c:
        print("\n== tools ==")
        print(" ", [t.name for t in await c.list_tools()])
        print("== prompts ==")
        print(" ", [(p.name, [a.name for a in p.arguments or []]) for p in await c.list_prompts()])
        print("== resources ==")
        print(" ", [str(r.uri) for r in await c.list_resources()])

        print("\n== 1. ROOTS: list_allowed_folders ==")
        show("list_allowed_folders", await c.call_tool("list_allowed_folders", {}))

        print("\n== 2. NOTIFICATIONS: estimate_fares ==")
        out = show("estimate_fares", await c.call_tool("estimate_fares", {"pickup": "Home", "dropoff": "Airport T2"}))
        quote_id = json.loads(out[0])["quote_id"]

        print(f"\n== 3. NOTIFICATIONS: book_ride({quote_id}) ==")
        out = show("book_ride", await c.call_tool("book_ride", {"quote_id": quote_id}))
        booking_id = json.loads(out[0])["booking_id"]

        print("\n== 4. ROOTS ok: read_trips_folder ==")
        show("read_trips_folder", await c.call_tool("read_trips_folder", {"path": DATA}))

        print("\n== 5. ROOTS denied: read_trips_folder(C:/Windows) ==")
        show("denied", await c.call_tool("read_trips_folder", {"path": "C:/Windows"}))

        print("\n== 5b. ROOTS traversal denied ==")
        show("traversal", await c.call_tool("read_trips_folder", {"path": DATA + "/../.."}))

        print("\n== 6. ROOTS write: export_receipt ==")
        show("export_receipt", await c.call_tool("export_receipt", {"booking_id": booking_id, "out_dir": DATA}))

        print("\n== 7. SAMPLING: summarize_spending ==")
        show("summarize_spending", await c.call_tool("summarize_spending", {"trips_file": DATA + "/trips.json"}))

        print("\n== 8. RESOURCE read ==")
        drivers = await c.read_resource("rideshare://drivers")
        print(f"  drivers -> {len(drivers)} records, first={drivers[0]['name']}")
        bk = await c.read_resource(f"rideshare://bookings/{booking_id}")
        print(f"  booking -> {bk.get('status')}")

        print("\n== 9. PROMPT get ==")
        msgs = await c.get_prompt("plan_trip", {"pickup": "Home", "dropoff": "Office Park"})
        print(f"  plan_trip -> {msgs[0].content.text[:90]!r}")

        print("\n== 10. cancel_ride ==")
        show("cancel_ride", await c.call_tool("cancel_ride", {"booking_id": booking_id}))

        print("\nALL OK")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
