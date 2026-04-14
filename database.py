import sqlite3
from datetime import datetime
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea las tablas si no existen."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            side TEXT,
            sl REAL,
            tp REAL,
            risk REAL,
            received_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id INTEGER,
            order_id TEXT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity REAL,
            avg_price REAL,
            status TEXT,
            executed_at TEXT NOT NULL,
            error TEXT,
            FOREIGN KEY (signal_id) REFERENCES signals(id)
        )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────
# SIGNALS
# ─────────────────────────────────────────

def save_signal(signal: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO signals (symbol, price, side, sl, tp, risk, received_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        signal.get("symbol"),
        signal.get("price"),
        signal.get("side"),
        signal.get("sl"),
        signal.get("tp"),
        signal.get("risk"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    conn.commit()
    signal_id = cursor.lastrowid
    conn.close()
    return signal_id


def get_signals(limit: int = 50) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM signals ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ─────────────────────────────────────────
# ORDERS
# ─────────────────────────────────────────

def save_order(signal_id: int, order: dict) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    avg_price = 0.0
    fills = order.get("fills", [])
    if fills:
        total_qty = sum(float(f["qty"]) for f in fills)
        total_cost = sum(float(f["price"]) * float(f["qty"]) for f in fills)
        avg_price = round(total_cost / total_qty, 5) if total_qty > 0 else 0.0

    cursor.execute("""
        INSERT INTO orders (signal_id, order_id, symbol, side, quantity, avg_price, status, executed_at, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        signal_id,
        str(order.get("order_id", "")),
        order.get("symbol", ""),
        order.get("side", ""),
        float(order.get("quantity", 0)),
        avg_price,
        order.get("status", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        order.get("error", ""),
    ))
    conn.commit()
    conn.close()


def get_orders(limit: int = 50) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_stats() -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM signals")
    total_signals = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM orders WHERE status = 'FILLED'")
    total_filled = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM orders WHERE error != ''")
    total_errors = cursor.fetchone()["total"]

    conn.close()
    return {
        "total_signals": total_signals,
        "total_filled": total_filled,
        "total_errors": total_errors,
    }
