"""
Core Prophet Model Training

Modul ini berisi logika utama untuk melatih model Prophet,
mengevaluasi akurasi, dan menghasilkan prediksi.
"""

import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .helpers import (
    winsorize_series,
    auto_changepoint_scale,
    clip_forecast_negative,
    is_sparse_series,
    auto_yearly_fourier,
)


def train_evaluate_predict_v5(df_specialty: pd.DataFrame, test_months: int = 6, periods_to_forecast: int = 12) -> dict:
    """
    Melatih model Prophet, mengevaluasi akurasi menggunakan data uji terakhir (backtesting), 
    lalu memprediksi periode ke depan.

    Parameters:
        df_specialty (pd.DataFrame): Data historis spesifik untuk satu entitas/spesialisasi.
        test_months (int): Jumlah bulan terakhir yang dialokasikan untuk evaluasi model.
        periods_to_forecast (int): Jumlah bulan ke depan untuk diprediksi dari data terakhir.

    Returns:
        dict: Kamus berisi status (skipped), metrik error, objek model, hasil prediksi (forecast), 
              data agregat asli (df_agg), dan nilai changepoint scale.
    """
    df_agg = df_specialty.groupby('ds')['y'].sum(min_count=1).reset_index()
    df_agg.dropna(subset=['y'], inplace=True)
    
    result = {
        'metrics': {'MAE': None, 'RMSE': None, 'WMAPE': None},
        'model': None,
        'forecast': None,
        'df_agg': df_agg,
        'changepoint_scale': None,
        'skipped': False,
        'skip_reason': None,
    }
    
    # 1. Sparse Check
    if is_sparse_series(df_agg, col='y', zero_threshold=0.50):
        result['skipped'] = True
        result['skip_reason'] = 'sparse (>50% nol)'
        return result
        
    # 2. Winsorization & Dinamis Konfigurasi
    df_agg = winsorize_series(df_agg, col='y', lower=0.02, upper=0.98)
    result['df_agg'] = df_agg
    n_points = len(df_agg)
    cps = auto_changepoint_scale(df_agg)
    yearly_f = auto_yearly_fourier(n_points)
    result['changepoint_scale'] = cps

    def build_model():
        m = Prophet(
            changepoint_prior_scale=cps,
            seasonality_prior_scale=1.0,
            yearly_seasonality=yearly_f,
            interval_width=0.80,
            weekly_seasonality=False,
            daily_seasonality=False,
            mcmc_samples=0,
        )
        m.add_country_holidays(country_name='NL')
        if n_points >= 24:
            m.add_seasonality(name='quarterly', period=91.25, fourier_order=4)
        return m

    # 3. Skema Jika Data Terlalu Sedikit
    min_required = test_months + 6
    if n_points <= min_required:
        final_model = build_model()
        final_model.fit(df_agg)
        future = final_model.make_future_dataframe(periods=periods_to_forecast, freq='MS')
        forecast = clip_forecast_negative(final_model.predict(future))
        result['forecast'] = forecast
        result['model'] = final_model
        return result

    # 4. Evaluasi (Backtesting)
    train_df = df_agg.iloc[:-test_months].copy()
    test_df = df_agg.iloc[-test_months:].copy()
    
    eval_model = build_model()
    eval_model.fit(train_df)
    total_periods = test_months + periods_to_forecast
    future_eval = eval_model.make_future_dataframe(periods=total_periods, freq='MS')
    fc_eval = clip_forecast_negative(eval_model.predict(future_eval))
    
    fc_test = fc_eval[fc_eval['ds'].isin(test_df['ds'])]['yhat'].values
    y_true = test_df['y'].values
    n_matched = min(len(y_true), len(fc_test))
    
    if n_matched > 0:
        y_true_m = y_true[:n_matched]
        fc_test_m = fc_test[:n_matched]
        sum_err = np.sum(np.abs(y_true_m - fc_test_m))
        sum_act = np.sum(np.abs(y_true_m))
        result['metrics']['MAE'] = mean_absolute_error(y_true_m, fc_test_m)
        result['metrics']['RMSE'] = np.sqrt(mean_squared_error(y_true_m, fc_test_m))
        result['metrics']['WMAPE'] = (sum_err / sum_act) * 100 if sum_act != 0 else 0
        
    # 5. Final Model Training (Keseluruhan Data)
    final_model = build_model()
    final_model.fit(df_agg)
    future = final_model.make_future_dataframe(periods=periods_to_forecast, freq='MS')
    forecast = clip_forecast_negative(final_model.predict(future))
    
    result['forecast'] = forecast
    result['model'] = final_model
    return result
