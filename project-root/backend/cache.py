import sqlite3
from pathlib import Path



def cache_db_path() -> Path:
    return "cache.sqlite"


def get_connection() -> sqlite3.Connection:
    db_path = cache_db_path()
    Path.touch(db_path, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS market_data (
            symbol TEXT NOT NULL,
            interval TEXT NOT NULL,
            ts TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            PRIMARY KEY (symbol, interval, ts)
        )
        """
    )
    conn.commit()


def load_cached_payload(symbol: str, interval: str):
    with get_connection() as conn:
        init_db(conn)
        rows = conn.execute(
            """
            SELECT ts, open, high, low, close, volume
            FROM market_data
            WHERE symbol = ? AND interval = ?
            ORDER BY ts
            """,
            (symbol, interval),
        ).fetchall()
    if not rows:
        return None
    data = {
        "dates": [row["ts"] for row in rows],
        "open": [row["open"] for row in rows],
        "high": [row["high"] for row in rows],
        "low": [row["low"] for row in rows],
        "close": [row["close"] for row in rows],
        "volume": [row["volume"] for row in rows],
    }
    return {"symbol": symbol, "interval": interval, "data": data}


def save_cached_payload(symbol: str, interval: str, data: dict) -> None:
    with get_connection() as conn:
        init_db(conn)
        conn.execute(
            "DELETE FROM market_data WHERE symbol = ? AND interval = ?",
            (symbol, interval),
        )
        rows = list(
            zip(
                data.get("dates", []),
                data.get("open", []),
                data.get("high", []),
                data.get("low", []),
                data.get("close", []),
                data.get("volume", []),
            )
        )
        unique_rows = {}
        for ts, open_value, high_value, low_value, close_value, volume_value in rows:
            unique_rows[ts] = (open_value, high_value, low_value, close_value, volume_value)
        deduped = [
            (ts, *unique_rows[ts])
            for ts in sorted(unique_rows.keys())
        ]
        conn.executemany(
            """
            INSERT INTO market_data (symbol, interval, ts, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(symbol, interval, ts, open, high, low, close, volume) for ts, open, high, low, close, volume in deduped],
        )
        conn.commit()