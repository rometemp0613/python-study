"""
연습 문제 21: 머신러닝/예측 모델 테스트

이상 탐지 모델의 학습, 예측, 특징 추출, 직렬화를 테스트하세요.
각 TODO 주석을 실제 테스트 코드로 교체하세요.
"""
import json
import math
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src_anomaly_model import SimpleAnomalyDetector


@pytest.fixture
def detector():
    """학습되지 않은 모델"""
    return SimpleAnomalyDetector()


@pytest.fixture
def fitted_detector():
    """학습된 모델 (mean=30.0)"""
    model = SimpleAnomalyDetector()
    model.fit([10.0, 20.0, 30.0, 40.0, 50.0])
    return model


# ============================================================
# 연습 1: 특징 추출 정확성 테스트
# ============================================================

class TestFeatureAccuracy:
    """extract_features 함수의 수학적 정확성 테스트"""

    def test_rms_known_values(self, detector):
        """알려진 값으로 RMS 계산 검증"""
        pytest.skip(
            "TODO: [1.0, 2.0, 3.0]으로 RMS를 계산하고 "
            "수동 계산 결과(sqrt((1+4+9)/3))와 비교하세요"
        )

    def test_peak_to_peak_with_negatives(self, detector):
        """음수를 포함한 데이터의 피크 대 피크"""
        pytest.skip(
            "TODO: [-10.0, 5.0, -3.0, 8.0]로 peak_to_peak이 "
            "18.0 (8.0-(-10.0))인지 확인하세요"
        )

    def test_std_known_values(self, detector):
        """알려진 값으로 표준편차 검증"""
        pytest.skip(
            "TODO: [2.0, 4.0, 6.0, 8.0]으로 std를 계산하고 "
            "수동 계산 결과와 비교하세요. 힌트: 모집단 표준편차 사용"
        )

    def test_crest_factor_sine_wave(self, detector):
        """사인파 유사 데이터의 크레스트 팩터"""
        pytest.skip(
            "TODO: [0.0, 1.0, 0.0, -1.0]로 crest_factor를 계산하고 "
            "max_abs / rms 값을 검증하세요"
        )


# ============================================================
# 연습 2: 모델 직렬화 왕복 테스트
# ============================================================

class TestSerializationRoundTrip:
    """모델 저장/로드 후 일관성 테스트"""

    def test_save_load_same_mean(self, tmp_path, fitted_detector):
        """저장 후 로드한 모델의 평균이 동일한지 확인"""
        pytest.skip(
            "TODO: fitted_detector를 저장하고, 새 모델로 로드한 후 "
            "mean 값이 동일한지 확인하세요"
        )

    def test_save_load_same_predictions(self, tmp_path, fitted_detector):
        """저장 후 로드한 모델이 동일한 예측을 하는지 확인"""
        pytest.skip(
            "TODO: 모델을 저장/로드한 후 동일한 테스트 데이터에 대해 "
            "predict() 결과가 같은지 확인하세요"
        )

    def test_save_load_same_classifications(self, tmp_path, fitted_detector):
        """저장 후 로드한 모델이 동일한 분류를 하는지 확인"""
        pytest.skip(
            "TODO: 모델을 저장/로드한 후 동일한 데이터에 대해 "
            "classify() 결과가 같은지 확인하세요"
        )


# ============================================================
# 연습 3: 엣지 케이스 및 에러 처리
# ============================================================

class TestEdgeCases:
    """엣지 케이스와 에러 처리 테스트"""

    def test_predict_before_fit(self, detector):
        """학습 전 예측 시도"""
        pytest.skip(
            "TODO: fit() 없이 predict()를 호출했을 때 "
            "RuntimeError가 발생하는지 확인하세요"
        )

    def test_fit_empty_list(self, detector):
        """빈 리스트로 학습 시도"""
        pytest.skip(
            "TODO: fit([])를 호출했을 때 "
            "ValueError가 발생하는지 확인하세요"
        )

    def test_classify_single_value(self, fitted_detector):
        """단일 값 분류"""
        pytest.skip(
            "TODO: 한 개의 값으로 classify()를 호출하고 "
            "결과가 [0] 또는 [1]인 길이 1 리스트인지 확인하세요"
        )

    def test_save_unfitted_model(self, tmp_path, detector):
        """학습 전 저장 시도"""
        pytest.skip(
            "TODO: 학습하지 않은 모델을 save_model()로 저장 시도했을 때 "
            "RuntimeError가 발생하는지 확인하세요"
        )
