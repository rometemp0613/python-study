"""
계산 모듈

공장 설비 모니터링에 필요한 기본 수학 연산 및 온도 관련 함수들.
pytest 기본기 학습을 위한 예제 코드.
"""


def add(a, b):
    """두 수를 더한다.

    Args:
        a: 첫 번째 수
        b: 두 번째 수

    Returns:
        두 수의 합
    """
    return a + b


def subtract(a, b):
    """두 수의 차를 계산한다.

    Args:
        a: 피감수
        b: 감수

    Returns:
        a - b
    """
    return a - b


def multiply(a, b):
    """두 수를 곱한다.

    Args:
        a: 첫 번째 수
        b: 두 번째 수

    Returns:
        두 수의 곱
    """
    return a * b


def divide(a, b):
    """두 수의 나눗셈을 수행한다.

    Args:
        a: 피제수 (나눠지는 수)
        b: 제수 (나누는 수)

    Returns:
        a / b (float)

    Raises:
        ZeroDivisionError: b가 0일 때
    """
    if b == 0:
        raise ZeroDivisionError("0으로 나눌 수 없습니다")
    return a / b


def celsius_to_fahrenheit(celsius):
    """섭씨를 화씨로 변환한다.

    공식: F = C * 9/5 + 32

    Args:
        celsius: 섭씨 온도

    Returns:
        화씨 온도 (float)
    """
    return celsius * 9 / 5 + 32


def fahrenheit_to_celsius(fahrenheit):
    """화씨를 섭씨로 변환한다.

    공식: C = (F - 32) * 5/9

    Args:
        fahrenheit: 화씨 온도

    Returns:
        섭씨 온도 (float)
    """
    return (fahrenheit - 32) * 5 / 9


def detect_anomaly_temperature(readings, threshold_multiplier=2.0):
    """이상 온도를 감지한다.

    평균에서 표준편차 * threshold_multiplier 이상 벗어난 값을 이상치로 판단한다.

    Args:
        readings: 온도 읽기 값 리스트
        threshold_multiplier: 이상치 판단 배수 (기본값: 2.0)

    Returns:
        이상치 리스트 (딕셔너리: {"index": 인덱스, "value": 값, "deviation": 편차})

    Raises:
        ValueError: 읽기 값이 2개 미만일 때
    """
    if len(readings) < 2:
        raise ValueError("이상치 감지를 위해 최소 2개의 읽기 값이 필요합니다")

    # 평균 계산
    mean = sum(readings) / len(readings)

    # 표준편차 계산
    variance = sum((x - mean) ** 2 for x in readings) / len(readings)
    std_dev = variance ** 0.5

    # 이상치가 없는 경우 (모든 값이 동일)
    if std_dev == 0:
        return []

    # 이상치 탐지
    threshold = std_dev * threshold_multiplier
    anomalies = []
    for i, value in enumerate(readings):
        deviation = abs(value - mean)
        if deviation >= threshold:
            anomalies.append({
                "index": i,
                "value": value,
                "deviation": round(deviation, 4),
            })

    return anomalies


def moving_average(values, window_size):
    """이동 평균을 계산한다.

    Args:
        values: 값 리스트
        window_size: 윈도우 크기

    Returns:
        이동 평균 리스트

    Raises:
        ValueError: window_size가 0 이하이거나 values 길이보다 클 때
    """
    if window_size <= 0:
        raise ValueError("윈도우 크기는 1 이상이어야 합니다")
    if window_size > len(values):
        raise ValueError("윈도우 크기가 데이터 길이보다 클 수 없습니다")

    result = []
    for i in range(len(values) - window_size + 1):
        window = values[i:i + window_size]
        avg = sum(window) / window_size
        result.append(round(avg, 4))

    return result
