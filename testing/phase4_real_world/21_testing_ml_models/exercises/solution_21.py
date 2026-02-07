"""
연습 문제 21 풀이: 머신러닝/예측 모델 테스트
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
        features = detector.extract_features([1.0, 2.0, 3.0])
        # RMS = sqrt((1 + 4 + 9) / 3) = sqrt(14/3)
        expected_rms = math.sqrt(14.0 / 3.0)
        assert features["rms"] == pytest.approx(expected_rms)

    def test_peak_to_peak_with_negatives(self, detector):
        """음수를 포함한 데이터의 피크 대 피크"""
        features = detector.extract_features([-10.0, 5.0, -3.0, 8.0])
        # peak_to_peak = 8.0 - (-10.0) = 18.0
        assert features["peak_to_peak"] == pytest.approx(18.0)

    def test_std_known_values(self, detector):
        """알려진 값으로 표준편차 검증"""
        features = detector.extract_features([2.0, 4.0, 6.0, 8.0])
        # 평균 = 5.0
        # 분산 = ((2-5)^2 + (4-5)^2 + (6-5)^2 + (8-5)^2) / 4
        #       = (9 + 1 + 1 + 9) / 4 = 5.0
        # 표준편차 = sqrt(5.0)
        expected_std = math.sqrt(5.0)
        assert features["std"] == pytest.approx(expected_std)

    def test_crest_factor_sine_wave(self, detector):
        """사인파 유사 데이터의 크레스트 팩터"""
        features = detector.extract_features([0.0, 1.0, 0.0, -1.0])
        # RMS = sqrt((0 + 1 + 0 + 1) / 4) = sqrt(0.5)
        # max_abs = 1.0
        # crest_factor = 1.0 / sqrt(0.5) = sqrt(2)
        expected_crest = 1.0 / math.sqrt(0.5)
        assert features["crest_factor"] == pytest.approx(expected_crest)


# ============================================================
# 연습 2: 모델 직렬화 왕복 테스트
# ============================================================

class TestSerializationRoundTrip:
    """모델 저장/로드 후 일관성 테스트"""

    def test_save_load_same_mean(self, tmp_path, fitted_detector):
        """저장 후 로드한 모델의 평균이 동일한지 확인"""
        model_path = str(tmp_path / "model.json")
        fitted_detector.save_model(model_path)

        loaded = SimpleAnomalyDetector()
        loaded.load_model(model_path)

        assert loaded.mean == pytest.approx(fitted_detector.mean)
        assert loaded.std == pytest.approx(fitted_detector.std)

    def test_save_load_same_predictions(self, tmp_path, fitted_detector):
        """저장 후 로드한 모델이 동일한 예측을 하는지 확인"""
        model_path = str(tmp_path / "model.json")
        fitted_detector.save_model(model_path)

        loaded = SimpleAnomalyDetector()
        loaded.load_model(model_path)

        test_data = [5.0, 15.0, 25.0, 35.0, 45.0, 55.0]
        original_scores = fitted_detector.predict(test_data)
        loaded_scores = loaded.predict(test_data)

        for orig, load in zip(original_scores, loaded_scores):
            assert orig == pytest.approx(load)

    def test_save_load_same_classifications(self, tmp_path, fitted_detector):
        """저장 후 로드한 모델이 동일한 분류를 하는지 확인"""
        model_path = str(tmp_path / "model.json")
        fitted_detector.save_model(model_path)

        loaded = SimpleAnomalyDetector()
        loaded.load_model(model_path)

        test_data = [10.0, 30.0, 50.0, 100.0, 200.0]
        original_labels = fitted_detector.classify(test_data, threshold=2.5)
        loaded_labels = loaded.classify(test_data, threshold=2.5)

        assert original_labels == loaded_labels


# ============================================================
# 연습 3: 엣지 케이스 및 에러 처리
# ============================================================

class TestEdgeCases:
    """엣지 케이스와 에러 처리 테스트"""

    def test_predict_before_fit(self, detector):
        """학습 전 예측 시도"""
        with pytest.raises(RuntimeError, match="학습되지 않았습니다"):
            detector.predict([1.0, 2.0, 3.0])

    def test_fit_empty_list(self, detector):
        """빈 리스트로 학습 시도"""
        with pytest.raises(ValueError, match="비어있습니다"):
            detector.fit([])

    def test_classify_single_value(self, fitted_detector):
        """단일 값 분류"""
        labels = fitted_detector.classify([30.0], threshold=3.0)
        assert len(labels) == 1
        assert labels[0] in [0, 1]

    def test_save_unfitted_model(self, tmp_path, detector):
        """학습 전 저장 시도"""
        model_path = str(tmp_path / "model.json")
        with pytest.raises(RuntimeError, match="학습되지 않은"):
            detector.save_model(model_path)
