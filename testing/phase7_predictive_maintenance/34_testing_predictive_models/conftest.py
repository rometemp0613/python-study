"""
예측 모델 테스트를 위한 공유 픽스처 모듈

학습/테스트 데이터, 특징 세트 등을 제공합니다.
"""

import pytest
import random


@pytest.fixture
def normal_training_data():
    """정상 상태 학습 데이터 (20개)"""
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


@pytest.fixture
def fault_training_data():
    """고장 상태 학습 데이터 (10개)"""
    random.seed(43)
    data = []
    for _ in range(10):
        data.append({
            "rms": 2.5 + random.gauss(0, 0.3),
            "kurtosis": 5.0 + random.gauss(0, 0.5),
            "crest_factor": 3.5 + random.gauss(0, 0.3),
            "label": "fault",
        })
    return data


@pytest.fixture
def mixed_training_data(normal_training_data, fault_training_data):
    """정상 + 고장 혼합 학습 데이터"""
    return normal_training_data + fault_training_data


@pytest.fixture
def normal_features():
    """정상 상태의 특징 세트"""
    return {
        "rms": 0.5,
        "kurtosis": 0.2,
        "crest_factor": 1.4,
    }


@pytest.fixture
def fault_features():
    """고장 상태의 특징 세트"""
    return {
        "rms": 3.0,
        "kurtosis": 8.0,
        "crest_factor": 5.0,
    }


@pytest.fixture
def test_data_with_labels():
    """평가용 테스트 데이터 (특징 + 라벨)"""
    random.seed(44)
    test_data = []
    true_labels = []

    # 정상 데이터 10개
    for _ in range(10):
        test_data.append({
            "rms": 0.5 + random.gauss(0, 0.05),
            "kurtosis": 0.2 + random.gauss(0, 0.03),
            "crest_factor": 1.4 + random.gauss(0, 0.05),
        })
        true_labels.append("normal")

    # 고장 데이터 10개
    for _ in range(10):
        test_data.append({
            "rms": 2.5 + random.gauss(0, 0.3),
            "kurtosis": 5.0 + random.gauss(0, 0.5),
            "crest_factor": 3.5 + random.gauss(0, 0.3),
        })
        true_labels.append("fault")

    return test_data, true_labels


@pytest.fixture
def declining_health_history():
    """건강도가 점차 하락하는 이력 데이터"""
    return [95.0, 90.0, 82.0, 75.0, 68.0, 60.0]


@pytest.fixture
def stable_health_history():
    """건강도가 안정적인 이력 데이터"""
    return [92.0, 91.0, 93.0, 90.0, 92.0, 91.0]
