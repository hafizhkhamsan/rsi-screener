"""Tetapan utama projek. Semua nilai yang mungkin diubah diletak di sini."""
from pathlib import Path

# Folder utama projek (satu tahap di atas folder app/)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Lokasi fail
DB_PATH = DATA_DIR / "prices.db"      # database SQLite (tidak masuk Git)
STOCKS_CSV = DATA_DIR / "stocks.csv"  # senarai kod saham

# Tetapan tarik data
YAHOO_SUFFIX = ".KL"          # Yahoo Finance guna akhiran .KL untuk Bursa
INITIAL_PERIOD = "1y"         # tempoh sejarah untuk tarikan kali pertama
OVERLAP_DAYS = 5              # tarik semula beberapa hari terakhir untuk selamat
REQUEST_DELAY_SECONDS = 1.0   # jeda antara saham, elak kena rate limit
MAX_RETRIES = 3               # bilangan cubaan jika gagal