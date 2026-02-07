"""
연습 문제 08 풀이: Parametrize - 매개변수화 테스트

각 연습의 풀이를 확인하세요.
"""

import pytest
import sys
import os

# 상위 디렉토리의 모듈을 import하기 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_anomaly_detector import AnomalyDetector, Severity


detector = AnomalyDetector()


# ============================================================
# 연습 1 풀이: 경계값 테스트
# ============================================================

@pytest.mark.parametrize("value, expected_anomaly", [
    (49.0, False),   # 임계값 - 1: 정상
    (50.0, False),   # 임계값과 동일: 정상 (초과가 아님)
    (51.0, True),    # 임계값 + 1: 이상
], ids=["임계값_미만", "임계값_동일", "임계값_초과"])
def test_boundary_values(value, expected_anomaly):
    """경계값 테스트: 임계값 50.0 전후의 동작 확인"""
    result = detector.detect(value, threshold=50.0)
    assert result.is_anomaly == expected_anomaly


# ============================================================
# 연습 2 풀이: 심각도 분류 테스트
# ============================================================

@pytest.mark.parametrize("value, expected_severity", [
    pytest.param(25.0, Severity.NORMAL, id="정상_25도"),
    pytest.param(55.0, Severity.LOW, id="저위험_55도"),
    pytest.param(75.0, Severity.MEDIUM, id="중위험_75도"),
    pytest.param(90.0, Severity.HIGH, id="고위험_90도"),
    pytest.param(100.0, Severity.CRITICAL, id="위험_100도"),
])
def test_severity_classification(value, expected_severity):
    """심각도 분류 테스트: 다단계 임계값 기반 분류"""
    thresholds = {"low": 50, "medium": 70, "high": 85, "critical": 95}
    result = detector.classify_severity(value, thresholds)
    assert result == expected_severity


# ============================================================
# 연습 3 풀이: 패턴 탐지 조합 테스트
# ============================================================

@pytest.mark.parametrize("window_size", [2, 3])
@pytest.mark.parametrize("data", [
    pytest.param([10, 20, 30, 40, 50], id="상승추세"),
    pytest.param([50, 50, 50, 50, 50], id="안정추세"),
])
def test_pattern_combinations(data, window_size):
    """패턴 탐지 조합 테스트 (데카르트 곱): 2가지 패턴 x 2가지 윈도우 = 4 테스트"""
    result = detector.detect_pattern(data, window_size)

    # 기본 구조 확인
    assert "trend" in result
    assert "moving_averages" in result
    assert "max_deviation" in result
    assert "is_anomaly" in result

    # 이동 평균 개수 확인
    expected_count = len(data) - window_size + 1
    assert len(result["moving_averages"]) == expected_count

    # 안정 데이터는 항상 안정 추세
    if all(v == data[0] for v in data):
        assert result["trend"] == "stable"
