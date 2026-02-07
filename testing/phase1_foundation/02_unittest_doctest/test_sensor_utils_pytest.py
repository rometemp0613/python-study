"""
센서 유틸리티 테스트 - pytest 스타일

동일한 기능을 pytest 스타일로 작성하여 unittest와 비교한다.
pytest의 간결함과 가독성을 확인할 수 있다.
"""

import pytest
from src_sensor_utils import (
    psi_to_bar,
    bar_to_psi,
    normalize_reading,
    calculate_statistics,
    classify_vibration_level,
)


# ============================================================
# PSI → Bar 변환 테스트
# ============================================================

class TestPsiToBar:
    """PSI → Bar 변환 테스트 (pytest 스타일)"""

    def test_표준_대기압(self):
        """표준 대기압 변환: 14.696 PSI = 1.01325 Bar"""
        assert psi_to_bar(14.696) == pytest.approx(1.01325, abs=0.0001)

    def test_0_변환(self):
        """0 PSI는 0 Bar"""
        assert psi_to_bar(0) == 0.0

    def test_100_psi(self):
        """100 PSI 변환"""
        assert psi_to_bar(100) == pytest.approx(6.89476, abs=0.0001)

    def test_음수_예외(self):
        """음수 PSI 입력 시 ValueError 발생"""
        with pytest.raises(ValueError):
            psi_to_bar(-1)

    def test_잘못된_타입(self):
        """숫자가 아닌 입력 시 TypeError 발생"""
        with pytest.raises(TypeError):
            psi_to_bar("100")

    def test_반환_타입(self):
        """반환값은 float 타입이어야 한다"""
        assert isinstance(psi_to_bar(14.696), float)


# ============================================================
# Bar → PSI 변환 테스트
# ============================================================

class TestBarToPsi:
    """Bar → PSI 변환 테스트 (pytest 스타일)"""

    def test_1_bar(self):
        """1 Bar = 14.504 PSI"""
        assert bar_to_psi(1.0) == pytest.approx(14.504, abs=0.01)

    def test_0_변환(self):
        """0 Bar는 0 PSI"""
        assert bar_to_psi(0) == 0.0

    def test_음수_예외(self):
        """음수 Bar 입력 시 ValueError 발생"""
        with pytest.raises(ValueError):
            bar_to_psi(-1)


# ============================================================
# 정규화 테스트
# ============================================================

class TestNormalizeReading:
    """센서 읽기 값 정규화 테스트 (pytest 스타일)"""

    def test_중간값(self):
        """중간값은 0.5로 정규화된다"""
        assert normalize_reading(50, 0, 100) == 0.5

    def test_최소값(self):
        """최소값은 0.0으로 정규화된다"""
        assert normalize_reading(0, 0, 100) == 0.0

    def test_최대값(self):
        """최대값은 1.0으로 정규화된다"""
        assert normalize_reading(100, 0, 100) == 1.0

    def test_범위_밖_값(self):
        """범위 밖의 값도 계산 가능"""
        assert normalize_reading(150, 0, 100) == 1.5

    def test_같은_범위_예외(self):
        """최소값과 최대값이 같으면 ValueError 발생"""
        with pytest.raises(ValueError):
            normalize_reading(50, 100, 100)


# ============================================================
# 통계 계산 테스트
# ============================================================

class TestCalculateStatistics:
    """센서 통계 계산 테스트 (pytest 스타일)"""

    def test_기본_통계(self):
        """기본 통계값이 올바르게 계산되어야 한다"""
        stats = calculate_statistics([10, 20, 30, 40, 50])
        assert stats["mean"] == 30.0
        assert stats["min"] == 10
        assert stats["max"] == 50
        assert stats["range"] == 40

    def test_빈_리스트_예외(self):
        """빈 리스트 입력 시 ValueError 발생"""
        with pytest.raises(ValueError):
            calculate_statistics([])

    def test_반환_키(self):
        """반환 딕셔너리에 모든 필수 키가 있어야 한다"""
        stats = calculate_statistics([1, 2, 3])
        assert "mean" in stats
        assert "min" in stats
        assert "max" in stats
        assert "range" in stats


# ============================================================
# 진동 수준 분류 테스트
# ============================================================

class TestClassifyVibrationLevel:
    """진동 수준 분류 테스트 (pytest 스타일)"""

    def test_양호(self):
        """1.8 mm/s 이하는 '양호'"""
        assert classify_vibration_level(1.0) == "양호"

    def test_허용(self):
        """1.8~4.5 mm/s는 '허용'"""
        assert classify_vibration_level(3.0) == "허용"

    def test_주의(self):
        """4.5~7.1 mm/s는 '주의'"""
        assert classify_vibration_level(5.0) == "주의"

    def test_위험(self):
        """7.1 mm/s 초과는 '위험'"""
        assert classify_vibration_level(10.0) == "위험"

    def test_음수_예외(self):
        """음수 입력 시 ValueError 발생"""
        with pytest.raises(ValueError):
            classify_vibration_level(-1)
