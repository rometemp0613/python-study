"""
솔루션 28: 나쁜 테스트를 좋은 테스트로 리팩토링하기

FIRST 원칙과 AAA 패턴을 적용한 리팩토링 결과입니다.

실행 방법:
    pytest exercises/solution_28.py -v
"""

import pytest
from datetime import date
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_maintenance_scheduler import MaintenanceScheduler


# =============================================================================
# 리팩토링 결과 1: 독립적인 테스트
# =============================================================================
# 각 테스트가 자체적으로 데이터를 준비하여 독립적으로 동작

class TestRefactor_독립성:
    """리팩토링 완료: 각 테스트가 독립적으로 동작"""

    def test_독립적_스케줄_추가(self):
        """유지보수를 스케줄링하면 조회할 수 있다."""
        # Arrange: 자체적으로 스케줄러 생성
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))

        # Act
        scheduler.schedule_maintenance("pump-001", "high")

        # Assert
        result = scheduler.get_next_maintenance("pump-001")
        assert result is not None
        assert result["equipment_id"] == "pump-001"

    def test_독립적_스케줄_조회(self):
        """스케줄이 없는 장비를 조회하면 None을 반환한다."""
        # Arrange: 자체적으로 스케줄러 생성 (위 테스트에 의존하지 않음)
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))

        # Act
        result = scheduler.get_next_maintenance("nonexistent")

        # Assert
        assert result is None


# =============================================================================
# 리팩토링 결과 2: 한 테스트 = 한 개념
# =============================================================================

class TestRefactor_개념분리:
    """리팩토링 완료: 각 테스트가 하나의 개념만 검증"""

    def test_유지보수_추가_검증(self):
        """유지보수를 추가하면 ID가 반환된다."""
        # Arrange
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))

        # Act
        maintenance_id = scheduler.schedule_maintenance("pump-001", "high")

        # Assert
        assert maintenance_id is not None
        assert len(maintenance_id) > 0

    def test_유지보수_조회_검증(self):
        """추가된 유지보수를 장비 ID로 조회할 수 있다."""
        # Arrange
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        scheduler.schedule_maintenance("pump-001", "high")

        # Act
        result = scheduler.get_next_maintenance("pump-001")

        # Assert
        assert result is not None
        assert result["equipment_id"] == "pump-001"
        assert result["priority"] == "high"

    def test_유지보수_취소_검증(self):
        """유지보수를 취소하면 더 이상 조회되지 않는다."""
        # Arrange
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        scheduler.schedule_maintenance("pump-001", "high")
        maintenance = scheduler.get_next_maintenance("pump-001")

        # Act
        success = scheduler.cancel_maintenance(maintenance["id"])

        # Assert
        assert success is True
        assert scheduler.get_next_maintenance("pump-001") is None


# =============================================================================
# 리팩토링 결과 3: AAA 패턴 적용
# =============================================================================

class TestRefactor_AAA:
    """리팩토링 완료: AAA 패턴으로 구조화"""

    def test_기한초과_유지보수_조회(self):
        """과거 날짜로 스케줄된 유지보수가 기한 초과 목록에 나온다."""
        # Arrange: 스케줄러를 생성하고 과거 날짜로 유지보수 등록
        today = date(2024, 6, 1)
        scheduler = MaintenanceScheduler(today=today)
        past_date = date(2024, 5, 1)
        scheduler.schedule_maintenance(
            "pump-001", "high", scheduled_date=past_date
        )

        # Act: 기한 초과 유지보수 조회
        overdue = scheduler.get_overdue_maintenances()

        # Assert: 결과 검증
        assert len(overdue) == 1
        assert overdue[0]["equipment_id"] == "pump-001"
        assert overdue[0]["priority"] == "high"

    def test_미래_유지보수는_기한초과_아님(self):
        """미래 날짜로 스케줄된 유지보수는 기한 초과에 포함되지 않는다."""
        # Arrange
        today = date(2024, 6, 1)
        scheduler = MaintenanceScheduler(today=today)
        future_date = date(2024, 7, 1)
        scheduler.schedule_maintenance(
            "pump-001", "high", scheduled_date=future_date
        )

        # Act
        overdue = scheduler.get_overdue_maintenances()

        # Assert
        assert len(overdue) == 0

    def test_기한초과_우선순위_정렬(self):
        """기한 초과 유지보수는 우선순위별로 정렬된다."""
        # Arrange
        today = date(2024, 6, 1)
        scheduler = MaintenanceScheduler(today=today)
        past_date = date(2024, 5, 1)
        scheduler.schedule_maintenance("pump-001", "low", scheduled_date=past_date)
        scheduler.schedule_maintenance("pump-002", "critical", scheduled_date=past_date)
        scheduler.schedule_maintenance("pump-003", "high", scheduled_date=past_date)

        # Act
        overdue = scheduler.get_overdue_maintenances()

        # Assert: critical → high → low 순서
        assert len(overdue) == 3
        assert overdue[0]["priority"] == "critical"
        assert overdue[1]["priority"] == "high"
        assert overdue[2]["priority"] == "low"
