"""
잘 설계된 테스트 예시

FIRST 원칙과 AAA 패턴을 따르는 테스트입니다.
각 테스트는 독립적이고, 하나의 개념만 검증하며,
동작(behavior)을 테스트합니다.

실행 방법:
    pytest test_good_design.py -v
"""

import pytest
from datetime import date, timedelta
from src_maintenance_scheduler import MaintenanceScheduler


# =============================================================================
# FIRST - Fast: 빠른 테스트
# =============================================================================

class TestScheduleMaintenance_빠른테스트:
    """빠르게 실행되는 테스트 (외부 의존성 없음)"""

    def test_유지보수_스케줄링(self):
        """유지보수를 스케줄링하면 조회할 수 있어야 한다."""
        # Arrange
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))

        # Act
        scheduler.schedule_maintenance("pump-001", "high")

        # Assert
        result = scheduler.get_next_maintenance("pump-001")
        assert result is not None
        assert result["equipment_id"] == "pump-001"


# =============================================================================
# FIRST - Isolated: 독립적인 테스트
# =============================================================================

class TestScheduleMaintenance_독립적:
    """각 테스트가 독립적으로 실행됩니다."""

    def test_스케줄_추가(self):
        """스케줄 추가 테스트 - 다른 테스트와 독립적"""
        # Arrange
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))

        # Act
        maintenance_id = scheduler.schedule_maintenance("pump-001", "high")

        # Assert
        assert maintenance_id is not None
        assert len(maintenance_id) > 0

    def test_스케줄_조회(self):
        """스케줄 조회 테스트 - 자체적으로 데이터를 준비"""
        # Arrange: 자체적으로 데이터 준비 (위 테스트에 의존하지 않음)
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        scheduler.schedule_maintenance("motor-002", "medium")

        # Act
        result = scheduler.get_next_maintenance("motor-002")

        # Assert
        assert result is not None
        assert result["equipment_id"] == "motor-002"


# =============================================================================
# FIRST - Repeatable: 반복 가능한 테스트
# =============================================================================

class TestScheduleMaintenance_반복가능:
    """환경에 관계없이 항상 같은 결과를 내는 테스트"""

    def test_고정_날짜_사용(self):
        """날짜를 고정하여 반복 가능성 확보"""
        # Arrange: 날짜를 주입하여 환경 독립적
        fixed_today = date(2024, 1, 15)
        scheduler = MaintenanceScheduler(today=fixed_today)

        # Act
        scheduler.schedule_maintenance("pump-001", "high")

        # Assert: 항상 같은 결과
        result = scheduler.get_next_maintenance("pump-001")
        expected_date = date(2024, 1, 22)  # 7일 후
        assert result["scheduled_date"] == expected_date

    def test_기한_초과_판정_고정_날짜(self):
        """기한 초과 판정도 날짜를 고정하여 테스트"""
        # Arrange
        fixed_today = date(2024, 6, 1)
        scheduler = MaintenanceScheduler(today=fixed_today)
        # 과거 날짜로 스케줄 (기한 초과)
        past_date = date(2024, 5, 1)
        scheduler.schedule_maintenance("pump-001", "high", scheduled_date=past_date)

        # Act
        overdue = scheduler.get_overdue_maintenances()

        # Assert
        assert len(overdue) == 1
        assert overdue[0]["equipment_id"] == "pump-001"


# =============================================================================
# FIRST - Self-validating: 자체 검증
# =============================================================================

class TestScheduleMaintenance_자체검증:
    """assert를 사용하여 자동으로 성공/실패를 판단"""

    def test_우선순위별_스케줄_날짜(self):
        """우선순위에 따라 적절한 날짜에 스케줄되는지 검증"""
        # Arrange
        today = date(2024, 1, 15)
        scheduler = MaintenanceScheduler(today=today)

        # Act
        scheduler.schedule_maintenance("pump-001", "critical")

        # Assert: 자동 검증 (print 대신 assert)
        result = scheduler.get_next_maintenance("pump-001")
        assert result["scheduled_date"] == date(2024, 1, 16)  # 1일 후


# =============================================================================
# AAA 패턴 (Arrange-Act-Assert)
# =============================================================================

class TestScheduleMaintenance_AAA:
    """AAA 패턴을 명확하게 따르는 테스트"""

    def test_유지보수_취소(self):
        """유지보수를 취소하면 더 이상 조회되지 않아야 한다."""
        # Arrange: 유지보수를 스케줄링
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        scheduler.schedule_maintenance("pump-001", "high")
        maintenance = scheduler.get_next_maintenance("pump-001")
        maintenance_id = maintenance["id"]

        # Act: 유지보수를 취소
        result = scheduler.cancel_maintenance(maintenance_id)

        # Assert: 취소 성공하고 더 이상 조회되지 않음
        assert result is True
        assert scheduler.get_next_maintenance("pump-001") is None

    def test_존재하지_않는_유지보수_취소_실패(self):
        """존재하지 않는 유지보수를 취소하면 False를 반환해야 한다."""
        # Arrange
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))

        # Act
        result = scheduler.cancel_maintenance("nonexistent-id")

        # Assert
        assert result is False


# =============================================================================
# 한 테스트에 하나의 개념
# =============================================================================

class TestScheduleMaintenance_하나의개념:
    """각 테스트가 하나의 개념만 검증"""

    def test_유효하지_않은_우선순위_거부(self):
        """유효하지 않은 우선순위는 ValueError를 발생시켜야 한다."""
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        with pytest.raises(ValueError, match="유효하지 않은 우선순위"):
            scheduler.schedule_maintenance("pump-001", "invalid")

    def test_스케줄_없는_장비_조회시_None(self):
        """스케줄이 없는 장비를 조회하면 None을 반환해야 한다."""
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        result = scheduler.get_next_maintenance("nonexistent-equipment")
        assert result is None

    def test_기한_초과_우선순위_정렬(self):
        """기한 초과 유지보수는 우선순위 순서로 정렬되어야 한다."""
        # Arrange
        today = date(2024, 6, 1)
        scheduler = MaintenanceScheduler(today=today)
        past = date(2024, 5, 1)
        scheduler.schedule_maintenance("pump-001", "low", scheduled_date=past)
        scheduler.schedule_maintenance("pump-002", "critical", scheduled_date=past)

        # Act
        overdue = scheduler.get_overdue_maintenances()

        # Assert: critical이 low보다 먼저
        assert len(overdue) == 2
        assert overdue[0]["priority"] == "critical"
        assert overdue[1]["priority"] == "low"


# =============================================================================
# 동작(Behavior) 테스트
# =============================================================================

class TestScheduleMaintenance_동작테스트:
    """내부 구현이 아닌 공개 인터페이스(동작)를 테스트"""

    def test_유지보수_완료_처리(self):
        """유지보수를 완료하면 더 이상 예정 목록에 나타나지 않아야 한다."""
        # Arrange
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        scheduler.schedule_maintenance("pump-001", "high")
        maintenance = scheduler.get_next_maintenance("pump-001")

        # Act: 공개 메서드로 완료 처리
        scheduler.complete_maintenance(maintenance["id"])

        # Assert: 공개 메서드로 결과 확인
        result = scheduler.get_next_maintenance("pump-001")
        assert result is None  # 더 이상 예정 없음

    def test_여러_장비_독립_관리(self):
        """각 장비의 유지보수는 독립적으로 관리되어야 한다."""
        # Arrange
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        scheduler.schedule_maintenance("pump-001", "high")
        scheduler.schedule_maintenance("motor-002", "low")

        # Act & Assert: 각 장비별 독립 조회
        pump_result = scheduler.get_next_maintenance("pump-001")
        motor_result = scheduler.get_next_maintenance("motor-002")

        assert pump_result["equipment_id"] == "pump-001"
        assert motor_result["equipment_id"] == "motor-002"
        assert pump_result["priority"] == "high"
        assert motor_result["priority"] == "low"
