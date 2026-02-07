"""
데이터 처리 모듈

센서 데이터를 정규화, 필터링, 집계하는 기능을 제공한다.
테스트 구조와 conftest.py 활용을 학습하기 위한 예제 모듈.
"""


def normalize_readings(readings, min_val=None, max_val=None):
    """센서 읽기 값을 0~1 범위로 정규화한다.

    min_val, max_val이 지정되지 않으면 데이터의 최소/최대를 사용한다.

    Args:
        readings: 읽기 값 리스트
        min_val: 최소값 (None이면 자동 계산)
        max_val: 최대값 (None이면 자동 계산)

    Returns:
        정규화된 값 리스트

    Raises:
        ValueError: readings가 비어있을 때
    """
    if not readings:
        raise ValueError("읽기 값이 비어있습니다")

    if min_val is None:
        min_val = min(readings)
    if max_val is None:
        max_val = max(readings)

    if max_val == min_val:
        return [0.5] * len(readings)

    return [(r - min_val) / (max_val - min_val) for r in readings]


def filter_outliers(readings, multiplier=2.0):
    """이상치를 제거한 읽기 값을 반환한다.

    평균 +/- (표준편차 * multiplier) 범위 밖의 값을 제거한다.

    Args:
        readings: 읽기 값 리스트
        multiplier: 표준편차 배수 (기본값: 2.0)

    Returns:
        이상치가 제거된 값 리스트

    Raises:
        ValueError: readings가 비어있을 때
    """
    if not readings:
        raise ValueError("읽기 값이 비어있습니다")

    if len(readings) < 2:
        return readings.copy()

    mean = sum(readings) / len(readings)
    variance = sum((x - mean) ** 2 for x in readings) / len(readings)
    std_dev = variance ** 0.5

    if std_dev == 0:
        return readings.copy()

    lower_bound = mean - std_dev * multiplier
    upper_bound = mean + std_dev * multiplier

    return [r for r in readings if lower_bound <= r <= upper_bound]


def aggregate_sensor_data(sensor_data_list):
    """여러 센서 데이터를 집계한다.

    각 센서의 읽기 값에 대해 평균, 최소, 최대를 계산한다.

    Args:
        sensor_data_list: 센서 데이터 딕셔너리 리스트
            각 딕셔너리: {"sensor_id": ..., "readings": [...], ...}

    Returns:
        집계 결과 딕셔너리:
        {sensor_id: {"mean": ..., "min": ..., "max": ..., "count": ...}}

    Raises:
        ValueError: sensor_data_list가 비어있을 때
    """
    if not sensor_data_list:
        raise ValueError("센서 데이터가 비어있습니다")

    result = {}
    for sensor in sensor_data_list:
        sensor_id = sensor["sensor_id"]
        readings = sensor.get("readings", [])

        if not readings:
            result[sensor_id] = {
                "mean": None,
                "min": None,
                "max": None,
                "count": 0,
            }
        else:
            result[sensor_id] = {
                "mean": round(sum(readings) / len(readings), 4),
                "min": min(readings),
                "max": max(readings),
                "count": len(readings),
            }

    return result


def check_thresholds(sensor_data, config):
    """센서 데이터가 설정된 임계값을 초과하는지 확인한다.

    Args:
        sensor_data: 센서 데이터 딕셔너리
            {"sensor_type": ..., "readings": [...]}
        config: 설정 딕셔너리
            {"temperature_threshold": ..., "vibration_threshold": ..., ...}

    Returns:
        딕셔너리: {"exceeded": bool, "max_value": ..., "threshold": ...}
    """
    sensor_type = sensor_data.get("sensor_type", "")
    readings = sensor_data.get("readings", [])

    # 센서 타입별 임계값 매핑
    threshold_map = {
        "temperature": config.get("temperature_threshold", 80.0),
        "vibration": config.get("vibration_threshold", 7.1),
        "pressure": config.get("pressure_threshold", 100.0),
    }

    threshold = threshold_map.get(sensor_type)

    if threshold is None or not readings:
        return {"exceeded": False, "max_value": None, "threshold": None}

    max_value = max(readings)
    return {
        "exceeded": max_value >= threshold,
        "max_value": max_value,
        "threshold": threshold,
    }


def generate_summary_report(sensor_data_list, config):
    """센서 데이터 요약 보고서를 생성한다.

    Args:
        sensor_data_list: 센서 데이터 딕셔너리 리스트
        config: 설정 딕셔너리

    Returns:
        요약 보고서 딕셔너리
    """
    if not sensor_data_list:
        return {"total_sensors": 0, "alerts": [], "summary": {}}

    aggregated = aggregate_sensor_data(sensor_data_list)
    alerts = []

    for sensor in sensor_data_list:
        threshold_result = check_thresholds(sensor, config)
        if threshold_result["exceeded"]:
            alerts.append({
                "sensor_id": sensor["sensor_id"],
                "sensor_type": sensor.get("sensor_type", "unknown"),
                "max_value": threshold_result["max_value"],
                "threshold": threshold_result["threshold"],
            })

    return {
        "total_sensors": len(sensor_data_list),
        "alerts": alerts,
        "summary": aggregated,
    }
