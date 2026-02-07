"""
연습 문제 03: pytest 기본기 실습

이상 온도 감지 및 이동 평균 함수에 대한 테스트를 작성하세요.
pytest.approx(), pytest.raises(), @pytest.mark.parametrize를 활용합니다.

실행 방법:
    pytest exercises/exercise_03.py -v
"""

import pytest


# ============================================================
# 테스트 대상 함수들
# ============================================================

def kelvin_to_celsius(kelvin):
    """켈빈을 섭씨로 변환한다.

    공식: C = K - 273.15

    Args:
        kelvin: 켈빈 온도 (0 이상)

    Returns:
        섭씨 온도

    Raises:
        ValueError: kelvin이 0 미만일 때 (절대영도 이하)
    """
    if kelvin < 0:
        raise ValueError("켈빈 온도는 0 이상이어야 합니다 (절대영도)")
    return kelvin - 273.15


def calculate_thermal_efficiency(input_energy, output_energy):
    """열효율을 계산한다.

    열효율 = (출력 에너지 / 입력 에너지) * 100

    Args:
        input_energy: 입력 에너지 (0보다 커야 함)
        output_energy: 출력 에너지 (0 이상)

    Returns:
        열효율 (%)

    Raises:
        ValueError: input_energy가 0 이하이거나 output_energy가 음수일 때
    """
    if input_energy <= 0:
        raise ValueError("입력 에너지는 0보다 커야 합니다")
    if output_energy < 0:
        raise ValueError("출력 에너지는 0 이상이어야 합니다")
    return (output_energy / input_energy) * 100


def find_peak_temperatures(readings, min_prominence=5.0):
    """온도 읽기 값에서 피크(극대값)를 찾는다.

    이전 값과 다음 값보다 모두 높은 값을 피크로 판단한다.
    min_prominence 이상의 돌출도를 가진 피크만 반환한다.

    Args:
        readings: 온도 읽기 값 리스트 (최소 3개)
        min_prominence: 최소 돌출도

    Returns:
        피크 리스트 [{"index": i, "value": v, "prominence": p}, ...]

    Raises:
        ValueError: 읽기 값이 3개 미만일 때
    """
    if len(readings) < 3:
        raise ValueError("피크 감지를 위해 최소 3개의 읽기 값이 필요합니다")

    peaks = []
    for i in range(1, len(readings) - 1):
        if readings[i] > readings[i - 1] and readings[i] > readings[i + 1]:
            prominence = min(
                readings[i] - readings[i - 1],
                readings[i] - readings[i + 1],
            )
            if prominence >= min_prominence:
                peaks.append({
                    "index": i,
                    "value": readings[i],
                    "prominence": round(prominence, 4),
                })

    return peaks


# ============================================================
# TODO: 아래에 테스트를 작성하세요
# ============================================================

class TestKelvinToCelsius:
    """켈빈 → 섭씨 변환 테스트"""

    @pytest.mark.parametrize("kelvin, expected_celsius", [
        # TODO: 최소 4개의 테스트 케이스를 추가하세요
        # 힌트: (273.15, 0), (373.15, 100), (0, -273.15), (310.15, 37)
    ])
    def test_변환_parametrize(self, kelvin, expected_celsius):
        """여러 온도값에 대해 변환을 검증한다"""
        # TODO: kelvin_to_celsius 함수를 호출하고 pytest.approx로 비교하세요
        pytest.skip("TODO: parametrize 테스트를 구현하세요")

    def test_절대영도_이하_예외(self):
        """절대영도(0K) 미만이면 ValueError가 발생해야 한다"""
        # TODO: kelvin_to_celsius(-1)에 대한 예외 테스트
        pytest.skip("TODO: 절대영도 이하 예외 테스트를 구현하세요")


class TestCalculateThermalEfficiency:
    """열효율 계산 테스트"""

    def test_100퍼센트_효율(self):
        """입력과 출력이 같으면 100% 효율"""
        # TODO: calculate_thermal_efficiency(100, 100)이 100.0인지 확인
        pytest.skip("TODO: 100% 효율 테스트를 구현하세요")

    def test_50퍼센트_효율(self):
        """출력이 입력의 절반이면 50% 효율"""
        # TODO: calculate_thermal_efficiency(100, 50)이 50.0인지 확인
        pytest.skip("TODO: 50% 효율 테스트를 구현하세요")

    def test_입력_에너지_0_예외(self):
        """입력 에너지가 0이면 ValueError 발생"""
        # TODO: pytest.raises를 사용하세요
        pytest.skip("TODO: 입력 에너지 0 예외 테스트를 구현하세요")

    def test_출력_에너지_음수_예외(self):
        """출력 에너지가 음수이면 ValueError 발생"""
        # TODO: pytest.raises를 사용하세요
        pytest.skip("TODO: 출력 에너지 음수 예외 테스트를 구현하세요")


class TestFindPeakTemperatures:
    """피크 온도 감지 테스트"""

    def test_단일_피크(self):
        """하나의 피크가 감지되어야 한다"""
        # TODO: [20, 30, 50, 30, 20] 에서 인덱스 2의 피크 감지
        pytest.skip("TODO: 단일 피크 테스트를 구현하세요")

    def test_피크_없음(self):
        """오름차순 데이터에서는 피크가 없어야 한다"""
        # TODO: [10, 20, 30, 40, 50]에서 빈 리스트 반환
        pytest.skip("TODO: 피크 없음 테스트를 구현하세요")

    def test_최소_데이터_예외(self):
        """3개 미만의 데이터에서는 ValueError 발생"""
        # TODO: pytest.raises 사용
        pytest.skip("TODO: 최소 데이터 예외 테스트를 구현하세요")
