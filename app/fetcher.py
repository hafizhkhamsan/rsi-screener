"""
Tarik data harga harian dari Yahoo Finance dan simpan ke SQLite.

Cara jalankan (dari folder utama projek):
    python -m app.fetcher
"""
import logging
import time
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

from app import config, database

logger = logging.getLogger(__name__)

PRICE_COLUMNS = ["open", "high", "low", "close", "adj_close", "volume"]


def load_stock_list() -> pd.DataFrame:
    """Baca senarai saham dari CSV. Kod dibaca sebagai teks supaya 0 di depan kekal."""
    df = pd.read_csv(config.STOCKS_CSV, dtype={"code": str})
    df["code"] = df["code"].str.strip()
    return df


def to_yahoo_symbol(code: str) -> str:
    """Contoh: '1155' -> '1155.KL'"""
    return f"{code}{config.YAHOO_SUFFIX}"


def download_history(symbol: str, start: str | None) -> pd.DataFrame:
    """Muat turun data harian dari Yahoo. Jika start None, ambil sejarah penuh."""
    ticker = yf.Ticker(symbol)
    if start:
        return ticker.history(start=start, interval="1d", auto_adjust=False)
    return ticker.history(period=config.INITIAL_PERIOD, interval="1d", auto_adjust=False)


def normalize(raw: pd.DataFrame) -> pd.DataFrame:
    """Tukar format data Yahoo kepada format jadual database kita."""
    if raw is None or raw.empty:
        return pd.DataFrame(columns=["date"] + PRICE_COLUMNS)

    df = raw.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
    })

    # Jika Yahoo tidak beri Adj Close, guna Close sebagai ganti
    if "adj_close" not in df.columns:
        df["adj_close"] = df["close"]

    df = df.dropna(subset=["close"])
    out = df[PRICE_COLUMNS].copy()
    out["volume"] = out["volume"].fillna(0).astype(int)
    # Index Yahoo ialah tarikh+masa; kita simpan tarikh sahaja (YYYY-MM-DD)
    out.insert(0, "date", pd.to_datetime(df.index).strftime("%Y-%m-%d"))
    return out.reset_index(drop=True)


def fetch_one(code: str) -> int | None:
    """
    Tarik dan simpan data untuk satu saham.
    Pulangkan: bilangan baris disimpan, 0 jika tiada data, None jika gagal.
    """
    last_date = database.get_last_date(code)
    start = None
    if last_date:
        start = (date.fromisoformat(last_date) - timedelta(days=config.OVERLAP_DAYS)).isoformat()

    symbol = to_yahoo_symbol(code)
    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            df = normalize(download_history(symbol, start))
            if df.empty:
                logger.warning("%s: tiada data diterima", symbol)
                return 0
            return database.upsert_prices(code, df)
        except Exception as exc:  # noqa: BLE001 - kita nak tangkap semua ralat rangkaian
            logger.warning("%s: cubaan %d/%d gagal: %s", symbol, attempt, config.MAX_RETRIES, exc)
            time.sleep(config.REQUEST_DELAY_SECONDS * attempt * 2)

    logger.error("%s: gagal selepas %d cubaan", symbol, config.MAX_RETRIES)
    return None


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    database.init_db()
    stocks = load_stock_list()
    logger.info("Mula tarik data untuk %d saham", len(stocks))

    ok, empty, failed = 0, 0, 0
    for code in stocks["code"]:
        result = fetch_one(code)
        if result is None:
            failed += 1
        elif result == 0:
            empty += 1
        else:
            ok += 1
            logger.info("%s: %d baris disimpan", code, result)
        time.sleep(config.REQUEST_DELAY_SECONDS)

    logger.info("Selesai. Berjaya: %d | Tiada data: %d | Gagal: %d", ok, empty, failed)


if __name__ == "__main__":
    main()