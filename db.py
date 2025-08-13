from pathlib import Path
import sqlite3

DB_PATH = Path("data/budget.sqlite3")

def get_conn() -> sqlite3.Connection:
    """
    Tworzy katalog data/ jeśli nie istnieje, otwiera połączenie i ustawia row_factory
    żeby móc czytać wyniki jako słowniki (sqlite3.Row).
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """
    Tworzy tabelę expenses (jeśli nie istnieje).
    amount REAL (z CHECK > 0), description TEXT, id autoincrement.
    """
    with get_conn() as conn:
        conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK (amount > 0),
                description TEXT NOT NULL
            );
            """
        )
