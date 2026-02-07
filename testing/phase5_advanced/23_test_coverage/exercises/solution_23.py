"""
연습문제 23 정답: 테스트 커버리지

놓친 분기를 모두 커버하는 테스트.
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
# 연습 1 정답: classify_status의 놓친 분기
# =============================================================================

class TestClassifyStatusMissingBranches:
    """classify_status()의 놓친 분기 테스트"""

    def test_low_temperature(self):
        """저온 (temp < 0) → danger_score +1 → caution"""
        result = classify_status(-10, 5, 5)
        # danger_score: 저온(+1) = 1 → caution
        assert result == "caution"

    def test_low_pressure(self):
        """저압 (pressure < 1) → danger_score +1 → caution"""
        result = classify_status(50, 5, 0.5)
        # danger_score: 저압(+1) = 1 → caution
        assert result == "caution"

    def test_critical_status(self):
        """danger_score >= 7 → critical"""
        # temp>120(+3) + vib>20(+3) + pres>10(+1) = 7 → critical
        result = classify_status(130, 25, 11)
        assert result == "critical"

    def test_extreme_all_sensors(self):
        """모든 센서가 극단적 → critical (score=9)"""
        # temp>120(+3) + vib>20(+3) + pres>15(+3) = 9 → critical
        result = classify_status(130, 25, 18)
        assert result == "critical"


# =============================================================================
# 연습 2 정답: should_shutdown의 놓친 분기
# =============================================================================

class TestShouldShutdownMissingBranches:
    """should_shutdown()의 놓친 분기 테스트"""

    def test_extreme_pressure_shutdown(self):
        """극고압 (pressure > 20) → 즉시 정지"""
        history = [{"temp": 50, "vibration": 5, "pressure": 25}]
        result, reason = should_shutdown(history)
        assert result is True
        assert "극고압" in reason

    def test_insufficient_history(self):
        """이력 2개 → 추세 분석 불가"""
        history = [
            {"temp": 50, "vibration": 5, "pressure": 5},
            {"temp": 55, "vibration": 6, "pressure": 5},
        ]
        result, reason = should_shutdown(history)
        assert result is False
        assert "이력 부족" in reason

    def test_consecutive_danger_readings(self):
        """3회 연속 위험 범위 → 정지"""
        history = [
            {"temp": 110, "vibration": 5, "pressure": 5},  # temp > 100
            {"temp": 105, "vibration": 5, "pressure": 5},  # temp > 100
            {"temp": 115, "vibration": 5, "pressure": 5},  # temp > 100
        ]
        result, reason = should_shutdown(history)
        assert result is True
        assert "3회 연속" in reason

    def test_temperature_spike(self):
        """온도 급상승 (직전 대비 50% 이상) → 정지"""
        history = [
            {"temp": 40, "vibration": 5, "pressure": 5},
            {"temp": 50, "vibration": 5, "pressure": 5},
            {"temp": 55, "vibration": 5, "pressure": 5},
            {"temp": 90, "vibration": 5, "pressure": 5},  # 55→90: 63% 증가
        ]
        result, reason = should_shutdown(history)
        assert result is True
        assert "급상승" in reason

    def test_vibration_increasing_trend(self):
        """진동 5회 연속 증가 + 15mm/s 초과 → 정지"""
        history = [
            {"temp": 50, "vibration": 10, "pressure": 5},
            {"temp": 50, "vibration": 11, "pressure": 5},
            {"temp": 50, "vibration": 12, "pressure": 5},
            {"temp": 50, "vibration": 14, "pressure": 5},
            {"temp": 50, "vibration": 16, "pressure": 5},  # 5회 연속 증가, 16 > 15
        ]
        result, reason = should_shutdown(history)
        assert result is True
        assert "5회 연속 증가" in reason


# =============================================================================
# 연습 3 정답: calculate_health_score의 놓친 분기
# =============================================================================

class TestHealthScoreMissingBranches:
    """calculate_health_score()의 놓친 분기 테스트"""

    def test_low_temperature_score(self):
        """저온 (temp < 20) → 점수 감소"""
        score = calculate_health_score(10, 5, 5)
        # temp: max(0, 100 - (20-10)*5) = max(0, 50) = 50
        # 나머지: 100
        # 평균: (50+100+100)/3 = 83.3
        assert score < 100.0
        assert score == pytest.approx(83.3, abs=0.1)

    def test_low_pressure_score(self):
        """저압 (pressure < 1) → 점수 감소"""
        score = calculate_health_score(50, 5, 0.5)
        # pressure: max(0, 100 - (1-0.5)*20) = max(0, 90) = 90
        # 나머지: 100
        # 평균: (100+100+90)/3 = 96.7
        assert score < 100.0
        assert score == pytest.approx(96.7, abs=0.1)

    def test_custom_weights(self):
        """사용자 정의 가중치: 온도가 높을 때 가중치 차이 검증"""
        # 온도만 높은 상황
        temp, vib, pres = 100, 5, 5

        # 온도 가중치가 높으면 점수가 더 낮아진다
        score_temp_heavy = calculate_health_score(
            temp, vib, pres,
            weights={"temp": 5.0, "vibration": 1.0, "pressure": 1.0}
        )
        score_equal = calculate_health_score(
            temp, vib, pres,
            weights={"temp": 1.0, "vibration": 1.0, "pressure": 1.0}
        )

        # 온도 점수가 100 미만이므로, 온도 가중치가 높을수록 총점이 낮다
        assert score_temp_heavy < score_equal
