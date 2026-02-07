"""
센서 유틸리티 테스트 - unittest 스타일

unittest.TestCase를 사용한 전통적인 Python 테스트 방식.
setUp/tearDown, 다양한 assertion 메서드 활용을 보여준다.
"""

import unittest
from src_sensor_utils import (
    psi_to_bar,
    bar_to_psi,
    normalize_reading,
    calculate_statistics,
    classify_vibration_level,
)


class TestPsiToBar(unittest.TestCase):
    """PSI → Bar 변환 테스트"""

    def test_표준_대기압(self):
        """표준 대기압 변환: 14.696 PSI = 1.01325 Bar"""
        result = psi_to_bar(14.696)
        self.assertAlmostEqual(result, 1.01325, places=4)

    def test_0_변환(self):
        """0 PSI는 0 Bar"""
        self.assertEqual(psi_to_bar(0), 0.0)

    def test_100_psi(self):
        """100 PSI 변환"""
        result = psi_to_bar(100)
        self.assertAlmostEqual(result, 6.89476, places=4)

    def test_음수_예외(self):
        """음수 PSI 입력 시 ValueError 발생"""
        with self.assertRaises(ValueError):
            psi_to_bar(-1)

    def test_잘못된_타입(self):
        """숫자가 아닌 입력 시 TypeError 발생"""
        with self.assertRaises(TypeError):
            psi_to_bar("100")

    def test_반환_타입(self):
        """반환값은 float 타입이어야 한다"""
        result = psi_to_bar(14.696)
        self.assertIsInstance(result, float)


class TestBarToPsi(unittest.TestCase):
    """Bar → PSI 변환 테스트"""

    def test_1_bar(self):
        """1 Bar = 14.504 PSI"""
        result = bar_to_psi(1.0)
        self.assertAlmostEqual(result, 14.504, places=2)

    def test_0_변환(self):
        """0 Bar는 0 PSI"""
        self.assertEqual(bar_to_psi(0), 0.0)

    def test_음수_예외(self):
        """음수 Bar 입력 시 ValueError 발생"""
        with self.assertRaises(ValueError):
            bar_to_psi(-1)


class TestNormalizeReading(unittest.TestCase):
    """센서 읽기 값 정규화 테스트"""

    def setUp(self):
        """공통 테스트 데이터 설정"""
        self.min_val = 0
        self.max_val = 100

    def test_중간값(self):
        """중간값은 0.5로 정규화된다"""
        result = normalize_reading(50, self.min_val, self.max_val)
        self.assertEqual(result, 0.5)

    def test_최소값(self):
        """최소값은 0.0으로 정규화된다"""
        result = normalize_reading(0, self.min_val, self.max_val)
        self.assertEqual(result, 0.0)

    def test_최대값(self):
        """최대값은 1.0으로 정규화된다"""
        result = normalize_reading(100, self.min_val, self.max_val)
        self.assertEqual(result, 1.0)

    def test_범위_밖_값(self):
        """범위 밖의 값도 계산 가능 (클리핑하지 않음)"""
        result = normalize_reading(150, self.min_val, self.max_val)
        self.assertEqual(result, 1.5)

    def test_같은_범위_예외(self):
        """최소값과 최대값이 같으면 ValueError 발생"""
        with self.assertRaises(ValueError):
            normalize_reading(50, 100, 100)


class TestCalculateStatistics(unittest.TestCase):
    """센서 통계 계산 테스트"""

    def setUp(self):
        """테스트용 샘플 데이터 준비"""
        self.sample_data = [10, 20, 30, 40, 50]

    def test_평균(self):
        """평균이 올바르게 계산되어야 한다"""
        stats = calculate_statistics(self.sample_data)
        self.assertEqual(stats["mean"], 30.0)

    def test_최소값(self):
        """최소값이 올바르게 계산되어야 한다"""
        stats = calculate_statistics(self.sample_data)
        self.assertEqual(stats["min"], 10)

    def test_최대값(self):
        """최대값이 올바르게 계산되어야 한다"""
        stats = calculate_statistics(self.sample_data)
        self.assertEqual(stats["max"], 50)

    def test_범위(self):
        """범위가 올바르게 계산되어야 한다"""
        stats = calculate_statistics(self.sample_data)
        self.assertEqual(stats["range"], 40)

    def test_빈_리스트_예외(self):
        """빈 리스트 입력 시 ValueError 발생"""
        with self.assertRaises(ValueError):
            calculate_statistics([])

    def test_반환_키(self):
        """반환 딕셔너리에 모든 키가 포함되어야 한다"""
        stats = calculate_statistics(self.sample_data)
        self.assertIn("mean", stats)
        self.assertIn("min", stats)
        self.assertIn("max", stats)
        self.assertIn("range", stats)

    def tearDown(self):
        """테스트 후 정리"""
        self.sample_data = None


class TestClassifyVibrationLevel(unittest.TestCase):
    """진동 수준 분류 테스트"""

    def test_양호(self):
        """1.8 mm/s 이하는 '양호'"""
        self.assertEqual(classify_vibration_level(0.5), "양호")
        self.assertEqual(classify_vibration_level(1.0), "양호")
        self.assertEqual(classify_vibration_level(1.8), "양호")

    def test_허용(self):
        """1.8~4.5 mm/s는 '허용'"""
        self.assertEqual(classify_vibration_level(2.0), "허용")
        self.assertEqual(classify_vibration_level(3.0), "허용")
        self.assertEqual(classify_vibration_level(4.5), "허용")

    def test_주의(self):
        """4.5~7.1 mm/s는 '주의'"""
        self.assertEqual(classify_vibration_level(5.0), "주의")
        self.assertEqual(classify_vibration_level(7.1), "주의")

    def test_위험(self):
        """7.1 mm/s 초과는 '위험'"""
        self.assertEqual(classify_vibration_level(8.0), "위험")
        self.assertEqual(classify_vibration_level(10.0), "위험")

    def test_음수_예외(self):
        """음수 입력 시 ValueError 발생"""
        with self.assertRaises(ValueError):
            classify_vibration_level(-1)


# unittest를 직접 실행할 때 사용
if __name__ == "__main__":
    unittest.main()
