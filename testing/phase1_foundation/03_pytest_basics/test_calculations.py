"""
계산 모듈 테스트

pytest의 기본 기능을 활용한 테스트:
- assert 매직
- pytest.approx()
- pytest.raises()
- @pytest.mark.parametrize
- 클래스 기반 테스트 구조
"""

import pytest
from src_calculations import (
    add,
    subtract,
    multiply,
    divide,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    detect_anomaly_temperature,
    moving_average,
)


# ============================================================
# 기본 산술 연산 테스트
# ============================================================

class TestBasicArithmetic:
    """기본 산술 연산 테스트 - assert 매직 데모"""

    def test_add_정수(self):
        """정수 덧셈"""
        assert add(2, 3) == 5

    def test_add_음수(self):
        """음수 포함 덧셈"""
        assert add(-1, 1) == 0
        assert add(-3, -5) == -8

    def test_add_소수(self):
        """소수 덧셈 - pytest.approx 사용"""
        assert add(0.1, 0.2) == pytest.approx(0.3)

    def test_subtract(self):
        """뺄셈"""
        assert subtract(10, 3) == 7
        assert subtract(5, 5) == 0
        assert subtract(3, 10) == -7

    def test_multiply(self):
        """곱셈"""
        assert multiply(3, 4) == 12
        assert multiply(-2, 5) == -10
        assert multiply(0, 100) == 0

    def test_divide_정상(self):
        """정상 나눗셈"""
        assert divide(10, 2) == 5.0
        assert divide(7, 2) == 3.5

    def test_divide_0으로_나누기(self):
        """0으로 나눌 때 예외 발생"""
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)


# ============================================================
# 온도 변환 테스트 - pytest.approx 활용
# ============================================================

class TestTemperatureConversion:
    """온도 변환 테스트 - pytest.approx()의 다양한 활용법"""

    def test_celsius_to_fahrenheit_끓는점(self):
        """물의 끓는점: 100°C = 212°F"""
        assert celsius_to_fahrenheit(100) == 212.0

    def test_celsius_to_fahrenheit_어는점(self):
        """물의 어는점: 0°C = 32°F"""
        assert celsius_to_fahrenheit(0) == 32.0

    def test_celsius_to_fahrenheit_체온(self):
        """체온: 37°C ≈ 98.6°F (pytest.approx 사용)"""
        result = celsius_to_fahrenheit(37)
        assert result == pytest.approx(98.6, abs=0.1)

    def test_fahrenheit_to_celsius_끓는점(self):
        """212°F = 100°C"""
        assert fahrenheit_to_celsius(212) == pytest.approx(100.0)

    def test_fahrenheit_to_celsius_어는점(self):
        """32°F = 0°C"""
        assert fahrenheit_to_celsius(32) == pytest.approx(0.0)

    def test_왕복_변환(self):
        """섭씨 → 화씨 → 섭씨 왕복 변환의 정확도"""
        original = 37.5
        converted = fahrenheit_to_celsius(celsius_to_fahrenheit(original))
        assert converted == pytest.approx(original)

    def test_approx_절대오차(self):
        """절대 오차 지정: abs=0.01"""
        result = celsius_to_fahrenheit(37)
        # 절대 오차 0.01 이내
        assert result == pytest.approx(98.6, abs=0.1)

    def test_approx_상대오차(self):
        """상대 오차 지정: rel=0.01 (1%)"""
        result = celsius_to_fahrenheit(100)
        # 상대 오차 1% 이내
        assert result == pytest.approx(212.0, rel=0.01)


# ============================================================
# @pytest.mark.parametrize 기초
# ============================================================

class TestParametrize:
    """@pytest.mark.parametrize를 사용한 데이터 기반 테스트"""

    @pytest.mark.parametrize("celsius, fahrenheit", [
        (0, 32.0),        # 어는점
        (100, 212.0),     # 끓는점
        (-40, -40.0),     # 동일값
        (37, 98.6),       # 체온
    ])
    def test_celsius_to_fahrenheit_여러값(self, celsius, fahrenheit):
        """여러 온도값에 대해 변환을 검증한다"""
        assert celsius_to_fahrenheit(celsius) == pytest.approx(fahrenheit, abs=0.1)

    @pytest.mark.parametrize("a, b, expected", [
        (1, 1, 2),
        (0, 0, 0),
        (-1, 1, 0),
        (100, 200, 300),
        (0.1, 0.2, 0.3),
    ])
    def test_add_parametrize(self, a, b, expected):
        """여러 입력값에 대해 덧셈을 검증한다"""
        assert add(a, b) == pytest.approx(expected)

    @pytest.mark.parametrize("a, b", [
        (10, 0),
        (0, 0),
        (-5, 0),
    ])
    def test_divide_0으로_나누기_parametrize(self, a, b):
        """다양한 피제수에 대해 0으로 나눌 때 예외 발생"""
        with pytest.raises(ZeroDivisionError):
            divide(a, b)


# ============================================================
# 이상 온도 감지 테스트
# ============================================================

class TestDetectAnomalyTemperature:
    """이상 온도 감지 함수 테스트"""

    def test_정상_데이터(self):
        """모든 값이 정상 범위 내일 때 빈 리스트 반환"""
        readings = [25.0, 25.1, 24.9, 25.0, 25.2]
        anomalies = detect_anomaly_temperature(readings)
        assert anomalies == []

    def test_이상치_감지(self):
        """이상치가 정확히 감지되어야 한다"""
        readings = [25.0, 25.0, 25.0, 25.0, 100.0]  # 100.0은 이상치
        anomalies = detect_anomaly_temperature(readings)
        assert len(anomalies) == 1
        assert anomalies[0]["index"] == 4
        assert anomalies[0]["value"] == 100.0

    def test_이상치_없는_동일값(self):
        """모든 값이 같으면 이상치 없음"""
        readings = [50.0, 50.0, 50.0, 50.0]
        anomalies = detect_anomaly_temperature(readings)
        assert anomalies == []

    def test_최소_데이터_예외(self):
        """2개 미만의 데이터로는 이상치 감지 불가"""
        with pytest.raises(ValueError, match="최소 2개"):
            detect_anomaly_temperature([25.0])

    def test_이상치_필드_확인(self):
        """이상치 결과에 필수 필드가 있어야 한다"""
        readings = [20.0, 20.0, 20.0, 20.0, 200.0]
        anomalies = detect_anomaly_temperature(readings)
        assert len(anomalies) > 0

        anomaly = anomalies[0]
        assert "index" in anomaly
        assert "value" in anomaly
        assert "deviation" in anomaly

    def test_threshold_multiplier(self):
        """threshold_multiplier를 조절하여 감도를 변경할 수 있다"""
        readings = [25.0, 25.0, 25.0, 30.0]

        # 낮은 배수: 더 민감 → 이상치 감지
        anomalies_sensitive = detect_anomaly_temperature(
            readings, threshold_multiplier=1.0
        )

        # 높은 배수: 덜 민감 → 이상치 미감지
        anomalies_lenient = detect_anomaly_temperature(
            readings, threshold_multiplier=5.0
        )

        assert len(anomalies_sensitive) >= len(anomalies_lenient)


# ============================================================
# 이동 평균 테스트
# ============================================================

class TestMovingAverage:
    """이동 평균 계산 테스트"""

    def test_기본_이동평균(self):
        """기본 이동 평균 계산"""
        values = [1, 2, 3, 4, 5]
        result = moving_average(values, window_size=3)
        assert result == pytest.approx([2.0, 3.0, 4.0])

    def test_윈도우_크기_1(self):
        """윈도우 크기가 1이면 원본 값과 같다"""
        values = [10, 20, 30]
        result = moving_average(values, window_size=1)
        assert result == pytest.approx([10.0, 20.0, 30.0])

    def test_윈도우_크기가_데이터_길이와_같음(self):
        """윈도우 크기가 데이터 길이와 같으면 전체 평균 하나"""
        values = [10, 20, 30]
        result = moving_average(values, window_size=3)
        assert result == pytest.approx([20.0])

    def test_윈도우_크기_0_예외(self):
        """윈도우 크기가 0 이하이면 예외 발생"""
        with pytest.raises(ValueError):
            moving_average([1, 2, 3], window_size=0)

    def test_윈도우_크기_초과_예외(self):
        """윈도우 크기가 데이터 길이보다 크면 예외 발생"""
        with pytest.raises(ValueError):
            moving_average([1, 2, 3], window_size=5)
