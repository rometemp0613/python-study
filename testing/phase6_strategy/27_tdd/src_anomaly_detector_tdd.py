"""
센서 이상 감지기 - TDD로 개발된 모듈

이 모듈은 TDD(Test-Driven Development) 방식으로 단계적으로 구현되었습니다.
각 메서드는 테스트가 먼저 작성된 후 구현되었습니다.

예지보전 시스템에서 센서 데이터의 이상치를 감지하는 데 사용됩니다.
"""

import math
from typing import List, Optional


class SensorAnomalyDetector:
    """
    센서 이상 감지기

    센서에서 수집된 데이터를 기반으로 통계적 방법(n-시그마)을 사용하여
    이상치를 감지합니다.

    TDD 개발 순서:
    1. 빈 감지기 생성 (get_reading_count)
    2. 데이터 추가 (add_reading)
    3. 평균 계산 (get_mean)
    4. 표준편차 계산 (get_std)
    5. 이상치 판별 (is_anomaly)
    6. 이상치 카운트 (get_anomaly_count)
    """

    def __init__(self):
        """감지기를 초기화합니다. 빈 상태로 시작합니다."""
        self._readings: List[float] = []
        self._anomaly_count: int = 0

    def add_reading(self, value: float) -> None:
        """
        센서 측정값을 추가합니다.

        Args:
            value: 센서 측정값 (유한한 숫자여야 함)

        Raises:
            ValueError: NaN 또는 무한대 값이 입력된 경우
            TypeError: 숫자가 아닌 값이 입력된 경우
        """
        # 입력값 검증 - TDD 3번째 사이클에서 추가됨
        if not isinstance(value, (int, float)):
            raise TypeError(f"숫자 타입이 필요합니다. 입력된 타입: {type(value).__name__}")

        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"유한한 숫자만 허용됩니다. 입력값: {value}")

        self._readings.append(float(value))

    def get_reading_count(self) -> int:
        """현재까지 추가된 측정값의 개수를 반환합니다."""
        return len(self._readings)

    def get_mean(self) -> float:
        """
        현재까지의 측정값들의 평균을 계산합니다.

        Returns:
            측정값들의 산술 평균

        Raises:
            ValueError: 데이터가 없는 경우
        """
        if not self._readings:
            raise ValueError("데이터가 없습니다. 먼저 add_reading()으로 데이터를 추가하세요.")

        return sum(self._readings) / len(self._readings)

    def get_std(self) -> float:
        """
        현재까지의 측정값들의 표준편차를 계산합니다 (모표준편차).

        Returns:
            측정값들의 모표준편차

        Raises:
            ValueError: 데이터가 없는 경우
        """
        if not self._readings:
            raise ValueError("데이터가 없습니다. 먼저 add_reading()으로 데이터를 추가하세요.")

        mean = self.get_mean()
        variance = sum((x - mean) ** 2 for x in self._readings) / len(self._readings)
        return math.sqrt(variance)

    def is_anomaly(self, value: float, n_sigma: float = 3.0) -> bool:
        """
        주어진 값이 이상치인지 판별합니다.

        n-시그마 방법을 사용합니다:
        |value - mean| > n_sigma * std 이면 이상치로 판단합니다.

        Args:
            value: 판별할 값
            n_sigma: 시그마 배수 (기본값: 3.0)

        Returns:
            이상치 여부

        Raises:
            ValueError: 데이터가 2개 미만인 경우
        """
        if len(self._readings) < 2:
            raise ValueError("이상치 판별에는 최소 2개의 데이터가 필요합니다.")

        mean = self.get_mean()
        std = self.get_std()

        # 표준편차가 0인 경우 (모든 값이 동일)
        if std == 0:
            is_anomalous = value != mean
        else:
            is_anomalous = abs(value - mean) > n_sigma * std

        # 이상치로 판별되면 카운트 증가
        if is_anomalous:
            self._anomaly_count += 1

        return is_anomalous

    def get_anomaly_count(self) -> int:
        """
        지금까지 감지된 이상치의 총 개수를 반환합니다.

        Returns:
            감지된 이상치 수
        """
        return self._anomaly_count

    def get_readings(self) -> List[float]:
        """
        현재까지 저장된 모든 측정값의 복사본을 반환합니다.

        Returns:
            측정값 리스트의 복사본
        """
        return self._readings.copy()

    def reset(self) -> None:
        """감지기의 상태를 초기화합니다."""
        self._readings.clear()
        self._anomaly_count = 0
