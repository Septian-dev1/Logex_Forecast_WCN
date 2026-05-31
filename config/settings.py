"""
WCN Forecast - Konfigurasi & Parameter Default

Semua konstanta dan parameter yang dapat disesuaikan
dipusatkan di sini untuk kemudahan pengelolaan.
"""

# === PARAMETER UTAMA ===
TARGET_TAHUN = 2025          # Tahun target forecast & pivot
TEST_MONTHS = 6              # Bulan yang dialokasikan untuk backtesting
N_JOBS = -1                  # Jumlah CPU cores (-1 = semua)

# === PROPHET CONFIG ===
INTERVAL_WIDTH = 0.80        # Confidence interval (80%)
SEASONALITY_PRIOR = 1.0      # Prior scale untuk seasonality
MCMC_SAMPLES = 0             # 0 = MAP estimation (cepat)
COUNTRY_HOLIDAYS = 'NL'      # Kalender libur negara

# === THRESHOLD ===
SPARSE_THRESHOLD = 0.50      # Max % nol sebelum skip
WINSORIZE_LOWER = 0.02       # Percentile bawah untuk outlier
WINSORIZE_UPPER = 0.98       # Percentile atas untuk outlier
MIN_INSURER_VOLUME = 10      # Minimum volume untuk product-level split

# === FILE PATHS ===
DATA_INPUT_PATH = "data/raw/Data 1-2.csv"
OUTPUT_CSV_PATH = "data/output/prophet_forecast.csv"
OUTPUT_EXCEL_PATH = "data/output/prophet_pivot_table.xlsx"

# === CSV FORMAT ===
CSV_SEPARATOR = ";"
CSV_DECIMAL = ","
CSV_ENCODING = "utf-8-sig"
