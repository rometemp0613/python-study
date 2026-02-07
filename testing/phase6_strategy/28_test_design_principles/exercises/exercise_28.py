"""
연습 28: 나쁜 테스트를 좋은 테스트로 리팩토링하기

아래의 나쁜 테스트들을 FIRST 원칙과 AAA 패턴에 맞게 리팩토링하세요.

요구사항:
1. 각 테스트가 독립적(Isolated)이어야 합니다
2. 한 테스트에 하나의 개념만 검증하세요
3. AAA 패턴(Arrange-Act-Assert)을 따르세요
4. 구현이 아닌 동작(behavior)을 테스트하세요
5. 명확한 테스트 이름을 사용하세요

실행 방법:
    pytest exercises/exercise_28.py -v
"""

import pytest
from datetime import date
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_maintenance_scheduler import MaintenanceScheduler


# =============================================================================
# 리팩토링 대상 1: 테스트 간 의존성 제거
# =============================================================================
# 아래 테스트는 공유 상태에 의존합니다.
# 각 테스트가 독립적으로 동작하도록 리팩토링하세요.

class TestRefactor_독립성:
    """TODO: 각 테스트가 독립적으로 동작하도록 리팩토링하세요."""

    def test_독립적_스케줄_추가(self):
        pytest.skip("TODO: 독립적인 테스트로 리팩토링하세요. 자체적으로 scheduler를 생성하고 데이터를 추가하세요.")
        # 힌트: 각 테스트에서 새로운 MaintenanceScheduler를 생성하세요
        # scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        # scheduler.schedule_maintenance("pump-001", "high")
        # result = scheduler.get_next_maintenance("pump-001")
        # assert result is not None

    def test_독립적_스케줄_조회(self):
        pytest.skip("TODO: 독립적인 테스트로 리팩토링하세요. 위 테스트에 의존하지 않고 자체 데이터를 사용하세요.")


# =============================================================================
# 리팩토링 대상 2: 여러 개념 분리
# =============================================================================
# 아래 테스트는 한 테스트에서 추가, 조회, 취소를 모두 검증합니다.
# 각 개념별로 분리된 테스트로 리팩토링하세요.

class TestRefactor_개념분리:
    """TODO: 한 테스트에서 하나의 개념만 검증하도록 분리하세요."""

    def test_유지보수_추가_검증(self):
        pytest.skip("TODO: 유지보수 추가만 검증하는 테스트를 작성하세요")

    def test_유지보수_조회_검증(self):
        pytest.skip("TODO: 유지보수 조회만 검증하는 테스트를 작성하세요")

    def test_유지보수_취소_검증(self):
        pytest.skip("TODO: 유지보수 취소만 검증하는 테스트를 작성하세요")


# =============================================================================
# 리팩토링 대상 3: AAA 패턴 적용
# =============================================================================
# 아래 테스트는 Arrange-Act-Assert가 뒤섞여 있습니다.
# AAA 패턴으로 재구성하세요.

class TestRefactor_AAA:
    """TODO: AAA 패턴(Arrange-Act-Assert)으로 재구성하세요."""

    def test_기한초과_유지보수_조회(self):
        pytest.skip(
            "TODO: AAA 패턴으로 리팩토링하세요.\n"
            "Arrange: 스케줄러 생성, 과거 날짜로 유지보수 등록\n"
            "Act: get_overdue_maintenances() 호출\n"
            "Assert: 결과 검증"
        )
        # 힌트:
        # # Arrange
        # today = date(2024, 6, 1)
        # scheduler = MaintenanceScheduler(today=today)
        # past = date(2024, 5, 1)
        # scheduler.schedule_maintenance("pump-001", "high", scheduled_date=past)
        #
        # # Act
        # overdue = scheduler.get_overdue_maintenances()
        #
        # # Assert
        # assert len(overdue) == 1
        # assert overdue[0]["equipment_id"] == "pump-001"
