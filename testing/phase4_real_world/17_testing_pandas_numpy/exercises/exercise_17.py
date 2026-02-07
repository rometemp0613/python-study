"""
연습 문제 17: Pandas/NumPy 코드 테스트

센서 데이터 전처리 함수들에 대한 테스트를 작성하세요.
각 TODO 주석을 실제 테스트 코드로 교체하세요.
"""
import pytest

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

from pandas.testing import assert_frame_equal, assert_series_equal
from numpy.testing import assert_allclose

# 부모 디렉토리의 모듈 임포트
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
        """평균 특징이 올바르게 계산되는지 테스트하세요"""
        pytest.skip("TODO: [1, 2, 3, 4, 5] 데이터로 평균이 3.0인지 확인")

    def test_rms_feature(self):
        """RMS 특징이 올바르게 계산되는지 테스트하세요"""
        pytest.skip(
            "TODO: 알려진 값으로 RMS를 계산하고 assert_allclose로 비교"
        )

    def test_peak_to_peak_feature(self):
        """피크 대 피크 특징이 올바르게 계산되는지 테스트하세요"""
        pytest.skip(
            "TODO: 최대값 - 최소값이 올바른지 확인"
        )

    def test_multiple_columns(self):
        """여러 수치 열에 대해 특징이 각각 추출되는지 테스트하세요"""
        pytest.skip(
            "TODO: temperature와 vibration 열 모두에 대해 특징이 생성되는지 확인"
        )


# ============================================================
# 연습 2: 엣지 케이스 처리 테스트
# ============================================================

class TestEdgeCases:
    """다양한 엣지 케이스에서의 함수 동작 테스트"""

    def test_clean_all_same_values(self):
        """모든 값이 동일한 데이터의 정제"""
        pytest.skip(
            "TODO: temperature가 모두 25.0인 DataFrame으로 "
            "clean_sensor_data가 데이터를 보존하는지 확인"
        )

    def test_rolling_stats_window_equals_data_length(self):
        """윈도우 크기와 데이터 길이가 같은 경우"""
        pytest.skip(
            "TODO: 데이터 5개, 윈도우 5일 때 마지막 행에만 값이 존재하는지 확인"
        )

    def test_extract_features_single_value(self):
        """단일 값 DataFrame에서 특징 추출"""
        pytest.skip(
            "TODO: 값이 하나인 DataFrame에서 mean == min == max == median인지 확인"
        )

    def test_merge_no_common_timestamps(self):
        """공통 타임스탬프가 없는 경우의 병합"""
        pytest.skip(
            "TODO: 완전히 다른 타임스탬프의 두 DataFrame 병합 결과가 빈 DataFrame인지 확인"
        )


# ============================================================
# 연습 3: 데이터 타입 검증 테스트
# ============================================================

class TestDataTypes:
    """전처리 후 데이터 타입 검증"""

    def test_clean_preserves_numeric_types(self):
        """정제 후 수치 열의 데이터 타입이 유지되는지 테스트하세요"""
        pytest.skip(
            "TODO: clean_sensor_data 후 temperature 열이 float64인지 확인"
        )

    def test_rolling_stats_are_float(self):
        """롤링 통계 열의 데이터 타입이 float인지 테스트하세요"""
        pytest.skip(
            "TODO: calculate_rolling_stats 후 새로 생성된 열이 float64인지 확인"
        )

    def test_features_are_float(self):
        """추출된 특징의 데이터 타입이 float인지 테스트하세요"""
        pytest.skip(
            "TODO: extract_features 결과의 모든 열이 float64인지 확인"
        )
