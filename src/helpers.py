"""
Helper Functions (Statistik & Thresholding)

Modul utilitas yang berisi fungsi-fungsi pendukung untuk
winsorization, konfigurasi otomatis, dan deteksi sparse series.
"""

import numpy as np
import pandas as pd


def winsorize_series(df: pd.DataFrame, col: str = 'y', lower: float = 0.02, upper: float = 0.98) -> pd.DataFrame:
    """
    Membatasi nilai ekstrem (outliers) pada deret waktu menggunakan metode Winsorization.

    Parameters:
        df (pd.DataFrame): DataFrame input.
        col (str): Nama kolom yang akan di-winsorize.
        lower (float): Persentil batas bawah (default 2%).
        upper (float): Persentil batas atas (default 98%).

    Returns:
        pd.DataFrame: DataFrame dengan nilai ekstrem yang telah dibatasi.
    """
    if len(df) < 10:
        return df
    q_low = df[col].quantile(lower)
    q_high = df[col].quantile(upper)
    df = df.copy()
    df[col] = df[col].clip(lower=q_low, upper=q_high)
    return df


def auto_changepoint_scale(df: pd.DataFrame) -> float:
    """
    Menentukan nilai changepoint_prior_scale Prophet secara dinamis 
    berdasarkan koefisien variasi (Coefficient of Variation) data.

    Parameters:
        df (pd.DataFrame): DataFrame dengan kolom target 'y'.

    Returns:
        float: Nilai scale yang direkomendasikan.
    """
    mean_val = df['y'].mean()
    if mean_val <= 0:
        return 0.05
    cov = df['y'].std() / mean_val
    if cov < 0.15:   return 0.01
    elif cov < 0.35: return 0.05
    elif cov < 0.60: return 0.15
    else:            return 0.30


def clip_forecast_negative(forecast: pd.DataFrame) -> pd.DataFrame:
    """
    Mencegah hasil prediksi Prophet memiliki nilai negatif.

    Parameters:
        forecast (pd.DataFrame): DataFrame hasil prediksi model Prophet.

    Returns:
        pd.DataFrame: DataFrame prediksi yang dinormalisasi ke minimum 0.
    """
    cols = [c for c in ['yhat', 'yhat_lower', 'yhat_upper'] if c in forecast.columns]
    forecast = forecast.copy()
    forecast[cols] = forecast[cols].clip(lower=0)
    return forecast


def is_sparse_series(df: pd.DataFrame, col: str = 'y', zero_threshold: float = 0.50) -> bool:
    """
    Mendeteksi apakah deret waktu terlalu banyak memiliki nilai nol (sparse).

    Parameters:
        df (pd.DataFrame): DataFrame deret waktu.
        col (str): Nama kolom target.
        zero_threshold (float): Ambang batas persentase nilai nol.

    Returns:
        bool: True jika data sparse, False jika memadai untuk prediksi.
    """
    if len(df) == 0:
        return True
    zero_frac = (df[col] == 0).sum() / len(df)
    return zero_frac > zero_threshold


def auto_yearly_fourier(n_points: int) -> int:
    """
    Menyesuaikan orde Fourier untuk musiman tahunan berdasarkan jumlah titik data historis.

    Parameters:
        n_points (int): Jumlah observasi historis (bulan).

    Returns:
        int: Orde Fourier yang direkomendasikan.
    """
    if n_points < 24:
        return 2
    elif n_points < 36:
        return 4
    else:
        return 6
