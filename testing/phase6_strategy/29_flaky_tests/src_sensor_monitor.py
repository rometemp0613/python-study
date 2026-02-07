"""
센서 모니터 모듈

센서 데이터를 실시간으로 모니터링하고 분석합니다.
시간, 랜덤 값, 부동소수점 계산 등 flaky 테스트의
원인이 될 수 있는 요소들이 포함되어 있습니다.
"""

import random
import math
from datetime import datetime
from typing import List, Optional, Tuple


class SensorMonitor:
    """
    센서 모니터

    센서 데이터를 모니터링하고 임계값 비교, 드리프트 계산,
    타임스탬프 포맷팅 등의 기능을 제공합니다.
    """

    def __init__(self, sensor_id: str = "default", seed: Optional[int] = None):
        """
        센서 모니터를 초기화합니다.

        Args:
            sensor_id: 센서 ID
            seed: 난수 시드 (테스트용, None이면 랜덤)
        """
        self._sensor_id = sensor_id
        self._rng = random.Random(seed)  # 독립적인 난수 생성기

    def get_current_reading(self, base_value: float = 100.0,
                            noise_level: float = 5.0) -> float:
        """
        현재 센서 측정값을 반환합니다.

        기본값에 노이즈를 더해 시뮬레이션합니다.

        Args:
            base_value: 기본 측정값
            noise_level: 노이즈 크기

        Returns:
            시뮬레이션된 측정값
        """
        noise = self._rng.gauss(0, noise_level)
        return base_value + noise

    def check_threshold(self, value: float, threshold: float) -> dict:
        """
        측정값을 임계값과 비교합니다.

        Args:
            value: 측정값
            threshold: 임계값

        Returns:
            비교 결과 딕셔너리
        """
        exceeded = value > threshold
        margin = abs(value - threshold)

        return {
            "value": value,
            "threshold": threshold,
            "exceeded": exceeded,
            "margin": round(margin, 6),  # 부동소수점 정밀도 관리
            "status": "alarm" if exceeded else "normal",
        }

    def calculate_drift(self, readings: List[float]) -> float:
        """
        센서 드리프트를 계산합니다.

        시계열 데이터의 선형 추세 기울기(시간 단위당 변화량)를 반환합니다.

        Args:
            readings: 시계열 측정값 리스트

        Returns:
            시간 단위당 드리프트 값

        Raises:
            ValueError: 데이터가 2개 미만인 경우
        """
        n = len(readings)
        if n < 2:
            raise ValueError("드리프트 계산에는 최소 2개의 데이터가 필요합니다.")

        # 단순 선형 회귀로 기울기 계산
        x_values = list(range(n))
        x_mean = sum(x_values) / n
        y_mean = sum(readings) / n

        numerator = sum(
            (x - x_mean) * (y - y_mean)
            for x, y in zip(x_values, readings)
        )
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def format_timestamp(self, dt: datetime) -> str:
        """
        날짜/시간을 표준 포맷으로 변환합니다.

        Args:
            dt: 날짜/시간 객체

        Returns:
            "YYYY-MM-DD HH:MM:SS" 형식의 문자열
        """
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def get_sensor_id(self) -> str:
        """센서 ID를 반환합니다."""
        return self._sensor_id

    def classify_reading(self, value: float,
                         normal_range: Tuple[float, float],
                         warning_range: Tuple[float, float]) -> str:
        """
        측정값을 분류합니다.

        Args:
            value: 측정값
            normal_range: 정상 범위 (min, max)
            warning_range: 경고 범위 (min, max)

        Returns:
            "normal", "warning", "critical" 중 하나
        """
        if normal_range[0] <= value <= normal_range[1]:
            return "normal"
        elif warning_range[0] <= value <= warning_range[1]:
            return "warning"
        else:
            return "critical"

    def calculate_statistics(self, readings: List[float]) -> dict:
        """
        측정값들의 통계를 계산합니다.

        Args:
            readings: 측정값 리스트

        Returns:
            통계 딕셔너리 (mean, std, min, max, count)

        Raises:
            ValueError: 빈 리스트인 경우
        """
        if not readings:
            raise ValueError("빈 리스트로는 통계를 계산할 수 없습니다.")

        n = len(readings)
        mean = sum(readings) / n
        variance = sum((x - mean) ** 2 for x in readings) / n
        std = math.sqrt(variance)

        return {
            "mean": round(mean, 6),
            "std": round(std, 6),
            "min": min(readings),
            "max": max(readings),
            "count": n,
        }
