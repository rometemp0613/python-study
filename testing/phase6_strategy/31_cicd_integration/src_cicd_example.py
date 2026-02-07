"""
CI/CD 예시 모듈

CI/CD 파이프라인에서 테스트되는 예지보전 유틸리티 함수들입니다.
JUnit XML 출력, 커버리지 리포트 등 CI 도구와의 호환성을 보여줍니다.
"""

import math
from typing import Dict, List, Optional, Tuple


def validate_sensor_reading(value: float, sensor_type: str = "temperature") -> bool:
    """
    센서 측정값의 유효성을 검증합니다.

    Args:
        value: 센서 측정값
        sensor_type: 센서 종류 ("temperature", "pressure", "vibration")

    Returns:
        유효 여부

    Raises:
        ValueError: 알 수 없는 센서 종류
    """
    valid_ranges = {
        "temperature": (-50.0, 500.0),    # 섭씨
        "pressure": (0.0, 1000.0),         # kPa
        "vibration": (0.0, 100.0),         # mm/s
    }

    if sensor_type not in valid_ranges:
        raise ValueError(f"알 수 없는 센서 종류: {sensor_type}")

    min_val, max_val = valid_ranges[sensor_type]
    return min_val <= value <= max_val


def calculate_health_score(readings: List[float],
                           baseline_mean: float,
                           baseline_std: float) -> float:
    """
    장비 건강 점수를 계산합니다 (0.0 ~ 1.0).

    현재 측정값과 기준선(baseline)의 차이를 기반으로 계산합니다.

    Args:
        readings: 현재 측정값 리스트
        baseline_mean: 정상 상태 평균
        baseline_std: 정상 상태 표준편차

    Returns:
        건강 점수 (1.0 = 완벽, 0.0 = 위험)

    Raises:
        ValueError: 빈 리스트이거나 baseline_std가 0 이하인 경우
    """
    if not readings:
        raise ValueError("측정값 리스트가 비어 있습니다.")

    if baseline_std <= 0:
        raise ValueError("기준선 표준편차는 0보다 커야 합니다.")

    current_mean = sum(readings) / len(readings)

    # 기준선과의 편차 (z-score)
    z_score = abs(current_mean - baseline_mean) / baseline_std

    # z-score를 0~1 범위의 건강 점수로 변환
    # z_score가 0이면 건강 점수 1.0, z_score가 클수록 0에 가까워짐
    health_score = max(0.0, 1.0 - (z_score / 6.0))

    return round(health_score, 4)


def classify_equipment_status(health_score: float) -> str:
    """
    건강 점수를 기반으로 장비 상태를 분류합니다.

    Args:
        health_score: 건강 점수 (0.0 ~ 1.0)

    Returns:
        상태 문자열 ("good", "warning", "critical", "failure")
    """
    if health_score >= 0.8:
        return "good"
    elif health_score >= 0.5:
        return "warning"
    elif health_score >= 0.2:
        return "critical"
    else:
        return "failure"


def generate_maintenance_report(
    equipment_id: str,
    readings: List[float],
    baseline_mean: float,
    baseline_std: float,
) -> Dict:
    """
    유지보수 보고서를 생성합니다.

    Args:
        equipment_id: 장비 ID
        readings: 현재 측정값 리스트
        baseline_mean: 정상 상태 평균
        baseline_std: 정상 상태 표준편차

    Returns:
        유지보수 보고서 딕셔너리
    """
    health = calculate_health_score(readings, baseline_mean, baseline_std)
    status = classify_equipment_status(health)

    current_mean = sum(readings) / len(readings)
    current_std = math.sqrt(
        sum((x - current_mean) ** 2 for x in readings) / len(readings)
    )

    report = {
        "equipment_id": equipment_id,
        "health_score": health,
        "status": status,
        "current_mean": round(current_mean, 4),
        "current_std": round(current_std, 4),
        "baseline_mean": baseline_mean,
        "baseline_std": baseline_std,
        "reading_count": len(readings),
        "recommendation": _get_recommendation(status),
    }

    return report


def _get_recommendation(status: str) -> str:
    """
    장비 상태에 따른 권장 조치를 반환합니다.

    Args:
        status: 장비 상태

    Returns:
        권장 조치 문자열
    """
    recommendations = {
        "good": "정상 운전을 유지하세요.",
        "warning": "모니터링을 강화하고 유지보수 일정을 확인하세요.",
        "critical": "즉시 점검이 필요합니다. 유지보수를 예약하세요.",
        "failure": "장비를 즉시 정지하고 긴급 점검을 실시하세요.",
    }
    return recommendations.get(status, "상태를 확인할 수 없습니다.")


def batch_validate_readings(
    readings: List[Tuple[str, float, str]]
) -> Dict[str, List]:
    """
    여러 센서 측정값을 일괄 검증합니다.

    Args:
        readings: (sensor_id, value, sensor_type) 튜플 리스트

    Returns:
        {"valid": [...], "invalid": [...]} 형태의 딕셔너리
    """
    result = {"valid": [], "invalid": []}

    for sensor_id, value, sensor_type in readings:
        try:
            is_valid = validate_sensor_reading(value, sensor_type)
            entry = {
                "sensor_id": sensor_id,
                "value": value,
                "sensor_type": sensor_type,
            }
            if is_valid:
                result["valid"].append(entry)
            else:
                entry["reason"] = "범위 초과"
                result["invalid"].append(entry)
        except ValueError as e:
            result["invalid"].append({
                "sensor_id": sensor_id,
                "value": value,
                "sensor_type": sensor_type,
                "reason": str(e),
            })

    return result
