"""
연습 문제 34 풀이: 예측 모델 테스트

각 테스트의 완성된 풀이입니다.
"""

import pytest
import random
import sys
import os

# 부모 디렉토리의 모듈을 임포트하기 위한 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_bearing_model import BearingFailurePredictor, HealthMetrics


@pytest.fixture
def training_data():
    """학습 데이터 (정상 20개)"""
    random.seed(42)
    data = []
    for _ in range(20):
        data.append({
            "rms": 0.5 + random.gauss(0, 0.05),
            "kurtosis": 0.2 + random.gauss(0, 0.03),
            "crest_factor": 1.4 + random.gauss(0, 0.05),
            "label": "normal",
        })
    return data


# ============================================================
# 연습 1: 모델 학습 상태 검증
# ============================================================

class TestModelFitState:
    """fit() 전후의 모델 상태 변화 테스트"""

    def test_학습전_is_fitted_False(self):
        """모델 생성 직후 is_fitted=False 확인"""
        # 준비 & 실행
        model = BearingFailurePredictor()

        # 검증
        assert model.is_fitted is False
        assert model.normal_params == {}

    def test_학습후_is_fitted_True(self, training_data):
        """fit() 후 is_fitted=True이고 파라미터가 저장됨"""
        # 준비
        model = BearingFailurePredictor()

        # 실행
        model.fit(training_data)

        # 검증
        assert model.is_fitted is True
        for feature in ["rms", "kurtosis", "crest_factor"]:
            assert feature in model.normal_params
            assert "mean" in model.normal_params[feature]
            assert "std" in model.normal_params[feature]
            assert model.normal_params[feature]["std"] > 0

    def test_정상_데이터_부족시_에러(self):
        """정상 데이터 1개로 fit() 시 ValueError"""
        # 준비
        model = BearingFailurePredictor()
        data = [{
            "rms": 0.5,
            "kurtosis": 0.2,
            "crest_factor": 1.4,
            "label": "normal",
        }]

        # 실행 & 검증
        with pytest.raises(ValueError, match="최소 2개"):
            model.fit(data)


# ============================================================
# 연습 2: 건강도 점수 범위 검증
# ============================================================

class TestHealthScoreRange:
    """predict_health_score() 출력 검증"""

    def test_정상_특징_높은_점수(self, training_data):
        """정상 패턴에 가까운 특징은 70점 이상"""
        # 준비
        model = BearingFailurePredictor()
        model.fit(training_data)
        normal_features = {"rms": 0.5, "kurtosis": 0.2, "crest_factor": 1.4}

        # 실행
        score = model.predict_health_score(normal_features)

        # 검증
        assert score >= 70.0, f"정상 특징 점수가 너무 낮음: {score}"

    def test_비정상_특징_낮은_점수(self, training_data):
        """비정상 특징은 50점 이하"""
        # 준비
        model = BearingFailurePredictor()
        model.fit(training_data)
        fault_features = {"rms": 3.0, "kurtosis": 8.0, "crest_factor": 5.0}

        # 실행
        score = model.predict_health_score(fault_features)

        # 검증
        assert score <= 50.0, f"비정상 특징 점수가 너무 높음: {score}"

    def test_점수_항상_0_100_범위(self, training_data):
        """극단적 입력에서도 0~100 범위 유지"""
        # 준비
        model = BearingFailurePredictor()
        model.fit(training_data)

        extreme_cases = [
            {"rms": 0.0, "kurtosis": 0.0, "crest_factor": 0.0},
            {"rms": 100.0, "kurtosis": 100.0, "crest_factor": 100.0},
        ]

        # 실행 & 검증
        for features in extreme_cases:
            score = model.predict_health_score(features)
            assert 0.0 <= score <= 100.0, f"범위 초과: {score}"


# ============================================================
# 연습 3: 모델 저장/로딩 테스트
# ============================================================

class TestModelPersistence:
    """모델 저장/로딩 일관성 테스트"""

    def test_저장후_로딩_동일_예측(self, training_data, tmp_path):
        """저장 후 로딩하면 동일한 예측 결과"""
        # 준비: 모델 학습
        model = BearingFailurePredictor()
        model.fit(training_data)
        test_features = {"rms": 0.5, "kurtosis": 0.2, "crest_factor": 1.4}

        # 저장 전 예측
        score_before = model.predict_health_score(test_features)

        # 저장
        filepath = str(tmp_path / "model.json")
        model.save_model(filepath)

        # 새 모델로 로딩
        loaded_model = BearingFailurePredictor()
        loaded_model.load_model(filepath)

        # 로딩 후 예측
        score_after = loaded_model.predict_health_score(test_features)

        # 검증
        assert score_before == pytest.approx(score_after)

    def test_미학습_모델_저장_에러(self, tmp_path):
        """미학습 모델 저장 시 RuntimeError"""
        # 준비
        model = BearingFailurePredictor()
        filepath = str(tmp_path / "model.json")

        # 실행 & 검증
        with pytest.raises(RuntimeError, match="학습되지 않은"):
            model.save_model(filepath)
