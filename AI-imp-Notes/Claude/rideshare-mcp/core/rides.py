"""Mock ride-hailing backend.

This stands in for the real thing (an Uber/Ola style HTTP API). It is
deliberately plain Python with no MCP imports so you can see the boundary:
this file is DOMAIN LOGIC, mcp_server.py is PROTOCOL.
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TIER_RATES = {
    # base fare, per-km rate
    "go": (35, 12.0),
    "premier": (60, 22.0),
    "xl": (80, 28.0),
}


class RideStore:
    """In-memory ride state. Resets every time the server process restarts."""

    def __init__(self):
        self.drivers = json.loads((DATA_DIR / "drivers.json").read_text())
        self.quotes: dict[str, dict] = {}
        self.bookings: dict[str, dict] = {}
        self._counter = 0

    def _next_id(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix}-{self._counter:04d}"

    # ---------- quoting ----------

    def estimate_distance(self, pickup: str, dropoff: str) -> float:
        """Fake but *stable* distance: same route always gives the same km."""
        seed = sum(ord(c) for c in (pickup + dropoff).lower())
        random.seed(seed)
        return round(random.uniform(3.0, 35.0), 1)

    def current_surge(self, pickup: str, dropoff: str) -> float:
        seed = sum(ord(c) for c in (dropoff + pickup).lower())
        random.seed(seed)
        return random.choice([1.0, 1.0, 1.2, 1.5, 1.8])

    def build_quotes(self, pickup: str, dropoff: str) -> list[dict]:
        distance = self.estimate_distance(pickup, dropoff)
        surge = self.current_surge(pickup, dropoff)
        quotes = []

        for tier, (base, per_km) in TIER_RATES.items():
            fare = round((base + per_km * distance) * surge)
            eta = min(
                (d["eta_minutes"] for d in self.drivers if d["tier"] == tier),
                default=12,
            )
            quote = {
                "quote_id": self._next_id("Q"),
                "tier": tier,
                "pickup": pickup,
                "dropoff": dropoff,
                "distance_km": distance,
                "surge": surge,
                "fare_inr": fare,
                "pickup_eta_minutes": eta,
            }
            self.quotes[quote["quote_id"]] = quote
            quotes.append(quote)

        return sorted(quotes, key=lambda q: q["fare_inr"])

    # ---------- booking ----------

    def match_driver(self, tier: str) -> dict:
        candidates = [d for d in self.drivers if d["tier"] == tier]
        if not candidates:
            candidates = self.drivers
        return max(candidates, key=lambda d: d["rating"])

    def create_booking(self, quote_id: str) -> dict:
        quote = self.quotes.get(quote_id)
        if quote is None:
            raise ValueError(
                f"Unknown quote_id '{quote_id}'. Call estimate_fares first."
            )

        driver = self.match_driver(quote["tier"])
        booking = {
            "booking_id": self._next_id("B"),
            "status": "driver_assigned",
            "quote_id": quote_id,
            "tier": quote["tier"],
            "pickup": quote["pickup"],
            "dropoff": quote["dropoff"],
            "fare_inr": quote["fare_inr"],
            "distance_km": quote["distance_km"],
            "driver": driver,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        self.bookings[booking["booking_id"]] = booking
        return booking

    def get_booking(self, booking_id: str) -> dict:
        booking = self.bookings.get(booking_id)
        if booking is None:
            raise ValueError(f"Unknown booking_id '{booking_id}'")
        return booking

    def cancel_booking(self, booking_id: str) -> dict:
        booking = self.get_booking(booking_id)
        if booking["status"] == "completed":
            raise ValueError("Cannot cancel a completed ride")
        booking["status"] = "cancelled"
        booking["cancellation_fee_inr"] = 30
        return booking

    def advance_status(self, booking_id: str, status: str) -> dict:
        booking = self.get_booking(booking_id)
        booking["status"] = status
        return booking

    # ---------- receipts ----------

    def render_receipt(self, booking_id: str) -> str:
        b = self.get_booking(booking_id)
        d = b["driver"]
        return "\n".join(
            [
                "RIDESHARE RECEIPT (mock)",
                "=" * 32,
                f"Booking   : {b['booking_id']}",
                f"Status    : {b['status']}",
                f"Route     : {b['pickup']} -> {b['dropoff']}",
                f"Distance  : {b['distance_km']} km",
                f"Tier      : {b['tier']}",
                f"Driver    : {d['name']} ({d['rating']}) {d['car']} {d['plate']}",
                f"Booked at : {b['created_at']}",
                "-" * 32,
                f"TOTAL     : INR {b['fare_inr']}",
            ]
        )

    # ---------- history ----------

    @staticmethod
    def load_trips(path: Path) -> list[dict]:
        return json.loads(path.read_text())

    @staticmethod
    def summarise_numbers(trips: list[dict]) -> dict:
        """Deterministic maths. Deliberately kept separate from the LLM call so
        you can see what sampling adds: numbers are computed here, *judgement*
        is delegated to the model."""
        total = sum(t["fare_inr"] for t in trips)
        surged = [t for t in trips if t["surge"] > 1.0]
        return {
            "trip_count": len(trips),
            "total_fare_inr": total,
            "average_fare_inr": round(total / len(trips), 1) if trips else 0,
            "total_distance_km": round(sum(t["distance_km"] for t in trips), 1),
            "surged_trip_count": len(surged),
            "surge_premium_inr": round(
                sum(t["fare_inr"] - t["fare_inr"] / t["surge"] for t in surged)
            ),
        }
