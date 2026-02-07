"""
온도 모니터링 모듈 테스트

src_temperature_fixed.py (수정된 버전)의 함수들을 테스트한다.
이 테스트들은 src_temperature.py (버그 버전)에 대해 실행하면 실패한다.
"""

import pytest

# 수정된 버전을 임포트하여 테스트 통과 확인
from src_temperature_fixed import (
    celsius_to_fahrenheit,
    is_overheating,
    calculate_average_temp,
    classify_temperature,
)


# ============================================================
# celsius_to_fahrenheit 테스트
# ============================================================

class TestCelsiusToFahrenheit:
    """섭씨 → 화씨 변환 함수 테스트"""

    def test_끓는점(self):
        """물의 끓는점: 100°C = 212°F"""
        assert celsius_to_fahrenheit(100) == 212.0

    def test_어는점(self):
        """물의 어는점: 0°C = 32°F"""
        assert celsius_to_fahrenheit(0) == 32.0

    def test_절대영도(self):
        """절대영도: -273.15°C = -459.67°F"""
        result = celsius_to_fahrenheit(-273.15)
        assert result == pytest.approx(-459.67, abs=0.01)

    def test_동일값(self):
        """섭씨와 화씨가 같아지는 온도: -40°C = -40°F"""
        assert celsius_to_fahrenheit(-40) == -40.0

    def test_체온(self):
        """사람 체온: 37°C = 98.6°F"""
        assert celsius_to_fahrenheit(37) == pytest.approx(98.6, abs=0.1)


# ============================================================
# is_overheating 테스트
# ============================================================

class TestIsOverheating:
    """과열 판단 함수 테스트"""

    def test_정상_온도(self):
        """정상 온도에서는 과열이 아니다"""
        assert is_overheating(50.0) is False

    def test_과열_온도(self):
        """임계값을 초과하면 과열이다"""
        assert is_overheating(90.0) is True

    def test_경계값_정확히_임계값(self):
        """임계값과 정확히 같으면 과열로 판단한다 (>= 사용)"""
        assert is_overheating(80.0) is True

    def test_경계값_바로_아래(self):
        """임계값 바로 아래는 과열이 아니다"""
        assert is_overheating(79.99) is False

    def test_사용자_정의_임계값(self):
        """사용자가 지정한 임계값으로 판단한다"""
        assert is_overheating(60.0, threshold=50.0) is True
        assert is_overheating(40.0, threshold=50.0) is False


# ============================================================
# calculate_average_temp 테스트
# ============================================================

class TestCalculateAverageTemp:
    """평균 온도 계산 함수 테스트"""

    def test_일반적인_경우(self):
        """여러 온도 값의 평균을 계산한다"""
        readings = [20.0, 25.0, 30.0, 25.0]
        assert calculate_average_temp(readings) == 25.0

    def test_단일_값(self):
        """읽기 값이 하나이면 그 값이 평균이다"""
        assert calculate_average_temp([42.0]) == 42.0

    def test_빈_리스트(self):
        """빈 리스트를 전달하면 ValueError가 발생해야 한다"""
        with pytest.raises(ValueError):
            calculate_average_temp([])

    def test_소수점_정확도(self):
        """소수점 계산이 정확해야 한다"""
        readings = [10.1, 10.2, 10.3]
        assert calculate_average_temp(readings) == pytest.approx(10.2)


# ============================================================
# classify_temperature 테스트
# ============================================================

class TestClassifyTemperature:
    """온도 분류 함수 테스트"""

    def test_정상_범위(self):
        """50도 미만은 정상이다"""
        assert classify_temperature(30) == "정상"
        assert classify_temperature(49.9) == "정상"

    def test_주의_범위(self):
        """50도 이상 70도 미만은 주의다"""
        assert classify_temperature(50) == "주의"
        assert classify_temperature(69.9) == "주의"

    def test_경고_범위(self):
        """70도 이상 90도 미만은 경고다"""
        assert classify_temperature(70) == "경고"
        assert classify_temperature(89.9) == "경고"

    def test_위험_범위(self):
        """90도 이상은 위험이다"""
        assert classify_temperature(90) == "위험"
        assert classify_temperature(150) == "위험"
