"""
진동 데이터 처리기 테스트 모듈

VibrationDataProcessor 클래스의 전체 파이프라인을 테스트합니다:
- CSV 로딩
- 데이터 클리닝 (결측치 보간)
- 이상치 제거
- 리샘플링
- 특징 추출 (RMS, Kurtosis, Peak-to-Peak, Crest Factor)
"""

import math
import pytest
from src_vibration_processor import VibrationDataProcessor


# ============================================================
# 픽스처
# ============================================================

@pytest.fixture
def processor():
    """VibrationDataProcessor 인스턴스"""
    return VibrationDataProcessor()


# ============================================================
# CSV 로딩 테스트
# ============================================================

class TestLoadCSV:
    """CSV 파일 로딩 관련 테스트"""

    def test_정상_csv_로딩(self, processor, sample_csv_file):
        """정상 CSV 파일을 올바르게 로딩하는지 테스트"""
        data = processor.load_csv(sample_csv_file)

        assert len(data) == 5
        assert data[0]["timestamp"] == 0.0
        assert data[0]["amplitude"] == 0.5
        assert data[4]["amplitude"] == -1.1

    def test_각_행이_딕셔너리로_변환(self, processor, sample_csv_file):
        """각 행이 올바른 키를 가진 딕셔너리인지 테스트"""
        data = processor.load_csv(sample_csv_file)

        for row in data:
            assert "timestamp" in row
            assert "amplitude" in row
            assert isinstance(row["timestamp"], float)
            assert isinstance(row["amplitude"], float)

    def test_빈_파일_로딩_에러(self, processor, empty_csv_file):
        """빈 CSV 파일 로딩 시 ValueError 발생"""
        with pytest.raises(ValueError, match="비어있습니다"):
            processor.load_csv(empty_csv_file)

    def test_헤더만_있는_파일(self, processor, header_only_csv_file):
        """헤더만 있고 데이터가 없는 CSV 파일"""
        data = processor.load_csv(header_only_csv_file)
        assert len(data) == 0

    def test_잘못된_데이터_타입(self, processor, malformed_csv_file):
        """숫자가 아닌 데이터가 포함된 CSV 파일"""
        with pytest.raises(ValueError, match="변환 오류"):
            processor.load_csv(malformed_csv_file)

    def test_필수_컬럼_누락(self, processor, missing_column_csv_file):
        """필수 컬럼(amplitude)이 없는 CSV 파일"""
        with pytest.raises(ValueError, match="필수 컬럼"):
            processor.load_csv(missing_column_csv_file)

    def test_존재하지_않는_파일(self, processor):
        """존재하지 않는 파일 경로"""
        with pytest.raises(FileNotFoundError):
            processor.load_csv("/nonexistent/path/data.csv")


# ============================================================
# 데이터 클리닝 테스트
# ============================================================

class TestCleanData:
    """결측치 처리 및 선형 보간 테스트"""

    def test_결측치_없는_데이터(self, processor):
        """결측치가 없으면 원본 그대로 반환"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        cleaned = processor.clean_data(data)
        assert cleaned == data

    def test_중간_결측치_선형보간(self, processor):
        """중간의 None을 선형 보간으로 채우는지 테스트"""
        data = [1.0, 2.0, None, 4.0, 5.0]
        cleaned = processor.clean_data(data)

        assert cleaned[2] == pytest.approx(3.0)
        assert None not in cleaned

    def test_연속_결측치_보간(self, processor):
        """연속된 None 값을 올바르게 보간하는지 테스트"""
        data = [0.0, None, None, None, 4.0]
        cleaned = processor.clean_data(data)

        assert cleaned[1] == pytest.approx(1.0)
        assert cleaned[2] == pytest.approx(2.0)
        assert cleaned[3] == pytest.approx(3.0)

    def test_시작부분_결측치(self, processor):
        """데이터 시작 부분의 None은 첫 유효값으로 채움"""
        data = [None, None, 3.0, 4.0, 5.0]
        cleaned = processor.clean_data(data)

        assert cleaned[0] == 3.0
        assert cleaned[1] == 3.0

    def test_끝부분_결측치(self, processor):
        """데이터 끝 부분의 None은 마지막 유효값으로 채움"""
        data = [1.0, 2.0, 3.0, None, None]
        cleaned = processor.clean_data(data)

        assert cleaned[3] == 3.0
        assert cleaned[4] == 3.0

    def test_결측치_포함_데이터_픽스처(self, processor, data_with_missing_values):
        """conftest에서 제공하는 결측치 데이터 테스트"""
        cleaned = processor.clean_data(data_with_missing_values)

        assert len(cleaned) == len(data_with_missing_values)
        assert None not in cleaned
        # 인덱스 2: 2.0과 5.0 사이 보간 → 3.0
        assert cleaned[2] == pytest.approx(3.0)
        # 인덱스 3: 2.0과 5.0 사이 보간 → 4.0
        assert cleaned[3] == pytest.approx(4.0)

    def test_빈_데이터_에러(self, processor):
        """빈 리스트에 대해 ValueError 발생"""
        with pytest.raises(ValueError, match="비어있습니다"):
            processor.clean_data([])

    def test_모든_값_결측_에러(self, processor):
        """모든 값이 None인 경우 ValueError 발생"""
        with pytest.raises(ValueError, match="모든 값이 결측치"):
            processor.clean_data([None, None, None])


# ============================================================
# 이상치 제거 테스트
# ============================================================

class TestRemoveOutliers:
    """IQR 방법 기반 이상치 제거 테스트"""

    def test_이상치_제거_기본(self, processor):
        """극단적인 이상치가 제거되는지 테스트"""
        data = [1.0, 1.1, 1.2, 0.9, 1.0, 100.0, 1.1, 0.8]
        cleaned = processor.remove_outliers(data, method="iqr")

        assert 100.0 not in cleaned
        assert len(cleaned) < len(data)

    def test_정상_데이터_유지(self, processor, sample_vibration_data):
        """정상 분포 데이터는 대부분 유지되어야 함"""
        cleaned = processor.remove_outliers(sample_vibration_data, method="iqr")

        # 사인파 데이터는 이상치가 없으므로 대부분 유지
        assert len(cleaned) >= len(sample_vibration_data) * 0.9

    def test_노이즈_데이터_이상치_제거(self, processor, noisy_vibration_data):
        """극단적 이상치(100, -100)가 제거되는지 테스트"""
        cleaned = processor.remove_outliers(noisy_vibration_data, method="iqr")

        assert 100.0 not in cleaned
        assert -100.0 not in cleaned

    def test_소량_데이터_원본_반환(self, processor):
        """데이터가 4개 미만이면 원본 그대로 반환"""
        data = [1.0, 2.0, 3.0]
        cleaned = processor.remove_outliers(data)
        assert cleaned == data

    def test_지원하지_않는_방법_에러(self, processor):
        """지원하지 않는 이상치 제거 방법"""
        with pytest.raises(ValueError, match="지원하지 않는"):
            processor.remove_outliers([1.0, 2.0, 3.0, 4.0], method="zscore")


# ============================================================
# 리샘플링 테스트
# ============================================================

class TestResample:
    """시계열 리샘플링 테스트"""

    def test_다운샘플링(self, processor):
        """10개 샘플을 5개로 다운샘플링"""
        data = list(range(10))
        resampled = processor.resample(data, target_freq=5)

        assert len(resampled) == 5

    def test_동일_주파수(self, processor):
        """같은 주파수면 원본 복사본 반환"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        resampled = processor.resample(data, target_freq=5)

        assert resampled == data

    def test_업샘플링(self, processor):
        """5개 샘플을 10개로 업샘플링"""
        data = [0.0, 1.0, 2.0, 3.0, 4.0]
        resampled = processor.resample(data, target_freq=10)

        assert len(resampled) == 10
        # 시작과 끝 값은 유지되어야 함
        assert resampled[0] == pytest.approx(0.0, abs=0.1)
        assert resampled[-1] == pytest.approx(4.0, abs=0.1)

    def test_빈_데이터_에러(self, processor):
        """빈 데이터 리샘플링 시 에러"""
        with pytest.raises(ValueError, match="비어있습니다"):
            processor.resample([], target_freq=5)

    def test_음수_주파수_에러(self, processor):
        """음수 주파수에 대해 에러"""
        with pytest.raises(ValueError, match="양수"):
            processor.resample([1.0, 2.0], target_freq=-1)


# ============================================================
# RMS 계산 테스트
# ============================================================

class TestCalculateRMS:
    """RMS(Root Mean Square) 계산 테스트"""

    def test_간단한_값(self, processor):
        """간단한 값으로 RMS 계산 검증"""
        # RMS of [3, 4] = sqrt((9+16)/2) = sqrt(12.5) ≈ 3.5355
        data = [3.0, 4.0]
        rms = processor.calculate_rms(data)
        assert rms == pytest.approx(3.5355, abs=0.001)

    def test_동일한_값(self, processor):
        """모든 값이 같으면 RMS = 그 값의 절대값"""
        data = [5.0, 5.0, 5.0]
        rms = processor.calculate_rms(data)
        assert rms == pytest.approx(5.0)

    def test_제로_데이터(self, processor):
        """모든 값이 0이면 RMS = 0"""
        data = [0.0, 0.0, 0.0]
        rms = processor.calculate_rms(data)
        assert rms == 0.0

    def test_음수_포함(self, processor):
        """음수를 포함한 데이터의 RMS"""
        # RMS of [-3, 4] = sqrt((9+16)/2) = sqrt(12.5)
        data = [-3.0, 4.0]
        rms = processor.calculate_rms(data)
        assert rms == pytest.approx(3.5355, abs=0.001)

    def test_사인파_RMS(self, processor, sample_vibration_data):
        """사인파의 RMS는 1/sqrt(2) ≈ 0.7071에 가까워야 함"""
        rms = processor.calculate_rms(sample_vibration_data)
        # 완전한 주기의 사인파 RMS = 1/sqrt(2)
        assert rms == pytest.approx(1.0 / math.sqrt(2), abs=0.05)

    def test_빈_데이터_에러(self, processor):
        """빈 데이터에 대해 ValueError 발생"""
        with pytest.raises(ValueError, match="비어있습니다"):
            processor.calculate_rms([])

    def test_단일_값(self, processor, single_value_data):
        """단일 값의 RMS는 그 값의 절대값"""
        rms = processor.calculate_rms(single_value_data)
        assert rms == pytest.approx(3.14)


# ============================================================
# 첨도(Kurtosis) 계산 테스트
# ============================================================

class TestCalculateKurtosis:
    """첨도(Kurtosis) 계산 테스트"""

    def test_균등분포_첨도(self, processor):
        """균등분포의 excess kurtosis는 약 -1.2"""
        # 균등분포 데이터
        data = [float(i) for i in range(1, 101)]
        kurtosis = processor.calculate_kurtosis(data)
        # 균등분포의 이론적 excess kurtosis ≈ -1.2
        assert kurtosis == pytest.approx(-1.2, abs=0.1)

    def test_일정한_데이터(self, processor, constant_data):
        """일정한 값의 첨도는 0 (분산이 0이므로)"""
        kurtosis = processor.calculate_kurtosis(constant_data)
        assert kurtosis == 0.0

    def test_데이터_부족_에러(self, processor):
        """4개 미만의 데이터에 대해 ValueError 발생"""
        with pytest.raises(ValueError, match="최소 4개"):
            processor.calculate_kurtosis([1.0, 2.0, 3.0])

    def test_충격_데이터_높은_첨도(self, processor):
        """충격 성분이 많은 데이터는 높은 첨도를 가짐"""
        # 대부분 0이지만 간헐적으로 큰 값 (충격)
        data = [0.0] * 96 + [10.0, -10.0, 10.0, -10.0]
        kurtosis = processor.calculate_kurtosis(data)
        # 충격 데이터는 높은 양의 첨도를 가져야 함
        assert kurtosis > 5.0


# ============================================================
# Peak-to-Peak 계산 테스트
# ============================================================

class TestCalculatePeakToPeak:
    """Peak-to-Peak 계산 테스트"""

    def test_기본_계산(self, processor):
        """단순한 Peak-to-Peak 계산"""
        data = [1.0, 5.0, 3.0, -2.0, 4.0]
        p2p = processor.calculate_peak_to_peak(data)
        assert p2p == pytest.approx(7.0)  # 5.0 - (-2.0) = 7.0

    def test_사인파(self, processor, sample_vibration_data):
        """사인파의 Peak-to-Peak은 약 2.0"""
        p2p = processor.calculate_peak_to_peak(sample_vibration_data)
        assert p2p == pytest.approx(2.0, abs=0.05)

    def test_동일한_값(self, processor, constant_data):
        """모든 값이 같으면 Peak-to-Peak = 0"""
        p2p = processor.calculate_peak_to_peak(constant_data)
        assert p2p == 0.0

    def test_빈_데이터_에러(self, processor):
        """빈 데이터에 대해 ValueError 발생"""
        with pytest.raises(ValueError, match="비어있습니다"):
            processor.calculate_peak_to_peak([])


# ============================================================
# Crest Factor 계산 테스트
# ============================================================

class TestCalculateCrestFactor:
    """Crest Factor(= peak / RMS) 계산 테스트"""

    def test_기본_계산(self, processor):
        """Crest Factor 기본 계산 검증"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        cf = processor.calculate_crest_factor(data)

        # peak = 5.0, RMS = sqrt((1+4+9+16+25)/5) = sqrt(11) ≈ 3.3166
        expected_rms = math.sqrt(55 / 5)
        expected_cf = 5.0 / expected_rms
        assert cf == pytest.approx(expected_cf, abs=0.001)

    def test_사인파_crest_factor(self, processor, sample_vibration_data):
        """사인파의 Crest Factor는 약 sqrt(2) ≈ 1.414"""
        cf = processor.calculate_crest_factor(sample_vibration_data)
        assert cf == pytest.approx(math.sqrt(2), abs=0.1)

    def test_일정한_값(self, processor):
        """일정한 양수 값의 Crest Factor = 1.0"""
        data = [3.0, 3.0, 3.0, 3.0]
        cf = processor.calculate_crest_factor(data)
        assert cf == pytest.approx(1.0)

    def test_제로_데이터_에러(self, processor):
        """모든 값이 0이면 RMS=0으로 인해 에러"""
        with pytest.raises(ValueError, match="RMS가 0"):
            processor.calculate_crest_factor([0.0, 0.0, 0.0])

    def test_빈_데이터_에러(self, processor):
        """빈 데이터에 대해 ValueError 발생"""
        with pytest.raises(ValueError, match="비어있습니다"):
            processor.calculate_crest_factor([])


# ============================================================
# 전체 특징 추출 테스트
# ============================================================

class TestExtractAllFeatures:
    """extract_all_features() 통합 테스트"""

    def test_반환_키_확인(self, processor, sample_vibration_data):
        """모든 예상 키가 포함되어 있는지 확인"""
        features = processor.extract_all_features(sample_vibration_data)

        expected_keys = {
            "rms", "kurtosis", "peak_to_peak", "crest_factor",
            "mean", "std", "max", "min",
        }
        assert set(features.keys()) == expected_keys

    def test_모든_값이_float(self, processor, sample_vibration_data):
        """모든 특징값이 float 타입인지 확인"""
        features = processor.extract_all_features(sample_vibration_data)

        for key, value in features.items():
            assert isinstance(value, float), f"{key}의 타입이 float가 아닙니다"

    def test_값_범위_합리성(self, processor, sample_vibration_data):
        """사인파 데이터의 특징값이 합리적인 범위인지 확인"""
        features = processor.extract_all_features(sample_vibration_data)

        # RMS는 양수
        assert features["rms"] > 0
        # Peak-to-Peak은 양수
        assert features["peak_to_peak"] > 0
        # Crest Factor >= 1 (peak >= RMS 이므로)
        assert features["crest_factor"] >= 1.0
        # max >= min
        assert features["max"] >= features["min"]
        # max와 min 사이에 mean이 있어야 함
        assert features["min"] <= features["mean"] <= features["max"]

    def test_데이터_부족_에러(self, processor):
        """4개 미만 데이터에 대해 ValueError"""
        with pytest.raises(ValueError, match="최소 4개"):
            processor.extract_all_features([1.0, 2.0, 3.0])

    def test_빈_데이터_에러(self, processor):
        """빈 데이터에 대해 ValueError"""
        with pytest.raises(ValueError, match="비어있습니다"):
            processor.extract_all_features([])


# ============================================================
# 통합 파이프라인 테스트
# ============================================================

class TestPipeline:
    """전체 데이터 처리 파이프라인 통합 테스트"""

    def test_csv에서_특징추출까지(self, processor, sample_csv_file):
        """CSV 로딩 → 진폭 추출 → 특징 추출 전체 흐름"""
        # 1단계: CSV 로딩
        raw_data = processor.load_csv(sample_csv_file)
        assert len(raw_data) > 0

        # 2단계: 진폭 값 추출
        amplitudes = [row["amplitude"] for row in raw_data]
        assert len(amplitudes) == len(raw_data)

        # 3단계: 특징 추출 (최소 4개 데이터 필요)
        features = processor.extract_all_features(amplitudes)
        assert "rms" in features
        assert features["rms"] > 0

    def test_클리닝후_특징추출(self, processor, data_with_missing_values):
        """결측치 처리 → 특징 추출 흐름"""
        # 1단계: 클리닝
        cleaned = processor.clean_data(data_with_missing_values)
        assert None not in cleaned

        # 2단계: 특징 추출
        features = processor.extract_all_features(cleaned)
        assert all(isinstance(v, float) for v in features.values())

    def test_이상치제거후_특징변화(self, processor, noisy_vibration_data):
        """이상치 제거 전후의 특징값 변화 검증"""
        # 이상치 포함 특징
        features_before = processor.extract_all_features(noisy_vibration_data)

        # 이상치 제거 후 특징
        cleaned = processor.remove_outliers(noisy_vibration_data)
        features_after = processor.extract_all_features(cleaned)

        # 이상치 제거 후 Peak-to-Peak은 크게 감소해야 함
        assert features_after["peak_to_peak"] < features_before["peak_to_peak"]
        # 이상치 제거 후 Crest Factor도 감소해야 함
        assert features_after["crest_factor"] < features_before["crest_factor"]

    def test_대량_데이터_처리(self, processor, large_vibration_data):
        """1000개 샘플 데이터의 전체 파이프라인 처리"""
        # 이상치 제거
        cleaned = processor.remove_outliers(large_vibration_data)
        assert len(cleaned) > 0

        # 리샘플링 (1000 → 500)
        resampled = processor.resample(cleaned, target_freq=500)
        assert len(resampled) == 500

        # 특징 추출
        features = processor.extract_all_features(resampled)
        assert features["rms"] > 0
        assert isinstance(features["kurtosis"], float)
