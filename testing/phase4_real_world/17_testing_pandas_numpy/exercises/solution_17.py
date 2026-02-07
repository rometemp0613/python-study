"""
연습 문제 17 풀이: Pandas/NumPy 코드 테스트

센서 데이터 전처리 함수들에 대한 테스트 풀이입니다.
"""
import pytest

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

from pandas.testing import assert_frame_equal, assert_series_equal
from numpy.testing import assert_allclose

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src_sensor_preprocessing import (
    clean_sensor_data,
    calculate_rolling_stats,
    extract_features,
    merge_sensor_data,
)


# ============================================================
# 연습 1: 특징 추출 함수의 정확성 테스트
# ============================================================

class TestFeatureExtraction:
    """extract_features 함수의 통계 특징 정확성 테스트"""

    def test_mean_feature(self):
        """평균 특징이 올바르게 계산되는지 테스트"""
        df = pd.DataFrame({"value": [1.0, 2.0, 3.0, 4.0, 5.0]})
        result = extract_features(df)
        assert_allclose(result["value_mean"].iloc[0], 3.0, rtol=1e-10)

    def test_rms_feature(self):
        """RMS 특징이 올바르게 계산되는지 테스트"""
        # RMS = sqrt(mean(x^2))
        df = pd.DataFrame({"value": [3.0, 4.0]})
        result = extract_features(df)
        # RMS = sqrt((9 + 16) / 2) = sqrt(12.5) ≈ 3.5355
        expected_rms = np.sqrt(np.mean(np.array([3.0, 4.0]) ** 2))
        assert_allclose(result["value_rms"].iloc[0], expected_rms, rtol=1e-10)

    def test_peak_to_peak_feature(self):
        """피크 대 피크 특징이 올바르게 계산되는지 테스트"""
        df = pd.DataFrame({"value": [5.0, 15.0, 10.0, 3.0, 8.0]})
        result = extract_features(df)
        # peak_to_peak = max - min = 15.0 - 3.0 = 12.0
        assert_allclose(
            result["value_peak_to_peak"].iloc[0], 12.0, rtol=1e-10
        )

    def test_multiple_columns(self):
        """여러 수치 열에 대해 특징이 각각 추출되는지 테스트"""
        df = pd.DataFrame({
            "temperature": [25.0, 26.0, 27.0],
            "vibration": [0.5, 0.6, 0.7],
        })
        result = extract_features(df)

        # temperature 특징 존재 확인
        assert "temperature_mean" in result.columns
        assert "temperature_std" in result.columns
        assert "temperature_rms" in result.columns

        # vibration 특징 존재 확인
        assert "vibration_mean" in result.columns
        assert "vibration_std" in result.columns
        assert "vibration_rms" in result.columns

        # 값 검증
        assert_allclose(result["temperature_mean"].iloc[0], 26.0, rtol=1e-10)
        assert_allclose(result["vibration_mean"].iloc[0], 0.6, rtol=1e-10)


# ============================================================
# 연습 2: 엣지 케이스 처리 테스트
# ============================================================

class TestEdgeCases:
    """다양한 엣지 케이스에서의 함수 동작 테스트"""

    def test_clean_all_same_values(self):
        """모든 값이 동일한 데이터의 정제"""
        df = pd.DataFrame({
            "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
            "temperature": [25.0] * 5,
            "vibration": [0.5] * 5,
        })
        result = clean_sensor_data(df)
        # 동일한 값은 이상치가 아니므로 모두 보존
        assert len(result) == 5

    def test_rolling_stats_window_equals_data_length(self):
        """윈도우 크기와 데이터 길이가 같은 경우"""
        df = pd.DataFrame({
            "temperature": [20.0, 22.0, 21.0, 23.0, 24.0],
        })
        result = calculate_rolling_stats(df, window=5)
        # 마지막 행에만 유효한 롤링 평균이 있어야 함
        assert pd.isna(result["temperature_rolling_mean"].iloc[3])
        assert not pd.isna(result["temperature_rolling_mean"].iloc[4])
        expected_mean = np.mean([20.0, 22.0, 21.0, 23.0, 24.0])
        assert_allclose(
            result["temperature_rolling_mean"].iloc[4],
            expected_mean,
            rtol=1e-10,
        )

    def test_extract_features_single_value(self):
        """단일 값 DataFrame에서 특징 추출"""
        df = pd.DataFrame({"value": [42.0]})
        result = extract_features(df)
        val = 42.0
        assert_allclose(result["value_mean"].iloc[0], val, rtol=1e-10)
        assert_allclose(result["value_min"].iloc[0], val, rtol=1e-10)
        assert_allclose(result["value_max"].iloc[0], val, rtol=1e-10)
        assert_allclose(result["value_median"].iloc[0], val, rtol=1e-10)
        assert_allclose(result["value_rms"].iloc[0], val, rtol=1e-10)
        assert_allclose(
            result["value_peak_to_peak"].iloc[0], 0.0, atol=1e-10
        )

    def test_merge_no_common_timestamps(self):
        """공통 타임스탬프가 없는 경우의 병합"""
        df1 = pd.DataFrame({
            "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
            "temperature": [25.0, 26.0, 27.0],
        })
        df2 = pd.DataFrame({
            "timestamp": pd.date_range("2024-06-01", periods=3, freq="h"),
            "vibration": [0.5, 0.6, 0.7],
        })
        result = merge_sensor_data(df1, df2, on="timestamp")
        assert len(result) == 0


# ============================================================
# 연습 3: 데이터 타입 검증 테스트
# ============================================================

class TestDataTypes:
    """전처리 후 데이터 타입 검증"""

    def test_clean_preserves_numeric_types(self):
        """정제 후 수치 열의 데이터 타입이 유지되는지 확인"""
        df = pd.DataFrame({
            "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
            "temperature": [25.0, 26.0, 27.0, 28.0, 29.0],
            "vibration": [0.5, 0.6, 0.7, 0.8, 0.9],
        })
        result = clean_sensor_data(df)
        assert result["temperature"].dtype == np.float64
        assert result["vibration"].dtype == np.float64

    def test_rolling_stats_are_float(self):
        """롤링 통계 열의 데이터 타입이 float인지 확인"""
        df = pd.DataFrame({
            "temperature": [25.0, 26.0, 27.0, 28.0, 29.0],
        })
        result = calculate_rolling_stats(df, window=3)
        rolling_cols = [c for c in result.columns if "rolling" in c]
        for col in rolling_cols:
            assert result[col].dtype == np.float64, (
                f"열 '{col}'의 타입이 float64가 아닙니다: {result[col].dtype}"
            )

    def test_features_are_float(self):
        """추출된 특징의 데이터 타입이 float인지 확인"""
        df = pd.DataFrame({
            "temperature": [25.0, 26.0, 27.0],
            "vibration": [0.5, 0.6, 0.7],
        })
        result = extract_features(df)
        for col in result.columns:
            assert result[col].dtype == np.float64, (
                f"특징 '{col}'의 타입이 float64가 아닙니다: {result[col].dtype}"
            )
