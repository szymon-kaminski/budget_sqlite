from typing import Iterable, List, Dict, Tuple
from db import get_conn, init_db

class SQLiteStorage:
    def __init__(self) -> None:
        init_db()

    def add(self, amount: float, description: str) -> int:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO expenses(amount, description) VALUES (?, ?)",
                (amount, description),
            )
            return int(cur.lastrowid)

    def add_many(self, items: Iterable[Tuple[float, str]]) -> int:
        items = list(items)
        if not items:
            return 0
        with get_conn() as conn:
            conn.executemany(
                "INSERT INTO expenses(amount, description) VALUES (?, ?)",
                items,
            )
            return len(items)

    def list_all(self) -> List[Dict]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT id, amount, description FROM expenses ORDER BY id"
            ).fetchall()
            return [dict(r) for r in rows]

    def total(self) -> float:
        with get_conn() as conn:
            row = conn.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses").fetchone()
            return float(row["total"] or 0.0)
