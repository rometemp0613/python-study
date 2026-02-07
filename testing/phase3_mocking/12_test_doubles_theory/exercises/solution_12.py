"""
연습 문제 12 풀이: 테스트 더블 이론

각 테스트 더블 유형을 직접 구현하고 사용한 풀이입니다.
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
# 연습 1 풀이: 스텁(Stub) 구현
# ============================================================

class StubSensorReader(SensorReader):
    """
    스텁 센서 리더: 미리 설정된 값을 반환

    생성자에서 받은 고정 값을 반환하여
    실제 센서 없이 테스트할 수 있게 합니다.
    """
    def __init__(self, temperature=25.0, vibration=2.0, pressure=5.0):
        self._temperature = temperature
        self._vibration = vibration
        self._pressure = pressure

    def read_temperature(self, sensor_id: str) -> float:
        return self._temperature

    def read_vibration(self, sensor_id: str) -> float:
        return self._vibration

    def read_pressure(self, sensor_id: str) -> float:
        return self._pressure


class TestExercise1:
    """연습 1 풀이: 스텁을 사용한 상태 검증"""

    def test_normal_status(self):
        """정상 범위 값에서 '정상' 상태를 반환한다"""
        # 정상 범위의 센서 값으로 스텁 생성
        stub_reader = StubSensorReader(
            temperature=25.0, vibration=2.0, pressure=5.0
        )

        # 분석기에 스텁 전달
        analyzer = EquipmentAnalyzer(sensor_reader=stub_reader)

        # 분석 수행 및 결과 검증
        result = analyzer.analyze("SENSOR-01")
        assert result.status == "정상"
        assert result.temperature == 25.0
        assert result.vibration == 2.0

    def test_warning_on_high_vibration(self):
        """진동이 높을 때 '경고' 상태를 반환한다"""
        # 진동 값이 경고 수준인 스텁 생성
        stub_reader = StubSensorReader(
            temperature=25.0, vibration=7.0, pressure=5.0
        )

        analyzer = EquipmentAnalyzer(sensor_reader=stub_reader)
        result = analyzer.analyze("SENSOR-01")

        assert result.status == "경고"
        assert result.vibration == 7.0


# ============================================================
# 연습 2 풀이: 스파이(Spy) 구현
# ============================================================

class SpyNotificationSender(EmailSender):
    """
    스파이 이메일 발송기: 호출 기록을 저장

    발송된 이메일의 상세 정보를 기록하여
    나중에 검증할 수 있게 합니다.
    """
    def __init__(self):
        self.sent_emails = []
        self.call_count = 0

    def send_email(self, to: str, subject: str, body: str) -> bool:
        self.call_count += 1
        self.sent_emails.append({
            "to": to,
            "subject": subject,
            "body": body
        })
        return True


class DummyLogger(Logger):
    """더미 로거: 아무 동작도 하지 않음"""
    def log(self, level, message):
        pass


class StubScheduler(MaintenanceScheduler):
    """스텁 스케줄러: 고정된 작업 ID를 반환"""
    def schedule_maintenance(self, equipment_id, priority, description):
        return "TASK-001"

    def get_next_maintenance(self, equipment_id):
        return None

    def cancel_maintenance(self, task_id):
        return True


class TestExercise2:
    """연습 2 풀이: 스파이를 사용한 호출 검증"""

    def test_email_sent_on_critical_temperature(self):
        """위험 온도에서 이메일이 발송된다"""
        # 위험 수준의 온도 값 설정
        stub_reader = StubSensorReader(
            temperature=110.0, vibration=2.0, pressure=5.0
        )
        spy_email = SpyNotificationSender()

        service = NotificationService(
            sensor_reader=stub_reader,
            email_sender=spy_email,
            scheduler=StubScheduler(),
            logger=DummyLogger()
        )

        service.check_equipment("EQ-001", "SENSOR-01", "admin@factory.com")

        # 이메일 발송 확인
        assert spy_email.call_count == 1
        assert "위험" in spy_email.sent_emails[0]["subject"]
        assert spy_email.sent_emails[0]["to"] == "admin@factory.com"

    def test_no_email_on_normal_readings(self):
        """정상 상태에서 이메일이 발송되지 않는다"""
        stub_reader = StubSensorReader(
            temperature=25.0, vibration=2.0, pressure=5.0
        )
        spy_email = SpyNotificationSender()

        service = NotificationService(
            sensor_reader=stub_reader,
            email_sender=spy_email,
            scheduler=StubScheduler(),
            logger=DummyLogger()
        )

        service.check_equipment("EQ-001", "SENSOR-01", "admin@factory.com")

        # 이메일 미발송 확인
        assert spy_email.call_count == 0
        assert len(spy_email.sent_emails) == 0


# ============================================================
# 연습 3 풀이: 페이크(Fake) 구현
# ============================================================

class FakeMaintenanceRepository:
    """
    인메모리 정비 작업 저장소

    딕셔너리를 사용하여 정비 작업의 CRUD를 구현합니다.
    실제 데이터베이스 대신 테스트에서 사용합니다.
    """
    def __init__(self):
        self._tasks = {}

    def add_task(self, task: dict) -> None:
        """정비 작업을 추가한다"""
        self._tasks[task["task_id"]] = task

    def get_task(self, task_id: str):
        """task_id로 작업을 조회한다"""
        return self._tasks.get(task_id)

    def get_tasks_by_equipment(self, equipment_id: str) -> list:
        """설비별 작업 목록을 반환한다"""
        return [
            task for task in self._tasks.values()
            if task["equipment_id"] == equipment_id
        ]

    def remove_task(self, task_id: str) -> None:
        """작업을 삭제한다"""
        self._tasks.pop(task_id, None)

    def count(self) -> int:
        """전체 작업 수를 반환한다"""
        return len(self._tasks)


class TestExercise3:
    """연습 3 풀이: 페이크를 사용한 CRUD 테스트"""

    def test_add_and_get_task(self):
        """정비 작업을 추가하고 조회할 수 있다"""
        repo = FakeMaintenanceRepository()

        task = {
            "task_id": "T-001",
            "equipment_id": "EQ-001",
            "priority": "높음",
            "description": "베어링 교체 필요"
        }
        repo.add_task(task)

        result = repo.get_task("T-001")
        assert result is not None
        assert result["equipment_id"] == "EQ-001"
        assert result["description"] == "베어링 교체 필요"

    def test_get_tasks_by_equipment(self):
        """설비별 작업 목록을 조회할 수 있다"""
        repo = FakeMaintenanceRepository()

        # EQ-001에 2개 작업 추가
        repo.add_task({"task_id": "T-001", "equipment_id": "EQ-001",
                        "priority": "높음", "description": "베어링 교체"})
        repo.add_task({"task_id": "T-002", "equipment_id": "EQ-001",
                        "priority": "보통", "description": "윤활유 보충"})

        # EQ-002에 1개 작업 추가
        repo.add_task({"task_id": "T-003", "equipment_id": "EQ-002",
                        "priority": "낮음", "description": "정기 점검"})

        eq001_tasks = repo.get_tasks_by_equipment("EQ-001")
        assert len(eq001_tasks) == 2

        eq002_tasks = repo.get_tasks_by_equipment("EQ-002")
        assert len(eq002_tasks) == 1

    def test_remove_task(self):
        """정비 작업을 삭제할 수 있다"""
        repo = FakeMaintenanceRepository()

        repo.add_task({"task_id": "T-001", "equipment_id": "EQ-001",
                        "priority": "높음", "description": "베어링 교체"})

        assert repo.count() == 1

        repo.remove_task("T-001")

        assert repo.get_task("T-001") is None
        assert repo.count() == 0
