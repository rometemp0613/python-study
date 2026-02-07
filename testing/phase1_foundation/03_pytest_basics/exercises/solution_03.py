"""
연습 문제 03: 풀이

pytest 기본기 실습 풀이.

실행 방법:
    pytest exercises/solution_03.py -v
"""

import pytest


# ============================================================
# 테스트 대상 함수들
# ============================================================

def kelvin_to_celsius(kelvin):
    """켈빈을 섭씨로 변환한다."""
    if kelvin < 0:
        raise ValueError("켈빈 온도는 0 이상이어야 합니다 (절대영도)")
    return kelvin - 273.15


def calculate_thermal_efficiency(input_energy, output_energy):
    """열효율을 계산한다."""
    if input_energy <= 0:
        raise ValueError("입력 에너지는 0보다 커야 합니다")
    if output_energy < 0:
        raise ValueError("출력 에너지는 0 이상이어야 합니다")
    return (output_energy / input_energy) * 100


def find_peak_temperatures(readings, min_prominence=5.0):
    """온도 읽기 값에서 피크를 찾는다."""
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
# 테스트 코드 (풀이)
# ============================================================

class TestKelvinToCelsius:
    """켈빈 → 섭씨 변환 테스트"""

    @pytest.mark.parametrize("kelvin, expected_celsius", [
        (273.15, 0.0),       # 물의 어는점
        (373.15, 100.0),     # 물의 끓는점
        (0, -273.15),        # 절대영도
        (310.15, 37.0),      # 체온
        (293.15, 20.0),      # 실온
    ])
    def test_변환_parametrize(self, kelvin, expected_celsius):
        """여러 온도값에 대해 변환을 검증한다"""
        result = kelvin_to_celsius(kelvin)
        assert result == pytest.approx(expected_celsius, abs=0.01)

    def test_절대영도_이하_예외(self):
        """절대영도(0K) 미만이면 ValueError가 발생해야 한다"""
        with pytest.raises(ValueError, match="절대영도"):
            kelvin_to_celsius(-1)

    def test_절대영도_정확히(self):
        """절대영도(0K)는 유효하다"""
        result = kelvin_to_celsius(0)
        assert result == pytest.approx(-273.15)


class TestCalculateThermalEfficiency:
    """열효율 계산 테스트"""

    def test_100퍼센트_효율(self):
        """입력과 출력이 같으면 100% 효율"""
        result = calculate_thermal_efficiency(100, 100)
        assert result == pytest.approx(100.0)

    def test_50퍼센트_효율(self):
        """출력이 입력의 절반이면 50% 효율"""
        result = calculate_thermal_efficiency(100, 50)
        assert result == pytest.approx(50.0)

    def test_0퍼센트_효율(self):
        """출력이 0이면 0% 효율"""
        result = calculate_thermal_efficiency(100, 0)
        assert result == pytest.approx(0.0)

    def test_소수점_효율(self):
        """소수점 효율 계산"""
        result = calculate_thermal_efficiency(300, 100)
        assert result == pytest.approx(33.333, abs=0.01)

    def test_입력_에너지_0_예외(self):
        """입력 에너지가 0이면 ValueError 발생"""
        with pytest.raises(ValueError, match="입력 에너지"):
            calculate_thermal_efficiency(0, 50)

    def test_입력_에너지_음수_예외(self):
        """입력 에너지가 음수이면 ValueError 발생"""
        with pytest.raises(ValueError):
            calculate_thermal_efficiency(-100, 50)

    def test_출력_에너지_음수_예외(self):
        """출력 에너지가 음수이면 ValueError 발생"""
        with pytest.raises(ValueError, match="출력 에너지"):
            calculate_thermal_efficiency(100, -10)


class TestFindPeakTemperatures:
    """피크 온도 감지 테스트"""

    def test_단일_피크(self):
        """하나의 피크가 감지되어야 한다"""
        readings = [20, 30, 50, 30, 20]
        peaks = find_peak_temperatures(readings)
        assert len(peaks) == 1
        assert peaks[0]["index"] == 2
        assert peaks[0]["value"] == 50

    def test_복수_피크(self):
        """여러 피크가 감지되어야 한다"""
        readings = [10, 30, 15, 40, 10]
        peaks = find_peak_temperatures(readings)
        assert len(peaks) == 2

    def test_피크_없음(self):
        """오름차순 데이터에서는 피크가 없어야 한다"""
        readings = [10, 20, 30, 40, 50]
        peaks = find_peak_temperatures(readings)
        assert peaks == []

    def test_내림차순_피크_없음(self):
        """내림차순 데이터에서도 피크가 없어야 한다"""
        readings = [50, 40, 30, 20, 10]
        peaks = find_peak_temperatures(readings)
        assert peaks == []

    def test_최소_돌출도(self):
        """min_prominence 미만의 피크는 무시해야 한다"""
        readings = [20, 22, 20]  # 돌출도 2 (기본 min_prominence=5 미만)
        peaks = find_peak_temperatures(readings)
        assert peaks == []

        # min_prominence를 1로 낮추면 감지됨
        peaks_sensitive = find_peak_temperatures(readings, min_prominence=1.0)
        assert len(peaks_sensitive) == 1

    def test_최소_데이터_예외(self):
        """3개 미만의 데이터에서는 ValueError 발생"""
        with pytest.raises(ValueError, match="최소 3개"):
            find_peak_temperatures([10, 20])

    def test_피크_필드_확인(self):
        """피크 결과에 필수 필드가 있어야 한다"""
        readings = [10, 50, 10]
        peaks = find_peak_temperatures(readings)
        assert len(peaks) == 1
        assert "index" in peaks[0]
        assert "value" in peaks[0]
        assert "prominence" in peaks[0]
