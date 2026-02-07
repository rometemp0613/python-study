"""
연습 문제 01: 풀이

센서 데이터 유효성 검사 함수들에 대한 테스트 풀이.

실행 방법:
    pytest exercises/solution_01.py -v
"""

import pytest


# ============================================================
# 테스트 대상 함수들
# ============================================================

def is_valid_temperature(value):
    """온도 값이 유효한 범위(-50 ~ 200도)인지 확인한다."""
    if not isinstance(value, (int, float)):
        return False
    return -50 <= value <= 200


def filter_valid_readings(readings):
    """유효한 온도 읽기 값만 필터링한다."""
    return [r for r in readings if is_valid_temperature(r)]


def get_temperature_status(temp):
    """온도에 따른 설비 상태를 반환한다."""
    if temp < 0:
        return {"status": "저온", "action": "난방 가동"}
    elif temp < 60:
        return {"status": "정상", "action": "유지"}
    elif temp < 80:
        return {"status": "주의", "action": "모니터링 강화"}
    else:
        return {"status": "위험", "action": "즉시 점검"}


# ============================================================
# 테스트 코드 (풀이)
# ============================================================

class TestIsValidTemperature:
    """is_valid_temperature 함수 테스트"""

    def test_유효한_온도(self):
        """정상 범위 내의 온도값은 True를 반환해야 한다"""
        assert is_valid_temperature(0) is True
        assert is_valid_temperature(25) is True
        assert is_valid_temperature(100) is True
        assert is_valid_temperature(-50) is True   # 경계값: 최소
        assert is_valid_temperature(200) is True    # 경계값: 최대
        assert is_valid_temperature(25.5) is True   # 소수점

    def test_범위_밖_온도(self):
        """범위 밖의 온도값은 False를 반환해야 한다"""
        assert is_valid_temperature(-51) is False   # 최소값 아래
        assert is_valid_temperature(201) is False   # 최대값 위
        assert is_valid_temperature(-100) is False
        assert is_valid_temperature(300) is False
        assert is_valid_temperature(1000) is False

    def test_잘못된_타입(self):
        """숫자가 아닌 값은 False를 반환해야 한다"""
        assert is_valid_temperature("25") is False
        assert is_valid_temperature(None) is False
        assert is_valid_temperature([25]) is False
        assert is_valid_temperature({"temp": 25}) is False


class TestFilterValidReadings:
    """filter_valid_readings 함수 테스트"""

    def test_모두_유효한_데이터(self):
        """모든 값이 유효하면 전체가 반환되어야 한다"""
        readings = [20.0, 50.0, 100.0, 150.0]
        result = filter_valid_readings(readings)
        assert result == [20.0, 50.0, 100.0, 150.0]
        assert len(result) == 4

    def test_일부_무효한_데이터(self):
        """무효한 값은 필터링되어야 한다"""
        readings = [20.0, -100.0, 50.0, 300.0, 100.0]
        result = filter_valid_readings(readings)
        assert result == [20.0, 50.0, 100.0]
        assert len(result) == 3

    def test_빈_리스트(self):
        """빈 리스트를 전달하면 빈 리스트가 반환되어야 한다"""
        result = filter_valid_readings([])
        assert result == []

    def test_모두_무효한_데이터(self):
        """모든 값이 무효하면 빈 리스트가 반환되어야 한다"""
        readings = [-100.0, 300.0, 500.0]
        result = filter_valid_readings(readings)
        assert result == []


class TestGetTemperatureStatus:
    """get_temperature_status 함수 테스트"""

    def test_저온_상태(self):
        """영하 온도에 대해 '저온' 상태를 반환해야 한다"""
        result = get_temperature_status(-10)
        assert result["status"] == "저온"
        assert result["action"] == "난방 가동"

    def test_정상_상태(self):
        """정상 범위 온도에 대해 올바른 상태를 반환해야 한다"""
        result = get_temperature_status(25)
        assert result["status"] == "정상"
        assert result["action"] == "유지"

    def test_주의_상태(self):
        """주의 범위 온도에 대해 올바른 상태를 반환해야 한다"""
        result = get_temperature_status(70)
        assert result["status"] == "주의"
        assert result["action"] == "모니터링 강화"

    def test_위험_상태(self):
        """높은 온도에 대해 '위험' 상태를 반환해야 한다"""
        result = get_temperature_status(85)
        assert result["status"] == "위험"
        assert result["action"] == "즉시 점검"

    def test_경계값(self):
        """경계값에서 올바른 상태를 반환해야 한다"""
        # 0도: 정상 (0 이상)
        assert get_temperature_status(0)["status"] == "정상"
        # 60도: 주의
        assert get_temperature_status(60)["status"] == "주의"
        # 80도: 위험
        assert get_temperature_status(80)["status"] == "위험"
