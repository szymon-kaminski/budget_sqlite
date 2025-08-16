from typing import Iterable, List, Dict, Tuple
from decimal import Decimal
from db_mysql import get_conn, init_mysql

class MySQLStorage:
    def __init__(self) -> None:
        init_mysql()

    def add(self, amount: float, description: str) -> int:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO expenses(amount, description) VALUES (%s, %s)",
                (amount, description),
            )
            new_id = cur.lastrowid
            cur.close()
            return int(new_id)

    def add_many(self, items: Iterable[Tuple[float, str]]) -> int:
        items = list(items)
        if not items:
            return 0
        with get_conn() as conn:
            cur = conn.cursor()
            cur.executemany(
                "INSERT INTO expenses(amount, description) VALUES (%s, %s)",
                items,
            )
            count = cur.rowcount if cur.rowcount is not None else len(items)
            cur.close()
            return count

    def list_all(self) -> List[Dict]:
        with get_conn() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id, amount, description FROM expenses ORDER BY id")
            rows = cur.fetchall()
            cur.close()
            # amount to DECIMAL → zamień na float jak w SQLite
            out = []
            for r in rows:
                amt = r["amount"]
                if isinstance(amt, Decimal):
                    r["amount"] = float(amt)
                out.append(r)
            return out

    def total(self) -> float:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses")
            (val,) = cur.fetchone()
            cur.close()
            if isinstance(val, Decimal):
                return float(val)
            return float(val or 0.0)
