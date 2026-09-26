"""Pengiraan penunjuk teknikal."""
import numpy as np
import pandas as pd


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    RSI kaedah Wilder (sama dengan ta.rsi di TradingView).

    Langkah:
      1. Perubahan harian = harga hari ini - harga semalam.
      2. Asingkan kenaikan (gain) dan penurunan (loss, sebagai nombor positif).
      3. Purata pertama = purata biasa (SMA) bagi `period` perubahan pertama.
      4. Purata seterusnya (smoothing Wilder):
             purata_baru = (purata_lama * (period - 1) + nilai_hari_ini) / period
      5. RSI = 100 - 100 / (1 + purata_gain / purata_loss)

    Nilai awal yang datanya belum cukup akan jadi NaN.
    """
    close = close.astype(float).reset_index(drop=True)
    delta = close.diff()
    gain = delta.clip(lower=0).to_numpy()
    loss = (-delta.clip(upper=0)).to_numpy()

    result = np.full(len(close), np.nan)
    if len(close) <= period:
        return pd.Series(result)

    # Indeks 0 ialah NaN (tiada hari sebelumnya), jadi perubahan bermula di indeks 1
    avg_gain = gain[1 : period + 1].mean()
    avg_loss = loss[1 : period + 1].mean()
    result[period] = _rsi_value(avg_gain, avg_loss)

    for i in range(period + 1, len(close)):
        avg_gain = (avg_gain * (period - 1) + gain[i]) / period
        avg_loss = (avg_loss * (period - 1) + loss[i]) / period
        result[i] = _rsi_value(avg_gain, avg_loss)

    return pd.Series(result)


def _rsi_value(avg_gain: float, avg_loss: float) -> float:
    """Kira RSI daripada purata. Kes tepi ikut peraturan TradingView."""
    if avg_loss == 0:
        return 100.0
    if avg_gain == 0:
        return 0.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)