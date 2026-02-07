"""
비동기 센서 데이터 수집 모듈.

공장 설비의 센서 데이터를 비동기적으로 수집하고
처리하는 함수와 클래스를 포함한다.

asyncio를 사용하여 여러 센서를 동시에 읽고,
실시간 모니터링을 수행한다.
"""

import asyncio
import random
import math
from typing import List, Dict, Any, Optional, Callable


async def fetch_sensor_data(sensor_id: str) -> Dict[str, Any]:
    """
    단일 센서의 데이터를 비동기적으로 가져온다.

    실제 환경에서는 네트워크 통신(OPC UA, MQTT 등)을
    시뮬레이션한다.

    Args:
        sensor_id: 센서 식별자

    Returns:
        센서 데이터 딕셔너리:
        {
            "sensor_id": str,
            "value": float,
            "status": str,
        }
    """
    # 네트워크 지연 시뮬레이션 (0.01~0.05초)
    await asyncio.sleep(random.uniform(0.01, 0.05))

    # 센서 ID에 따라 다른 범위의 값 생성
    if sensor_id.startswith("TEMP"):
        value = round(random.uniform(20.0, 80.0), 2)
    elif sensor_id.startswith("VIB"):
        value = round(random.uniform(0.0, 15.0), 2)
    elif sensor_id.startswith("PRES"):
        value = round(random.uniform(1.0, 10.0), 2)
    else:
        value = round(random.uniform(0.0, 100.0), 2)

    return {
        "sensor_id": sensor_id,
        "value": value,
        "status": "ok",
    }


async def collect_multiple_sensors(
    sensor_ids: List[str],
    fetch_func: Optional[Callable] = None,
) -> List[Dict[str, Any]]:
    """
    여러 센서의 데이터를 동시에 수집한다.

    asyncio.gather()를 사용하여 모든 센서를
    병렬로 읽어 효율성을 높인다.

    Args:
        sensor_ids: 센서 ID 리스트
        fetch_func: 센서 데이터 읽기 함수 (테스트용 주입 가능)

    Returns:
        센서 데이터 리스트
    """
    if fetch_func is None:
        fetch_func = fetch_sensor_data

    if not sensor_ids:
        return []

    # 모든 센서를 동시에 읽기
    results = await asyncio.gather(
        *[fetch_func(sid) for sid in sensor_ids],
        return_exceptions=True,
    )

    # 에러가 발생한 센서 처리
    processed = []
    for sensor_id, result in zip(sensor_ids, results):
        if isinstance(result, Exception):
            processed.append({
                "sensor_id": sensor_id,
                "value": None,
                "status": "error",
                "error": str(result),
            })
        else:
            processed.append(result)

    return processed


async def monitor_sensor(
    sensor_id: str,
    duration: float,
    interval: float = 0.1,
    fetch_func: Optional[Callable] = None,
) -> List[Dict[str, Any]]:
    """
    지정된 시간 동안 센서를 지속적으로 모니터링한다.

    Args:
        sensor_id: 센서 식별자
        duration: 모니터링 시간 (초)
        interval: 읽기 간격 (초)
        fetch_func: 센서 데이터 읽기 함수 (테스트용 주입 가능)

    Returns:
        모니터링 기간 동안 수집된 데이터 리스트
    """
    if fetch_func is None:
        fetch_func = fetch_sensor_data

    readings = []
    elapsed = 0.0

    while elapsed < duration:
        try:
            data = await fetch_func(sensor_id)
            readings.append(data)
        except Exception as e:
            readings.append({
                "sensor_id": sensor_id,
                "value": None,
                "status": "error",
                "error": str(e),
            })

        await asyncio.sleep(interval)
        elapsed += interval

    return readings


class AsyncSensorCollector:
    """
    비동기 센서 데이터 수집기 클래스.

    여러 센서를 등록하고, 주기적으로 데이터를 수집하며,
    알림 조건이 충족되면 콜백을 호출한다.
    """

    def __init__(self, fetch_func: Optional[Callable] = None):
        """
        수집기를 초기화한다.

        Args:
            fetch_func: 센서 데이터 읽기 함수 (테스트용 주입 가능)
        """
        self._fetch_func = fetch_func or fetch_sensor_data
        self._sensors: List[str] = []
        self._readings: Dict[str, List[Dict[str, Any]]] = {}
        self._is_running = False
        self._alert_callback: Optional[Callable] = None
        self._alert_thresholds: Dict[str, float] = {}

    @property
    def is_running(self) -> bool:
        """수집기가 실행 중인지 반환"""
        return self._is_running

    @property
    def registered_sensors(self) -> List[str]:
        """등록된 센서 목록"""
        return list(self._sensors)

    def register_sensor(
        self,
        sensor_id: str,
        alert_threshold: Optional[float] = None,
    ) -> None:
        """
        모니터링할 센서를 등록한다.

        Args:
            sensor_id: 센서 식별자
            alert_threshold: 알림 임계값 (초과 시 알림)
        """
        if sensor_id not in self._sensors:
            self._sensors.append(sensor_id)
            self._readings[sensor_id] = []
            if alert_threshold is not None:
                self._alert_thresholds[sensor_id] = alert_threshold

    def set_alert_callback(self, callback: Callable) -> None:
        """
        알림 콜백 함수를 설정한다.

        Args:
            callback: 알림 시 호출할 함수 (sensor_id, value, threshold)
        """
        self._alert_callback = callback

    async def collect_once(self) -> Dict[str, Dict[str, Any]]:
        """
        등록된 모든 센서에서 한 번 데이터를 수집한다.

        Returns:
            {sensor_id: data} 딕셔너리
        """
        if not self._sensors:
            return {}

        results = await collect_multiple_sensors(
            self._sensors,
            fetch_func=self._fetch_func,
        )

        collected = {}
        for data in results:
            sensor_id = data["sensor_id"]
            self._readings[sensor_id].append(data)
            collected[sensor_id] = data

            # 알림 체크
            if (
                self._alert_callback
                and sensor_id in self._alert_thresholds
                and data.get("value") is not None
                and data["value"] > self._alert_thresholds[sensor_id]
            ):
                await self._alert_callback(
                    sensor_id,
                    data["value"],
                    self._alert_thresholds[sensor_id],
                )

        return collected

    async def start(self, interval: float = 1.0, max_iterations: int = 10) -> None:
        """
        주기적 수집을 시작한다.

        Args:
            interval: 수집 간격 (초)
            max_iterations: 최대 반복 횟수 (안전장치)
        """
        self._is_running = True
        iteration = 0

        try:
            while self._is_running and iteration < max_iterations:
                await self.collect_once()
                iteration += 1
                if self._is_running:
                    await asyncio.sleep(interval)
        finally:
            self._is_running = False

    def stop(self) -> None:
        """주기적 수집을 중지한다."""
        self._is_running = False

    def get_readings(self, sensor_id: str) -> List[Dict[str, Any]]:
        """
        특정 센서의 수집된 데이터를 반환한다.

        Args:
            sensor_id: 센서 식별자

        Returns:
            해당 센서의 데이터 리스트
        """
        return self._readings.get(sensor_id, [])

    def get_statistics(self, sensor_id: str) -> Dict[str, Any]:
        """
        특정 센서의 수집 통계를 반환한다.

        Args:
            sensor_id: 센서 식별자

        Returns:
            통계 딕셔너리 (count, mean, min, max)
        """
        readings = self._readings.get(sensor_id, [])
        values = [r["value"] for r in readings if r.get("value") is not None]

        if not values:
            return {
                "sensor_id": sensor_id,
                "count": 0,
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
            }

        return {
            "sensor_id": sensor_id,
            "count": len(values),
            "mean": round(sum(values) / len(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
        }
