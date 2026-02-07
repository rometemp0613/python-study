"""
예지보전 시스템의 알림 서비스 모듈

이 모듈은 공장 설비 모니터링 시스템에서 사용되는
다양한 서비스 인터페이스와 구현체를 정의합니다.
테스트 더블 학습을 위한 소스 코드입니다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


# ============================================================
# 인터페이스 (추상 클래스) 정의
# ============================================================

class EmailSender(ABC):
    """이메일 발송 인터페이스"""

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """이메일을 발송한다"""
        pass


class SensorReader(ABC):
    """센서 데이터 읽기 인터페이스"""

    @abstractmethod
    def read_temperature(self, sensor_id: str) -> float:
        """온도 센서 값을 읽는다 (섭씨)"""
        pass

    @abstractmethod
    def read_vibration(self, sensor_id: str) -> float:
        """진동 센서 값을 읽는다 (mm/s)"""
        pass

    @abstractmethod
    def read_pressure(self, sensor_id: str) -> float:
        """압력 센서 값을 읽는다 (bar)"""
        pass


class MaintenanceScheduler(ABC):
    """정비 일정 관리 인터페이스"""

    @abstractmethod
    def schedule_maintenance(self, equipment_id: str, priority: str,
                             description: str) -> str:
        """정비 작업을 예약하고 작업 ID를 반환한다"""
        pass

    @abstractmethod
    def get_next_maintenance(self, equipment_id: str) -> Optional[dict]:
        """다음 예정된 정비 작업을 조회한다"""
        pass

    @abstractmethod
    def cancel_maintenance(self, task_id: str) -> bool:
        """예약된 정비 작업을 취소한다"""
        pass


class Logger(ABC):
    """로깅 인터페이스"""

    @abstractmethod
    def log(self, level: str, message: str) -> None:
        """로그 메시지를 기록한다"""
        pass


# ============================================================
# 데이터 클래스
# ============================================================

@dataclass
class SensorReading:
    """센서 측정값을 담는 데이터 클래스"""
    sensor_id: str
    temperature: float
    vibration: float
    pressure: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AnalysisResult:
    """분석 결과를 담는 데이터 클래스"""
    equipment_id: str
    status: str  # "정상", "주의", "경고", "위험"
    temperature: float
    vibration: float
    pressure: float
    message: str = ""


@dataclass
class MaintenanceTask:
    """정비 작업 정보"""
    task_id: str
    equipment_id: str
    priority: str  # "낮음", "보통", "높음", "긴급"
    description: str
    scheduled_date: Optional[datetime] = None


# ============================================================
# 서비스 구현체
# ============================================================

class NotificationService:
    """
    알림 서비스

    센서 데이터를 분석하고 이상이 감지되면
    이메일 알림을 보내고 정비를 예약합니다.
    """

    # 임계값 설정
    TEMP_WARNING = 80.0      # 온도 경고 (섭씨)
    TEMP_CRITICAL = 100.0    # 온도 위험 (섭씨)
    VIBRATION_WARNING = 5.0  # 진동 경고 (mm/s)
    VIBRATION_CRITICAL = 10.0  # 진동 위험 (mm/s)
    PRESSURE_WARNING = 8.0   # 압력 경고 (bar)
    PRESSURE_CRITICAL = 12.0  # 압력 위험 (bar)

    def __init__(self, sensor_reader: SensorReader,
                 email_sender: EmailSender,
                 scheduler: MaintenanceScheduler,
                 logger: Logger):
        self._sensor_reader = sensor_reader
        self._email_sender = email_sender
        self._scheduler = scheduler
        self._logger = logger

    def check_equipment(self, equipment_id: str,
                        sensor_id: str,
                        notify_email: str) -> AnalysisResult:
        """
        설비 상태를 점검하고 필요시 알림을 발송한다.

        Args:
            equipment_id: 설비 ID
            sensor_id: 센서 ID
            notify_email: 알림 받을 이메일 주소

        Returns:
            AnalysisResult: 분석 결과
        """
        # 센서 데이터 읽기
        temperature = self._sensor_reader.read_temperature(sensor_id)
        vibration = self._sensor_reader.read_vibration(sensor_id)
        pressure = self._sensor_reader.read_pressure(sensor_id)

        self._logger.log("INFO",
                         f"센서 데이터 수집 완료: {sensor_id}")

        # 상태 분석
        status = self._analyze_status(temperature, vibration, pressure)
        message = self._build_message(equipment_id, status,
                                      temperature, vibration, pressure)

        result = AnalysisResult(
            equipment_id=equipment_id,
            status=status,
            temperature=temperature,
            vibration=vibration,
            pressure=pressure,
            message=message
        )

        # 경고 이상이면 알림 발송
        if status in ("경고", "위험"):
            self._email_sender.send_email(
                to=notify_email,
                subject=f"[{status}] 설비 {equipment_id} 이상 감지",
                body=message
            )
            self._logger.log("WARNING",
                             f"알림 발송: {equipment_id} - {status}")

        # 위험이면 긴급 정비 예약
        if status == "위험":
            task_id = self._scheduler.schedule_maintenance(
                equipment_id=equipment_id,
                priority="긴급",
                description=message
            )
            self._logger.log("CRITICAL",
                             f"긴급 정비 예약: {task_id}")

        return result

    def _analyze_status(self, temperature: float,
                        vibration: float,
                        pressure: float) -> str:
        """센서 값을 기반으로 설비 상태를 판단한다"""
        if (temperature >= self.TEMP_CRITICAL or
                vibration >= self.VIBRATION_CRITICAL or
                pressure >= self.PRESSURE_CRITICAL):
            return "위험"
        elif (temperature >= self.TEMP_WARNING or
              vibration >= self.VIBRATION_WARNING or
              pressure >= self.PRESSURE_WARNING):
            return "경고"
        elif (temperature >= self.TEMP_WARNING * 0.9 or
              vibration >= self.VIBRATION_WARNING * 0.9 or
              pressure >= self.PRESSURE_WARNING * 0.9):
            return "주의"
        else:
            return "정상"

    def _build_message(self, equipment_id: str, status: str,
                       temperature: float, vibration: float,
                       pressure: float) -> str:
        """상태에 따른 알림 메시지를 생성한다"""
        return (
            f"설비 {equipment_id} 상태: {status}\n"
            f"온도: {temperature}°C, "
            f"진동: {vibration}mm/s, "
            f"압력: {pressure}bar"
        )


class EquipmentAnalyzer:
    """
    설비 분석기

    센서 데이터를 분석하여 설비 상태를 판별합니다.
    """

    def __init__(self, sensor_reader: SensorReader, logger: Logger = None):
        self._sensor_reader = sensor_reader
        self._logger = logger

    def analyze(self, sensor_id: str) -> AnalysisResult:
        """센서 데이터를 분석하여 상태를 반환한다"""
        temperature = self._sensor_reader.read_temperature(sensor_id)
        vibration = self._sensor_reader.read_vibration(sensor_id)
        pressure = self._sensor_reader.read_pressure(sensor_id)

        if temperature > 100 or vibration > 10:
            status = "위험"
        elif temperature > 80 or vibration > 5:
            status = "경고"
        else:
            status = "정상"

        return AnalysisResult(
            equipment_id=sensor_id,
            status=status,
            temperature=temperature,
            vibration=vibration,
            pressure=pressure
        )


class SensorDataRepository:
    """
    센서 데이터 저장소

    센서 데이터를 저장하고 조회하는 역할을 합니다.
    실제 구현은 데이터베이스를 사용하지만,
    테스트에서는 FakeDatabase로 대체할 수 있습니다.
    """

    def __init__(self, database):
        self._db = database

    def save_reading(self, sensor_id: str, data: dict) -> None:
        """센서 측정값을 저장한다"""
        self._db.save(sensor_id, data)

    def get_reading(self, sensor_id: str) -> Optional[dict]:
        """센서 측정값을 조회한다"""
        return self._db.load(sensor_id)

    def delete_reading(self, sensor_id: str) -> None:
        """센서 측정값을 삭제한다"""
        self._db.delete(sensor_id)
