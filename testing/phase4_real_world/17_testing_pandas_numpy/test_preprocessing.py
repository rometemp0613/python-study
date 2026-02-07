"""
센서 데이터 전처리 테스트

pandas.testing과 numpy.testing을 활용하여
센서 데이터 전처리 함수들의 정확성을 검증합니다.
"""
import pytest

# pandas/numpy가 없으면 전체 모듈 건너뜀
pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

from pandas.testing import assert_frame_equal, assert_series_equal
from numpy.testing import assert_allclose

from src_sensor_preprocessing import (
    clean_sensor_data,
    calculate_rolling_stats,
    extract_features,
    merge_sensor_data,
)


# ============================================================
# clean_sensor_data 테스트
# ============================================================

class TestCleanSensorData:
    """센서 데이터 정제 함수 테스트"""

    def test_removes_nan_rows(self, sample_sensor_df):
        """NaN 값이 포함된 행이 제거되는지 확인"""
        result = clean_sensor_data(sample_sensor_df)
        # 모든 수치 열에 NaN이 없어야 함
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            assert result[col].isna().sum() == 0, (
                f"열 '{col}'에 NaN이 남아 있습니다"
            )

    def test_removes_outliers(self, sample_sensor_df):
        """IQR 방법으로 이상치가 제거되는지 확인"""
        result = clean_sensor_data(sample_sensor_df)
        # 200도는 명백한 이상치 - 제거되어야 함
        assert result["temperature"].max() < 100, (
            "온도 이상치(200도)가 제거되지 않았습니다"
        )

    def test_preserves_valid_data(self, clean_sensor_df):
        """정상 데이터가 보존되는지 확인"""
        result = clean_sensor_data(clean_sensor_df)
        # 이상치와 NaN이 없는 데이터는 그대로 유지
        assert len(result) == len(clean_sensor_df)

    def test_returns_copy(self, sample_sensor_df):
        """원본 데이터가 변경되지 않는지 확인"""
        original = sample_sensor_df.copy()
        _ = clean_sensor_data(sample_sensor_df)
        assert_frame_equal(sample_sensor_df, original)

    def test_empty_dataframe(self, empty_sensor_df):
        """빈 DataFrame 처리"""
        result = clean_sensor_data(empty_sensor_df)
        assert len(result) == 0
        # 열 구조는 유지되어야 함
        assert list(result.columns) == list(empty_sensor_df.columns)

    def test_all_nan_dataframe(self, all_nan_df):
        """모든 값이 NaN인 DataFrame 처리"""
        result = clean_sensor_data(all_nan_df)
        assert len(result) == 0

    def test_single_row(self, single_row_df):
        """단일 행 DataFrame 처리"""
        result = clean_sensor_data(single_row_df)
        assert len(result) == 1
        assert result["temperature"].iloc[0] == 25.0

    def test_index_is_reset(self, sample_sensor_df):
        """행 제거 후 인덱스가 리셋되는지 확인"""
        result = clean_sensor_data(sample_sensor_df)
        expected_index = pd.RangeIndex(start=0, stop=len(result), step=1)
        assert result.index.equals(expected_index)


# ============================================================
# calculate_rolling_stats 테스트
# ============================================================

class TestRollingStats:
    """롤링 통계 계산 테스트"""

    def test_rolling_columns_created(self, clean_sensor_df):
        """롤링 통계 열이 올바르게 생성되는지 확인"""
        result = calculate_rolling_stats(clean_sensor_df, window=3)
        expected_cols = [
            "temperature_rolling_mean",
            "temperature_rolling_std",
            "temperature_rolling_min",
            "temperature_rolling_max",
            "vibration_rolling_mean",
            "vibration_rolling_std",
            "vibration_rolling_min",
            "vibration_rolling_max",
        ]
        for col in expected_cols:
            assert col in result.columns, f"열 '{col}'이 생성되지 않았습니다"

    def test_rolling_mean_values(self):
        """롤링 평균값의 정확성 검증"""
        df = pd.DataFrame({
            "temperature": [20.0, 22.0, 21.0, 23.0, 22.0],
        })
        result = calculate_rolling_stats(df, window=3)

        # 윈도우=3: 인덱스 0,1은 NaN, 인덱스 2부터 값 존재
        expected_means = [np.nan, np.nan, 21.0, 22.0, 22.0]
        assert_allclose(
            result["temperature_rolling_mean"].values,
            expected_means,
            rtol=1e-10,
            equal_nan=True,
        )

    def test_rolling_std_values(self):
        """롤링 표준편차값의 정확성 검증"""
        df = pd.DataFrame({
            "temperature": [10.0, 10.0, 10.0, 10.0, 10.0],
        })
        result = calculate_rolling_stats(df, window=3)

        # 모든 값이 같으면 표준편차는 0
        valid_stds = result["temperature_rolling_std"].dropna()
        assert_allclose(valid_stds.values, [0.0, 0.0, 0.0], atol=1e-10)

    def test_empty_dataframe(self, empty_sensor_df):
        """빈 DataFrame 처리"""
        result = calculate_rolling_stats(empty_sensor_df, window=3)
        assert len(result) == 0

    def test_single_row_returns_nan_rolling(self, single_row_df):
        """단일 행일 때 롤링 통계는 NaN"""
        result = calculate_rolling_stats(single_row_df, window=3)
        assert len(result) == 1
        assert pd.isna(result["temperature_rolling_mean"].iloc[0])

    def test_window_larger_than_data(self):
        """윈도우가 데이터보다 큰 경우"""
        df = pd.DataFrame({
            "temperature": [25.0, 26.0],
        })
        result = calculate_rolling_stats(df, window=5)
        # 모든 롤링 값은 NaN이어야 함
        assert result["temperature_rolling_mean"].isna().all()

    def test_preserves_original_columns(self, clean_sensor_df):
        """원래 열이 보존되는지 확인"""
        result = calculate_rolling_stats(clean_sensor_df, window=3)
        for col in clean_sensor_df.columns:
            assert col in result.columns


# ============================================================
# extract_features 테스트
# ============================================================

class TestExtractFeatures:
    """특징 추출 테스트"""

    def test_feature_columns_created(self, clean_sensor_df):
        """예상된 특징 열이 생성되는지 확인"""
        result = extract_features(clean_sensor_df)
        expected_features = [
            "temperature_mean", "temperature_std",
            "temperature_min", "temperature_max",
            "temperature_median", "temperature_rms",
            "temperature_peak_to_peak",
        ]
        for feat in expected_features:
            assert feat in result.columns, f"특징 '{feat}'이 없습니다"

    def test_mean_calculation(self):
        """평균 계산 정확성"""
        df = pd.DataFrame({"value": [10.0, 20.0, 30.0]})
        result = extract_features(df)
        assert_allclose(result["value_mean"].iloc[0], 20.0, rtol=1e-10)

    def test_std_calculation(self):
        """표준편차 계산 정확성"""
        df = pd.DataFrame({"value": [10.0, 10.0, 10.0]})
        result = extract_features(df)
        assert_allclose(result["value_std"].iloc[0], 0.0, atol=1e-10)

    def test_rms_calculation(self):
        """RMS(Root Mean Square) 계산 정확성"""
        df = pd.DataFrame({"value": [3.0, 4.0]})
        result = extract_features(df)
        # RMS = sqrt((9 + 16) / 2) = sqrt(12.5)
        expected_rms = np.sqrt(12.5)
        assert_allclose(result["value_rms"].iloc[0], expected_rms, rtol=1e-10)

    def test_peak_to_peak(self):
        """피크 대 피크 계산"""
        df = pd.DataFrame({"value": [5.0, 15.0, 10.0]})
        result = extract_features(df)
        assert_allclose(
            result["value_peak_to_peak"].iloc[0], 10.0, rtol=1e-10
        )

    def test_returns_single_row(self, clean_sensor_df):
        """결과가 단일 행인지 확인"""
        result = extract_features(clean_sensor_df)
        assert len(result) == 1

    def test_empty_dataframe(self, empty_sensor_df):
        """빈 DataFrame 처리"""
        result = extract_features(empty_sensor_df)
        assert len(result) == 0


# ============================================================
# merge_sensor_data 테스트
# ============================================================

class TestMergeSensorData:
    """센서 데이터 병합 테스트"""

    def test_basic_merge(self, temperature_df, vibration_df):
        """기본 병합 동작 확인"""
        result = merge_sensor_data(temperature_df, vibration_df, on="timestamp")
        assert "temperature" in result.columns
        assert "vibration" in result.columns
        assert len(result) == 5

    def test_merge_values_preserved(self, temperature_df, vibration_df):
        """병합 후 값이 보존되는지 확인"""
        result = merge_sensor_data(temperature_df, vibration_df, on="timestamp")
        assert_allclose(
            result["temperature"].values,
            [25.0, 26.0, 27.0, 28.0, 29.0],
            rtol=1e-10,
        )
        assert_allclose(
            result["vibration"].values,
            [0.5, 0.6, 0.7, 0.8, 0.9],
            rtol=1e-10,
        )

    def test_mismatched_timestamps(self, mismatched_timestamp_df):
        """타임스탬프가 불일치할 때 내부 조인"""
        df1, df2 = mismatched_timestamp_df
        result = merge_sensor_data(df1, df2, on="timestamp")
        # df1: 00:00~04:00, df2: 02:00~06:00 => 교집합: 02:00, 03:00, 04:00
        assert len(result) == 3

    def test_empty_dataframe_merge(self, temperature_df, empty_sensor_df):
        """빈 DataFrame과의 병합"""
        result = merge_sensor_data(temperature_df, empty_sensor_df, on="timestamp")
        assert len(result) == 0

    def test_merge_sorted_by_timestamp(self):
        """병합 결과가 타임스탬프 순으로 정렬되는지 확인"""
        df1 = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-01 03:00", "2024-01-01 01:00"]),
            "temperature": [27.0, 25.0],
        })
        df2 = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-01 01:00", "2024-01-01 03:00"]),
            "vibration": [0.5, 0.7],
        })
        result = merge_sensor_data(df1, df2, on="timestamp")
        assert result["timestamp"].is_monotonic_increasing
