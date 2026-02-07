"""
베어링 고장 예측 모델 테스트 모듈

BearingFailurePredictor 클래스의 전체 ML 파이프라인을 테스트합니다:
- 모델 학습 (fit)
- 건강도 예측 (predict_health_score)
- 잔여 수명 예측 (predict_rul)
- 모델 평가 (evaluate)
- 모델 저장/로딩 (save_model / load_model)
- 결정론적 테스트 (fixed seed)
- 성능 임계값 테스트 (regression test)
"""

import pytest
import random
from src_bearing_model import BearingFailurePredictor, HealthMetrics


# ============================================================
# 픽스처
# ============================================================

@pytest.fixture
def model():
    """학습되지 않은 BearingFailurePredictor 인스턴스"""
    return BearingFailurePredictor()


@pytest.fixture
def fitted_model(model, mixed_training_data):
    """학습 완료된 모델"""
    model.fit(mixed_training_data)
    return model


# ============================================================
# 모델 학습(fit) 테스트
# ============================================================

class TestFit:
    """모델 학습 관련 테스트"""

    def test_학습전_상태(self, model):
        """학습 전 is_fitted=False"""
        assert model.is_fitted is False
        assert model.normal_params == {}

    def test_학습후_상태(self, model, mixed_training_data):
        """학습 후 is_fitted=True이고 파라미터가 저장됨"""
        model.fit(mixed_training_data)

        assert model.is_fitted is True
        assert len(model.normal_params) > 0

    def test_학습후_정상_파라미터(self, fitted_model):
        """학습 후 각 특징의 mean/std가 저장됨"""
        for feature in BearingFailurePredictor.FEATURE_NAMES:
            assert feature in fitted_model.normal_params
            params = fitted_model.normal_params[feature]
            assert "mean" in params
            assert "std" in params
            assert params["std"] > 0  # 표준편차는 양수

    def test_정상_데이터만_학습에_사용(self, model, mixed_training_data):
        """label='normal'인 데이터만 패턴 학습에 사용됨"""
        model.fit(mixed_training_data)

        # 정상 데이터의 RMS 평균은 ~0.5 근처여야 함 (고장 데이터의 ~2.5가 아닌)
        rms_mean = model.normal_params["rms"]["mean"]
        assert 0.3 <= rms_mean <= 0.7, f"RMS 평균이 정상 범위에서 벗어남: {rms_mean}"

    def test_정상_데이터_부족_에러(self, model):
        """정상 데이터가 2개 미만이면 에러"""
        training_data = [
            {"rms": 0.5, "kurtosis": 0.2, "crest_factor": 1.4, "label": "normal"},
        ]
        with pytest.raises(ValueError, match="최소 2개"):
            model.fit(training_data)

    def test_정상_데이터_없음_에러(self, model):
        """정상 라벨이 전혀 없으면 에러"""
        training_data = [
            {"rms": 2.5, "kurtosis": 5.0, "crest_factor": 3.5, "label": "fault"},
            {"rms": 3.0, "kurtosis": 6.0, "crest_factor": 4.0, "label": "fault"},
        ]
        with pytest.raises(ValueError, match="최소 2개"):
            model.fit(training_data)


# ============================================================
# 건강도 예측 테스트
# ============================================================

class TestPredictHealthScore:
    """건강도 점수 예측 테스트"""

    def test_정상_데이터_높은_점수(self, fitted_model, normal_features):
        """정상 상태 데이터는 높은 건강도 점수"""
        score = fitted_model.predict_health_score(normal_features)

        assert 70.0 <= score <= 100.0, f"정상 데이터 점수가 낮음: {score}"

    def test_고장_데이터_낮은_점수(self, fitted_model, fault_features):
        """고장 상태 데이터는 낮은 건강도 점수"""
        score = fitted_model.predict_health_score(fault_features)

        assert 0.0 <= score <= 50.0, f"고장 데이터 점수가 높음: {score}"

    def test_점수_범위_0_100(self, fitted_model):
        """건강도 점수는 항상 0~100 범위"""
        # 극단적인 값들로 테스트
        test_cases = [
            {"rms": 0.0, "kurtosis": 0.0, "crest_factor": 0.0},
            {"rms": 100.0, "kurtosis": 100.0, "crest_factor": 100.0},
            {"rms": 0.5, "kurtosis": 0.2, "crest_factor": 1.4},
        ]

        for features in test_cases:
            score = fitted_model.predict_health_score(features)
            assert 0.0 <= score <= 100.0, f"점수 범위 초과: {score}"

    def test_미학습_모델_에러(self, model, normal_features):
        """학습하지 않은 모델로 예측 시 에러"""
        with pytest.raises(RuntimeError, match="학습되지 않았습니다"):
            model.predict_health_score(normal_features)

    def test_정상에_가까울수록_높은_점수(self, fitted_model):
        """정상 패턴에 가까운 데이터일수록 점수가 높아야 함"""
        # 점점 비정상적인 데이터
        slight_abnormal = {"rms": 0.8, "kurtosis": 0.5, "crest_factor": 1.8}
        moderate_abnormal = {"rms": 1.5, "kurtosis": 2.0, "crest_factor": 2.5}
        severe_abnormal = {"rms": 3.0, "kurtosis": 8.0, "crest_factor": 5.0}

        score_slight = fitted_model.predict_health_score(slight_abnormal)
        score_moderate = fitted_model.predict_health_score(moderate_abnormal)
        score_severe = fitted_model.predict_health_score(severe_abnormal)

        # 점수가 단조 감소해야 함
        assert score_slight > score_moderate > score_severe


# ============================================================
# RUL 예측 테스트
# ============================================================

class TestPredictRUL:
    """잔여 수명(Remaining Useful Life) 예측 테스트"""

    def test_하락_추세_양수_RUL(self, fitted_model, declining_health_history):
        """건강도가 하락하면 양수의 RUL을 반환"""
        rul = fitted_model.predict_rul(declining_health_history)

        assert rul > 0, "하락 추세에서 RUL은 양수여야 합니다"

    def test_안정_추세_큰_RUL(self, fitted_model, stable_health_history):
        """건강도가 안정적이면 매우 큰 RUL을 반환"""
        rul = fitted_model.predict_rul(stable_health_history)

        # 안정적이거나 상승 추세면 RUL이 매우 크거나 999
        assert rul >= 100, f"안정 추세에서 RUL이 너무 작음: {rul}"

    def test_임계값_도달시_RUL_0(self, fitted_model):
        """건강도가 이미 임계값 이하이면 RUL=0"""
        health_history = [60.0, 50.0, 40.0, 30.0]
        rul = fitted_model.predict_rul(health_history)

        assert rul == 0.0

    def test_RUL_합리적_범위(self, fitted_model, declining_health_history):
        """RUL이 합리적인 범위 내인지 확인"""
        rul = fitted_model.predict_rul(declining_health_history)

        # 건강도가 60에서 하락 중이므로, 임계값(50)까지 얼마 안 남음
        assert 0 < rul < 100, f"RUL이 비현실적: {rul}"

    def test_이력_부족_에러(self, fitted_model):
        """건강도 이력이 2개 미만이면 에러"""
        with pytest.raises(ValueError, match="최소 2개"):
            fitted_model.predict_rul([90.0])

    def test_급격한_하락_짧은_RUL(self, fitted_model):
        """급격한 하락은 짧은 RUL, 완만한 하락은 긴 RUL"""
        rapid_decline = [90.0, 70.0, 55.0]  # 급격한 하락
        slow_decline = [90.0, 88.0, 85.0]   # 완만한 하락

        rul_rapid = fitted_model.predict_rul(rapid_decline)
        rul_slow = fitted_model.predict_rul(slow_decline)

        assert rul_rapid < rul_slow, \
            f"급격한 하락({rul_rapid})이 완만한 하락({rul_slow})보다 RUL이 커서는 안됨"


# ============================================================
# 모델 평가 테스트
# ============================================================

class TestEvaluate:
    """모델 평가(evaluate) 테스트"""

    def test_평가_반환_타입(self, fitted_model, test_data_with_labels):
        """evaluate()가 HealthMetrics를 반환하는지 확인"""
        test_data, true_labels = test_data_with_labels
        metrics = fitted_model.evaluate(test_data, true_labels)

        assert isinstance(metrics, HealthMetrics)

    def test_지표_범위_0_1(self, fitted_model, test_data_with_labels):
        """모든 지표가 0~1 범위인지 확인"""
        test_data, true_labels = test_data_with_labels
        metrics = fitted_model.evaluate(test_data, true_labels)

        assert 0.0 <= metrics.accuracy <= 1.0
        assert 0.0 <= metrics.precision <= 1.0
        assert 0.0 <= metrics.recall <= 1.0
        assert 0.0 <= metrics.f1 <= 1.0

    def test_정확도_임계값(self, fitted_model, test_data_with_labels):
        """정확도가 최소 기준(70%)을 만족하는지 확인"""
        test_data, true_labels = test_data_with_labels
        metrics = fitted_model.evaluate(test_data, true_labels)

        assert metrics.accuracy >= 0.7, \
            f"정확도({metrics.accuracy:.2f})가 최소 기준(0.7)에 미달"

    def test_재현율_중요도(self, fitted_model, test_data_with_labels):
        """재현율(recall)이 적정 수준인지 확인 (고장 미탐지 방지)"""
        test_data, true_labels = test_data_with_labels
        metrics = fitted_model.evaluate(test_data, true_labels)

        # 예지보전에서 recall은 특히 중요 (고장을 놓치면 안 됨)
        assert metrics.recall >= 0.6, \
            f"재현율({metrics.recall:.2f})이 너무 낮음 - 고장 미탐지 위험"

    def test_미학습_모델_에러(self, model, test_data_with_labels):
        """학습하지 않은 모델로 평가 시 에러"""
        test_data, true_labels = test_data_with_labels
        with pytest.raises(RuntimeError, match="학습되지 않았습니다"):
            model.evaluate(test_data, true_labels)

    def test_데이터_라벨_수_불일치_에러(self, fitted_model):
        """데이터와 라벨 수가 다르면 에러"""
        test_data = [{"rms": 0.5, "kurtosis": 0.2, "crest_factor": 1.4}]
        true_labels = ["normal", "fault"]  # 2개 (데이터는 1개)

        with pytest.raises(ValueError, match="수가 다릅니다"):
            fitted_model.evaluate(test_data, true_labels)


# ============================================================
# 모델 저장/로딩 테스트
# ============================================================

class TestSaveLoad:
    """모델 저장/로딩 테스트"""

    def test_저장_로딩_일관성(self, fitted_model, normal_features, tmp_path):
        """저장 후 로딩하면 동일한 예측 결과"""
        # 저장 전 예측
        score_before = fitted_model.predict_health_score(normal_features)

        # 저장 → 로딩
        filepath = str(tmp_path / "model.json")
        fitted_model.save_model(filepath)

        loaded_model = BearingFailurePredictor()
        loaded_model.load_model(filepath)

        # 로딩 후 예측
        score_after = loaded_model.predict_health_score(normal_features)

        assert score_before == pytest.approx(score_after)

    def test_로딩후_is_fitted(self, fitted_model, tmp_path):
        """로딩 후 is_fitted=True"""
        filepath = str(tmp_path / "model.json")
        fitted_model.save_model(filepath)

        loaded_model = BearingFailurePredictor()
        loaded_model.load_model(filepath)

        assert loaded_model.is_fitted is True

    def test_로딩후_파라미터_동일(self, fitted_model, tmp_path):
        """로딩 후 normal_params가 동일"""
        filepath = str(tmp_path / "model.json")
        fitted_model.save_model(filepath)

        loaded_model = BearingFailurePredictor()
        loaded_model.load_model(filepath)

        for feature in BearingFailurePredictor.FEATURE_NAMES:
            orig = fitted_model.normal_params[feature]
            loaded = loaded_model.normal_params[feature]
            assert orig["mean"] == pytest.approx(loaded["mean"])
            assert orig["std"] == pytest.approx(loaded["std"])

    def test_미학습_모델_저장_에러(self, model, tmp_path):
        """학습하지 않은 모델 저장 시 에러"""
        filepath = str(tmp_path / "model.json")
        with pytest.raises(RuntimeError, match="학습되지 않은"):
            model.save_model(filepath)

    def test_존재하지_않는_파일_로딩_에러(self, model):
        """존재하지 않는 파일 로딩 시 에러"""
        with pytest.raises(FileNotFoundError):
            model.load_model("/nonexistent/model.json")

    def test_잘못된_JSON_로딩_에러(self, model, tmp_path):
        """잘못된 JSON 파일 로딩 시 에러"""
        filepath = tmp_path / "bad_model.json"
        filepath.write_text("이것은 JSON이 아닙니다")

        with pytest.raises(ValueError, match="JSON"):
            model.load_model(str(filepath))

    def test_필수키_누락_JSON_에러(self, model, tmp_path):
        """필수 키가 누락된 JSON 파일 로딩 시 에러"""
        filepath = tmp_path / "incomplete.json"
        filepath.write_text('{"some_key": "value"}')

        with pytest.raises(ValueError, match="누락"):
            model.load_model(str(filepath))


# ============================================================
# 결정론적(deterministic) 테스트
# ============================================================

class TestDeterminism:
    """고정 시드를 사용한 결정론적 테스트"""

    def test_동일_시드_동일_결과(self):
        """같은 시드와 같은 데이터면 같은 결과"""
        def create_and_predict(seed):
            random.seed(seed)
            data = []
            for _ in range(20):
                data.append({
                    "rms": 0.5 + random.gauss(0, 0.05),
                    "kurtosis": 0.2 + random.gauss(0, 0.03),
                    "crest_factor": 1.4 + random.gauss(0, 0.05),
                    "label": "normal",
                })

            model = BearingFailurePredictor()
            model.fit(data)
            return model.predict_health_score(
                {"rms": 0.5, "kurtosis": 0.2, "crest_factor": 1.4}
            )

        result1 = create_and_predict(seed=42)
        result2 = create_and_predict(seed=42)

        assert result1 == pytest.approx(result2)

    def test_다른_시드_다른_결과(self):
        """다른 시드를 사용하면 (일반적으로) 다른 결과"""
        def create_and_predict(seed):
            random.seed(seed)
            data = []
            for _ in range(20):
                data.append({
                    "rms": 0.5 + random.gauss(0, 0.1),
                    "kurtosis": 0.2 + random.gauss(0, 0.05),
                    "crest_factor": 1.4 + random.gauss(0, 0.1),
                    "label": "normal",
                })

            model = BearingFailurePredictor()
            model.fit(data)
            return model.normal_params["rms"]["mean"]

        mean1 = create_and_predict(seed=42)
        mean2 = create_and_predict(seed=99)

        # 정확히 같을 확률은 극히 낮음
        assert mean1 != mean2


# ============================================================
# 성능 회귀 테스트 (Regression Test)
# ============================================================

class TestPerformanceRegression:
    """모델 성능이 기준선 이하로 떨어지지 않는지 확인"""

    # 기준선 성능 (이 값 이하로 떨어지면 회귀 발생)
    BASELINE_ACCURACY = 0.65
    BASELINE_F1 = 0.60

    def test_정확도_기준선_유지(self, fitted_model, test_data_with_labels):
        """정확도가 기준선 이상인지 확인"""
        test_data, true_labels = test_data_with_labels
        metrics = fitted_model.evaluate(test_data, true_labels)

        assert metrics.accuracy >= self.BASELINE_ACCURACY, \
            f"정확도 회귀 감지: {metrics.accuracy:.3f} < {self.BASELINE_ACCURACY}"

    def test_F1_기준선_유지(self, fitted_model, test_data_with_labels):
        """F1 점수가 기준선 이상인지 확인"""
        test_data, true_labels = test_data_with_labels
        metrics = fitted_model.evaluate(test_data, true_labels)

        assert metrics.f1 >= self.BASELINE_F1, \
            f"F1 회귀 감지: {metrics.f1:.3f} < {self.BASELINE_F1}"


# ============================================================
# HealthMetrics 데이터클래스 테스트
# ============================================================

class TestHealthMetrics:
    """HealthMetrics 데이터클래스 테스트"""

    def test_생성(self):
        """HealthMetrics 인스턴스 생성"""
        metrics = HealthMetrics(
            accuracy=0.9,
            precision=0.85,
            recall=0.92,
            f1=0.88,
        )
        assert metrics.accuracy == 0.9
        assert metrics.precision == 0.85
        assert metrics.recall == 0.92
        assert metrics.f1 == 0.88
