"""
연습 문제 02: unittest 스타일로 테스트 작성하기

아래 진동 센서 유틸리티 함수들에 대해 unittest 스타일의 테스트를 작성하세요.
setUp 메서드를 활용하여 공통 데이터를 준비하세요.

실행 방법:
    pytest exercises/exercise_02.py -v
"""

import unittest
import pytest


# ============================================================
# 테스트 대상 함수들
# ============================================================

def mm_per_sec_to_in_per_sec(mm_s):
    """진동 속도를 mm/s에서 in/s로 변환한다.

    1 mm/s = 0.03937 in/s

    Args:
        mm_s: mm/s 단위의 진동 속도

    Returns:
        in/s 단위의 진동 속도 (소수점 5자리)

    Raises:
        ValueError: 음수 입력 시
    """
    if mm_s < 0:
        raise ValueError("진동 속도는 0 이상이어야 합니다")
    return round(mm_s * 0.03937, 5)


def calculate_rms(values):
    """RMS(Root Mean Square) 값을 계산한다.

    RMS = sqrt(mean(x^2))

    Args:
        values: 측정값 리스트

    Returns:
        RMS 값

    Raises:
        ValueError: 빈 리스트 입력 시
    """
    if not values:
        raise ValueError("측정값이 비어있습니다")
    squared = [v ** 2 for v in values]
    return round((sum(squared) / len(squared)) ** 0.5, 5)


def is_vibration_alarm(rms_value, alarm_threshold=7.1):
    """진동 RMS 값이 알람 기준을 초과하는지 확인한다.

    Args:
        rms_value: RMS 값 (mm/s)
        alarm_threshold: 알람 기준값 (기본값: 7.1 mm/s)

    Returns:
        알람 여부 (bool)
    """
    return rms_value > alarm_threshold


# ============================================================
# TODO: unittest.TestCase를 상속하여 테스트 클래스를 작성하세요
# ============================================================

class TestMmPerSecToInPerSec(unittest.TestCase):
    """mm/s → in/s 변환 테스트"""

    def test_기본_변환(self):
        """기본 변환이 올바른지 확인한다"""
        # TODO: mm_per_sec_to_in_per_sec(25.4)가 약 1.0인지 확인하세요
        # 힌트: self.assertAlmostEqual()을 사용하세요
        pytest.skip("TODO: 기본 변환 테스트를 구현하세요")

    def test_0_변환(self):
        """0 입력 시 0이 반환되어야 한다"""
        # TODO: 0 입력에 대한 테스트를 작성하세요
        pytest.skip("TODO: 0 변환 테스트를 구현하세요")

    def test_음수_예외(self):
        """음수 입력 시 ValueError가 발생해야 한다"""
        # TODO: self.assertRaises()를 사용하세요
        pytest.skip("TODO: 음수 예외 테스트를 구현하세요")


class TestCalculateRms(unittest.TestCase):
    """RMS 계산 테스트"""

    def setUp(self):
        """공통 테스트 데이터 설정"""
        # TODO: 테스트에 사용할 샘플 데이터를 설정하세요
        # 힌트: self.sample_values = [3, 4] (RMS = 약 3.53553)
        pass

    def test_기본_계산(self):
        """RMS 계산이 올바른지 확인한다"""
        # TODO: 샘플 데이터의 RMS를 계산하고 검증하세요
        pytest.skip("TODO: RMS 기본 계산 테스트를 구현하세요")

    def test_동일값(self):
        """모든 값이 같으면 RMS는 그 값이어야 한다"""
        # TODO: [5, 5, 5, 5]의 RMS가 5인지 확인하세요
        pytest.skip("TODO: 동일값 RMS 테스트를 구현하세요")

    def test_빈_리스트_예외(self):
        """빈 리스트 입력 시 ValueError가 발생해야 한다"""
        # TODO: 빈 리스트에 대한 예외 테스트를 작성하세요
        pytest.skip("TODO: 빈 리스트 예외 테스트를 구현하세요")


class TestIsVibrationAlarm(unittest.TestCase):
    """진동 알람 테스트"""

    def test_알람_발생(self):
        """기준값 초과 시 True를 반환해야 한다"""
        # TODO: 7.1 초과 값에 대한 테스트
        pytest.skip("TODO: 알람 발생 테스트를 구현하세요")

    def test_알람_미발생(self):
        """기준값 이하일 때 False를 반환해야 한다"""
        # TODO: 7.1 이하 값에 대한 테스트
        pytest.skip("TODO: 알람 미발생 테스트를 구현하세요")

    def test_사용자_정의_기준값(self):
        """사용자 지정 기준값으로 판단해야 한다"""
        # TODO: alarm_threshold 파라미터를 사용한 테스트
        pytest.skip("TODO: 사용자 정의 기준값 테스트를 구현하세요")


# unittest 직접 실행 시
if __name__ == "__main__":
    unittest.main()
