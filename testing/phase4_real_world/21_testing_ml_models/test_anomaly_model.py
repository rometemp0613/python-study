"""
이상 탐지 모델 테스트

SimpleAnomalyDetector의 학습, 예측, 분류, 특징 추출,
직렬화/역직렬화를 검증합니다.

외부 의존성 없이 표준 라이브러리만 사용합니다.
"""
import json
import math
import pytest

from src_anomaly_model import SimpleAnomalyDetector


# ============================================================
# 픽스처
# ============================================================

@pytest.fixture
def detector():
    """학습되지 않은 모델 인스턴스"""
    return SimpleAnomalyDetector()


@pytest.fixture
def fitted_detector():
    """학습된 모델 인스턴스"""
    model = SimpleAnomalyDetector()
    model.fit([10.0, 20.0, 30.0, 40.0, 50.0])
    return model


@pytest.fixture
def known_detector():
    """파라미터가 알려진 모델 (mean=50, std=10)"""
    model = SimpleAnomalyDetector()
    model.mean = 50.0
    model.std = 10.0
    model.is_fitted = True
    model.n_samples = 100
    return model


# ============================================================
# fit() 테스트
# ============================================================

class TestFit:
    """모델 학습 테스트"""

    def test_mean_calculation(self, detector):
        """평균 계산 정확성"""
        detector.fit([10.0, 20.0, 30.0, 40.0, 50.0])
        assert detector.mean == pytest.approx(30.0)

    def test_std_calculation(self, detector):
        """표준편차 계산 정확성"""
        detector.fit([10.0, 20.0, 30.0, 40.0, 50.0])
        # 모집단 표준편차: sqrt(200) = 14.1421...
        expected_std = math.sqrt(
            sum((x - 30.0) ** 2 for x in [10, 20, 30, 40, 50]) / 5
        )
        assert detector.std == pytest.approx(expected_std, rel=1e-10)

    def test_fit_sets_is_fitted(self, detector):
        """학습 후 is_fitted 플래그 설정"""
        assert detector.is_fitted is False
        detector.fit([1.0, 2.0, 3.0])
        assert detector.is_fitted is True

    def test_fit_records_sample_count(self, detector):
        """학습 데이터 개수 기록"""
        detector.fit([1.0, 2.0, 3.0, 4.0])
        assert detector.n_samples == 4

    def test_fit_single_value(self, detector):
        """단일 값으로 학습"""
        detector.fit([42.0])
        assert detector.mean == 42.0
        assert detector.std == 0.0

    def test_fit_constant_values(self, detector):
        """모든 값이 동일한 데이터로 학습"""
        detector.fit([25.0, 25.0, 25.0, 25.0])
        assert detector.mean == 25.0
        assert detector.std == 0.0

    def test_fit_empty_data_raises_error(self, detector):
        """빈 데이터로 학습 시도 -> ValueError"""
        with pytest.raises(ValueError, match="비어있습니다"):
            detector.fit([])

    def test_fit_updates_previous_model(self, fitted_detector):
        """재학습 시 기존 파라미터가 업데이트되는지 확인"""
        old_mean = fitted_detector.mean
        fitted_detector.fit([100.0, 200.0, 300.0])
        assert fitted_detector.mean != old_mean
        assert fitted_detector.mean == pytest.approx(200.0)


# ============================================================
# predict() 테스트
# ============================================================

class TestPredict:
    """이상 점수 예측 테스트"""

    def test_predict_known_z_scores(self, known_detector):
        """알려진 Z-score 값 검증"""
        scores = known_detector.predict([50.0, 60.0, 70.0, 30.0])
        # z = |x - 50| / 10
        assert scores[0] == pytest.approx(0.0)   # |50-50|/10 = 0.0
        assert scores[1] == pytest.approx(1.0)   # |60-50|/10 = 1.0
        assert scores[2] == pytest.approx(2.0)   # |70-50|/10 = 2.0
        assert scores[3] == pytest.approx(2.0)   # |30-50|/10 = 2.0

    def test_predict_returns_positive_scores(self, known_detector):
        """Z-score는 항상 0 이상"""
        scores = known_detector.predict([0.0, 50.0, 100.0, -50.0])
        assert all(score >= 0 for score in scores)

    def test_predict_mean_value_is_zero(self, known_detector):
        """평균값의 Z-score는 0"""
        scores = known_detector.predict([50.0])
        assert scores[0] == pytest.approx(0.0)

    def test_predict_std_zero_same_as_mean(self, detector):
        """std=0이고 값이 평균과 같으면 Z-score=0"""
        detector.fit([25.0, 25.0, 25.0])
        scores = detector.predict([25.0])
        assert scores[0] == 0.0

    def test_predict_std_zero_different_from_mean(self, detector):
        """std=0이고 값이 평균과 다르면 Z-score=inf"""
        detector.fit([25.0, 25.0, 25.0])
        scores = detector.predict([30.0])
        assert scores[0] == float("inf")

    def test_predict_not_fitted_raises_error(self, detector):
        """학습 전 예측 시도 -> RuntimeError"""
        with pytest.raises(RuntimeError, match="학습되지 않았습니다"):
            detector.predict([1.0, 2.0])

    def test_predict_empty_data_raises_error(self, fitted_detector):
        """빈 데이터로 예측 시도 -> ValueError"""
        with pytest.raises(ValueError, match="비어있습니다"):
            fitted_detector.predict([])

    def test_predict_returns_correct_length(self, known_detector):
        """예측 결과 길이가 입력 데이터와 같은지 확인"""
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        scores = known_detector.predict(data)
        assert len(scores) == len(data)


# ============================================================
# classify() 테스트
# ============================================================

class TestClassify:
    """이진 분류 테스트"""

    def test_classify_normal_and_anomaly(self, known_detector):
        """정상과 이상 데이터 분류"""
        # mean=50, std=10, threshold=2.0
        # z < 2: 정상, z >= 2: 이상
        labels = known_detector.classify(
            [50.0, 55.0, 65.0, 80.0], threshold=2.0
        )
        # z-scores: [0.0, 0.5, 1.5, 3.0]
        assert labels == [0, 0, 0, 1]

    def test_classify_all_normal(self, known_detector):
        """모든 데이터가 정상인 경우"""
        labels = known_detector.classify(
            [48.0, 50.0, 52.0], threshold=3.0
        )
        assert all(label == 0 for label in labels)

    def test_classify_all_anomaly(self, known_detector):
        """모든 데이터가 이상인 경우"""
        labels = known_detector.classify(
            [200.0, -100.0, 150.0], threshold=2.0
        )
        assert all(label == 1 for label in labels)

    def test_classify_boundary_value(self, known_detector):
        """임계값 경계에서의 분류"""
        # z = |70 - 50| / 10 = 2.0, threshold=2.0 -> 이상 (>=)
        labels = known_detector.classify([70.0], threshold=2.0)
        assert labels == [1]

    def test_default_threshold_is_three(self, known_detector):
        """기본 임계값은 3.0"""
        # z = |80 - 50| / 10 = 3.0 -> 이상 (기본 threshold=3.0)
        labels = known_detector.classify([80.0])
        assert labels == [1]

        # z = 2.9 -> 정상
        labels = known_detector.classify([79.0])
        assert labels == [0]


# ============================================================
# save_model / load_model 테스트
# ============================================================

class TestModelSerialization:
    """모델 직렬화/역직렬화 테스트"""

    def test_save_creates_file(self, tmp_path, fitted_detector):
        """모델 파일이 생성되는지 확인"""
        model_path = tmp_path / "model.json"
        fitted_detector.save_model(str(model_path))
        assert model_path.exists()

    def test_save_file_contains_parameters(self, tmp_path, fitted_detector):
        """저장된 파일에 필수 파라미터가 있는지 확인"""
        model_path = tmp_path / "model.json"
        fitted_detector.save_model(str(model_path))

        with open(str(model_path), "r") as f:
            data = json.load(f)

        assert "mean" in data
        assert "std" in data
        assert "is_fitted" in data

    def test_round_trip_preserves_parameters(self, tmp_path, fitted_detector):
        """저장 후 로드하면 파라미터가 보존되는지 확인"""
        model_path = tmp_path / "model.json"
        fitted_detector.save_model(str(model_path))

        loaded = SimpleAnomalyDetector()
        loaded.load_model(str(model_path))

        assert loaded.mean == pytest.approx(fitted_detector.mean)
        assert loaded.std == pytest.approx(fitted_detector.std)
        assert loaded.is_fitted == fitted_detector.is_fitted

    def test_round_trip_same_predictions(self, tmp_path, fitted_detector):
        """저장 후 로드한 모델이 동일한 예측을 하는지 확인"""
        model_path = tmp_path / "model.json"
        fitted_detector.save_model(str(model_path))

        loaded = SimpleAnomalyDetector()
        loaded.load_model(str(model_path))

        test_data = [15.0, 25.0, 35.0, 45.0, 55.0]
        original_scores = fitted_detector.predict(test_data)
        loaded_scores = loaded.predict(test_data)

        for orig, load in zip(original_scores, loaded_scores):
            assert orig == pytest.approx(load)

    def test_save_not_fitted_raises_error(self, detector, tmp_path):
        """학습 전 저장 시도 -> RuntimeError"""
        model_path = tmp_path / "model.json"
        with pytest.raises(RuntimeError, match="학습되지 않은"):
            detector.save_model(str(model_path))

    def test_load_nonexistent_file(self, detector):
        """존재하지 않는 파일 로드 -> FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            detector.load_model("/nonexistent/model.json")

    def test_load_invalid_json(self, tmp_path, detector):
        """잘못된 JSON 파일 로드 -> ValueError"""
        bad_file = tmp_path / "bad_model.json"
        bad_file.write_text("not valid json")

        with pytest.raises(ValueError, match="JSON"):
            detector.load_model(str(bad_file))

    def test_load_missing_fields(self, tmp_path, detector):
        """필수 필드 누락된 파일 로드 -> ValueError"""
        incomplete = tmp_path / "incomplete.json"
        incomplete.write_text(json.dumps({"mean": 50.0}))

        with pytest.raises(ValueError, match="필수 필드"):
            detector.load_model(str(incomplete))

    def test_save_creates_directory(self, tmp_path, fitted_detector):
        """저장 경로의 디렉토리가 없으면 자동 생성"""
        model_path = tmp_path / "subdir" / "nested" / "model.json"
        fitted_detector.save_model(str(model_path))
        assert model_path.exists()


# ============================================================
# extract_features() 테스트
# ============================================================

class TestExtractFeatures:
    """특징 추출 테스트"""

    def test_rms_calculation(self, detector):
        """RMS(Root Mean Square) 계산 정확성"""
        features = detector.extract_features([3.0, 4.0])
        expected_rms = math.sqrt((9.0 + 16.0) / 2)
        assert features["rms"] == pytest.approx(expected_rms)

    def test_peak_to_peak(self, detector):
        """피크 대 피크 계산"""
        features = detector.extract_features([5.0, -3.0, 8.0, -1.0])
        assert features["peak_to_peak"] == pytest.approx(11.0)

    def test_std_calculation(self, detector):
        """표준편차 계산"""
        features = detector.extract_features([10.0, 10.0, 10.0])
        assert features["std"] == pytest.approx(0.0)

    def test_mean_calculation(self, detector):
        """평균 계산"""
        features = detector.extract_features([10.0, 20.0, 30.0])
        assert features["mean"] == pytest.approx(20.0)

    def test_max_abs(self, detector):
        """최대 절대값"""
        features = detector.extract_features([5.0, -10.0, 3.0])
        assert features["max_abs"] == pytest.approx(10.0)

    def test_crest_factor(self, detector):
        """크레스트 팩터 (peak / rms)"""
        # 단순한 경우: 단일 값
        features = detector.extract_features([5.0])
        # RMS = 5.0, max_abs = 5.0, crest = 5.0/5.0 = 1.0
        assert features["crest_factor"] == pytest.approx(1.0)

    def test_all_features_present(self, detector):
        """모든 특징이 결과에 포함되는지 확인"""
        features = detector.extract_features([1.0, 2.0, 3.0])
        expected_keys = [
            "mean", "std", "rms", "peak_to_peak", "max_abs", "crest_factor"
        ]
        for key in expected_keys:
            assert key in features, f"특징 '{key}'가 없습니다"

    def test_empty_data_raises_error(self, detector):
        """빈 데이터 -> ValueError"""
        with pytest.raises(ValueError, match="비어있습니다"):
            detector.extract_features([])

    def test_single_value(self, detector):
        """단일 값 특징 추출"""
        features = detector.extract_features([42.0])
        assert features["mean"] == pytest.approx(42.0)
        assert features["std"] == pytest.approx(0.0)
        assert features["rms"] == pytest.approx(42.0)
        assert features["peak_to_peak"] == pytest.approx(0.0)

    def test_negative_values(self, detector):
        """음수 값 특징 추출"""
        features = detector.extract_features([-5.0, -10.0, -15.0])
        assert features["mean"] == pytest.approx(-10.0)
        assert features["max_abs"] == pytest.approx(15.0)


# ============================================================
# 성능 회귀 테스트
# ============================================================

class TestPerformanceRegression:
    """모델 성능 회귀 테스트"""

    def test_normal_data_classified_correctly(self):
        """정상 데이터가 정상으로 분류되는지 확인"""
        model = SimpleAnomalyDetector()
        # 정상 가동 데이터로 학습
        normal_data = [50.0 + i * 0.1 for i in range(100)]
        model.fit(normal_data)

        # 정상 범위의 테스트 데이터
        test_normal = [50.0, 51.0, 49.5, 50.5, 52.0, 48.0]
        labels = model.classify(test_normal, threshold=3.0)
        assert all(label == 0 for label in labels), (
            "정상 데이터가 이상으로 오탐되었습니다"
        )

    def test_anomaly_data_detected(self):
        """이상 데이터가 감지되는지 확인"""
        model = SimpleAnomalyDetector()
        normal_data = [50.0 + i * 0.1 for i in range(100)]
        model.fit(normal_data)

        # 명백한 이상 데이터
        test_anomaly = [200.0, -50.0, 500.0]
        labels = model.classify(test_anomaly, threshold=3.0)
        assert all(label == 1 for label in labels), (
            "이상 데이터가 감지되지 않았습니다"
        )

    def test_end_to_end_pipeline(self, tmp_path):
        """학습 -> 저장 -> 로드 -> 예측 전체 파이프라인"""
        # 1. 학습
        model = SimpleAnomalyDetector()
        training_data = [50.0 + i * 0.5 for i in range(50)]
        model.fit(training_data)

        # 2. 특징 추출
        features = model.extract_features(training_data)
        assert features["mean"] > 0

        # 3. 저장
        model_path = str(tmp_path / "pipeline_model.json")
        model.save_model(model_path)

        # 4. 로드
        loaded = SimpleAnomalyDetector()
        loaded.load_model(model_path)

        # 5. 예측
        test_data = [50.0, 55.0, 100.0, 200.0]
        scores = loaded.predict(test_data)
        labels = loaded.classify(test_data, threshold=3.0)

        # 50.0, 55.0은 정상 범위
        assert labels[0] == 0
        assert labels[1] == 0
        # 200.0은 이상
        assert labels[3] == 1
