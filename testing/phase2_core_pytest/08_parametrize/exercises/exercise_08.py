"""
연습 문제 08: Parametrize - 매개변수화 테스트

아래 TODO를 완성하여 parametrize 테스트를 작성하세요.
pytest.skip()을 제거하고 코드를 구현하세요.
"""

import pytest
import sys
import os

# 상위 디렉토리의 모듈을 import하기 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_anomaly_detector import AnomalyDetector, Severity


detector = AnomalyDetector()


# ============================================================
# 연습 1: 경계값 테스트
# ============================================================
# detect(value, threshold) 메서드를 경계값으로 테스트하세요.
# 경계값: threshold-1, threshold, threshold+1

# TODO: @pytest.mark.parametrize를 사용하여
# 임계값 50.0 기준 경계값 테스트를 작성하세요.
# (49.0, False), (50.0, False), (51.0, True) 세 가지 케이스
def test_boundary_values():
    """경계값 테스트: 임계값 전후의 동작 확인"""
    pytest.skip("TODO: parametrize로 경계값 테스트를 작성하세요")


# ============================================================
# 연습 2: 심각도 분류 테스트
# ============================================================
# classify_severity를 다양한 값으로 테스트하세요.
# thresholds = {"low": 50, "medium": 70, "high": 85, "critical": 95}

# TODO: pytest.param을 사용하여 테스트 ID를 지정하세요.
# 최소 5가지 케이스: NORMAL, LOW, MEDIUM, HIGH, CRITICAL
def test_severity_classification():
    """심각도 분류 테스트"""
    pytest.skip("TODO: pytest.param으로 심각도 분류 테스트를 작성하세요")


# ============================================================
# 연습 3: 패턴 탐지 조합 테스트
# ============================================================
# 여러 데이터 패턴과 window_size를 중첩 parametrize로 테스트하세요.

# TODO: 두 개의 @pytest.mark.parametrize를 중첩하여
# 데이터 패턴 x 윈도우 크기 조합 테스트를 작성하세요.
# 데이터: [10,20,30,40,50] (상승), [50,50,50,50,50] (안정)
# 윈도우: 2, 3
def test_pattern_combinations():
    """패턴 탐지 조합 테스트 (데카르트 곱)"""
    pytest.skip("TODO: 중첩 parametrize로 조합 테스트를 작성하세요")
