"""
센서 데이터 수집 모듈

외부 센서 API로부터 데이터를 수집하고,
분석하여 저장하는 기능을 제공합니다.
unittest.mock 학습을 위한 소스 코드입니다.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


# ============================================================
# 외부 API 인터페이스
# ============================================================

class SensorAPI:
    """
    센서 데이터 API

    실제로는 HTTP 요청을 통해 센서 게이트웨이와 통신합니다.
    테스트에서는 Mock으로 대체합니다.
    """

    def __init__(self, base_url: str, api_key: str):
        """API 클라이언트 초기화"""
        self._base_url = base_url
        self._api_key = api_key

    def connect(self) -> bool:
        """센서 게이트웨이에 연결한다"""
        # 실제로는 HTTP 연결 수행
        raise NotImplementedError("실제 API 연결 필요")

    def fetch_reading(self, sensor_id: str) -> dict:
        """센서에서 최신 측정값을 가져온다"""
        # 실제로는 HTTP GET 요청
        raise NotImplementedError("실제 API 호출 필요")

    def fetch_batch(self, sensor_ids: list) -> list:
        """여러 센서의 데이터를 일괄 조회한다"""
        raise NotImplementedError("실제 API 호출 필요")

    def get_sensor_status(self, sensor_id: str) -> str:
        """센서의 현재 상태를 조회한다 (active/inactive/error)"""
        raise NotImplementedError("실제 API 호출 필요")

    @property
    def connection_status(self) -> str:
        """현재 연결 상태를 반환한다"""
        raise NotImplementedError("실제 연결 상태 확인 필요")


# ============================================================
# 데이터 클래스
# ============================================================

@dataclass
class SensorReading:
    """센서 측정값"""
    sensor_id: str
    temperature: float
    vibration: float
    pressure: float
    timestamp: datetime = field(default_factory=datetime.now)
    is_valid: bool = True


@dataclass
class CollectionResult:
    """수집 결과 요약"""
    total_sensors: int
    successful: int
    failed: int
    readings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """수집 성공률을 계산한다"""
        if self.total_sensors == 0:
            return 0.0
        return self.successful / self.total_sensors * 100


# ============================================================
# 데이터 저장소
# ============================================================

class DataStore:
    """
    데이터 저장소 인터페이스

    수집된 센서 데이터를 영구 저장소에 저장합니다.
    """

    def save(self, reading: SensorReading) -> bool:
        """측정값을 저장한다"""
        raise NotImplementedError("실제 저장소 연결 필요")

    def save_batch(self, readings: list) -> int:
        """여러 측정값을 일괄 저장하고 저장된 개수를 반환한다"""
        raise NotImplementedError("실제 저장소 연결 필요")

    def get_latest(self, sensor_id: str) -> Optional[SensorReading]:
        """특정 센서의 최신 측정값을 조회한다"""
        raise NotImplementedError("실제 저장소 연결 필요")


# ============================================================
# 센서 데이터 수집기
# ============================================================

class SensorCollector:
    """
    센서 데이터 수집기

    여러 센서로부터 데이터를 수집하고,
    유효성을 검사한 후 저장소에 저장합니다.
    """

    # 유효 범위 설정
    TEMP_MIN = -40.0
    TEMP_MAX = 200.0
    VIBRATION_MIN = 0.0
    VIBRATION_MAX = 50.0
    PRESSURE_MIN = 0.0
    PRESSURE_MAX = 20.0

    def __init__(self, api: SensorAPI, store: DataStore):
        self._api = api
        self._store = store

    def collect_single(self, sensor_id: str) -> SensorReading:
        """
        단일 센서에서 데이터를 수집한다.

        Args:
            sensor_id: 센서 식별자

        Returns:
            SensorReading: 수집된 측정값

        Raises:
            ConnectionError: API 연결 실패 시
            ValueError: 잘못된 센서 데이터 시
        """
        # API에서 데이터 가져오기
        raw_data = self._api.fetch_reading(sensor_id)

        # 데이터 변환
        reading = SensorReading(
            sensor_id=sensor_id,
            temperature=raw_data["temperature"],
            vibration=raw_data["vibration"],
            pressure=raw_data["pressure"]
        )

        # 유효성 검사
        reading.is_valid = self._validate(reading)

        # 유효한 데이터만 저장
        if reading.is_valid:
            self._store.save(reading)

        return reading

    def collect_multiple(self, sensor_ids: list) -> CollectionResult:
        """
        여러 센서에서 데이터를 일괄 수집한다.

        실패한 센서가 있어도 다른 센서의 수집은 계속합니다.
        """
        result = CollectionResult(
            total_sensors=len(sensor_ids),
            successful=0,
            failed=0
        )

        for sensor_id in sensor_ids:
            try:
                reading = self.collect_single(sensor_id)
                if reading.is_valid:
                    result.successful += 1
                    result.readings.append(reading)
                else:
                    result.failed += 1
                    result.errors.append(
                        f"{sensor_id}: 유효하지 않은 데이터"
                    )
            except Exception as e:
                result.failed += 1
                result.errors.append(f"{sensor_id}: {str(e)}")

        return result

    def collect_with_retry(self, sensor_id: str,
                           max_retries: int = 3) -> Optional[SensorReading]:
        """
        재시도 로직이 포함된 데이터 수집

        연결 실패 시 최대 max_retries번 재시도합니다.
        """
        for attempt in range(max_retries):
            try:
                return self.collect_single(sensor_id)
            except ConnectionError:
                if attempt == max_retries - 1:
                    return None  # 모든 재시도 실패
                continue  # 다시 시도

    def _validate(self, reading: SensorReading) -> bool:
        """측정값이 유효 범위 내인지 검사한다"""
        if not (self.TEMP_MIN <= reading.temperature <= self.TEMP_MAX):
            return False
        if not (self.VIBRATION_MIN <= reading.vibration <= self.VIBRATION_MAX):
            return False
        if not (self.PRESSURE_MIN <= reading.pressure <= self.PRESSURE_MAX):
            return False
        return True

    def check_sensor_health(self, sensor_id: str) -> dict:
        """
        센서 상태를 확인한다.

        Returns:
            dict: {"sensor_id": str, "status": str, "healthy": bool}
        """
        status = self._api.get_sensor_status(sensor_id)
        return {
            "sensor_id": sensor_id,
            "status": status,
            "healthy": status == "active"
        }
