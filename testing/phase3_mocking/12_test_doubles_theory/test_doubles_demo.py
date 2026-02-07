"""
테스트 더블 데모

5가지 테스트 더블(Dummy, Stub, Spy, Mock, Fake)을 각각 사용하여
예지보전 시스템의 컴포넌트를 테스트하는 예제입니다.
"""

import pytest
from unittest.mock import Mock
from src_notification_service import (
    NotificationService,
    EquipmentAnalyzer,
    SensorDataRepository,
    SensorReader,
    EmailSender,
    MaintenanceScheduler,
    Logger,
)


# ============================================================
# 1. Dummy (더미) - 매개변수 채우기용
# ============================================================

class DummyLogger(Logger):
    """
    더미 로거: 아무 동작도 하지 않음

    NotificationService 생성 시 Logger가 필수이지만,
    로깅 동작 자체를 테스트하지 않을 때 사용합니다.
    """
    def log(self, level: str, message: str) -> None:
        pass  # 아무것도 하지 않음


class TestDummy:
    """더미 테스트 더블 사용 예제"""

    def test_equipment_analyzer_creation_with_dummy_logger(self):
        """더미 로거를 사용하여 분석기 생성을 테스트한다"""
        # DummyLogger는 실제로 사용되지 않지만
        # EquipmentAnalyzer 생성 시 필요한 매개변수를 채워줌
        dummy_logger = DummyLogger()

        # 스텁 센서 리더도 함께 사용 (이 테스트의 초점은 더미)
        stub_reader = StubSensorReader()

        analyzer = EquipmentAnalyzer(
            sensor_reader=stub_reader,
            logger=dummy_logger
        )

        # 분석기가 정상적으로 생성되었는지 확인
        assert analyzer is not None

    def test_none_as_dummy_when_optional(self):
        """Optional 매개변수에 None을 더미로 사용할 수 있다"""
        stub_reader = StubSensorReader()

        # logger가 Optional이므로 None을 전달 (더미 역할)
        analyzer = EquipmentAnalyzer(
            sensor_reader=stub_reader,
            logger=None
        )

        result = analyzer.analyze("SENSOR-01")
        assert result.status == "정상"


# ============================================================
# 2. Stub (스텁) - 미리 준비된 응답 반환
# ============================================================

class StubSensorReader(SensorReader):
    """
    스텁 센서 리더: 미리 설정된 값을 반환

    실제 센서 하드웨어 없이 테스트할 수 있도록
    고정된 센서 데이터를 반환합니다.
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


class StubEmailSender(EmailSender):
    """항상 성공을 반환하는 스텁 이메일 발송기"""
    def send_email(self, to: str, subject: str, body: str) -> bool:
        return True


class StubScheduler(MaintenanceScheduler):
    """고정된 작업 ID를 반환하는 스텁 스케줄러"""
    def schedule_maintenance(self, equipment_id: str, priority: str,
                             description: str) -> str:
        return "TASK-001"

    def get_next_maintenance(self, equipment_id: str):
        return None

    def cancel_maintenance(self, task_id: str) -> bool:
        return True


class TestStub:
    """스텁 테스트 더블 사용 예제"""

    def test_normal_status_with_normal_readings(self):
        """정상 범위의 센서 값일 때 '정상' 상태를 반환한다"""
        # 정상 범위 값을 반환하도록 스텁 설정
        stub_reader = StubSensorReader(
            temperature=25.0, vibration=2.0, pressure=5.0
        )

        analyzer = EquipmentAnalyzer(sensor_reader=stub_reader)
        result = analyzer.analyze("SENSOR-01")

        # 상태 검증 (State Verification)
        assert result.status == "정상"
        assert result.temperature == 25.0

    def test_warning_status_with_high_temperature(self):
        """온도가 높을 때 '경고' 상태를 반환한다"""
        # 높은 온도를 반환하도록 스텁 설정
        stub_reader = StubSensorReader(
            temperature=85.0, vibration=2.0, pressure=5.0
        )

        analyzer = EquipmentAnalyzer(sensor_reader=stub_reader)
        result = analyzer.analyze("SENSOR-01")

        assert result.status == "경고"
        assert result.temperature == 85.0

    def test_critical_status_with_extreme_vibration(self):
        """진동이 극도로 높을 때 '위험' 상태를 반환한다"""
        # 위험 수준 진동을 반환하도록 스텁 설정
        stub_reader = StubSensorReader(
            temperature=25.0, vibration=15.0, pressure=5.0
        )

        analyzer = EquipmentAnalyzer(sensor_reader=stub_reader)
        result = analyzer.analyze("SENSOR-01")

        assert result.status == "위험"


# ============================================================
# 3. Spy (스파이) - 호출 기록 추적
# ============================================================

class SpyEmailSender(EmailSender):
    """
    스파이 이메일 발송기: 호출 기록을 저장

    실제 이메일을 보내지 않지만,
    send_email이 호출된 내역을 기록합니다.
    """
    def __init__(self):
        self.sent_emails = []  # 발송 기록
        self.call_count = 0    # 호출 횟수

    def send_email(self, to: str, subject: str, body: str) -> bool:
        self.call_count += 1
        self.sent_emails.append({
            "to": to,
            "subject": subject,
            "body": body
        })
        return True


class TestSpy:
    """스파이 테스트 더블 사용 예제"""

    def test_email_sent_on_warning(self):
        """경고 상태에서 이메일이 발송된다"""
        # 경고 수준 센서 값 설정
        stub_reader = StubSensorReader(
            temperature=85.0, vibration=6.0, pressure=5.0
        )
        spy_email = SpyEmailSender()

        service = NotificationService(
            sensor_reader=stub_reader,
            email_sender=spy_email,
            scheduler=StubScheduler(),
            logger=DummyLogger()
        )

        service.check_equipment("EQ-001", "SENSOR-01", "admin@factory.com")

        # 스파이를 통해 이메일 발송 여부 확인
        assert spy_email.call_count == 1
        assert spy_email.sent_emails[0]["to"] == "admin@factory.com"
        assert "경고" in spy_email.sent_emails[0]["subject"]

    def test_no_email_on_normal_status(self):
        """정상 상태에서는 이메일이 발송되지 않는다"""
        stub_reader = StubSensorReader(
            temperature=25.0, vibration=2.0, pressure=5.0
        )
        spy_email = SpyEmailSender()

        service = NotificationService(
            sensor_reader=stub_reader,
            email_sender=spy_email,
            scheduler=StubScheduler(),
            logger=DummyLogger()
        )

        service.check_equipment("EQ-001", "SENSOR-01", "admin@factory.com")

        # 정상이면 이메일 발송 안 됨
        assert spy_email.call_count == 0
        assert len(spy_email.sent_emails) == 0

    def test_email_contains_sensor_data(self):
        """발송된 이메일에 센서 데이터가 포함된다"""
        stub_reader = StubSensorReader(
            temperature=105.0, vibration=3.0, pressure=5.0
        )
        spy_email = SpyEmailSender()

        service = NotificationService(
            sensor_reader=stub_reader,
            email_sender=spy_email,
            scheduler=StubScheduler(),
            logger=DummyLogger()
        )

        service.check_equipment("EQ-001", "SENSOR-01", "admin@factory.com")

        # 이메일 본문에 센서 데이터가 포함되어 있는지 확인
        body = spy_email.sent_emails[0]["body"]
        assert "105.0" in body
        assert "EQ-001" in body


# ============================================================
# 4. Mock (목) - 기대 행위 검증
# ============================================================

class TestMock:
    """Mock 객체를 사용한 행위 검증 예제"""

    def test_maintenance_scheduled_on_critical(self):
        """위험 상태에서 긴급 정비가 예약된다"""
        # 위험 수준 센서 값
        stub_reader = StubSensorReader(
            temperature=110.0, vibration=12.0, pressure=5.0
        )

        # unittest.mock.Mock 사용
        mock_scheduler = Mock(spec=MaintenanceScheduler)
        mock_scheduler.schedule_maintenance.return_value = "TASK-999"

        service = NotificationService(
            sensor_reader=stub_reader,
            email_sender=StubEmailSender(),
            scheduler=mock_scheduler,
            logger=DummyLogger()
        )

        service.check_equipment("EQ-001", "SENSOR-01", "admin@factory.com")

        # Mock을 통해 schedule_maintenance가 올바르게 호출되었는지 검증
        mock_scheduler.schedule_maintenance.assert_called_once()

        # 호출 인자 검증
        call_args = mock_scheduler.schedule_maintenance.call_args
        assert call_args.kwargs["equipment_id"] == "EQ-001"
        assert call_args.kwargs["priority"] == "긴급"

    def test_no_maintenance_on_normal(self):
        """정상 상태에서는 정비가 예약되지 않는다"""
        stub_reader = StubSensorReader(
            temperature=25.0, vibration=2.0, pressure=5.0
        )
        mock_scheduler = Mock(spec=MaintenanceScheduler)

        service = NotificationService(
            sensor_reader=stub_reader,
            email_sender=StubEmailSender(),
            scheduler=mock_scheduler,
            logger=DummyLogger()
        )

        service.check_equipment("EQ-001", "SENSOR-01", "admin@factory.com")

        # 정비 예약이 호출되지 않았는지 검증
        mock_scheduler.schedule_maintenance.assert_not_called()

    def test_logger_called_for_data_collection(self):
        """센서 데이터 수집 시 로그가 기록된다"""
        stub_reader = StubSensorReader()
        mock_logger = Mock(spec=Logger)

        service = NotificationService(
            sensor_reader=stub_reader,
            email_sender=StubEmailSender(),
            scheduler=StubScheduler(),
            logger=mock_logger
        )

        service.check_equipment("EQ-001", "SENSOR-01", "admin@factory.com")

        # 로그가 최소 1번 호출되었는지 검증
        assert mock_logger.log.call_count >= 1

        # 첫 번째 호출의 인자 확인
        first_call = mock_logger.log.call_args_list[0]
        assert first_call[0][0] == "INFO"  # 로그 레벨
        assert "SENSOR-01" in first_call[0][1]  # 메시지에 센서 ID 포함


# ============================================================
# 5. Fake (페이크) - 간소화된 실제 구현
# ============================================================

class FakeDatabase:
    """
    페이크 데이터베이스: 인메모리 딕셔너리로 구현

    실제 데이터베이스와 동일한 인터페이스를 제공하지만
    메모리에서 동작하여 빠르고 테스트 후 정리가 필요 없습니다.
    """
    def __init__(self):
        self._data = {}

    def save(self, key: str, value) -> None:
        self._data[key] = value

    def load(self, key: str):
        return self._data.get(key)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def count(self) -> int:
        return len(self._data)


class TestFake:
    """페이크 테스트 더블 사용 예제"""

    def test_save_and_retrieve_sensor_data(self):
        """센서 데이터를 저장하고 조회할 수 있다"""
        fake_db = FakeDatabase()
        repo = SensorDataRepository(database=fake_db)

        sensor_data = {
            "temperature": 75.5,
            "vibration": 3.2,
            "pressure": 6.1
        }
        repo.save_reading("SENSOR-01", sensor_data)

        # 저장한 데이터를 다시 조회
        result = repo.get_reading("SENSOR-01")
        assert result["temperature"] == 75.5
        assert result["vibration"] == 3.2

    def test_delete_sensor_data(self):
        """센서 데이터를 삭제할 수 있다"""
        fake_db = FakeDatabase()
        repo = SensorDataRepository(database=fake_db)

        repo.save_reading("SENSOR-01", {"temp": 25.0})
        repo.delete_reading("SENSOR-01")

        result = repo.get_reading("SENSOR-01")
        assert result is None

    def test_nonexistent_sensor_returns_none(self):
        """존재하지 않는 센서 ID로 조회하면 None을 반환한다"""
        fake_db = FakeDatabase()
        repo = SensorDataRepository(database=fake_db)

        result = repo.get_reading("NONEXISTENT")
        assert result is None

    def test_multiple_sensors_independent(self):
        """여러 센서의 데이터가 독립적으로 관리된다"""
        fake_db = FakeDatabase()
        repo = SensorDataRepository(database=fake_db)

        repo.save_reading("SENSOR-01", {"temp": 25.0})
        repo.save_reading("SENSOR-02", {"temp": 30.0})

        assert repo.get_reading("SENSOR-01")["temp"] == 25.0
        assert repo.get_reading("SENSOR-02")["temp"] == 30.0
        assert fake_db.count() == 2
