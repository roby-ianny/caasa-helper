import sqlite3

from scraper import __sanitize_key

DB_PATH = "caasa.db"


def get_connection() -> sqlite3.Connection:
    """
    Return a connection with row_factory set to access_data as a dictionary
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create the table if it doesn't exist
    """

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT NOT NULL UNIQUE,
                prezzo INTEGER,
                m2 INTEGER,
                indirizzo TEXT,
                link_indirizzo TEXT,
                bagni INTEGER,
                piano TEXT,
                terrazza BOOLEAN DEFAULT FALSE,
                giardino BOOLEAN DEFAULT FALSE,
                balcone BOOLEAN DEFAULT FALSE,
                arredato BOOLEAN DEFAULT FALSE,
                posto_auto BOOLEAN DEFAULT FALSE,
                cantina BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def ensure_columns(conn: sqlite3.Connection, listing: dict):
    """
    Add missing colums fo any new key found in listing
    """
    cursor = conn.execute("PRAGMA table_info(listings)")
    existing = {row["name"] for row in cursor.fetchall()}

    for key in listing:
        if key not in existing:
            conn.execute(f"ALTER TABLE listings ADD COLUMN[{key}] TEXT")


def insert_listing(listing: dict) -> bool:
    """
    Insert a listing into the database.
    Returns True if the listing was inserted, False if it already exists.
    """
    cols = ", ".join(listing.keys())
    vals = ", ".join([f":{k}" for k in listing])

    with get_connection() as conn:
        ensure_columns(conn, clean_listing)

        columns = ", ".join(f"[{k}]" for k in clean_listing)
        placeholders = ", ".join(f":{k}" for k in clean_listing)

        cursor = conn.execute(
            f"INSERT OR IGNORE INTO listings ({cols}) VALUES ({vals})",
            listing,
        )

        conn.commit()

    return cursor.rowcount > 0


def bulk_insert(listings: list[dict]) -> tuple[int, int]:
    """
    Insert a list of listings into the database.
    Returns a tuple of (inserted, skipped/duplicates)
    """
    inserted = 0
    duplicates = 0
    for listing in listings:
        if insert_listing(listing):
            inserted += 1
        else:
            duplicates += 1
    return (inserted, duplicates)
