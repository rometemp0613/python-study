"""
센서 데이터 변환 함수 모듈.

이 모듈은 센서 데이터를 변환, 인코딩, 검증하는
순수 함수(pure function)들을 포함한다.

순수 함수는 속성 기반 테스트(property-based testing)에
매우 적합하다. 같은 입력에 항상 같은 출력을 보장하기 때문이다.
"""

from typing import List, Dict, Optional, Tuple


# 센서 타입과 코드 매핑 테이블
SENSOR_TYPE_MAP = {
    "temperature": 1,
    "vibration": 2,
    "pressure": 3,
    "current": 4,
    "humidity": 5,
}

# 역매핑 테이블 (코드 → 타입)
SENSOR_CODE_MAP = {v: k for k, v in SENSOR_TYPE_MAP.items()}


def normalize(values: List[float]) -> List[float]:
    """
    값들을 0~1 범위로 정규화한다 (min-max scaling).

    불변 속성(invariant):
    - 결과의 모든 값은 0 이상 1 이하이다
    - 최솟값은 0.0으로 매핑된다
    - 최댓값은 1.0으로 매핑된다
    - 결과 리스트의 길이는 입력과 동일하다
    - 입력의 순서 관계가 보존된다

    Args:
        values: 정규화할 값 리스트 (최소 2개)

    Returns:
        0~1 범위로 정규화된 값 리스트

    Raises:
        ValueError: 리스트가 2개 미만이거나 모든 값이 동일한 경우
    """
    if len(values) < 2:
        raise ValueError("정규화하려면 최소 2개의 값이 필요합니다")

    min_val = min(values)
    max_val = max(values)

    if min_val == max_val:
        raise ValueError("모든 값이 동일하면 정규화할 수 없습니다")

    range_val = max_val - min_val
    return [(v - min_val) / range_val for v in values]


def encode_sensor_type(sensor_type: str) -> int:
    """
    센서 타입 문자열을 정수 코드로 인코딩한다.

    왕복 속성(roundtrip):
    - decode_sensor_type(encode_sensor_type(x)) == x

    Args:
        sensor_type: 센서 타입 문자열

    Returns:
        정수 코드

    Raises:
        ValueError: 알 수 없는 센서 타입
    """
    sensor_type_lower = sensor_type.lower().strip()
    if sensor_type_lower not in SENSOR_TYPE_MAP:
        raise ValueError(
            f"알 수 없는 센서 타입: {sensor_type}. "
            f"허용: {list(SENSOR_TYPE_MAP.keys())}"
        )
    return SENSOR_TYPE_MAP[sensor_type_lower]


def decode_sensor_type(code: int) -> str:
    """
    정수 코드를 센서 타입 문자열로 디코딩한다.

    왕복 속성(roundtrip):
    - encode_sensor_type(decode_sensor_type(x)) == x

    Args:
        code: 정수 코드

    Returns:
        센서 타입 문자열

    Raises:
        ValueError: 알 수 없는 코드
    """
    if code not in SENSOR_CODE_MAP:
        raise ValueError(
            f"알 수 없는 센서 코드: {code}. "
            f"허용: {list(SENSOR_CODE_MAP.keys())}"
        )
    return SENSOR_CODE_MAP[code]


def validate_reading(
    value: float,
    min_val: float,
    max_val: float
) -> Dict[str, any]:
    """
    측정값이 유효 범위 내에 있는지 검증한다.

    불변 속성:
    - min_val <= max_val이면 항상 결과를 반환한다
    - is_valid가 True이면 min_val <= value <= max_val이다
    - is_valid가 False이면 value < min_val 또는 value > max_val이다
    - deviation은 항상 0 이상이다

    Args:
        value: 측정값
        min_val: 최소 허용값
        max_val: 최대 허용값

    Returns:
        검증 결과 딕셔너리:
        {
            "is_valid": bool,
            "value": float,
            "deviation": float (범위 이탈 정도, 0이면 정상),
            "status": str ("normal", "below_range", "above_range")
        }

    Raises:
        ValueError: min_val > max_val인 경우
    """
    if min_val > max_val:
        raise ValueError(
            f"최소값({min_val})이 최대값({max_val})보다 클 수 없습니다"
        )

    if value < min_val:
        deviation = min_val - value
        return {
            "is_valid": False,
            "value": value,
            "deviation": deviation,
            "status": "below_range",
        }
    elif value > max_val:
        deviation = value - max_val
        return {
            "is_valid": False,
            "value": value,
            "deviation": deviation,
            "status": "above_range",
        }
    else:
        return {
            "is_valid": True,
            "value": value,
            "deviation": 0.0,
            "status": "normal",
        }


def aggregate_readings(readings: List[float]) -> Dict[str, float]:
    """
    측정값 리스트를 집계한다.

    동치 속성(equivalence):
    - mean == sum / count
    - min_val <= mean <= max_val
    - count == len(readings)

    불변 속성:
    - sum == sum(readings)
    - min_val <= 모든 값
    - max_val >= 모든 값

    Args:
        readings: 측정값 리스트

    Returns:
        집계 결과 딕셔너리:
        {
            "count": int,
            "sum": float,
            "mean": float,
            "min_val": float,
            "max_val": float,
            "range": float (max - min),
        }

    Raises:
        ValueError: 빈 리스트인 경우
    """
    if not readings:
        raise ValueError("빈 측정값 리스트를 집계할 수 없습니다")

    total = sum(readings)
    count = len(readings)
    min_val = min(readings)
    max_val = max(readings)

    return {
        "count": count,
        "sum": total,
        "mean": total / count,
        "min_val": min_val,
        "max_val": max_val,
        "range": max_val - min_val,
    }


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    값을 지정된 범위로 제한한다.

    불변 속성:
    - 결과는 항상 min_val 이상이다
    - 결과는 항상 max_val 이하이다
    - min_val <= value <= max_val이면 결과 == value (멱등성)

    Args:
        value: 원본 값
        min_val: 하한값
        max_val: 상한값

    Returns:
        범위로 제한된 값
    """
    if min_val > max_val:
        raise ValueError(
            f"최소값({min_val})이 최대값({max_val})보다 클 수 없습니다"
        )
    return max(min_val, min(value, max_val))
