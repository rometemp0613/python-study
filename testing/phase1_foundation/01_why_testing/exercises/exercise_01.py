"""
연습 문제 01: 센서 데이터 유효성 검사 테스트 작성하기

아래에 센서 데이터를 검증하는 함수가 제공됩니다.
이 함수들에 대한 테스트를 작성하세요.

실행 방법:
    pytest exercises/exercise_01.py -v
"""

import pytest


# ============================================================
# 테스트 대상 함수들
# ============================================================

def is_valid_temperature(value):
    """온도 값이 유효한 범위(-50 ~ 200도)인지 확인한다.

    Args:
        value: 온도 값

    Returns:
        유효하면 True, 아니면 False
    """
    if not isinstance(value, (int, float)):
        return False
    return -50 <= value <= 200


def filter_valid_readings(readings):
    """유효한 온도 읽기 값만 필터링한다.

    Args:
        readings: 온도 읽기 값 리스트

    Returns:
        유효한 값들만 포함된 리스트
    """
    return [r for r in readings if is_valid_temperature(r)]


def get_temperature_status(temp):
    """온도에 따른 설비 상태를 반환한다.

    Args:
        temp: 섭씨 온도

    Returns:
        상태 딕셔너리 {"status": ..., "action": ...}
    """
    if temp < 0:
        return {"status": "저온", "action": "난방 가동"}
    elif temp < 60:
        return {"status": "정상", "action": "유지"}
    elif temp < 80:
        return {"status": "주의", "action": "모니터링 강화"}
    else:
        return {"status": "위험", "action": "즉시 점검"}


# ============================================================
# TODO: 아래에 테스트를 작성하세요
# ============================================================

class TestIsValidTemperature:
    """is_valid_temperature 함수 테스트"""

    def test_유효한_온도(self):
        """정상 범위 내의 온도값은 True를 반환해야 한다"""
        # TODO: 정상 범위 내의 다양한 온도값으로 테스트하세요
        # 예: 0, 25, 100, -50, 200
        pytest.skip("TODO: 정상 범위 온도 테스트를 구현하세요")

    def test_범위_밖_온도(self):
        """범위 밖의 온도값은 False를 반환해야 한다"""
        # TODO: 범위 밖의 온도값으로 테스트하세요
        # 예: -51, 201, -100, 300
        pytest.skip("TODO: 범위 밖 온도 테스트를 구현하세요")

    def test_잘못된_타입(self):
        """숫자가 아닌 값은 False를 반환해야 한다"""
        # TODO: 문자열, None, 리스트 등 잘못된 타입으로 테스트하세요
        pytest.skip("TODO: 잘못된 타입 테스트를 구현하세요")


class TestFilterValidReadings:
    """filter_valid_readings 함수 테스트"""

    def test_모두_유효한_데이터(self):
        """모든 값이 유효하면 전체가 반환되어야 한다"""
        # TODO: 모든 값이 유효한 리스트로 테스트하세요
        pytest.skip("TODO: 유효한 데이터 필터링 테스트를 구현하세요")

    def test_일부_무효한_데이터(self):
        """무효한 값은 필터링되어야 한다"""
        # TODO: 유효한 값과 무효한 값이 섞인 리스트로 테스트하세요
        pytest.skip("TODO: 무효한 데이터 필터링 테스트를 구현하세요")

    def test_빈_리스트(self):
        """빈 리스트를 전달하면 빈 리스트가 반환되어야 한다"""
        # TODO: 빈 리스트로 테스트하세요
        pytest.skip("TODO: 빈 리스트 테스트를 구현하세요")


class TestGetTemperatureStatus:
    """get_temperature_status 함수 테스트"""

    def test_정상_상태(self):
        """정상 범위 온도에 대해 올바른 상태를 반환해야 한다"""
        # TODO: 정상 범위 온도로 테스트하세요
        # 반환값의 "status"와 "action" 모두 확인하세요
        pytest.skip("TODO: 정상 상태 테스트를 구현하세요")

    def test_위험_상태(self):
        """높은 온도에 대해 '위험' 상태를 반환해야 한다"""
        # TODO: 80도 이상의 온도로 테스트하세요
        pytest.skip("TODO: 위험 상태 테스트를 구현하세요")
