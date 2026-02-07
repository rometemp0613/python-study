"""
연습 문제 32 풀이: 센서 데이터 수집/처리 테스트

각 테스트의 완성된 풀이입니다.
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
    """온도 센서 데이터 전처리 테스트"""

    def test_결측치_forward_fill_시뮬레이션(self, processor):
        """결측치를 보간으로 채우는 동작 테스트"""
        # 준비
        data = [None, 25.0, None, 27.0, None]

        # 실행
        cleaned = processor.clean_data(data)

        # 검증
        # 시작 None은 첫 유효값(25.0)으로 채움
        assert cleaned[0] == 25.0
        # 25.0과 27.0 사이 보간 → 26.0
        assert cleaned[2] == pytest.approx(26.0)
        # 끝 None은 마지막 유효값(27.0)으로 채움
        assert cleaned[4] == 27.0
        # None이 없어야 함
        assert None not in cleaned

    def test_극단적_온도값_이상치_제거(self, processor):
        """물리적으로 불가능한 온도값이 제거되는지 테스트"""
        # 준비: 정상 온도 범위(23~26) + 극단적 이상치(500)
        data = [25.0, 26.0, 24.0, 25.0, 500.0, 23.0, 25.0, 24.0]

        # 실행
        cleaned = processor.remove_outliers(data, method="iqr")

        # 검증
        assert 500.0 not in cleaned
        # 정상 데이터는 유지되어야 함
        assert len(cleaned) == 7
        # 남은 값들은 합리적 범위 내
        assert all(20.0 <= v <= 30.0 for v in cleaned)


# ============================================================
# 연습 2: 특징 추출 파이프라인 테스트
# ============================================================

class TestFeatureExtractionPipeline:
    """extract_all_features() 함수 검증"""

    def test_특징_딕셔너리_키_확인(self, processor):
        """모든 필수 키가 존재하는지 확인"""
        # 준비
        data = [1.0, 2.0, 3.0, 4.0, 5.0]

        # 실행
        features = processor.extract_all_features(data)

        # 검증
        expected_keys = {
            "rms", "kurtosis", "peak_to_peak", "crest_factor",
            "mean", "std", "max", "min",
        }
        assert set(features.keys()) == expected_keys

    def test_특징값_유효성_검증(self, processor):
        """추출된 특징값의 물리적 유효성 검증"""
        # 준비: 사인파 형태의 진동 데이터
        data = [math.sin(2 * math.pi * i / 50) for i in range(100)]

        # 실행
        features = processor.extract_all_features(data)

        # 검증
        assert features["rms"] > 0, "RMS는 양수여야 합니다"
        assert features["peak_to_peak"] >= 0, "Peak-to-Peak은 0 이상이어야 합니다"
        assert features["crest_factor"] >= 1.0, "Crest Factor는 1 이상이어야 합니다"
        assert features["min"] <= features["mean"] <= features["max"], \
            "mean은 min과 max 사이여야 합니다"
        assert features["std"] >= 0, "표준편차는 0 이상이어야 합니다"

    def test_알려진_데이터의_정확한_특징값(self, processor):
        """수동 계산값과 비교"""
        # 준비
        data = [1.0, 2.0, 3.0, 4.0]

        # 실행
        features = processor.extract_all_features(data)

        # 검증
        assert features["mean"] == pytest.approx(2.5)
        assert features["max"] == pytest.approx(4.0)
        assert features["min"] == pytest.approx(1.0)
        assert features["peak_to_peak"] == pytest.approx(3.0)
        # RMS = sqrt((1+4+9+16)/4) = sqrt(7.5) ≈ 2.7386
        assert features["rms"] == pytest.approx(math.sqrt(7.5), abs=0.001)


# ============================================================
# 연습 3: CSV 파일 에러 처리 테스트
# ============================================================

class TestCSVErrorHandling:
    """CSV 파일 오류 상황 테스트"""

    def test_빈_csv_파일(self, processor, tmp_path):
        """빈 CSV 파일 로딩 시 ValueError 발생"""
        # 준비: 빈 파일 생성
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        # 실행 & 검증
        with pytest.raises(ValueError, match="비어있습니다"):
            processor.load_csv(str(csv_file))

    def test_잘못된_숫자형식_csv(self, processor, tmp_path):
        """숫자 컬럼에 문자열이 있는 CSV 파일"""
        # 준비: 잘못된 형식의 CSV 생성
        csv_file = tmp_path / "malformed.csv"
        csv_file.write_text(
            "timestamp,amplitude\n"
            "0.001,1.2\n"
            "abc,xyz\n"
        )

        # 실행 & 검증
        with pytest.raises(ValueError, match="변환 오류"):
            processor.load_csv(str(csv_file))

    def test_존재하지_않는_파일(self, processor):
        """존재하지 않는 파일 경로로 FileNotFoundError 발생"""
        with pytest.raises(FileNotFoundError):
            processor.load_csv("/존재하지않는경로/data.csv")
