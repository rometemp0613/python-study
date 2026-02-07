"""
나쁜 설계의 테스트 예시 (안티패턴 모음)

이 파일의 테스트는 모두 통과(PASS)하지만,
테스트 설계 원칙에 위반되는 부분이 있습니다.
각 테스트에 무엇이 잘못되었는지 주석으로 설명합니다.

비교 학습용으로, test_good_design.py와 함께 보세요.

실행 방법:
    pytest test_bad_design.py -v
"""

import pytest
from datetime import date, timedelta
from src_maintenance_scheduler import MaintenanceScheduler


# =============================================================================
# 안티패턴 1: 테스트 간 의존성 (Isolated 위반)
# =============================================================================
# 문제점: 모듈 수준 변수를 공유하여 테스트 간 의존성이 생김
# 이 경우 테스트 실행 순서에 따라 결과가 달라질 수 있음
# (다행히 이 예시에서는 순서대로 실행되어 통과하지만,
#  pytest-randomly 플러그인 사용 시 실패할 수 있음)

_shared_scheduler = MaintenanceScheduler(today=date(2024, 1, 15))


class TestBad_테스트간의존성:
    """안티패턴: 테스트 간 상태 공유 (PASS하지만 설계가 나쁨)"""

    def test_step1_스케줄_추가(self):
        """문제: 공유 상태에 데이터를 추가"""
        # 문제점: 모듈 수준 변수를 사용하여 상태를 공유
        _shared_scheduler.schedule_maintenance("pump-001", "high")
        result = _shared_scheduler.get_next_maintenance("pump-001")
        assert result is not None

    def test_step2_스케줄_확인(self):
        """문제: 위 테스트에서 추가한 데이터에 의존"""
        # 문제점: test_step1이 실행되지 않으면 실패할 수 있음
        result = _shared_scheduler.get_next_maintenance("pump-001")
        assert result is not None  # test_step1에 의존


# =============================================================================
# 안티패턴 2: 여러 개념을 한 테스트에 (한 테스트 = 한 개념 위반)
# =============================================================================

class TestBad_여러개념혼합:
    """안티패턴: 한 테스트에서 여러 기능을 검증"""

    def test_스케줄러_모든_기능을_한번에(self):
        """
        문제: 추가, 조회, 취소, 완료를 모두 한 테스트에서 검증
        → 실패 시 어떤 기능에 문제가 있는지 파악하기 어려움
        """
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))

        # 추가 검증
        mid = scheduler.schedule_maintenance("pump-001", "high")
        assert mid is not None

        # 조회 검증
        result = scheduler.get_next_maintenance("pump-001")
        assert result is not None
        assert result["equipment_id"] == "pump-001"
        assert result["priority"] == "high"

        # 취소 검증
        success = scheduler.cancel_maintenance(result["id"])
        assert success is True
        assert scheduler.get_next_maintenance("pump-001") is None

        # 다시 추가하고 완료 검증
        mid2 = scheduler.schedule_maintenance("pump-001", "low")
        result2 = scheduler.get_next_maintenance("pump-001")
        scheduler.complete_maintenance(result2["id"])
        assert scheduler.get_next_maintenance("pump-001") is None


# =============================================================================
# 안티패턴 3: 구현 세부사항 테스트 (동작 테스트 원칙 위반)
# =============================================================================

class TestBad_구현세부사항:
    """안티패턴: 내부 구현에 의존하는 테스트"""

    def test_내부_리스트_직접_확인(self):
        """
        문제: _schedules (private) 속성에 직접 접근
        → 내부 구현이 변경되면 테스트가 깨짐
        """
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        scheduler.schedule_maintenance("pump-001", "high")

        # 문제점: 내부 구현(private 속성)에 직접 접근
        assert len(scheduler._schedules) == 1
        assert scheduler._schedules[0]["equipment_id"] == "pump-001"
        assert scheduler._schedules[0]["status"] == "scheduled"

    def test_내부_today_확인(self):
        """
        문제: 내부 _today 속성에 직접 접근
        """
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))

        # 문제점: private 속성에 접근하여 내부 상태 확인
        assert scheduler._today == date(2024, 1, 15)


# =============================================================================
# 안티패턴 4: 매직 넘버와 불명확한 의도
# =============================================================================

class TestBad_매직넘버:
    """안티패턴: 의미 없는 숫자와 불명확한 테스트 이름"""

    def test_something(self):
        """
        문제: 테스트 이름이 불명확 → 무엇을 테스트하는지 알 수 없음
        """
        s = MaintenanceScheduler(today=date(2024, 1, 15))
        s.schedule_maintenance("p1", "high")
        r = s.get_next_maintenance("p1")
        # 문제점: 매직 넘버, 약어, 의미 불명확
        assert r["scheduled_date"] == date(2024, 1, 22)

    def test_data(self):
        """
        문제: 테스트 이름에서 무엇을 검증하는지 알 수 없음
        """
        s = MaintenanceScheduler(today=date(2024, 1, 15))
        s.schedule_maintenance("x", "low", scheduled_date=date(2024, 1, 1))
        o = s.get_overdue_maintenances()
        assert len(o) == 1


# =============================================================================
# 안티패턴 5: 검증 없는 테스트 (Self-validating 위반)
# =============================================================================

class TestBad_검증없음:
    """안티패턴: assert가 없거나 의미 없는 검증"""

    def test_동작_확인(self):
        """
        문제: assert가 없음 → 에러 없이 실행만 되면 통과
        → 실제로 올바른 동작인지 검증하지 않음
        """
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        scheduler.schedule_maintenance("pump-001", "high")
        scheduler.get_next_maintenance("pump-001")
        # 문제점: assert 없음!

    def test_의미없는_검증(self):
        """
        문제: 항상 통과하는 의미 없는 assert
        """
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        scheduler.schedule_maintenance("pump-001", "high")
        result = scheduler.get_next_maintenance("pump-001")
        # 문제점: 너무 약한 검증
        assert result is not None  # 아무 딕셔너리나 반환해도 통과


# =============================================================================
# 안티패턴 6: AAA 패턴 위반 (구조 불명확)
# =============================================================================

class TestBad_구조불명확:
    """안티패턴: Arrange-Act-Assert 구분이 없는 테스트"""

    def test_뒤섞인_구조(self):
        """
        문제: 설정, 실행, 검증이 뒤섞여 있어 가독성이 떨어짐
        """
        scheduler = MaintenanceScheduler(today=date(2024, 1, 15))
        scheduler.schedule_maintenance("pump-001", "high")
        assert scheduler.get_next_maintenance("pump-001") is not None  # 검증과 실행 혼합
        scheduler.schedule_maintenance("motor-002", "low")             # 다시 설정
        assert scheduler.get_next_maintenance("motor-002") is not None  # 다시 검증
        mid = scheduler.get_next_maintenance("pump-001")["id"]
        scheduler.cancel_maintenance(mid)                               # 또 실행
        assert scheduler.get_next_maintenance("pump-001") is None      # 또 검증
