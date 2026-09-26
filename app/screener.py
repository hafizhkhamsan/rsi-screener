"""
Kira RSI terkini untuk semua saham dan senaraikan yang di bawah threshold.

Cara jalankan (dari folder utama projek):
    python -m app.screener
"""
import pandas as pd

from app import config, database
from app.fetcher import load_stock_list
from app.indicators import rsi


def latest_rsi_table() -> pd.DataFrame:
    """Bina jadual RSI terkini untuk setiap saham dalam stocks.csv."""
    stocks = load_stock_list()
    rows = []
    for stock in stocks.itertuples(index=False):
        prices = database.load_prices(stock.code)
        bars = len(prices)
        if bars < config.RSI_MIN_BARS:
            rows.append({"code": stock.code, "name": stock.name, "date": None,
                         "close": None, "rsi": None, "bars": bars,
                         "status": "data tak cukup"})
            continue

        values = rsi(prices[config.RSI_PRICE_COLUMN], config.RSI_PERIOD)
        last = prices.iloc[-1]
        latest = float(values.iloc[-1])
        rows.append({
            "code": stock.code,
            "name": stock.name,
            "date": last["date"],
            "close": last["close"],
            "rsi": round(latest, 2),
            "bars": bars,
            "status": "OVERSOLD" if latest < config.RSI_THRESHOLD else "",
        })

    return pd.DataFrame(rows).sort_values("rsi", na_position="last").reset_index(drop=True)


def main() -> None:
    table = latest_rsi_table()
    print(table.to_string(index=False))
    oversold = table[table["status"] == "OVERSOLD"]
    print(f"\nSaham RSI < {config.RSI_THRESHOLD}: {len(oversold)}")


if __name__ == "__main__":
    main()