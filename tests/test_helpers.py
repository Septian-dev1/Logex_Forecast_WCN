"""
Unit tests for helper functions.
"""

import pytest
import numpy as np
import pandas as pd

from src.helpers import (
    winsorize_series,
    auto_changepoint_scale,
    clip_forecast_negative,
    is_sparse_series,
    auto_yearly_fourier,
)


class TestWinsorizeSeries:
    def test_short_series_unchanged(self):
        """Series dengan < 10 data points tidak di-winsorize."""
        df = pd.DataFrame({'y': [1, 2, 3, 4, 5]})
        result = winsorize_series(df)
        pd.testing.assert_frame_equal(result, df)

    def test_clips_outliers(self):
        """Outlier di-clip ke persentil batas."""
        data = list(range(100)) + [10000]
        df = pd.DataFrame({'y': data})
        result = winsorize_series(df, col='y', lower=0.02, upper=0.98)
        assert result['y'].max() < 10000


class TestAutoChangepointScale:
    def test_stable_series(self):
        """Series stabil → CPS rendah."""
        df = pd.DataFrame({'y': [100] * 50})
        assert auto_changepoint_scale(df) == 0.01

    def test_volatile_series(self):
        """Series volatil → CPS tinggi."""
        np.random.seed(42)
        df = pd.DataFrame({'y': np.random.uniform(0, 1000, 50)})
        assert auto_changepoint_scale(df) >= 0.15

    def test_zero_mean(self):
        """Mean ≤ 0 → default CPS."""
        df = pd.DataFrame({'y': [0] * 50})
        assert auto_changepoint_scale(df) == 0.05


class TestClipForecastNegative:
    def test_clips_negative_values(self):
        """Nilai negatif di-clip ke 0."""
        df = pd.DataFrame({'yhat': [-5, 10, -3], 'yhat_lower': [-10, 5, -1], 'yhat_upper': [5, 15, 8]})
        result = clip_forecast_negative(df)
        assert (result[['yhat', 'yhat_lower', 'yhat_upper']] >= 0).all().all()


class TestIsSparseSeries:
    def test_all_zeros_is_sparse(self):
        """100% nol → sparse."""
        df = pd.DataFrame({'y': [0] * 20})
        assert is_sparse_series(df) is True

    def test_no_zeros_is_not_sparse(self):
        """0% nol → tidak sparse."""
        df = pd.DataFrame({'y': [10] * 20})
        assert is_sparse_series(df) is False

    def test_empty_is_sparse(self):
        """DataFrame kosong → sparse."""
        df = pd.DataFrame({'y': []})
        assert is_sparse_series(df) is True


class TestAutoYearlyFourier:
    def test_short_data(self):
        assert auto_yearly_fourier(12) == 2

    def test_medium_data(self):
        assert auto_yearly_fourier(30) == 4

    def test_long_data(self):
        assert auto_yearly_fourier(48) == 6
