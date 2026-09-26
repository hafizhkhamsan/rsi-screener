"""Ujian automatik untuk pengiraan RSI. Jalankan: python -m pytest"""
import math

import pandas as pd
import pytest

from app.indicators import rsi


def test_contoh_kira_tangan():
    # period=2, harga [1, 2, 1, 2] -> perubahan [+1, -1, +1]
    # Indeks 2: purata gain = (1+0)/2 = 0.5, purata loss = (0+1)/2 = 0.5 -> RSI 50
    # Indeks 3: gain = (0.5*1 + 1)/2 = 0.75, loss = (0.5*1 + 0)/2 = 0.25
    #           RS = 3 -> RSI = 100 - 100/4 = 75
    result = rsi(pd.Series([1, 2, 1, 2]), period=2)
    assert math.isnan(result[0])
    assert math.isnan(result[1])
    assert result[2] == pytest.approx(50.0)
    assert result[3] == pytest.approx(75.0)


def test_harga_naik_sahaja_rsi_100():
    result = rsi(pd.Series(range(1, 31)), period=14)
    assert result.iloc[-1] == pytest.approx(100.0)


def test_harga_turun_sahaja_rsi_0():
    result = rsi(pd.Series(range(30, 0, -1)), period=14)
    assert result.iloc[-1] == pytest.approx(0.0)


def test_nilai_sebelum_cukup_data_ialah_nan():
    result = rsi(pd.Series(range(1, 31)), period=14)
    assert result.iloc[:14].isna().all()
    assert not math.isnan(result.iloc[14])


def test_data_terlalu_pendek_semua_nan():
    result = rsi(pd.Series([1, 2, 3]), period=14)
    assert result.isna().all()


def test_rsi_sentiasa_antara_0_dan_100():
    harga = pd.Series([10, 11, 10.5, 12, 11, 13, 12.5, 12, 14, 13, 12, 15,
                       14, 13.5, 13, 16, 15, 14, 17, 16])
    result = rsi(harga, period=5).dropna()
    assert ((result >= 0) & (result <= 100)).all()