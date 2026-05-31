<div align="center">

# 🏥 WCN Forecast

### AI-Powered Healthcare Volume Forecasting Engine

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Prophet](https://img.shields.io/badge/Prophet-Meta-0467DF?style=for-the-badge&logo=meta&logoColor=white)](https://facebook.github.io/prophet/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org)

<br/>

> **Prediksi volume produksi rumah sakit per spesialisasi secara akurat menggunakan Facebook Prophet, dengan backtesting otomatis, parallel processing, dan ekspor laporan siap pakai.**

<br/>

[🚀 Mulai Cepat](#-mulai-cepat) · [📖 Dokumentasi](#-arsitektur-pipeline) · [📊 Output](#-output--hasil) · [🤝 Kontribusi](#-kontribusi)

---

</div>

## 📋 Daftar Isi

- [Tentang Project](#-tentang-project)
- [Fitur Utama](#-fitur-utama)
- [Arsitektur Pipeline](#-arsitektur-pipeline)
- [Struktur Folder](#-struktur-folder)
- [Mulai Cepat](#-mulai-cepat)
- [Format Data Input](#-format-data-input)
- [Konfigurasi](#%EF%B8%8F-konfigurasi)
- [Output & Hasil](#-output--hasil)
- [Metodologi](#-metodologi)
- [FAQ](#-faq)
- [Kontribusi](#-kontribusi)

---

## 🎯 Tentang Project

**WCN Forecast** adalah engine prediksi volume produksi rumah sakit yang dirancang untuk kebutuhan perencanaan kapasitas dan negosiasi kontrak asuransi di sektor kesehatan Belanda. Sistem ini memanfaatkan **Facebook Prophet** sebagai core model untuk menghasilkan forecast bulanan per spesialisasi medis.

### Mengapa WCN Forecast?

| Masalah | Solusi WCN Forecast |
|---------|---------------------|
| Forecast manual memakan waktu berhari-hari | ⚡ Batch processing paralel — selesai dalam menit |
| Tidak ada ukuran akurasi yang objektif | 📊 Backtesting otomatis dengan WMAPE, MAE, RMSE |
| Model satu ukuran untuk semua | 🧠 Konfigurasi adaptif per spesialisasi (auto-tuning) |
| Sulit memecah forecast ke level detail | 🔀 Granularisasi otomatis ke level produk × asuransi |
| Hasil sulit dibaca oleh manajemen | 📑 Export Excel & CSV siap presentasi |

---

## ✨ Fitur Utama

<table>
<tr>
<td width="50%">

### 🧹 Data Preprocessing
- Pembersihan otomatis: duplikasi, missing values, format angka
- Winsorization untuk menangani outlier
- Deteksi sparse series (data terlalu banyak nol)

</td>
<td width="50%">

### 🤖 Adaptive Modeling
- Auto changepoint scale berdasarkan coefficient of variation
- Dynamic Fourier order untuk seasonality
- Holiday effects (Netherlands 🇳🇱)
- Quarterly seasonality detection

</td>
</tr>
<tr>
<td width="50%">

### ⚡ Parallel Processing
- Batch training dengan Joblib
- Multi-core CPU utilization
- Proses ratusan kombinasi spesialisasi × snapshot

</td>
<td width="50%">

### 📊 Comprehensive Output
- Visualisasi interaktif dengan Plotly
- Pivot table multi-snapshot
- Export CSV & Excel bergaya korporat
- Laporan akurasi backtesting

</td>
</tr>
</table>

---

## 🔧 Arsitektur Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WCN FORECAST PIPELINE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐              │
│  │ Data CSV  │───▶│ Preprocessing │───▶│ Batch Engine  │              │
│  │ (Input)   │    │  & Cleaning   │    │  (Parallel)   │              │
│  └──────────┘    └──────────────┘    └───────┬───────┘              │
│                                              │                       │
│                    ┌─────────────────────────┼─────────┐            │
│                    ▼                         ▼         ▼            │
│            ┌──────────────┐     ┌──────────┐  ┌──────────┐         │
│            │  Backtesting  │     │ Prophet  │  │  Prophet │         │
│            │  (Evaluation) │     │ Model A  │  │ Model B  │  ...   │
│            └──────┬───────┘     └────┬─────┘  └────┬─────┘         │
│                   │                  │              │                │
│                   ▼                  ▼              ▼                │
│            ┌──────────────┐   ┌──────────────────────┐              │
│            │  Accuracy     │   │  Master Forecast     │              │
│            │  Report       │   │  Aggregation         │              │
│            └──────────────┘   └──────────┬───────────┘              │
│                                          │                           │
│                    ┌─────────────────────┼──────────────┐           │
│                    ▼                     ▼              ▼           │
│            ┌──────────────┐   ┌──────────────┐  ┌───────────┐      │
│            │ Insurer Split │   │  Pivot Table  │  │  Plotly   │      │
│            │ & Granular    │   │  Engine       │  │  Charts   │      │
│            └──────┬───────┘   └──────┬───────┘  └───────────┘      │
│                   │                  │                               │
│                   ▼                  ▼                               │
│            ┌──────────────┐   ┌──────────────┐                      │
│            │  CSV Export   │   │ Excel Export  │                      │
│            │  (Granular)   │   │ (Pivot View)  │                      │
│            └──────────────┘   └──────────────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Struktur Folder

```
WCN_Forecast/
│
├── 📄 README.md                  # Dokumentasi project (file ini)
├── 📄 requirements.txt           # Daftar dependensi Python
├── 📄 .gitignore                 # File yang diabaikan Git
├── 📄 .env.example               # Template konfigurasi environment
│
├── 📁 data/                      # Data input & output
│   ├── 📁 raw/                   # ← Taruh file CSV mentah di sini
│   │   └── 📄 .gitkeep
│   ├── 📁 processed/             # Data hasil preprocessing
│   │   └── 📄 .gitkeep
│   └── 📁 output/                # Hasil forecast (CSV & Excel)
│       └── 📄 .gitkeep
│
├── 📁 notebooks/                 # Jupyter Notebooks
│   └── 📄 forecast_pipeline.ipynb # Notebook utama pipeline
│
├── 📁 src/                       # Source code modular
│   ├── 📄 __init__.py
│   ├── 📄 preprocessing.py       # Fungsi data cleaning & prep
│   ├── 📄 helpers.py             # Statistik & thresholding utils
│   ├── 📄 model.py               # Core Prophet training & evaluation
│   ├── 📄 batch.py               # Parallel processing engine
│   ├── 📄 pivot.py               # Pivot table builder
│   ├── 📄 split.py               # Insurer split & granular detail
│   └── 📄 export.py              # CSV & Excel export manager
│
├── 📁 config/                    # Konfigurasi project
│   └── 📄 settings.py            # Parameter default & konstanta
│
├── 📁 reports/                   # Laporan & visualisasi tersimpan
│   └── 📄 .gitkeep
│
└── 📁 tests/                    # Unit tests
    ├── 📄 __init__.py
    └── 📄 test_helpers.py        # Test fungsi helper
```

---

## 🚀 Mulai Cepat

### Prasyarat

- **Python 3.9** atau lebih baru
- **pip** (Python package manager)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/<username>/wcn-forecast.git
cd wcn-forecast
```

### 2️⃣ Buat Virtual Environment

```bash
# Membuat virtual environment
python -m venv venv

# Aktivasi (Windows)
venv\Scripts\activate

# Aktivasi (macOS/Linux)
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Siapkan Data

Letakkan file CSV data historis Anda di folder `data/raw/`:

```bash
cp /path/to/your/data.csv data/raw/
```

### 5️⃣ Jalankan Pipeline

**Opsi A — Jupyter Notebook (Interaktif):**
```bash
jupyter notebook notebooks/forecast_pipeline.ipynb
```

**Opsi B — Script Python (Production):**
```bash
python -m src.batch --input data/raw/data.csv --output data/output/
```

---

## 📥 Format Data Input

Data input harus berupa file **CSV** dengan separator `;` (semicolon) dan format desimal `,` (koma). Kolom yang diperlukan:

| Kolom | Tipe | Deskripsi | Contoh |
|-------|------|-----------|--------|
| `year` | int | Tahun observasi | `2024` |
| `month` | int | Bulan observasi (1-12) | `6` |
| `volume` | float | Volume produksi | `1.234,56` |
| `specialism_code` | str | Kode spesialisasi medis | `0303` |
| `monitor_month` | date | Tanggal snapshot data | `2024-07-01` |
| `is_forecast` | int | Flag: 0 = aktual, 1 = forecast | `0` |

### Kolom Opsional (untuk granularisasi):

| Kolom | Deskripsi |
|-------|-----------|
| `product_code` | Kode produk DBC/DOT |
| `diagnosis_code` | Kode diagnosis |
| `care_type_code` | Kode jenis perawatan |
| `uzovi_code` / `payer_code` | Kode asuransi (UZOVI) |
| `revenue` | Omzet/pendapatan |

### Contoh Data

```csv
year;month;volume;specialism_code;product_code;monitor_month;is_forecast
2023;1;150,5;0303;14C054;2024-01-01;0
2023;2;142,3;0303;14C054;2024-01-01;0
2023;3;168,0;0303;14C054;2024-01-01;0
```

---

## ⚙️ Konfigurasi

Sesuaikan parameter di `config/settings.py` atau langsung di notebook:

```python
# === PARAMETER UTAMA ===
TARGET_TAHUN = 2025          # Tahun target forecast & pivot
TEST_MONTHS = 6              # Bulan yang dialokasikan untuk backtesting
N_JOBS = -1                  # Jumlah CPU cores (-1 = semua)

# === PROPHET CONFIG ===
INTERVAL_WIDTH = 0.80        # Confidence interval (80%)
SEASONALITY_PRIOR = 1.0      # Prior scale untuk seasonality
MCMC_SAMPLES = 0             # 0 = MAP estimation (cepat)

# === THRESHOLD ===
SPARSE_THRESHOLD = 0.50      # Max % nol sebelum skip
WINSORIZE_LOWER = 0.02       # Percentile bawah untuk outlier
WINSORIZE_UPPER = 0.98       # Percentile atas untuk outlier
MIN_INSURER_VOLUME = 10      # Minimum volume untuk product-level split
```

---

## 📊 Output & Hasil

### 📈 Visualisasi Interaktif

Setiap spesialisasi menghasilkan chart Plotly interaktif yang menampilkan:

- **Garis hitam putus-putus** — Volume aktual historis
- **Garis biru solid** — Prediksi Prophet
- **Area biru transparan** — 80% confidence interval
- **Garis merah vertikal** — Batas mulai forecast

### 📋 Laporan Akurasi

```
═══════════════════════════════════════════════════════════════════════
 📊 LAPORAN AKURASI PREDIKSI AI (Backtesting 6 Bulan Terakhir)
═══════════════════════════════════════════════════════════════════════
Spesialisasi: 0303
  > Snapshot [2024-07-01] | WMAPE: 12.45% | MAE:  18.32 | RMSE:  22.10 | CPS: 0.05
  > Snapshot [2024-10-01] | WMAPE:  9.87% | MAE:  14.55 | RMSE:  17.89 | CPS: 0.05
---------------------------------------------------------------------------

📈 Rata-rata WMAPE keseluruhan : 11.16%
   Median WMAPE                : 11.16%
```

### 📁 File Output

| File | Deskripsi |
|------|-----------|
| `prophet_forecast.csv` | Detail forecast granular (produk × asuransi), filter Mei-Des tahun target |
| `prophet_pivot_table.xlsx` | Pivot table bergaya korporat dengan formatting Excel profesional |

---

## 🔬 Metodologi

### Model Selection: Facebook Prophet

Prophet dipilih karena kelebihan berikut untuk use case ini:

1. **Robust terhadap missing data** — Data rumah sakit sering memiliki gap
2. **Holiday effects** — Mendukung kalender libur Belanda 🇳🇱
3. **Interpretable components** — Trend, seasonality, holiday bisa dipisahkan
4. **Cepat di-train** — MAP estimation tanpa MCMC

### Adaptive Configuration

Model melakukan **auto-tuning** berdasarkan karakteristik data masing-masing spesialisasi:

```
┌──────────────────────────────────────────────────────┐
│              AUTO-TUNING DECISION TREE                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Coefficient of Variation (CV)                       │
│  ├── CV < 0.15  → CPS = 0.01 (Stabil, trend halus)  │
│  ├── CV < 0.35  → CPS = 0.05 (Moderate)             │
│  ├── CV < 0.60  → CPS = 0.15 (Volatil)              │
│  └── CV ≥ 0.60  → CPS = 0.30 (Sangat volatil)       │
│                                                      │
│  Jumlah Data Points (n)                              │
│  ├── n < 24 bulan → Fourier order = 2               │
│  ├── n < 36 bulan → Fourier order = 4               │
│  └── n ≥ 36 bulan → Fourier order = 6               │
│                                                      │
│  Sparse Detection                                    │
│  └── > 50% nilai nol → SKIP (tidak di-forecast)     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Insurer Split Strategy

Forecast level spesialisasi dipecah ke level asuransi menggunakan **hierarchical market share**:

| Level | Kondisi | Metode |
|-------|---------|--------|
| 1 — Product | Volume produk ≥ 10 | Share berdasarkan product × insurer |
| 2 — Specialism | Volume produk < 10, volume spec ≥ 10 | Share berdasarkan specialism × insurer |
| 3 — Hospital | Volume spec < 10 | Share berdasarkan total rumah sakit |

---

## ❓ FAQ

<details>
<summary><strong>Q: Data saya berbahasa Inggris, bisa dipakai?</strong></summary>

Ya! Pastikan nama kolom sesuai dengan format yang didokumentasikan di [Format Data Input](#-format-data-input). Konten data bisa dalam bahasa apapun.
</details>

<details>
<summary><strong>Q: Berapa lama waktu training?</strong></summary>

Tergantung jumlah spesialisasi dan snapshot. Sebagai referensi:
- **20 spesialisasi × 8 snapshot** ≈ 2-5 menit (8 core CPU)
- **50 spesialisasi × 12 snapshot** ≈ 10-15 menit (8 core CPU)
</details>

<details>
<summary><strong>Q: Bisakah saya menambahkan regressor eksternal?</strong></summary>

Ya, Anda bisa menambahkan regressor pada fungsi `build_model()` di `src/model.py` menggunakan `m.add_regressor('nama_kolom')`. Pastikan data regressor tersedia di DataFrame training dan future.
</details>

<details>
<summary><strong>Q: Kenapa ada spesialisasi yang di-skip?</strong></summary>

Spesialisasi di-skip jika lebih dari 50% data historisnya bernilai nol (sparse). Model Prophet tidak reliable untuk data seperti ini. Threshold bisa disesuaikan di konfigurasi.
</details>

---

## 🤝 Kontribusi

Kontribusi sangat diterima! Berikut cara berkontribusi:

1. **Fork** repository ini
2. Buat **branch** fitur baru (`git checkout -b feature/nama-fitur`)
3. **Commit** perubahan (`git commit -m 'Menambahkan fitur XYZ'`)
4. **Push** ke branch (`git push origin feature/nama-fitur`)
5. Buat **Pull Request**

### Development Setup

```bash
# Clone fork Anda
git clone https://github.com/<your-username>/wcn-forecast.git
cd wcn-forecast

# Install dev dependencies
pip install -r requirements.txt

# Jalankan tests
python -m pytest tests/
```

---

<div align="center">

**Dibuat dengan ❤️ untuk ekosistem kesehatan yang lebih baik**

⭐ Star repo ini jika bermanfaat! ⭐

</div>
