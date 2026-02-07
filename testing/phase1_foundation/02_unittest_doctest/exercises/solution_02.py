"""
연습 문제 02: 풀이

진동 센서 유틸리티 함수들에 대한 unittest 스타일 테스트 풀이.

실행 방법:
    pytest exercises/solution_02.py -v
"""

import unittest


# ============================================================
# 테스트 대상 함수들
# ============================================================

def mm_per_sec_to_in_per_sec(mm_s):
    """진동 속도를 mm/s에서 in/s로 변환한다."""
    if mm_s < 0:
        raise ValueError("진동 속도는 0 이상이어야 합니다")
    return round(mm_s * 0.03937, 5)


def calculate_rms(values):
    """RMS(Root Mean Square) 값을 계산한다."""
    if not values:
        raise ValueError("측정값이 비어있습니다")
    squared = [v ** 2 for v in values]
    return round((sum(squared) / len(squared)) ** 0.5, 5)


def is_vibration_alarm(rms_value, alarm_threshold=7.1):
    """진동 RMS 값이 알람 기준을 초과하는지 확인한다."""
    return rms_value > alarm_threshold


# ============================================================
# 테스트 코드 (풀이)
# ============================================================

class TestMmPerSecToInPerSec(unittest.TestCase):
    """mm/s → in/s 변환 테스트"""

    def test_기본_변환(self):
        """기본 변환이 올바른지 확인한다"""
        # 25.4 mm/s ≈ 1.0 in/s
        result = mm_per_sec_to_in_per_sec(25.4)
        self.assertAlmostEqual(result, 1.0, places=3)

    def test_0_변환(self):
        """0 입력 시 0이 반환되어야 한다"""
        self.assertEqual(mm_per_sec_to_in_per_sec(0), 0.0)

    def test_음수_예외(self):
        """음수 입력 시 ValueError가 발생해야 한다"""
        with self.assertRaises(ValueError):
            mm_per_sec_to_in_per_sec(-5)

    def test_반환_타입(self):
        """반환값은 float이어야 한다"""
        result = mm_per_sec_to_in_per_sec(10)
        self.assertIsInstance(result, float)


class TestCalculateRms(unittest.TestCase):
    """RMS 계산 테스트"""

    def setUp(self):
        """공통 테스트 데이터 설정"""
        # 3-4-5 삼각형: RMS([3, 4]) = sqrt((9+16)/2) = sqrt(12.5) ≈ 3.53553
        self.sample_values = [3, 4]

    def test_기본_계산(self):
        """RMS 계산이 올바른지 확인한다"""
        result = calculate_rms(self.sample_values)
        self.assertAlmostEqual(result, 3.53553, places=4)

    def test_동일값(self):
        """모든 값이 같으면 RMS는 그 값이어야 한다"""
        result = calculate_rms([5, 5, 5, 5])
        self.assertAlmostEqual(result, 5.0, places=4)

    def test_단일값(self):
        """단일 값의 RMS는 그 값의 절대값이어야 한다"""
        result = calculate_rms([7])
        self.assertAlmostEqual(result, 7.0, places=4)

    def test_빈_리스트_예외(self):
        """빈 리스트 입력 시 ValueError가 발생해야 한다"""
        with self.assertRaises(ValueError):
            calculate_rms([])

    def tearDown(self):
        """테스트 후 정리"""
        self.sample_values = None


class TestIsVibrationAlarm(unittest.TestCase):
    """진동 알람 테스트"""

    def test_알람_발생(self):
        """기준값 초과 시 True를 반환해야 한다"""
        self.assertTrue(is_vibration_alarm(8.0))
        self.assertTrue(is_vibration_alarm(10.0))
        self.assertTrue(is_vibration_alarm(7.2))

    def test_알람_미발생(self):
        """기준값 이하일 때 False를 반환해야 한다"""
        self.assertFalse(is_vibration_alarm(5.0))
        self.assertFalse(is_vibration_alarm(7.0))
        self.assertFalse(is_vibration_alarm(7.1))  # 경계값: 초과가 아닌 이하

    def test_사용자_정의_기준값(self):
        """사용자 지정 기준값으로 판단해야 한다"""
        # 기준값을 5.0으로 낮춤
        self.assertTrue(is_vibration_alarm(6.0, alarm_threshold=5.0))
        self.assertFalse(is_vibration_alarm(4.0, alarm_threshold=5.0))

    def test_경계값(self):
        """정확히 기준값과 같으면 알람이 발생하지 않아야 한다 (> 사용)"""
        self.assertFalse(is_vibration_alarm(7.1))


if __name__ == "__main__":
    unittest.main()
