"""
온도 모니터링 모듈 (버그가 수정된 버전)

공장 설비의 온도 센서 데이터를 처리하는 함수들을 제공한다.
src_temperature.py의 버그를 수정한 버전이다.
"""


def celsius_to_fahrenheit(celsius):
    """섭씨 온도를 화씨 온도로 변환한다.

    공식: F = C * 9/5 + 32

    Args:
        celsius: 섭씨 온도 (숫자)

    Returns:
        화씨 온도 (float)
    """
    # 수정됨: 올바른 공식 적용 (+32)
    return celsius * 9 / 5 + 32


def is_overheating(temp_celsius, threshold=80.0):
    """설비가 과열 상태인지 판단한다.

    Args:
        temp_celsius: 현재 섭씨 온도
        threshold: 과열 기준 온도 (기본값: 80도)

    Returns:
        과열이면 True, 아니면 False
    """
    return temp_celsius >= threshold


def calculate_average_temp(readings):
    """센서 읽기 값들의 평균 온도를 계산한다.

    Args:
        readings: 온도 읽기 값 리스트

    Returns:
        평균 온도 (float)

    Raises:
        ValueError: 읽기 값이 비어있을 때
    """
    # 수정됨: 빈 리스트에 대해 예외를 발생시킴
    if not readings:
        raise ValueError("온도 읽기 값이 비어있습니다")
    return sum(readings) / len(readings)


def classify_temperature(temp_celsius):
    """온도를 상태로 분류한다.

    Args:
        temp_celsius: 섭씨 온도

    Returns:
        상태 문자열 ("정상", "주의", "경고", "위험")
    """
    if temp_celsius < 50:
        return "정상"
    elif temp_celsius < 70:
        return "주의"
    elif temp_celsius < 90:
        return "경고"
    else:
        return "위험"
