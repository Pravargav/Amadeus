"""Plain business logic. Knows nothing about Claude, tools, or schemas.

This is the layer you'd already have in a real app. Keeping it separate makes
the point that a "tool" is just a published interface onto code you already own.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "bookstore.db"

SEED = [
    # isbn, title, author, price, stock
    ("9780553380163", "A Brief History of Time", "Stephen Hawking", 18.00, 7),
    ("9780262033848", "Introduction to Algorithms", "Cormen et al.", 94.50, 2),
    ("9781449355739", "Fluent Python", "Luciano Ramalho", 64.99, 0),
    ("9780374533557", "Thinking, Fast and Slow", "Daniel Kahneman", 17.25, 12),
    ("9780060850524", "Brave New World", "Aldous Huxley", 15.99, 4),
    ("9780451524935", "1984", "George Orwell", 13.50, 23),
]


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset: bool = False) -> None:
    """Create and seed the database. Idempotent unless reset=True."""
    if reset and DB_PATH.exists():
        DB_PATH.unlink()

    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (
                isbn   TEXT PRIMARY KEY,
                title  TEXT NOT NULL,
                author TEXT NOT NULL,
                price  REAL NOT NULL,
                stock  INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS orders (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn     TEXT NOT NULL REFERENCES books(isbn),
                quantity INTEGER NOT NULL,
                total    REAL NOT NULL
            );
            """
        )
        if not conn.execute("SELECT 1 FROM books LIMIT 1").fetchone():
            conn.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?)", SEED)


def search(query: str, limit: int = 5) -> list[dict]:
    like = f"%{query}%"
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? LIMIT ?",
            (like, like, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def get_book(isbn: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM books WHERE isbn = ?", (isbn,)).fetchone()
    return dict(row) if row else None


def record_order(isbn: str, quantity: int) -> dict:
    """Decrement stock and insert an order row. Raises on bad input."""
    with connect() as conn:
        row = conn.execute("SELECT * FROM books WHERE isbn = ?", (isbn,)).fetchone()
        if row is None:
            raise KeyError(f"no book with ISBN {isbn}")
        if row["stock"] < quantity:
            raise ValueError(f"only {row['stock']} copies in stock, asked for {quantity}")

        total = round(row["price"] * quantity, 2)
        conn.execute("UPDATE books SET stock = stock - ? WHERE isbn = ?", (quantity, isbn))
        cur = conn.execute(
            "INSERT INTO orders (isbn, quantity, total) VALUES (?, ?, ?)",
            (isbn, quantity, total),
        )
        return {
            "order_id": cur.lastrowid,
            "isbn": isbn,
            "title": row["title"],
            "quantity": quantity,
            "total": total,
        }


if __name__ == "__main__":
    init_db(reset=True)
    print(f"seeded {DB_PATH} with {len(SEED)} books")
