"""
연습문제 23: 테스트 커버리지

이 연습에서는 커버리지 갭을 분석하고, 놓친 분기를 커버하는 테스트를 작성한다.
TODO 부분을 채워서 테스트를 완성하라.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_equipment_classifier import (
    classify_status,
    get_maintenance_priority,
    should_shutdown,
    calculate_health_score,
)


# =============================================================================
# 연습 1: classify_status의 놓친 분기 커버
# =============================================================================

class TestClassifyStatusMissingBranches:
    """
    test_coverage_demo.py에서 놓친 분기를 테스트하라.

    놓친 분기:
    1. temp < 0 (저온 주의)
    2. pressure < 1 (저압 주의)
    3. danger_score >= 7 (critical)
    4. temp > 120 (극고온)
    5. vibration > 20 (극심한 진동)
    6. pressure > 15 (극고압)
    """

    def test_low_temperature(self):
        """
        TODO: 저온 (temp < 0)이 danger_score에 +1을 더하는지 확인하라.

        힌트: temp=-10, vibration=5, pressure=5로 테스트
        """
        pytest.skip("TODO: 저온 분기를 테스트하세요")

    def test_low_pressure(self):
        """
        TODO: 저압 (pressure < 1)이 danger_score에 +1을 더하는지 확인하라.

        힌트: temp=50, vibration=5, pressure=0.5로 테스트
        """
        pytest.skip("TODO: 저압 분기를 테스트하세요")

    def test_critical_status(self):
        """
        TODO: danger_score >= 7인 경우 "critical"이 반환되는지 확인하라.

        힌트: 세 가지 센서 모두 극단적인 값을 사용
        """
        pytest.skip("TODO: critical 상태를 테스트하세요")

    def test_extreme_all_sensors(self):
        """
        TODO: 모든 센서가 극단적인 값일 때의 상태를 확인하라.

        힌트: temp>120, vibration>20, pressure>15
        """
        pytest.skip("TODO: 극단적 복합 상태를 테스트하세요")


# =============================================================================
# 연습 2: should_shutdown의 놓친 분기 커버
# =============================================================================

class TestShouldShutdownMissingBranches:
    """
    should_shutdown()에서 놓친 분기를 테스트하라.

    놓친 분기:
    1. 극고압 (pressure > 20)
    2. 이력 부족 (len < 3)
    3. 3회 연속 위험 범위
    4. 온도 급상승
    5. 진동 5회 연속 증가
    """

    def test_extreme_pressure_shutdown(self):
        """
        TODO: 극고압(pressure > 20)으로 인한 비상 정지를 테스트하라.
        """
        pytest.skip("TODO: 극고압 비상 정지를 테스트하세요")

    def test_insufficient_history(self):
        """
        TODO: 이력이 3개 미만일 때 추세 분석 불가를 테스트하라.

        힌트: 2개의 정상 측정값을 가진 이력
        """
        pytest.skip("TODO: 이력 부족을 테스트하세요")

    def test_consecutive_danger_readings(self):
        """
        TODO: 3회 연속 위험 범위 측정으로 비상 정지를 테스트하라.

        힌트: 3개의 측정값 모두 temp > 100 또는 vibration > 20
        """
        pytest.skip("TODO: 3회 연속 위험 범위를 테스트하세요")

    def test_temperature_spike(self):
        """
        TODO: 온도 급상승(직전 대비 50% 이상)을 테스트하라.

        힌트: 최소 3개의 이력, 마지막 측정의 temp가 직전의 1.5배 이상
        """
        pytest.skip("TODO: 온도 급상승을 테스트하세요")

    def test_vibration_increasing_trend(self):
        """
        TODO: 진동 5회 연속 증가 + 15mm/s 초과를 테스트하라.

        힌트: 5개의 측정값, 진동이 연속 증가, 마지막이 15 초과
        """
        pytest.skip("TODO: 진동 증가 추세를 테스트하세요")


# =============================================================================
# 연습 3: calculate_health_score의 놓친 분기 커버
# =============================================================================

class TestHealthScoreMissingBranches:
    """
    calculate_health_score()의 놓친 분기를 테스트하라.
    """

    def test_low_temperature_score(self):
        """
        TODO: 저온(temp < 20)일 때 점수가 감소하는지 확인하라.
        """
        pytest.skip("TODO: 저온 건강 점수를 테스트하세요")

    def test_low_pressure_score(self):
        """
        TODO: 저압(pressure < 1)일 때 점수가 감소하는지 확인하라.
        """
        pytest.skip("TODO: 저압 건강 점수를 테스트하세요")

    def test_custom_weights(self):
        """
        TODO: 사용자 정의 가중치가 점수에 영향을 미치는지 확인하라.

        힌트: 온도만 높고 가중치를 다르게 설정
        """
        pytest.skip("TODO: 사용자 정의 가중치를 테스트하세요")
