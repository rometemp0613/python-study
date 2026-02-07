"""
커버리지 완전판: 모든 분기를 커버하는 테스트.

이 파일은 src_equipment_classifier.py의 모든 분기를 테스트한다.
test_coverage_demo.py에서 놓친 분기를 포함하여 높은 커버리지를 달성한다.

실행 방법:
    pytest test_coverage_complete.py --cov=src_equipment_classifier --cov-branch --cov-report=term-missing -v
"""

import pytest
from src_equipment_classifier import (
    classify_status,
    get_maintenance_priority,
    should_shutdown,
    calculate_health_score,
)


# =============================================================================
# classify_status: 모든 분기 커버
# =============================================================================

class TestClassifyStatusComplete:
    """설비 상태 분류 - 전체 분기 커버"""

    # --- 정상 범위 ---
    def test_all_normal(self):
        """모든 값이 정상 → normal (danger_score=0)"""
        assert classify_status(50, 5, 5) == "normal"

    # --- 온도 분기 ---
    def test_temp_extreme_high(self):
        """극고온 (>120) → score +3"""
        # temp=130, vib=5, pres=5 → score=3 → warning
        assert classify_status(130, 5, 5) == "warning"

    def test_temp_high(self):
        """고온 (100~120) → score +2"""
        assert classify_status(110, 5, 5) == "caution"

    def test_temp_caution(self):
        """주의 온도 (80~100) → score +1"""
        assert classify_status(90, 5, 5) == "caution"

    def test_temp_low(self):
        """저온 (<0) → score +1"""
        assert classify_status(-10, 5, 5) == "caution"

    # --- 진동 분기 ---
    def test_vibration_extreme(self):
        """극심한 진동 (>20) → score +3"""
        assert classify_status(50, 25, 5) == "warning"

    def test_vibration_high(self):
        """높은 진동 (15~20) → score +2"""
        assert classify_status(50, 17, 5) == "caution"

    def test_vibration_caution(self):
        """주의 진동 (10~15) → score +1"""
        assert classify_status(50, 12, 5) == "caution"

    # --- 압력 분기 ---
    def test_pressure_extreme(self):
        """극고압 (>15) → score +3"""
        assert classify_status(50, 5, 18) == "warning"

    def test_pressure_high(self):
        """고압 (12~15) → score +2"""
        assert classify_status(50, 5, 13) == "caution"

    def test_pressure_caution(self):
        """주의 압력 (10~12) → score +1"""
        assert classify_status(50, 5, 11) == "caution"

    def test_pressure_low(self):
        """저압 (<1) → score +1"""
        assert classify_status(50, 5, 0.5) == "caution"

    # --- 복합 상태 ---
    def test_danger_status(self):
        """danger (score 5~6): 여러 지표가 동시에 높음"""
        # temp>120(+3) + vib>15(+2) → score=5 → danger
        assert classify_status(130, 17, 5) == "danger"

    def test_critical_status(self):
        """critical (score >= 7): 모든 지표가 위험"""
        # temp>120(+3) + vib>20(+3) + pres>10(+1) → score=7 → critical
        assert classify_status(130, 25, 11) == "critical"

    def test_warning_combined(self):
        """warning (score 3~4): 여러 지표 주의"""
        # temp>80(+1) + vib>10(+1) + pres>10(+1) → score=3 → warning
        assert classify_status(85, 12, 11) == "warning"

    # --- 유효성 검사 ---
    def test_invalid_temp_high(self):
        """온도 상한 초과"""
        with pytest.raises(ValueError, match="비정상 온도"):
            classify_status(501, 5, 5)

    def test_invalid_temp_low(self):
        """온도 하한 미만"""
        with pytest.raises(ValueError, match="비정상 온도"):
            classify_status(-51, 5, 5)

    def test_invalid_vibration(self):
        """음수 진동"""
        with pytest.raises(ValueError, match="진동은 음수"):
            classify_status(50, -1, 5)

    def test_invalid_pressure(self):
        """음수 압력"""
        with pytest.raises(ValueError, match="압력은 음수"):
            classify_status(50, 5, -1)


# =============================================================================
# get_maintenance_priority: 모든 상태 커버
# =============================================================================

class TestGetMaintenancePriorityComplete:
    """유지보수 우선순위 - 모든 상태 커버"""

    @pytest.mark.parametrize("status,expected_priority,expected_max_hours", [
        ("critical", 1, 1),
        ("danger", 2, 4),
        ("warning", 3, 24),
        ("caution", 4, 72),
        ("normal", 5, 168),
    ])
    def test_all_statuses(self, status, expected_priority, expected_max_hours):
        """모든 상태에 대한 우선순위와 대응 시간 검증"""
        result = get_maintenance_priority(status)
        assert result["priority"] == expected_priority
        assert result["max_response_hours"] == expected_max_hours
        assert "action" in result

    def test_unknown_status(self):
        """알 수 없는 상태"""
        with pytest.raises(ValueError, match="알 수 없는 상태"):
            get_maintenance_priority("exploded")


# =============================================================================
# should_shutdown: 모든 분기 커버
# =============================================================================

class TestShouldShutdownComplete:
    """비상 정지 판단 - 모든 분기 커버"""

    def test_empty_history(self):
        """빈 이력"""
        result, reason = should_shutdown([])
        assert result is False
        assert "이력 없음" in reason

    def test_extreme_temp(self):
        """극고온 (>150)"""
        history = [{"temp": 200, "vibration": 5, "pressure": 5}]
        result, reason = should_shutdown(history)
        assert result is True
        assert "극고온" in reason

    def test_extreme_vibration(self):
        """극심한 진동 (>30)"""
        history = [{"temp": 50, "vibration": 35, "pressure": 5}]
        result, reason = should_shutdown(history)
        assert result is True
        assert "진동" in reason

    def test_extreme_pressure(self):
        """극고압 (>20)"""
        history = [{"temp": 50, "vibration": 5, "pressure": 25}]
        result, reason = should_shutdown(history)
        assert result is True
        assert "극고압" in reason

    def test_insufficient_history(self):
        """이력이 3개 미만 → 추세 분석 불가"""
        history = [
            {"temp": 50, "vibration": 5, "pressure": 5},
            {"temp": 55, "vibration": 6, "pressure": 5},
        ]
        result, reason = should_shutdown(history)
        assert result is False
        assert "이력 부족" in reason

    def test_consecutive_danger(self):
        """3회 연속 위험 범위"""
        history = [
            {"temp": 110, "vibration": 5, "pressure": 5},
            {"temp": 115, "vibration": 5, "pressure": 5},
            {"temp": 120, "vibration": 5, "pressure": 5},
        ]
        result, reason = should_shutdown(history)
        assert result is True
        assert "3회 연속" in reason

    def test_temp_spike(self):
        """온도 급상승 (50% 이상 증가)"""
        history = [
            {"temp": 40, "vibration": 5, "pressure": 5},
            {"temp": 50, "vibration": 5, "pressure": 5},
            {"temp": 50, "vibration": 5, "pressure": 5},
            {"temp": 80, "vibration": 5, "pressure": 5},  # 50→80: 60% 증가
        ]
        result, reason = should_shutdown(history)
        assert result is True
        assert "급상승" in reason

    def test_vibration_trend_increasing(self):
        """진동 5회 연속 증가 (15mm/s 초과)"""
        history = [
            {"temp": 50, "vibration": 10, "pressure": 5},
            {"temp": 50, "vibration": 11, "pressure": 5},
            {"temp": 50, "vibration": 13, "pressure": 5},
            {"temp": 50, "vibration": 14, "pressure": 5},
            {"temp": 50, "vibration": 16, "pressure": 5},
        ]
        result, reason = should_shutdown(history)
        assert result is True
        assert "5회 연속 증가" in reason

    def test_vibration_trend_not_exceeding_threshold(self):
        """진동 증가하지만 15mm/s 이하 → 정지 불필요"""
        history = [
            {"temp": 50, "vibration": 1, "pressure": 5},
            {"temp": 50, "vibration": 2, "pressure": 5},
            {"temp": 50, "vibration": 3, "pressure": 5},
            {"temp": 50, "vibration": 4, "pressure": 5},
            {"temp": 50, "vibration": 5, "pressure": 5},
        ]
        result, reason = should_shutdown(history)
        assert result is False

    def test_normal_long_history(self):
        """긴 이력이지만 정상"""
        history = [
            {"temp": 50 + i, "vibration": 5, "pressure": 5}
            for i in range(10)
        ]
        result, reason = should_shutdown(history)
        assert result is False
        assert "정상" in reason


# =============================================================================
# calculate_health_score: 모든 분기 커버
# =============================================================================

class TestCalculateHealthScoreComplete:
    """건강 점수 계산 - 모든 분기 커버"""

    def test_all_normal(self):
        """모든 값이 정상 범위 → 100점"""
        score = calculate_health_score(50, 5, 5)
        assert score == 100.0

    def test_default_weights(self):
        """기본 가중치(동일) 사용"""
        score = calculate_health_score(50, 5, 5, weights=None)
        assert score == 100.0

    def test_custom_weights(self):
        """사용자 정의 가중치"""
        # 온도에 더 높은 가중치
        score = calculate_health_score(
            50, 5, 5,
            weights={"temp": 3.0, "vibration": 1.0, "pressure": 1.0}
        )
        assert score == 100.0  # 모두 정상이면 가중치 무관

    def test_high_temp_reduces_score(self):
        """높은 온도 → 점수 감소"""
        score = calculate_health_score(100, 5, 5)
        assert score < 100.0

    def test_low_temp_reduces_score(self):
        """낮은 온도 → 점수 감소"""
        score = calculate_health_score(10, 5, 5)
        assert score < 100.0

    def test_high_vibration_reduces_score(self):
        """높은 진동 → 점수 감소"""
        score = calculate_health_score(50, 15, 5)
        assert score < 100.0

    def test_high_pressure_reduces_score(self):
        """높은 압력 → 점수 감소"""
        score = calculate_health_score(50, 5, 15)
        assert score < 100.0

    def test_low_pressure_reduces_score(self):
        """낮은 압력 → 점수 감소"""
        score = calculate_health_score(50, 5, 0.5)
        assert score < 100.0

    def test_zero_weights(self):
        """가중치 합이 0 → 0점"""
        score = calculate_health_score(
            50, 5, 5,
            weights={"temp": 0, "vibration": 0, "pressure": 0}
        )
        assert score == 0.0

    def test_extreme_values_floor_at_zero(self):
        """극단적 값은 0점으로 바닥"""
        # 매우 높은 온도 → max(0, ...) 보장
        score = calculate_health_score(200, 5, 5)
        assert score >= 0.0

    def test_score_range(self):
        """건강 점수는 0~100 범위"""
        test_cases = [
            (50, 5, 5),      # 정상
            (130, 25, 18),    # 극단
            (-10, 0, 0.5),   # 저온/저압
        ]
        for temp, vib, pres in test_cases:
            score = calculate_health_score(temp, vib, pres)
            assert 0 <= score <= 100, f"점수 범위 초과: {score}"
