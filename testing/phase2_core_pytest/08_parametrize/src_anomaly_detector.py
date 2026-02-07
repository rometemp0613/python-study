"""
이상 탐지 모듈

공장 설비의 센서 데이터에서 이상을 탐지하는 기능을 제공한다.
- 단순 임계값 기반 탐지
- 심각도 분류
- 패턴 기반 탐지 (이동 평균 기반)
"""

from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """이상 심각도 레벨"""
    NORMAL = "normal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DetectionResult:
    """이상 탐지 결과"""
    is_anomaly: bool         # 이상 여부
    value: float             # 탐지된 값
    threshold: float         # 사용된 임계값
    severity: Severity       # 심각도
    message: str = ""        # 상세 메시지


class AnomalyDetector:
    """
    센서 데이터 이상 탐지기

    임계값, 심각도 분류, 패턴 분석 기능을 제공한다.
    """

    def detect(self, value: float, threshold: float) -> DetectionResult:
        """
        단순 임계값 기반 이상 탐지.

        Args:
            value: 센서 측정값
            threshold: 이상 판단 임계값

        Returns:
            DetectionResult: 탐지 결과

        Raises:
            ValueError: threshold가 0 이하일 때
        """
        if threshold <= 0:
            raise ValueError("임계값은 0보다 커야 합니다")

        is_anomaly = abs(value) > threshold

        if is_anomaly:
            # 초과 비율에 따라 심각도 결정
            ratio = abs(value) / threshold
            if ratio > 2.0:
                severity = Severity.CRITICAL
            elif ratio > 1.5:
                severity = Severity.HIGH
            elif ratio > 1.0:
                severity = Severity.MEDIUM
            else:
                severity = Severity.NORMAL
        else:
            severity = Severity.NORMAL

        return DetectionResult(
            is_anomaly=is_anomaly,
            value=value,
            threshold=threshold,
            severity=severity,
            message=f"값 {value}이(가) 임계값 {threshold}을(를) {'초과' if is_anomaly else '미초과'}",
        )

    def classify_severity(self, value: float,
                          thresholds: dict[str, float]) -> Severity:
        """
        다단계 임계값을 사용한 심각도 분류.

        Args:
            value: 센서 측정값
            thresholds: 심각도별 임계값 딕셔너리
                        {"low": 50, "medium": 70, "high": 85, "critical": 95}

        Returns:
            Severity: 분류된 심각도 레벨

        Raises:
            ValueError: thresholds에 필수 키가 없을 때
        """
        required_keys = {"low", "medium", "high", "critical"}
        if not required_keys.issubset(thresholds.keys()):
            missing = required_keys - thresholds.keys()
            raise ValueError(f"필수 임계값이 없습니다: {missing}")

        abs_value = abs(value)

        if abs_value >= thresholds["critical"]:
            return Severity.CRITICAL
        elif abs_value >= thresholds["high"]:
            return Severity.HIGH
        elif abs_value >= thresholds["medium"]:
            return Severity.MEDIUM
        elif abs_value >= thresholds["low"]:
            return Severity.LOW
        else:
            return Severity.NORMAL

    def detect_pattern(self, values: list[float],
                       window_size: int = 3) -> dict:
        """
        이동 평균 기반 패턴 탐지.

        연속된 값의 이동 평균을 계산하고, 추세를 분석한다.

        Args:
            values: 시계열 센서 측정값 리스트
            window_size: 이동 평균 윈도우 크기

        Returns:
            dict: {
                "moving_averages": list[float],  # 이동 평균 리스트
                "trend": str,                     # "increasing", "decreasing", "stable"
                "max_deviation": float,           # 이동 평균에서 최대 편차
                "is_anomaly": bool,               # 이상 패턴 여부
            }

        Raises:
            ValueError: values가 window_size보다 짧을 때
            ValueError: window_size가 1 미만일 때
        """
        if window_size < 1:
            raise ValueError("윈도우 크기는 1 이상이어야 합니다")

        if len(values) < window_size:
            raise ValueError(
                f"데이터 길이({len(values)})가 윈도우 크기({window_size})보다 작습니다"
            )

        # 이동 평균 계산
        moving_averages = []
        for i in range(len(values) - window_size + 1):
            window = values[i:i + window_size]
            avg = sum(window) / window_size
            moving_averages.append(round(avg, 4))

        # 추세 분석
        if len(moving_averages) < 2:
            trend = "stable"
        else:
            diffs = [
                moving_averages[i + 1] - moving_averages[i]
                for i in range(len(moving_averages) - 1)
            ]
            avg_diff = sum(diffs) / len(diffs)

            if avg_diff > 0.5:
                trend = "increasing"
            elif avg_diff < -0.5:
                trend = "decreasing"
            else:
                trend = "stable"

        # 최대 편차 계산 (전체 평균 대비)
        overall_avg = sum(values) / len(values)
        max_deviation = max(abs(v - overall_avg) for v in values)
        max_deviation = round(max_deviation, 4)

        # 이상 패턴 판정: 최대 편차가 전체 평균의 50% 이상이면 이상
        if overall_avg != 0:
            is_anomaly = (max_deviation / abs(overall_avg)) > 0.5
        else:
            is_anomaly = max_deviation > 0

        return {
            "moving_averages": moving_averages,
            "trend": trend,
            "max_deviation": max_deviation,
            "is_anomaly": is_anomaly,
        }
