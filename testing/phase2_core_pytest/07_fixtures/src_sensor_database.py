"""
센서 데이터베이스 모듈

공장 설비의 센서 읽기값을 저장하고 조회하는 인메모리 데이터베이스.
예지보전 시스템에서 센서 데이터 관리의 기본 단위를 제공한다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SensorReading:
    """센서 읽기값을 표현하는 데이터 클래스"""
    sensor_id: str           # 센서 식별자 (예: "TEMP-001")
    value: float             # 측정값
    timestamp: datetime      # 측정 시각
    unit: str = ""           # 단위 (예: "°C", "mm/s")
    status: str = "normal"   # 상태 (normal, warning, critical)

    def is_critical(self) -> bool:
        """위험 상태인지 확인"""
        return self.status == "critical"

    def is_warning(self) -> bool:
        """경고 상태인지 확인"""
        return self.status == "warning"


@dataclass
class SensorDatabase:
    """
    인메모리 센서 데이터베이스

    센서 읽기값을 딕셔너리 기반으로 저장하고 조회한다.
    실제 운영에서는 DB를 사용하겠지만, 테스트 학습용으로 인메모리 구현.
    """
    _data: dict = field(default_factory=dict)  # {sensor_id: [SensorReading, ...]}
    _initialized: bool = False
    _closed: bool = False

    def initialize(self) -> None:
        """데이터베이스를 초기화한다"""
        self._data = {}
        self._initialized = True
        self._closed = False

    def close(self) -> None:
        """데이터베이스 연결을 닫는다"""
        self._closed = True

    @property
    def is_initialized(self) -> bool:
        """초기화 상태 확인"""
        return self._initialized and not self._closed

    def add_reading(self, sensor_id: str, value: float,
                    unit: str = "", status: str = "normal",
                    timestamp: Optional[datetime] = None) -> SensorReading:
        """
        센서 읽기값을 추가한다.

        Args:
            sensor_id: 센서 식별자
            value: 측정값
            unit: 단위
            status: 상태
            timestamp: 측정 시각 (None이면 현재 시각)

        Returns:
            추가된 SensorReading 객체

        Raises:
            RuntimeError: 데이터베이스가 초기화되지 않았거나 닫혔을 때
        """
        if not self.is_initialized:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다")

        reading = SensorReading(
            sensor_id=sensor_id,
            value=value,
            timestamp=timestamp or datetime.now(),
            unit=unit,
            status=status,
        )

        if sensor_id not in self._data:
            self._data[sensor_id] = []
        self._data[sensor_id].append(reading)
        return reading

    def get_readings(self, sensor_id: str) -> list[SensorReading]:
        """특정 센서의 모든 읽기값을 반환한다"""
        if not self.is_initialized:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다")
        return self._data.get(sensor_id, [])

    def get_latest(self, sensor_id: str) -> Optional[SensorReading]:
        """특정 센서의 최신 읽기값을 반환한다"""
        readings = self.get_readings(sensor_id)
        if not readings:
            return None
        return max(readings, key=lambda r: r.timestamp)

    def get_average(self, sensor_id: str) -> Optional[float]:
        """특정 센서의 평균값을 반환한다"""
        readings = self.get_readings(sensor_id)
        if not readings:
            return None
        return sum(r.value for r in readings) / len(readings)

    def get_all_sensor_ids(self) -> list[str]:
        """등록된 모든 센서 ID를 반환한다"""
        if not self.is_initialized:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다")
        return list(self._data.keys())

    def count_readings(self, sensor_id: str) -> int:
        """특정 센서의 읽기값 개수를 반환한다"""
        return len(self.get_readings(sensor_id))

    def clear(self) -> None:
        """모든 데이터를 삭제한다"""
        if not self.is_initialized:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다")
        self._data.clear()

    def get_readings_by_status(self, status: str) -> list[SensorReading]:
        """특정 상태의 모든 읽기값을 반환한다"""
        if not self.is_initialized:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다")
        result = []
        for readings in self._data.values():
            result.extend(r for r in readings if r.status == status)
        return result

    def get_min_max(self, sensor_id: str) -> Optional[tuple[float, float]]:
        """특정 센서의 최솟값과 최댓값을 반환한다"""
        readings = self.get_readings(sensor_id)
        if not readings:
            return None
        values = [r.value for r in readings]
        return (min(values), max(values))
