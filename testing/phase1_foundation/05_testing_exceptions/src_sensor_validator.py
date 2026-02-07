"""
센서 데이터 검증 모듈

센서 데이터의 유효성을 검증하고, 잘못된 데이터에 대해
적절한 커스텀 예외를 발생시킨다.
"""

import warnings


# ============================================================
# 커스텀 예외 클래스 계층 구조
# ============================================================

class SensorError(Exception):
    """센서 관련 기본 예외 클래스.

    모든 센서 예외의 부모 클래스로, 공통 속성을 정의한다.
    """

    def __init__(self, sensor_id, message):
        self.sensor_id = sensor_id
        self.message = message
        super().__init__(f"[{sensor_id}] {message}")


class SensorDataError(SensorError):
    """센서 데이터 형식 또는 내용 오류.

    데이터가 잘못된 형식이거나 누락된 필드가 있을 때 발생한다.
    """

    def __init__(self, sensor_id, message, error_code="E000"):
        self.error_code = error_code
        super().__init__(sensor_id, f"{message} (코드: {error_code})")


class SensorRangeError(SensorError):
    """센서 값이 유효 범위를 벗어남.

    측정값이 센서의 물리적 측정 범위를 초과할 때 발생한다.
    """

    def __init__(self, sensor_id, value, valid_range):
        self.value = value
        self.valid_range = valid_range
        message = f"값 {value}가 유효 범위 {valid_range}를 벗어남"
        super().__init__(sensor_id, message)


class SensorTimeoutError(SensorError):
    """센서 통신 타임아웃.

    센서로부터 지정된 시간 내에 응답이 없을 때 발생한다.
    """

    def __init__(self, sensor_id, timeout_seconds):
        self.timeout_seconds = timeout_seconds
        message = f"{timeout_seconds}초 동안 응답 없음 (타임아웃)"
        super().__init__(sensor_id, message)


# ============================================================
# 검증 함수들
# ============================================================

def validate_sensor_data(data):
    """센서 데이터의 기본 구조를 검증한다.

    필수 필드: sensor_id, sensor_type, readings

    Args:
        data: 센서 데이터 딕셔너리

    Returns:
        True (검증 통과)

    Raises:
        SensorDataError: 필수 필드가 누락되었을 때
        TypeError: data가 딕셔너리가 아닐 때
    """
    if not isinstance(data, dict):
        raise TypeError("센서 데이터는 딕셔너리여야 합니다")

    required_fields = ["sensor_id", "sensor_type", "readings"]
    for field in required_fields:
        if field not in data:
            sensor_id = data.get("sensor_id", "UNKNOWN")
            raise SensorDataError(
                sensor_id,
                f"필수 필드 '{field}'가 누락됨",
                error_code="E001",
            )

    if not isinstance(data["readings"], list):
        raise SensorDataError(
            data["sensor_id"],
            "readings 필드는 리스트여야 합니다",
            error_code="E002",
        )

    return True


def validate_temperature_reading(sensor_id, value, min_temp=-50, max_temp=200):
    """온도 읽기 값의 범위를 검증한다.

    Args:
        sensor_id: 센서 ID
        value: 온도 값
        min_temp: 유효 최소 온도 (기본: -50)
        max_temp: 유효 최대 온도 (기본: 200)

    Returns:
        True (검증 통과)

    Raises:
        SensorRangeError: 온도가 유효 범위를 벗어날 때
        TypeError: value가 숫자가 아닐 때
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"온도 값은 숫자여야 합니다: {type(value)}")

    if value < min_temp or value > max_temp:
        raise SensorRangeError(
            sensor_id,
            value,
            valid_range=(min_temp, max_temp),
        )

    return True


def validate_readings_batch(sensor_id, readings, valid_range=(-50, 200)):
    """센서 읽기 값 묶음을 검증한다.

    모든 값을 검증하고, 범위를 약간 벗어나는 값에 대해서는 경고를 발생시킨다.

    Args:
        sensor_id: 센서 ID
        readings: 읽기 값 리스트
        valid_range: 유효 범위 튜플

    Returns:
        유효한 읽기 값 리스트

    Raises:
        SensorDataError: readings가 비어있을 때
        SensorRangeError: 값이 유효 범위를 크게 벗어날 때 (범위의 2배 이상)
    """
    if not readings:
        raise SensorDataError(
            sensor_id,
            "읽기 값이 비어있습니다",
            error_code="E003",
        )

    min_val, max_val = valid_range
    range_span = max_val - min_val
    valid_readings = []

    for i, value in enumerate(readings):
        if not isinstance(value, (int, float)):
            raise SensorDataError(
                sensor_id,
                f"인덱스 {i}의 값 '{value}'는 숫자가 아닙니다",
                error_code="E004",
            )

        # 범위를 크게 벗어남 (2배 이상) → 에러
        if value < min_val - range_span or value > max_val + range_span:
            raise SensorRangeError(
                sensor_id, value, valid_range
            )

        # 범위를 약간 벗어남 → 경고 후 제외
        if value < min_val or value > max_val:
            warnings.warn(
                f"[{sensor_id}] 인덱스 {i}의 값 {value}가 "
                f"유효 범위 {valid_range}를 벗어남 (경고)",
                UserWarning,
            )
            continue

        valid_readings.append(value)

    return valid_readings


def check_sensor_connection(sensor_id, response_time, timeout=5.0):
    """센서 연결 상태를 확인한다.

    Args:
        sensor_id: 센서 ID
        response_time: 응답 시간 (초)
        timeout: 타임아웃 기준 (초, 기본: 5.0)

    Returns:
        "connected" (정상 연결)

    Raises:
        SensorTimeoutError: 응답 시간이 타임아웃을 초과할 때
    """
    if response_time > timeout:
        raise SensorTimeoutError(sensor_id, timeout)

    # 응답이 느리면 경고
    if response_time > timeout * 0.8:
        warnings.warn(
            f"[{sensor_id}] 응답 시간 {response_time}초 - 연결 불안정",
            UserWarning,
        )

    return "connected"
