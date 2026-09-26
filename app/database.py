"""Semua urusan dengan database SQLite."""
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from app.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS prices (
    code      TEXT NOT NULL,
    date      TEXT NOT NULL,
    open      REAL,
    high      REAL,
    low       REAL,
    close     REAL,
    adj_close REAL,
    volume    INTEGER,
    PRIMARY KEY (code, date)
);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Buka sambungan ke database. Folder dicipta jika belum wujud."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_db(db_path: Path = DB_PATH) -> None:
    """Cipta jadual jika belum wujud. Selamat dijalankan berulang kali."""
    with closing(get_connection(db_path)) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def get_last_date(code: str, db_path: Path = DB_PATH) -> str | None:
    """Tarikh terakhir yang ada dalam database untuk satu saham (atau None)."""
    with closing(get_connection(db_path)) as conn:
        row = conn.execute(
            "SELECT MAX(date) FROM prices WHERE code = ?", (code,)
        ).fetchone()
    return row[0]


def upsert_prices(code: str, df: pd.DataFrame, db_path: Path = DB_PATH) -> int:
    """
    Simpan data harga. Jika (code, date) sudah wujud, rekod lama diganti.
    df mesti ada lajur: date, open, high, low, close, adj_close, volume
    Pulangkan bilangan baris yang disimpan.
    """
    rows = [
        (code, r.date, r.open, r.high, r.low, r.close, r.adj_close, int(r.volume))
        for r in df.itertuples(index=False)
    ]
    with closing(get_connection(db_path)) as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO prices
                (code, date, open, high, low, close, adj_close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    return len(rows)