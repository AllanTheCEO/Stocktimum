import sqlite3
import time
from pathlib import Path

from config import settings


def cache_db_path() -> Path:
    return Path(settings.data_dir) / "cache.sqlite"


def is_cache_fresh(updated_at: float) -> bool:
    if settings.cache_ttl_seconds <= 0:
        return False
    age_seconds = time.time() - updated_at
    return age_seconds < settings.cache_ttl_seconds


def get_connection() -> sqlite3.Connection:
    db_path = cache_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cache_meta (
            symbol TEXT NOT NULL,
            interval TEXT NOT NULL,
            updated_at REAL NOT NULL,
            PRIMARY KEY (symbol, interval)
        )
        """
    )
    conn.commit()


def load_cached_payload(symbol: str, interval: str):
    with get_connection() as conn:
        init_db(conn)
        meta = conn.execute(
            "SELECT updated_at FROM cache_meta WHERE symbol = ? AND interval = ?",
            (symbol, interval),
        ).fetchone()
        if not meta or not is_cache_fresh(meta["updated_at"]):
            return None
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
        conn.executemany(
            """
            INSERT INTO market_data (symbol, interval, ts, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(symbol, interval, ts, open, high, low, close, volume) for ts, open, high, low, close, volume in rows],
        )
        conn.execute(
            """
            INSERT INTO cache_meta (symbol, interval, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(symbol, interval)
            DO UPDATE SET updated_at=excluded.updated_at
            """,
            (symbol, interval, time.time()),
        )
        conn.commit()


# Future cache plan: keep indicator and model feature caches under
# data_cache/{symbol}/{interval}.<ext> (for raw data) alongside
# data_cache/{symbol}/{interval}_indicators.json and
# data_cache/{symbol}/{interval}_features.json to reuse TTL/force logic.
