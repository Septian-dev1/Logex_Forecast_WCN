"""
Batch & Parallel Processing

Modul ini mengeksekusi proses pelatihan model secara paralel
untuk setiap kombinasi spesialisasi dan bulan monitor.
"""

import pandas as pd
from joblib import Parallel, delayed

from .model import train_evaluate_predict_v5


def _worker(spec: str, mon: str, df_clean: pd.DataFrame, test_months: int) -> tuple:
    """
    Fungsi worker tunggal untuk diproses secara paralel oleh Joblib.
    """
    mon_date = pd.to_datetime(mon)
    df_train = df_clean[
        (df_clean['specialism_code'] == spec) &
        (df_clean['monitor_month'] == mon)
    ].copy()
    
    df_train = df_train[~(
        (df_train['year'] == mon_date.year) &
        (df_train['month'] == mon_date.month) &
        (df_train['is_forecast'] == 0)
    )]
    
    if len(df_train['ds'].unique()) < 2:
        return (spec, mon, None)
        
    hasil = train_evaluate_predict_v5(df_train, test_months=test_months)
    return (spec, mon, hasil)


def run_batch(df_clean: pd.DataFrame, specialties: list, q_monitors: list, test_months: int = 6, n_jobs: int = -1) -> dict:
    """
    Mengeksekusi proses pelatihan model secara paralel untuk setiap kombinasi spesialisasi dan bulan monitor.

    Parameters:
        df_clean (pd.DataFrame): DataFrame yang sudah dibersihkan.
        specialties (list): Daftar kode spesialisasi unik.
        q_monitors (list): Daftar tanggal monitor untuk diproses.
        test_months (int): Jumlah bulan alokasi test backtesting.
        n_jobs (int): Jumlah CPU core yang digunakan (-1 untuk semua core tersedia).

    Returns:
        dict: Struktur kamus tersarang (nested) berisi hasil pemodelan [spesialisasi][monitor_month].
    """
    tasks = [
        (spec, mon)
        for spec in specialties
        for mon in q_monitors
    ]
    
    print(f"🚀 Memulai batch training: {len(tasks)} kombinasi spec×snapshot")
    print(f"   Paralel dengan n_jobs={n_jobs} (joblib)\n")
    
    results = Parallel(n_jobs=n_jobs, backend='loky', verbose=5)(
        delayed(_worker)(spec, mon, df_clean, test_months)
        for spec, mon in tasks
    )
    
    forecasts_dict: dict = {}
    for spec, mon, hasil in results:
        if spec not in forecasts_dict:
            forecasts_dict[spec] = {}
        if hasil is not None:
            forecasts_dict[spec][mon] = hasil
            
    return forecasts_dict
