"""
성능이 중요한 센서 데이터 처리 함수들.

이 모듈은 예지보전 시스템에서 실시간 센서 데이터를 처리하는
성능 민감(performance-critical) 함수들을 포함한다.
pytest-benchmark로 벤치마크 테스트할 대상이다.
"""

import math
from typing import List, Dict, Any, Optional


def calculate_rms(values: List[float]) -> float:
    """
    RMS(Root Mean Square) 값을 계산한다.

    RMS는 진동 센서 데이터의 전체적인 에너지 수준을 나타내는
    핵심 지표이다. 설비의 건강 상태를 판단하는 데 사용된다.

    Args:
        values: 센서 측정값 리스트

    Returns:
        RMS 값 (float)

    Raises:
        ValueError: 빈 리스트가 입력된 경우
    """
    if not values:
        raise ValueError("빈 데이터로는 RMS를 계산할 수 없습니다")

    # 각 값의 제곱의 평균의 제곱근
    sum_of_squares = sum(v ** 2 for v in values)
    mean_of_squares = sum_of_squares / len(values)
    return math.sqrt(mean_of_squares)


def detect_peaks(values: List[float], threshold: float) -> List[Dict[str, Any]]:
    """
    임계값을 초과하는 피크를 감지한다.

    센서 데이터에서 비정상적으로 높은 값(피크)을 찾는다.
    이는 설비 이상의 초기 징후일 수 있다.

    Args:
        values: 센서 측정값 리스트
        threshold: 피크 판정 임계값

    Returns:
        피크 정보 딕셔너리 리스트 [{index, value, severity}]
    """
    if not values:
        return []

    peaks = []
    for i, value in enumerate(values):
        if value > threshold:
            # 심각도 계산: 임계값 대비 초과 비율
            severity = (value - threshold) / threshold
            severity_level = (
                "critical" if severity > 0.5
                else "warning" if severity > 0.2
                else "info"
            )
            peaks.append({
                "index": i,
                "value": value,
                "severity": severity_level,
            })

    return peaks


def moving_average(values: List[float], window: int) -> List[float]:
    """
    이동 평균을 계산한다.

    센서 데이터의 노이즈를 제거하고 트렌드를 파악하기 위해
    이동 평균(moving average)을 사용한다.

    Args:
        values: 센서 측정값 리스트
        window: 이동 평균 윈도우 크기

    Returns:
        이동 평균 값 리스트

    Raises:
        ValueError: 윈도우가 0 이하이거나 데이터보다 큰 경우
    """
    if window <= 0:
        raise ValueError("윈도우 크기는 1 이상이어야 합니다")
    if window > len(values):
        raise ValueError("윈도우 크기가 데이터 길이보다 클 수 없습니다")

    result = []
    for i in range(len(values) - window + 1):
        window_values = values[i:i + window]
        avg = sum(window_values) / window
        result.append(avg)

    return result


def batch_process_sensors(sensor_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    여러 센서 데이터를 일괄 처리한다.

    공장의 모든 센서 데이터를 한 번에 처리하여
    각 센서의 상태 요약 정보를 반환한다.

    Args:
        sensor_data_list: 센서 데이터 딕셔너리 리스트
            각 항목은 {"sensor_id": str, "values": List[float], "threshold": float}

    Returns:
        처리 결과 리스트 [{sensor_id, rms, peak_count, avg, status}]
    """
    results = []

    for sensor_data in sensor_data_list:
        sensor_id = sensor_data["sensor_id"]
        values = sensor_data["values"]
        threshold = sensor_data.get("threshold", 100.0)

        # 빈 데이터 처리
        if not values:
            results.append({
                "sensor_id": sensor_id,
                "rms": 0.0,
                "peak_count": 0,
                "avg": 0.0,
                "status": "no_data",
            })
            continue

        # 각 지표 계산
        rms = calculate_rms(values)
        peaks = detect_peaks(values, threshold)
        avg = sum(values) / len(values)

        # 상태 판정
        if len(peaks) > 5:
            status = "critical"
        elif len(peaks) > 2:
            status = "warning"
        elif rms > threshold * 0.8:
            status = "watch"
        else:
            status = "normal"

        results.append({
            "sensor_id": sensor_id,
            "rms": round(rms, 4),
            "peak_count": len(peaks),
            "avg": round(avg, 4),
            "status": status,
        })

    return results


def calculate_crest_factor(values: List[float]) -> float:
    """
    크레스트 팩터(Crest Factor)를 계산한다.

    크레스트 팩터 = 최대값 / RMS
    베어링 결함 초기 단계에서 이 값이 증가하는 경향이 있다.

    Args:
        values: 센서 측정값 리스트

    Returns:
        크레스트 팩터 값
    """
    if not values:
        raise ValueError("빈 데이터로는 크레스트 팩터를 계산할 수 없습니다")

    rms = calculate_rms(values)
    if rms == 0:
        return 0.0

    peak = max(abs(v) for v in values)
    return peak / rms
