"""
센서 유틸리티 모듈

공장 설비의 센서 데이터를 처리하기 위한 유틸리티 함수들.
각 함수에 doctest 예시가 포함되어 있다.
"""


def psi_to_bar(psi):
    """PSI(Pounds per Square Inch)를 Bar 단위로 변환한다.

    1 PSI = 0.0689476 Bar

    Args:
        psi: PSI 단위의 압력 값 (0 이상)

    Returns:
        Bar 단위의 압력 값 (소수점 5자리 반올림)

    Raises:
        ValueError: psi가 음수일 때
        TypeError: psi가 숫자가 아닐 때

    >>> psi_to_bar(14.696)
    1.01325
    >>> psi_to_bar(0)
    0.0
    >>> psi_to_bar(100)
    6.89476
    """
    if not isinstance(psi, (int, float)):
        raise TypeError("PSI 값은 숫자여야 합니다")
    if psi < 0:
        raise ValueError("PSI 값은 0 이상이어야 합니다")
    return round(psi * 0.0689476, 5)


def bar_to_psi(bar):
    """Bar를 PSI 단위로 변환한다.

    1 Bar = 14.5038 PSI

    Args:
        bar: Bar 단위의 압력 값 (0 이상)

    Returns:
        PSI 단위의 압력 값 (소수점 3자리 반올림)

    Raises:
        ValueError: bar가 음수일 때

    >>> bar_to_psi(1.0)
    14.504
    >>> bar_to_psi(0)
    0.0
    """
    if not isinstance(bar, (int, float)):
        raise TypeError("Bar 값은 숫자여야 합니다")
    if bar < 0:
        raise ValueError("Bar 값은 0 이상이어야 합니다")
    return round(bar * 14.5038, 3)


def normalize_reading(value, min_val, max_val):
    """센서 읽기 값을 0~1 범위로 정규화한다.

    정규화 공식: (value - min) / (max - min)

    Args:
        value: 센서 읽기 값
        min_val: 가능한 최소값
        max_val: 가능한 최대값

    Returns:
        0.0 ~ 1.0 사이의 정규화된 값

    Raises:
        ValueError: min_val과 max_val이 같을 때

    >>> normalize_reading(50, 0, 100)
    0.5
    >>> normalize_reading(0, 0, 100)
    0.0
    >>> normalize_reading(100, 0, 100)
    1.0
    >>> normalize_reading(75, 50, 100)
    0.5
    """
    if max_val == min_val:
        raise ValueError("최대값과 최소값이 같을 수 없습니다")
    return (value - min_val) / (max_val - min_val)


def calculate_statistics(readings):
    """센서 읽기 값들의 기본 통계를 계산한다.

    Args:
        readings: 센서 읽기 값 리스트

    Returns:
        딕셔너리: {"mean": 평균, "min": 최소, "max": 최대, "range": 범위}

    Raises:
        ValueError: 읽기 값이 비어있을 때

    >>> stats = calculate_statistics([10, 20, 30, 40, 50])
    >>> stats["mean"]
    30.0
    >>> stats["min"]
    10
    >>> stats["max"]
    50
    >>> stats["range"]
    40
    """
    if not readings:
        raise ValueError("읽기 값이 비어있습니다")

    return {
        "mean": sum(readings) / len(readings),
        "min": min(readings),
        "max": max(readings),
        "range": max(readings) - min(readings),
    }


def classify_vibration_level(mm_per_sec):
    """진동 수준을 ISO 10816 기준에 따라 분류한다.

    Args:
        mm_per_sec: 진동 속도 (mm/s RMS)

    Returns:
        등급 문자열 ("양호", "허용", "주의", "위험")

    >>> classify_vibration_level(1.0)
    '양호'
    >>> classify_vibration_level(3.0)
    '허용'
    >>> classify_vibration_level(5.0)
    '주의'
    >>> classify_vibration_level(10.0)
    '위험'
    """
    if mm_per_sec < 0:
        raise ValueError("진동 속도는 0 이상이어야 합니다")

    if mm_per_sec <= 1.8:
        return "양호"
    elif mm_per_sec <= 4.5:
        return "허용"
    elif mm_per_sec <= 7.1:
        return "주의"
    else:
        return "위험"
