"""
Data Preprocessing Pipeline

Modul ini bertanggung jawab untuk membersihkan dan memformat
DataFrame mentah agar siap digunakan untuk pemodelan Prophet.
"""

import pandas as pd


def load_and_preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membersihkan dan memformat DataFrame mentah untuk pemodelan Prophet.
    
    Proses yang dilakukan meliputi:
    1. Penghapusan duplikasi dan nilai kosong pada kolom esensial.
    2. Konversi format string angka (mengandung koma) menjadi float.
    3. Penyaringan nilai volume negatif.
    4. Pembuatan kolom tanggal ('ds') dan target ('y') sesuai standar Prophet.
    5. Pengurutan data historis berdasarkan tanggal dan spesialisasi.

    Parameters:
        df (pd.DataFrame): DataFrame mentah hasil ekstraksi.

    Returns:
        pd.DataFrame: DataFrame bersih yang siap digunakan untuk training.
    """
    data = df.copy()
    print("Memulai proses pembersihan data...")
    
    data.drop_duplicates(inplace=True)
    data.dropna(subset=['year', 'month', 'volume'], inplace=True)
    
    if data['volume'].dtype in ['object', 'O']:
        data['volume'] = data['volume'].astype(str).str.replace(',', '.').astype(float)
        
    if 'revenue' in data.columns and data['revenue'].dtype in ['object', 'O']:
        data['revenue'] = data['revenue'].astype(str).str.replace(',', '.').astype(float)
        
    data = data[data['volume'] >= 0]
    data['year'] = data['year'].astype(int)
    data['month'] = data['month'].astype(int)
    data['ds'] = pd.to_datetime(data[['year', 'month']].assign(DAY=1))
    
    data.rename(columns={'volume': 'y'}, inplace=True)
    
    data_actual = (
        data[data['is_forecast'] == 0].copy()
        if 'is_forecast' in data.columns
        else data.copy()
    )
    
    data_actual['monitor_month'] = pd.to_datetime(data_actual['monitor_month']).dt.strftime('%Y-%m-%d')
    
    if 'specialism_code' in data_actual.columns:
        data_actual.sort_values(by=['specialism_code', 'ds'], inplace=True)
    else:
        data_actual.sort_values(by=['ds'], inplace=True)
        
    data_actual.reset_index(drop=True, inplace=True)
    print(f"✅ Preprocessing Selesai! Data bersih siap digunakan: {len(data_actual)} baris.")
    
    return data_actual
