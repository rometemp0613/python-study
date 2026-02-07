"""
연습 문제 34: 예측 모델 테스트

이 파일의 TODO를 완성하여 베어링 고장 예측 모델을 테스트하세요.
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
    """
    fit() 호출 전후의 모델 상태 변화를 테스트하세요.
    """

    def test_학습전_is_fitted_False(self):
        """
        모델 생성 직후 is_fitted가 False인지 확인하세요.
        """
        pytest.skip("TODO: BearingFailurePredictor를 생성하고 is_fitted를 확인하세요")

    def test_학습후_is_fitted_True(self, training_data):
        """
        fit() 호출 후 is_fitted가 True이고,
        normal_params에 각 특징의 mean/std가 저장되는지 확인하세요.

        확인할 특징: rms, kurtosis, crest_factor
        """
        pytest.skip("TODO: fit() 후 is_fitted와 normal_params를 검증하세요")

    def test_정상_데이터_부족시_에러(self):
        """
        정상(label='normal') 데이터가 1개만 있을 때
        ValueError가 발생하는지 확인하세요.
        """
        pytest.skip("TODO: 정상 데이터 1개로 fit()을 호출하고 ValueError를 확인하세요")


# ============================================================
# 연습 2: 건강도 점수 범위 검증
# ============================================================

class TestHealthScoreRange:
    """
    predict_health_score()의 출력 범위와 의미를 검증하세요.
    """

    def test_정상_특징_높은_점수(self, training_data):
        """
        정상 패턴에 가까운 특징(rms=0.5, kurtosis=0.2, crest_factor=1.4)이
        70점 이상의 건강도를 반환하는지 테스트하세요.
        """
        pytest.skip("TODO: 모델을 학습시키고 정상 특징으로 70점 이상을 확인하세요")

    def test_비정상_특징_낮은_점수(self, training_data):
        """
        비정상 특징(rms=3.0, kurtosis=8.0, crest_factor=5.0)이
        50점 이하의 건강도를 반환하는지 테스트하세요.
        """
        pytest.skip("TODO: 비정상 특징으로 50점 이하를 확인하세요")

    def test_점수_항상_0_100_범위(self, training_data):
        """
        극단적인 입력(모든 특징이 0 또는 100)에 대해서도
        건강도 점수가 0~100 범위를 벗어나지 않는지 확인하세요.
        """
        pytest.skip("TODO: 극단적 입력으로 0~100 범위를 확인하세요")


# ============================================================
# 연습 3: 모델 저장/로딩 테스트
# ============================================================

class TestModelPersistence:
    """
    모델을 JSON으로 저장하고 로딩한 후
    동일한 예측을 하는지 테스트하세요.
    """

    def test_저장후_로딩_동일_예측(self, training_data, tmp_path):
        """
        1. 모델을 학습시킵니다
        2. 정상 특징으로 건강도 점수를 예측합니다 (score_before)
        3. 모델을 tmp_path에 JSON으로 저장합니다
        4. 새 모델 인스턴스를 만들어 JSON에서 로딩합니다
        5. 같은 특징으로 건강도 점수를 예측합니다 (score_after)
        6. score_before == score_after를 확인합니다

        힌트: pytest.approx()를 사용하세요.
        """
        pytest.skip("TODO: 저장/로딩 후 동일 예측을 확인하세요")

    def test_미학습_모델_저장_에러(self, tmp_path):
        """
        학습하지 않은 모델을 저장하려 하면
        RuntimeError가 발생하는지 확인하세요.
        """
        pytest.skip("TODO: 미학습 모델의 save_model()에서 RuntimeError를 확인하세요")
