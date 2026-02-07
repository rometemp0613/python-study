"""
Parametrize 데모 테스트

@pytest.mark.parametrize를 활용한 다양한 매개변수화 테스트 패턴을 시연한다:
1. 단일 매개변수
2. 다중 매개변수
3. 테스트 ID 지정
4. 중첩 데코레이터 (데카르트 곱)
5. pytest.param과 마커
6. indirect parametrize
"""

import pytest
from src_anomaly_detector import AnomalyDetector, Severity, DetectionResult


# ============================================================
# 전역 인스턴스 (테스트 편의용)
# ============================================================

detector = AnomalyDetector()


# ============================================================
# 1. 단일 매개변수 parametrize
# ============================================================

class TestSingleParam:
    """단일 매개변수로 여러 값을 테스트"""

    @pytest.mark.parametrize("value", [10.0, 25.0, 49.9, 50.0])
    def test_single_param_normal_range(self, value):
        """정상 범위 내의 값들이 이상으로 탐지되지 않는지 확인"""
        result = detector.detect(value, threshold=50.0)
        assert not result.is_anomaly

    @pytest.mark.parametrize("value", [50.1, 75.0, 100.0, 200.0])
    def test_single_param_anomaly_range(self, value):
        """임계값을 초과하는 값들이 이상으로 탐지되는지 확인"""
        result = detector.detect(value, threshold=50.0)
        assert result.is_anomaly

    @pytest.mark.parametrize("threshold", [0, -1, -100.0])
    def test_single_param_invalid_threshold(self, threshold):
        """0 이하의 임계값에서 ValueError가 발생하는지 확인"""
        with pytest.raises(ValueError, match="0보다 커야"):
            detector.detect(25.0, threshold=threshold)


# ============================================================
# 2. 다중 매개변수 parametrize
# ============================================================

class TestMultipleParams:
    """여러 매개변수를 조합한 테스트"""

    @pytest.mark.parametrize("value, threshold, expected_anomaly", [
        (25.0, 50.0, False),    # 정상: 임계값 미만
        (50.0, 50.0, False),    # 정상: 임계값과 동일
        (50.1, 50.0, True),     # 이상: 임계값 초과
        (100.0, 50.0, True),    # 이상: 임계값의 2배
        (-25.0, 50.0, False),   # 정상: 음수값이지만 절댓값이 임계값 미만
        (-51.0, 50.0, True),    # 이상: 음수값의 절댓값이 임계값 초과
    ])
    def test_detect_various_cases(self, value, threshold, expected_anomaly):
        """다양한 값과 임계값 조합으로 이상 탐지 검증"""
        result = detector.detect(value, threshold)
        assert result.is_anomaly == expected_anomaly

    @pytest.mark.parametrize("value, threshold, expected_severity", [
        (25.0, 50.0, Severity.NORMAL),     # 정상 범위
        (60.0, 50.0, Severity.MEDIUM),     # 1.0 < ratio <= 1.5
        (80.0, 50.0, Severity.HIGH),       # 1.5 < ratio <= 2.0
        (110.0, 50.0, Severity.CRITICAL),  # ratio > 2.0
    ])
    def test_detect_severity_levels(self, value, threshold, expected_severity):
        """값과 임계값의 비율에 따른 심각도 레벨 확인"""
        result = detector.detect(value, threshold)
        assert result.severity == expected_severity


# ============================================================
# 3. 테스트 ID 지정
# ============================================================

class TestWithIDs:
    """테스트 ID를 지정하여 결과를 읽기 쉽게 만듦"""

    @pytest.mark.parametrize("value, expected_severity", [
        (25.0, Severity.NORMAL),
        (55.0, Severity.LOW),
        (75.0, Severity.MEDIUM),
        (90.0, Severity.HIGH),
        (100.0, Severity.CRITICAL),
    ], ids=[
        "정상범위_25도",
        "저위험_55도",
        "중위험_75도",
        "고위험_90도",
        "위험_100도",
    ])
    def test_classify_with_ids(self, value, expected_severity):
        """한국어 테스트 ID로 결과를 확인"""
        thresholds = {"low": 50.0, "medium": 70.0, "high": 85.0, "critical": 95.0}
        result = detector.classify_severity(value, thresholds)
        assert result == expected_severity


# ============================================================
# 4. 중첩 데코레이터 (데카르트 곱)
# ============================================================

class TestCartesianProduct:
    """두 데코레이터의 데카르트 곱으로 모든 조합 테스트"""

    @pytest.mark.parametrize("value", [10.0, 50.0, 90.0])
    @pytest.mark.parametrize("threshold", [30.0, 60.0])
    def test_cartesian_detect(self, value, threshold):
        """3 x 2 = 6가지 조합으로 테스트 실행"""
        result = detector.detect(value, threshold)
        # 기본 속성 확인
        assert result.value == value
        assert result.threshold == threshold
        assert isinstance(result.is_anomaly, bool)

    @pytest.mark.parametrize("window_size", [2, 3, 5])
    @pytest.mark.parametrize("data", [
        [10.0, 20.0, 30.0, 40.0, 50.0],
        [50.0, 50.0, 50.0, 50.0, 50.0],
    ], ids=["상승추세", "안정추세"])
    def test_cartesian_pattern(self, data, window_size):
        """데이터 패턴 x 윈도우 크기 = 6가지 조합 테스트"""
        result = detector.detect_pattern(data, window_size)
        assert "trend" in result
        assert "moving_averages" in result
        assert len(result["moving_averages"]) == len(data) - window_size + 1


# ============================================================
# 5. pytest.param과 마커
# ============================================================

class TestPytestParam:
    """pytest.param을 사용한 개별 케이스 설정"""

    @pytest.mark.parametrize("value, threshold, expected", [
        pytest.param(25.0, 50.0, False, id="정상_범위내"),
        pytest.param(75.0, 50.0, True, id="이상_1.5배초과"),
        pytest.param(0.0, 50.0, False, id="정상_제로값"),
        pytest.param(
            50.0, 50.0, False,
            id="경계값_임계값동일",
        ),
    ])
    def test_param_with_ids(self, value, threshold, expected):
        """pytest.param으로 ID가 지정된 테스트"""
        result = detector.detect(value, threshold)
        assert result.is_anomaly == expected

    @pytest.mark.parametrize("values, window, expected_trend", [
        pytest.param(
            [10, 20, 30, 40, 50], 3, "increasing",
            id="명확한_상승추세"
        ),
        pytest.param(
            [50, 40, 30, 20, 10], 3, "decreasing",
            id="명확한_하강추세"
        ),
        pytest.param(
            [30, 30, 30, 30, 30], 3, "stable",
            id="안정추세"
        ),
        pytest.param(
            [30, 31, 30, 31, 30], 3, "stable",
            id="미세변동_안정으로_분류"
        ),
    ])
    def test_pattern_trend_classification(self, values, window, expected_trend):
        """패턴 추세 분류 테스트 (각 케이스에 ID 부여)"""
        result = detector.detect_pattern(values, window)
        assert result["trend"] == expected_trend


# ============================================================
# 6. Indirect Parametrize
# ============================================================

@pytest.fixture
def configured_detector(request):
    """
    indirect parametrize용 fixture.
    request.param으로 전달된 임계값 딕셔너리를 사용한다.
    """
    det = AnomalyDetector()
    # request.param은 parametrize에서 전달된 값
    return det, request.param


@pytest.mark.parametrize("configured_detector", [
    {"low": 30, "medium": 50, "high": 70, "critical": 90},
    {"low": 50, "medium": 70, "high": 85, "critical": 95},
], indirect=True, ids=["느슨한_임계값", "엄격한_임계값"])
def test_indirect_parametrize(configured_detector):
    """indirect parametrize: fixture를 통해 매개변수 전달"""
    det, thresholds = configured_detector
    # 25.0은 두 설정 모두에서 NORMAL
    result = det.classify_severity(25.0, thresholds)
    assert result == Severity.NORMAL


# ============================================================
# 7. 에러 케이스 parametrize
# ============================================================

class TestErrorCases:
    """에러 케이스를 parametrize로 효율적으로 테스트"""

    @pytest.mark.parametrize("thresholds, missing_key", [
        ({"medium": 70, "high": 85, "critical": 95}, "low"),
        ({"low": 50, "high": 85, "critical": 95}, "medium"),
        ({"low": 50, "medium": 70, "critical": 95}, "high"),
        ({"low": 50, "medium": 70, "high": 85}, "critical"),
    ], ids=["low누락", "medium누락", "high누락", "critical누락"])
    def test_missing_threshold_keys(self, thresholds, missing_key):
        """필수 임계값 키가 누락되면 ValueError 발생"""
        with pytest.raises(ValueError, match="필수 임계값"):
            detector.classify_severity(50.0, thresholds)

    @pytest.mark.parametrize("values, window_size, error_msg", [
        ([1.0, 2.0], 3, "데이터 길이"),
        ([1.0], 2, "데이터 길이"),
        ([1.0, 2.0, 3.0], 0, "윈도우 크기"),
        ([1.0, 2.0, 3.0], -1, "윈도우 크기"),
    ], ids=["짧은데이터", "최소데이터", "윈도우_0", "윈도우_음수"])
    def test_detect_pattern_errors(self, values, window_size, error_msg):
        """detect_pattern의 다양한 에러 케이스"""
        with pytest.raises(ValueError, match=error_msg):
            detector.detect_pattern(values, window_size)
