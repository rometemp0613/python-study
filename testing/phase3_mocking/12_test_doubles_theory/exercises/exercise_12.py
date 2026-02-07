"""
연습 문제 12: 테스트 더블 이론

각 테스트 더블 유형을 직접 구현하고 사용하여
예지보전 시스템의 컴포넌트를 테스트하세요.
"""

import pytest
import sys
import os

# 상위 디렉토리의 모듈을 임포트하기 위한 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src_notification_service import (
    SensorReader,
    EmailSender,
    MaintenanceScheduler,
    Logger,
    EquipmentAnalyzer,
    SensorDataRepository,
    NotificationService,
)


# ============================================================
# 연습 1: 스텁(Stub) 구현 및 사용
# ============================================================

class StubSensorReader(SensorReader):
    """
    TODO: 스텁 센서 리더를 구현하세요.

    요구사항:
    - 생성자에서 temperature, vibration, pressure 값을 받는다
    - 각 read_* 메서드는 생성자에서 받은 값을 반환한다
    """
    pass


class TestExercise1:
    """연습 1: 스텁을 사용한 상태 검증"""

    def test_normal_status(self):
        """정상 범위 값에서 '정상' 상태를 반환하는지 테스트하세요"""
        pytest.skip("TODO: StubSensorReader를 구현하고 이 테스트를 완성하세요")
        # TODO:
        # 1. StubSensorReader를 정상 범위 값으로 생성
        # 2. EquipmentAnalyzer에 전달
        # 3. analyze() 호출 후 status가 "정상"인지 검증

    def test_warning_on_high_vibration(self):
        """진동이 높을 때 '경고' 상태를 반환하는지 테스트하세요"""
        pytest.skip("TODO: 높은 진동 값으로 스텁을 설정하고 테스트하세요")
        # TODO:
        # 1. 진동 값이 7.0인 StubSensorReader 생성
        # 2. analyze() 결과의 status가 "경고"인지 검증


# ============================================================
# 연습 2: 스파이(Spy) 구현 및 사용
# ============================================================

class SpyNotificationSender(EmailSender):
    """
    TODO: 스파이 이메일 발송기를 구현하세요.

    요구사항:
    - sent_emails 리스트에 발송된 이메일 정보를 기록한다
    - call_count로 호출 횟수를 추적한다
    - send_email은 항상 True를 반환한다
    """
    pass


class DummyLogger(Logger):
    """더미 로거 (제공됨)"""
    def log(self, level, message):
        pass


class StubScheduler(MaintenanceScheduler):
    """스텁 스케줄러 (제공됨)"""
    def schedule_maintenance(self, equipment_id, priority, description):
        return "TASK-001"

    def get_next_maintenance(self, equipment_id):
        return None

    def cancel_maintenance(self, task_id):
        return True


class TestExercise2:
    """연습 2: 스파이를 사용한 호출 검증"""

    def test_email_sent_on_critical_temperature(self):
        """위험 온도에서 이메일이 발송되는지 검증하세요"""
        pytest.skip("TODO: SpyNotificationSender를 구현하고 이메일 발송을 검증하세요")
        # TODO:
        # 1. 온도 110도인 StubSensorReader 생성
        # 2. SpyNotificationSender 생성
        # 3. NotificationService에 전달하여 check_equipment 호출
        # 4. spy의 call_count가 1인지 확인
        # 5. 발송된 이메일 제목에 "위험"이 포함되었는지 확인

    def test_no_email_on_normal_readings(self):
        """정상 상태에서 이메일이 발송되지 않는지 검증하세요"""
        pytest.skip("TODO: 정상 값에서 이메일이 안 보내지는 것을 검증하세요")
        # TODO:
        # 1. 정상 범위 StubSensorReader 생성
        # 2. SpyNotificationSender로 이메일 미발송 확인


# ============================================================
# 연습 3: 페이크(Fake) 구현 및 사용
# ============================================================

class FakeMaintenanceRepository:
    """
    TODO: 인메모리 정비 작업 저장소를 구현하세요.

    요구사항:
    - add_task(task): 정비 작업을 추가한다
    - get_task(task_id): task_id로 작업을 조회한다
    - get_tasks_by_equipment(equipment_id): 설비별 작업 목록을 반환한다
    - remove_task(task_id): 작업을 삭제한다
    - count(): 전체 작업 수를 반환한다
    """
    pass


class TestExercise3:
    """연습 3: 페이크를 사용한 CRUD 테스트"""

    def test_add_and_get_task(self):
        """정비 작업을 추가하고 조회할 수 있는지 테스트하세요"""
        pytest.skip("TODO: FakeMaintenanceRepository를 구현하고 테스트하세요")
        # TODO:
        # 1. FakeMaintenanceRepository 생성
        # 2. 작업 추가: {"task_id": "T-001", "equipment_id": "EQ-001", ...}
        # 3. get_task("T-001")로 조회하여 데이터 확인

    def test_get_tasks_by_equipment(self):
        """설비별 작업 목록을 조회할 수 있는지 테스트하세요"""
        pytest.skip("TODO: 설비별 조회 기능을 테스트하세요")
        # TODO:
        # 1. EQ-001에 2개, EQ-002에 1개 작업 추가
        # 2. get_tasks_by_equipment("EQ-001") 결과가 2개인지 확인

    def test_remove_task(self):
        """정비 작업을 삭제할 수 있는지 테스트하세요"""
        pytest.skip("TODO: 작업 삭제 기능을 테스트하세요")
        # TODO:
        # 1. 작업 추가 후 삭제
        # 2. 조회 시 None 반환 확인
