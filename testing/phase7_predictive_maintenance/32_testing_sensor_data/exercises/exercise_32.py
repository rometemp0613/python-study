"""
연습 문제 32: 센서 데이터 수집/처리 테스트

이 파일의 TODO를 완성하여 센서 데이터 처리 함수들을 테스트하세요.
"""

import math
import pytest
import sys
import os

# 부모 디렉토리의 모듈을 임포트하기 위한 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_vibration_processor import VibrationDataProcessor


@pytest.fixture
def processor():
    """VibrationDataProcessor 인스턴스"""
    return VibrationDataProcessor()


# ============================================================
# 연습 1: 온도 센서 데이터 전처리 테스트
# ============================================================

class TestTemperatureDataCleaning:
    """
    온도 센서 데이터 전처리를 테스트하세요.

    VibrationDataProcessor의 clean_data와 remove_outliers를
    온도 데이터에 적용하는 시나리오입니다.
    """

    def test_결측치_forward_fill_시뮬레이션(self, processor):
        """
        결측치를 이전 유효값으로 채우는 동작을 테스트하세요.

        clean_data()는 선형 보간을 사용하지만,
        시작 부분의 None은 첫 유효값으로 채우는 것을 확인하세요.

        데이터: [None, 25.0, None, 27.0, None]
        기대값: [25.0, 25.0, 26.0, 27.0, 27.0]
        """
        pytest.skip("TODO: clean_data()로 결측치 처리 후 기대값과 비교하세요")

    def test_극단적_온도값_이상치_제거(self, processor):
        """
        물리적으로 불가능한 온도값이 이상치로 제거되는지 테스트하세요.

        데이터: [25.0, 26.0, 24.0, 25.0, 500.0, 23.0, 25.0, 24.0]
        500.0은 공장 온도로 불가능하므로 제거되어야 합니다.
        """
        pytest.skip("TODO: remove_outliers()를 사용하여 500.0이 제거되는지 확인하세요")


# ============================================================
# 연습 2: 특징 추출 파이프라인 테스트
# ============================================================

class TestFeatureExtractionPipeline:
    """
    extract_all_features() 함수의 반환값을 검증하세요.
    """

    def test_특징_딕셔너리_키_확인(self, processor):
        """
        extract_all_features()가 반환하는 딕셔너리에
        모든 필수 키가 존재하는지 확인하세요.

        필수 키: rms, kurtosis, peak_to_peak, crest_factor,
                mean, std, max, min
        """
        pytest.skip("TODO: [1.0, 2.0, 3.0, 4.0, 5.0] 데이터로 특징을 추출하고 키를 확인하세요")

    def test_특징값_유효성_검증(self, processor):
        """
        추출된 특징값들이 물리적으로 유효한지 검증하세요.

        - rms > 0
        - peak_to_peak >= 0
        - crest_factor >= 1.0
        - min <= mean <= max
        - std >= 0
        """
        pytest.skip("TODO: 진동 데이터에서 추출한 특징값의 유효성을 검증하세요")

    def test_알려진_데이터의_정확한_특징값(self, processor):
        """
        수동으로 계산 가능한 데이터의 특징값을 검증하세요.

        데이터: [1.0, 2.0, 3.0, 4.0]
        - mean = 2.5
        - max = 4.0
        - min = 1.0
        - peak_to_peak = 3.0
        - rms = sqrt((1+4+9+16)/4) = sqrt(7.5) ≈ 2.7386
        """
        pytest.skip("TODO: 수동 계산값과 함수 출력을 pytest.approx로 비교하세요")


# ============================================================
# 연습 3: CSV 파일 에러 처리 테스트
# ============================================================

class TestCSVErrorHandling:
    """
    다양한 CSV 파일 오류 상황에 대한 에러 처리를 테스트하세요.
    """

    def test_빈_csv_파일(self, processor, tmp_path):
        """
        빈 CSV 파일을 로딩할 때 ValueError가 발생하는지 테스트하세요.

        힌트: tmp_path를 사용하여 빈 파일을 생성하세요.
        """
        pytest.skip("TODO: 빈 CSV 파일을 생성하고 load_csv()가 ValueError를 발생시키는지 확인하세요")

    def test_잘못된_숫자형식_csv(self, processor, tmp_path):
        """
        숫자 컬럼에 문자열이 들어있는 CSV 파일을 테스트하세요.

        CSV 내용:
        timestamp,amplitude
        0.001,1.2
        abc,xyz
        """
        pytest.skip("TODO: 잘못된 형식의 CSV 파일을 만들고 ValueError 발생을 확인하세요")

    def test_존재하지_않는_파일(self, processor):
        """
        존재하지 않는 파일 경로로 load_csv()를 호출할 때
        FileNotFoundError가 발생하는지 테스트하세요.
        """
        pytest.skip("TODO: 존재하지 않는 경로로 load_csv()를 호출하세요")
