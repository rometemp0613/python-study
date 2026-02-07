"""
커버리지 데모: 의도적으로 일부 분기를 놓친 테스트.

이 파일은 커버리지 리포트에서 "어떤 부분이 테스트되지 않았는지"를
확인하는 학습 목적으로, 일부 분기를 의도적으로 테스트하지 않는다.

실행 방법:
    pytest test_coverage_demo.py --cov=src_equipment_classifier --cov-report=term-missing -v

놓치는 부분:
    - classify_status: 저온/저압 분기, critical 상태
    - should_shutdown: 극고압, 3회 연속 위험, 진동 추세 분기
    - calculate_health_score: 저온/저압 점수, weights=None 아닌 경우
"""

import pytest
from src_equipment_classifier import (
    classify_status,
    get_maintenance_priority,
    should_shutdown,
    calculate_health_score,
)


class TestClassifyStatusPartial:
    """설비 상태 분류 - 부분 커버리지"""

    def test_normal_status(self):
        """정상 범위의 센서 값 → normal"""
        result = classify_status(50, 5, 5)
        assert result == "normal"

    def test_high_temp_caution(self):
        """온도만 주의 범위 → caution"""
        result = classify_status(85, 5, 5)
        assert result == "caution"

    def test_high_temp_warning(self):
        """온도가 고온 범위 → warning과 관련"""
        result = classify_status(105, 5, 5)
        # danger_score = 2 (고온) → caution도 가능
        assert result in ("caution", "warning")

    def test_high_vibration(self):
        """진동이 높은 경우"""
        result = classify_status(50, 16, 5)
        assert result in ("caution", "warning")

    def test_high_pressure(self):
        """압력이 높은 경우"""
        result = classify_status(50, 5, 13)
        assert result in ("caution", "warning")

    def test_invalid_temp(self):
        """비정상 온도값은 ValueError"""
        with pytest.raises(ValueError, match="비정상 온도"):
            classify_status(600, 5, 5)

    def test_negative_vibration(self):
        """음수 진동은 ValueError"""
        with pytest.raises(ValueError, match="진동은 음수"):
            classify_status(50, -1, 5)

    # ※ 놓친 분기들:
    # - temp < 0 (저온 주의)
    # - pressure < 1 (저압 주의)
    # - danger_score >= 7 (critical)
    # - temp > 120 (극고온)
    # - vibration > 20 (극심한 진동)
    # - pressure > 15 (극고압)
    # - 음수 압력 검증


class TestGetMaintenancePriorityPartial:
    """유지보수 우선순위 - 부분 커버리지"""

    def test_normal_priority(self):
        """정상 상태의 우선순위"""
        result = get_maintenance_priority("normal")
        assert result["priority"] == 5

    def test_warning_priority(self):
        """경고 상태의 우선순위"""
        result = get_maintenance_priority("warning")
        assert result["priority"] == 3

    def test_unknown_status(self):
        """알 수 없는 상태는 ValueError"""
        with pytest.raises(ValueError, match="알 수 없는 상태"):
            get_maintenance_priority("unknown")

    # ※ 놓친 분기들:
    # - "critical" 상태
    # - "danger" 상태
    # - "caution" 상태


class TestShouldShutdownPartial:
    """비상 정지 판단 - 부분 커버리지"""

    def test_empty_history(self):
        """빈 이력 → 정지 불필요"""
        result, reason = should_shutdown([])
        assert result is False

    def test_extreme_temp(self):
        """극고온 → 즉시 정지"""
        history = [{"temp": 200, "vibration": 5, "pressure": 5}]
        result, reason = should_shutdown(history)
        assert result is True
        assert "극고온" in reason

    def test_extreme_vibration(self):
        """극심한 진동 → 즉시 정지"""
        history = [{"temp": 50, "vibration": 35, "pressure": 5}]
        result, reason = should_shutdown(history)
        assert result is True

    def test_normal_readings(self):
        """정상 범위 → 정지 불필요"""
        history = [
            {"temp": 50, "vibration": 5, "pressure": 5},
            {"temp": 52, "vibration": 6, "pressure": 5},
            {"temp": 51, "vibration": 5, "pressure": 5},
        ]
        result, reason = should_shutdown(history)
        assert result is False

    # ※ 놓친 분기들:
    # - 극고압 (pressure > 20)
    # - 이력 부족 (len < 3)
    # - 3회 연속 위험 범위
    # - 온도 급상승
    # - 진동 5회 연속 증가
