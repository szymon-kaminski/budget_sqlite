import os
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv

load_dotenv()  # czyta .env jeśli jest

CFG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "budget"),
}

def _connect_without_db():
    """
    do tworzenia DB jeśli jeszcze nie istnieje
    """
    cfg = CFG.copy()
    cfg.pop("database", None)
    return mysql.connector.connect(**cfg)

def get_conn():
    """
    Zwraca połączenie do DB (z ustawioną bazą). Autocommit włączony.
    """
    conn = mysql.connector.connect(**CFG)
    conn.autocommit = True
    return conn

def init_mysql():
    """
    Tworzy bazę (jeśli brak) i tabelę expenses (jeśli brak).
    Używamy InnoDB i utf8mb4.
    """
    # 1) upewnij się, że DB istnieje
    try:
        # spróbuj połączyć się z DB
        conn = get_conn()
        conn.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            # brak DB → utwórz
            with _connect_without_db() as c:
                cur = c.cursor()
                cur.execute(f"CREATE DATABASE `{CFG['database']}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;")
                cur.close()
        else:
            raise

    # 2) utwórz tabelę
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                amount DECIMAL(10,2) NOT NULL,
                description VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cur.close()
