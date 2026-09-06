"""RideShare MCP server (mock Uber-style service).

This single server exercises all three server->client capabilities:

  NOTIFICATIONS  ctx.info() / ctx.report_progress()   -> book_ride, estimate_fares
  ROOTS          ctx.session.list_roots()             -> read_trips_folder, export_receipt
  SAMPLING       ctx.session.create_message()         -> summarize_spending

...plus the ordinary client->server primitives: tools, resources and prompts.
"""

import asyncio
import json
from pathlib import Path

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import SamplingMessage, TextContent
from pydantic import Field

from core.rides import RideStore
from core.utils import file_url_to_path

# log_level="ERROR" keeps the SDK's own logs off stdout. On a stdio transport
# stdout IS the protocol channel -- a stray print() corrupts the JSON-RPC stream.
mcp = FastMCP("rideshare-mcp", log_level="ERROR")

store = RideStore()


# ---------------------------------------------------------------------------
# ROOTS: the single enforcement point for filesystem access.
# ---------------------------------------------------------------------------
async def is_path_allowed(requested_path: Path, ctx: Context) -> bool:
    """Ask the CLIENT which folders we may touch, then check containment.

    Note the direction: the server is the *requester* here. `list_roots` only
    works because the client registered a `list_roots_callback` and therefore
    advertised the `roots` capability during initialize().

    Roots are ADVISORY. The protocol sandboxes nothing -- this function is the
    sandbox. Every filesystem-touching tool must call it.
    """
    roots_result = await ctx.session.list_roots()

    # Resolve first: turns "root/../../etc" into an absolute path so the
    # containment check below cannot be fooled by traversal segments.
    requested_path = requested_path.resolve()

    # A file is allowed if its *parent directory* is inside a root.
    probe = requested_path.parent if requested_path.is_file() else requested_path

    for root in roots_result.roots:
        root_path = file_url_to_path(root.uri)
        try:
            probe.relative_to(root_path)
            return True
        except ValueError:
            continue  # not under this root, try the next one

    return False


# ---------------------------------------------------------------------------
# TOOLS
# ---------------------------------------------------------------------------
@mcp.tool()
async def list_allowed_folders(ctx: Context) -> list[str]:
    """List the folders this server is allowed to read from or write to.

    Call this first if the user asks about files -- it stops the model guessing
    paths that will be rejected.
    """
    roots_result = await ctx.session.list_roots()
    return [str(file_url_to_path(root.uri)) for root in roots_result.roots]


@mcp.tool()
async def estimate_fares(
    pickup: str = Field(description="Pickup location, e.g. 'Home'"),
    dropoff: str = Field(description="Destination, e.g. 'Airport T2'"),
    *,
    ctx: Context,
) -> list[dict]:
    """Get fare quotes for every ride tier (go, premier, xl) on a route.

    Returns quote_ids -- pass one to book_ride.
    """
    # NOTIFICATIONS: a short tool, but still worth narrating.
    await ctx.info(f"Pricing {pickup} -> {dropoff}...")
    await ctx.report_progress(30, 100)
    await asyncio.sleep(0.6)

    quotes = store.build_quotes(pickup, dropoff)

    surge = quotes[0]["surge"]
    if surge > 1.0:
        await ctx.warning(f"Surge pricing active: {surge}x")

    await ctx.report_progress(100, 100)
    return quotes


@mcp.tool()
async def book_ride(
    quote_id: str = Field(description="A quote_id returned by estimate_fares"),
    *,
    ctx: Context,
) -> dict:
    """Book a ride from a fare quote and wait for the driver to arrive.

    This takes several seconds and reports progress while it runs.
    """
    # NOTIFICATIONS showcase: a genuinely slow, multi-stage tool. Without these
    # the user would stare at a frozen prompt for ~5 seconds with no idea
    # whether anything is happening.
    stages = [
        ("Searching for nearby drivers...", 15),
        ("Driver assigned, confirming...", 45),
        ("Driver is en route to pickup...", 75),
        ("Driver has arrived.", 100),
    ]

    booking = None
    for index, (message, pct) in enumerate(stages):
        await ctx.info(message)
        await ctx.report_progress(pct, 100, message)

        if index == 1:
            # Create the booking once the "driver is assigned" stage is reached.
            booking = store.create_booking(quote_id)
            d = booking["driver"]
            await ctx.info(
                f"Matched {d['name']} ({d['rating']}*) in a {d['car']}, {d['plate']}"
            )
        elif index == 2 and booking:
            store.advance_status(booking["booking_id"], "en_route")
        elif index == 3 and booking:
            store.advance_status(booking["booking_id"], "arrived")

        await asyncio.sleep(1.2)

    return booking


@mcp.tool()
async def ride_status(
    booking_id: str = Field(description="A booking_id returned by book_ride"),
    *,
    ctx: Context,
) -> dict:
    """Check the current status of a booking."""
    return store.get_booking(booking_id)


@mcp.tool()
async def cancel_ride(
    booking_id: str = Field(description="A booking_id returned by book_ride"),
    *,
    ctx: Context,
) -> dict:
    """Cancel a booking. A small cancellation fee applies."""
    await ctx.info(f"Cancelling {booking_id}...")
    booking = store.cancel_booking(booking_id)
    await ctx.warning(
        f"Cancellation fee of INR {booking['cancellation_fee_inr']} applied"
    )
    return booking


@mcp.tool()
async def read_trips_folder(
    path: str = Field(description="Path to a folder to list"),
    *,
    ctx: Context,
) -> list[str]:
    """List the files in a folder. Only works inside the client's roots."""
    requested = Path(path).resolve()

    # ROOTS gate.
    if not await is_path_allowed(requested, ctx):
        raise ValueError(
            f"Access denied: '{path}' is outside the folders you shared. "
            "Call list_allowed_folders to see what is available."
        )

    if not requested.is_dir():
        raise ValueError(f"Not a folder: {path}")

    return sorted(entry.name for entry in requested.iterdir())


@mcp.tool()
async def export_receipt(
    booking_id: str = Field(description="A booking_id returned by book_ride"),
    out_dir: str = Field(description="Folder to write the receipt into"),
    *,
    ctx: Context,
) -> str:
    """Write a ride receipt to a text file. The folder must be inside a root."""
    target_dir = Path(out_dir).resolve()

    # ROOTS gate -- note this guards a WRITE. Getting the read path right but
    # forgetting the write path is the classic roots mistake.
    if not await is_path_allowed(target_dir, ctx):
        raise ValueError(
            f"Access denied: cannot write to '{out_dir}', it is outside your shared folders."
        )

    await ctx.info(f"Rendering receipt for {booking_id}...")
    await ctx.report_progress(50, 100)

    receipt_path = target_dir / f"receipt_{booking_id}.txt"
    receipt_path.write_text(store.render_receipt(booking_id), encoding="utf-8")

    await ctx.report_progress(100, 100)
    return f"Receipt written to {receipt_path}"


@mcp.tool()
async def summarize_spending(
    trips_file: str = Field(
        description="Path to a trips JSON file, e.g. <root>/trips.json"
    ),
    *,
    ctx: Context,
) -> str:
    """Analyse a rider's trip history and explain their spending patterns.

    Reads the file, computes the totals, then asks for a written analysis.
    """
    # -------- ROOTS: may we read this file? --------
    path = Path(trips_file).resolve()
    if not await is_path_allowed(path, ctx):
        raise ValueError(
            f"Access denied: '{trips_file}' is outside your shared folders."
        )
    if not path.is_file():
        raise ValueError(f"Not a file: {trips_file}")

    # -------- NOTIFICATIONS: narrate the three phases --------
    await ctx.info(f"Reading trip history from {path.name}...")
    await ctx.report_progress(20, 100, "reading history")

    trips = store.load_trips(path)
    stats = store.summarise_numbers(trips)

    await ctx.info(
        f"Found {stats['trip_count']} trips totalling INR {stats['total_fare_inr']}."
    )
    await ctx.report_progress(45, 100, "computing totals")

    # -------- SAMPLING: borrow the client's model --------
    # This server has no API key and imports no LLM SDK. It contributes the
    # prompt; the client contributes the inference. `create_message` is a
    # server->client REQUEST, so this coroutine suspends here while the
    # original tools/call is still open on the wire.
    prompt = f"""A rider's ride-hailing history is below.

Computed totals:
{json.dumps(stats, indent=2)}

Individual trips:
{json.dumps(trips, indent=2)}

Write a short analysis (max 150 words) covering:
1. Their commute pattern.
2. How much surge pricing is costing them.
3. One concrete, specific suggestion to spend less.
Use the actual numbers. No preamble."""

    await ctx.info("Asking your client's model to write the analysis...")
    await ctx.report_progress(60, 100, "sampling")

    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user", content=TextContent(type="text", text=prompt)
            )
        ],
        max_tokens=600,
        system_prompt=(
            "You are a blunt, numerate travel-spend analyst. "
            "Always cite figures. Never pad your answer."
        ),
        temperature=0.3,
    )

    await ctx.report_progress(100, 100, "done")

    if result.content.type != "text":
        raise ValueError("Sampling returned non-text content")

    # The model that actually ran is the CLIENT's choice, not ours -- it is
    # reported back to us in result.model.
    return f"[analysis by {result.model}]\n\n{result.content.text}"


# ---------------------------------------------------------------------------
# RESOURCES: read-only data the client can pull without the model deciding to.
# ---------------------------------------------------------------------------
@mcp.resource("rideshare://drivers", mime_type="application/json")
def drivers_resource() -> str:
    """All drivers currently on the platform."""
    return json.dumps(store.drivers, indent=2)


@mcp.resource("rideshare://bookings", mime_type="application/json")
def bookings_resource() -> str:
    """Every booking made in this session."""
    return json.dumps(list(store.bookings.values()), indent=2)


@mcp.resource("rideshare://bookings/{booking_id}", mime_type="application/json")
def booking_resource(booking_id: str) -> str:
    """A single booking by id (templated resource)."""
    return json.dumps(store.bookings.get(booking_id, {"error": "not found"}), indent=2)


# ---------------------------------------------------------------------------
# PROMPTS: reusable, user-invoked templates. Surfaced as /slash commands.
# ---------------------------------------------------------------------------
@mcp.prompt()
def plan_trip(pickup: str, dropoff: str) -> str:
    """Compare every tier on a route and recommend one."""
    return (
        f"I need to get from {pickup} to {dropoff}.\n\n"
        "Use estimate_fares to price every tier, then tell me which one to take "
        "and why, considering both cost and pickup wait time. "
        "Do not book anything yet."
    )


@mcp.prompt()
def monthly_report(trips_file: str) -> str:
    """Produce a full spending report from a trips file."""
    return (
        f"Produce my ride spending report using the history at {trips_file}.\n\n"
        "Use summarize_spending for the written analysis, and list the three "
        "most expensive individual trips separately."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
