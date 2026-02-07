"""
pytest 플러그인 생태계 데모 테스트.

이 테스트 파일은 플러그인 없이도 실행 가능하지만,
각 플러그인이 설치되면 추가 기능을 제공하는 방식으로 작성되었다.

실행 방법:
    pytest test_plugins_demo.py -v
"""

import time
import math
import pytest

from src_performance_critical import (
    calculate_rms,
    detect_peaks,
    moving_average,
    batch_process_sensors,
    calculate_crest_factor,
)


# =============================================================================
# 기본 기능 테스트 (플러그인 없이도 동작)
# =============================================================================

class TestCalculateRMS:
    """RMS 계산 기능 테스트"""

    def test_rms_single_value(self):
        """단일 값의 RMS는 절대값과 같다"""
        assert calculate_rms([5.0]) == 5.0
        assert calculate_rms([-5.0]) == 5.0

    def test_rms_identical_values(self):
        """동일한 값들의 RMS는 그 값의 절대값과 같다"""
        result = calculate_rms([3.0, 3.0, 3.0])
        assert result == pytest.approx(3.0)

    def test_rms_known_values(self):
        """알려진 값으로 RMS 계산 검증"""
        # RMS([1, 2, 3, 4]) = sqrt((1+4+9+16)/4) = sqrt(7.5)
        result = calculate_rms([1.0, 2.0, 3.0, 4.0])
        expected = math.sqrt(7.5)
        assert result == pytest.approx(expected)

    def test_rms_empty_raises(self):
        """빈 리스트는 ValueError를 발생시킨다"""
        with pytest.raises(ValueError, match="빈 데이터"):
            calculate_rms([])

    def test_rms_with_negative_values(self):
        """음수 값도 올바르게 처리한다 (제곱하므로 부호 무관)"""
        result_positive = calculate_rms([3.0, 4.0])
        result_mixed = calculate_rms([-3.0, 4.0])
        assert result_positive == pytest.approx(result_mixed)


class TestDetectPeaks:
    """피크 감지 기능 테스트"""

    def test_no_peaks(self):
        """임계값 이하의 데이터에서는 피크가 없다"""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = detect_peaks(values, threshold=10.0)
        assert result == []

    def test_all_peaks(self):
        """모든 값이 임계값 초과인 경우"""
        values = [15.0, 20.0, 25.0]
        result = detect_peaks(values, threshold=10.0)
        assert len(result) == 3

    def test_peak_severity_info(self):
        """임계값 대비 20% 이하 초과 → info 등급"""
        # threshold=10, value=11 → severity = 0.1 (10%) → info
        result = detect_peaks([11.0], threshold=10.0)
        assert result[0]["severity"] == "info"

    def test_peak_severity_warning(self):
        """임계값 대비 20~50% 초과 → warning 등급"""
        # threshold=10, value=13 → severity = 0.3 (30%) → warning
        result = detect_peaks([13.0], threshold=10.0)
        assert result[0]["severity"] == "warning"

    def test_peak_severity_critical(self):
        """임계값 대비 50% 초과 → critical 등급"""
        # threshold=10, value=16 → severity = 0.6 (60%) → critical
        result = detect_peaks([16.0], threshold=10.0)
        assert result[0]["severity"] == "critical"

    def test_peak_index_tracking(self):
        """피크의 인덱스가 올바르게 기록된다"""
        values = [1.0, 2.0, 15.0, 3.0, 20.0]
        result = detect_peaks(values, threshold=10.0)
        indices = [p["index"] for p in result]
        assert indices == [2, 4]

    def test_empty_input(self):
        """빈 리스트는 빈 결과를 반환한다"""
        assert detect_peaks([], threshold=10.0) == []


class TestMovingAverage:
    """이동 평균 테스트"""

    def test_window_equals_length(self):
        """윈도우가 데이터 길이와 같으면 전체 평균 하나만 반환"""
        result = moving_average([1.0, 2.0, 3.0], window=3)
        assert result == [pytest.approx(2.0)]

    def test_window_one(self):
        """윈도우 1이면 원본 값과 동일"""
        values = [1.0, 2.0, 3.0]
        result = moving_average(values, window=1)
        assert result == [pytest.approx(v) for v in values]

    def test_known_moving_average(self):
        """알려진 이동 평균 계산 검증"""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = moving_average(values, window=3)
        # [avg(1,2,3), avg(2,3,4), avg(3,4,5)]
        expected = [2.0, 3.0, 4.0]
        assert result == [pytest.approx(e) for e in expected]

    def test_invalid_window_zero(self):
        """윈도우 0은 ValueError"""
        with pytest.raises(ValueError, match="1 이상"):
            moving_average([1.0, 2.0], window=0)

    def test_window_too_large(self):
        """윈도우가 데이터보다 크면 ValueError"""
        with pytest.raises(ValueError, match="데이터 길이보다"):
            moving_average([1.0, 2.0], window=5)


class TestBatchProcessSensors:
    """센서 일괄 처리 테스트"""

    def test_single_sensor_normal(self):
        """정상 범위의 단일 센서 처리"""
        data = [{
            "sensor_id": "VIB_001",
            "values": [10.0, 12.0, 11.0, 9.0, 10.5],
            "threshold": 100.0,
        }]
        result = batch_process_sensors(data)
        assert len(result) == 1
        assert result[0]["sensor_id"] == "VIB_001"
        assert result[0]["status"] == "normal"
        assert result[0]["peak_count"] == 0

    def test_sensor_with_warnings(self):
        """경고 수준 피크가 있는 센서"""
        data = [{
            "sensor_id": "TEMP_001",
            "values": [50, 60, 110, 55, 120, 130],
            "threshold": 100.0,
        }]
        result = batch_process_sensors(data)
        assert result[0]["peak_count"] == 3
        assert result[0]["status"] == "warning"

    def test_sensor_critical(self):
        """위험 수준 피크가 많은 센서"""
        data = [{
            "sensor_id": "VIB_002",
            "values": [150, 160, 170, 180, 190, 200],
            "threshold": 100.0,
        }]
        result = batch_process_sensors(data)
        assert result[0]["status"] == "critical"
        assert result[0]["peak_count"] == 6

    def test_empty_sensor_data(self):
        """빈 데이터를 가진 센서"""
        data = [{
            "sensor_id": "VIB_003",
            "values": [],
            "threshold": 100.0,
        }]
        result = batch_process_sensors(data)
        assert result[0]["status"] == "no_data"
        assert result[0]["rms"] == 0.0

    def test_multiple_sensors(self):
        """여러 센서 동시 처리"""
        data = [
            {"sensor_id": "S1", "values": [10, 20, 30], "threshold": 100},
            {"sensor_id": "S2", "values": [150, 200, 250], "threshold": 100},
            {"sensor_id": "S3", "values": [], "threshold": 100},
        ]
        result = batch_process_sensors(data)
        assert len(result) == 3
        assert result[0]["status"] == "normal"
        assert result[1]["status"] == "warning"
        assert result[2]["status"] == "no_data"


# =============================================================================
# 플러그인 활용 테스트 (플러그인 설치 시 추가 기능)
# =============================================================================


class TestWithTimeout:
    """
    pytest-timeout 활용 테스트.

    pytest-timeout이 설치되면 @pytest.mark.timeout 데코레이터가
    지정된 시간 내에 테스트가 완료되지 않으면 실패 처리한다.
    설치되지 않아도 테스트 자체는 정상 동작한다.
    """

    # pytest-timeout 설치 시: 이 테스트는 2초 이내에 완료되어야 한다
    @pytest.mark.timeout(2)
    def test_rms_completes_quickly(self):
        """RMS 계산이 빠르게 완료되는지 확인"""
        values = list(range(10000))
        result = calculate_rms(values)
        assert result > 0

    @pytest.mark.timeout(2)
    def test_peak_detection_performance(self):
        """피크 감지가 빠르게 완료되는지 확인"""
        values = [float(i % 100) for i in range(10000)]
        result = detect_peaks(values, threshold=90.0)
        assert isinstance(result, list)

    @pytest.mark.timeout(2)
    def test_batch_processing_performance(self):
        """일괄 처리가 합리적인 시간 내에 완료되는지 확인"""
        sensor_data = [
            {
                "sensor_id": f"sensor_{i}",
                "values": [float(j) for j in range(100)],
                "threshold": 80.0,
            }
            for i in range(50)
        ]
        result = batch_process_sensors(sensor_data)
        assert len(result) == 50


class TestBenchmarkReady:
    """
    pytest-benchmark 활용 준비 테스트.

    pytest-benchmark가 설치되면 benchmark 픽스처를 사용하여
    정밀한 성능 측정이 가능하다. 여기서는 수동 시간 측정으로 대체한다.

    pytest-benchmark 사용 시:
        def test_rms_benchmark(self, benchmark):
            values = list(range(10000))
            result = benchmark(calculate_rms, values)
            assert result > 0
    """

    def test_rms_execution_time(self):
        """RMS 계산 시간이 합리적인지 확인 (수동 벤치마크)"""
        values = list(range(10000))

        start = time.perf_counter()
        for _ in range(100):
            calculate_rms(values)
        elapsed = time.perf_counter() - start

        # 100회 실행이 1초 이내여야 한다
        assert elapsed < 1.0, f"RMS 계산이 너무 느림: {elapsed:.3f}초 / 100회"

    def test_moving_average_execution_time(self):
        """이동 평균 계산 시간이 합리적인지 확인"""
        values = list(range(1000))

        start = time.perf_counter()
        for _ in range(100):
            moving_average(values, window=10)
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"이동 평균 계산이 너무 느림: {elapsed:.3f}초 / 100회"


class TestCrestFactor:
    """크레스트 팩터 테스트"""

    def test_constant_signal(self):
        """일정한 신호의 크레스트 팩터는 1.0"""
        result = calculate_crest_factor([5.0, 5.0, 5.0, 5.0])
        assert result == pytest.approx(1.0)

    def test_impulse_signal(self):
        """충격 신호는 크레스트 팩터가 높다"""
        # 하나만 큰 값 → 크레스트 팩터가 높음
        values = [0.0, 0.0, 10.0, 0.0, 0.0]
        result = calculate_crest_factor(values)
        # RMS = sqrt(100/5) = sqrt(20) ≈ 4.47
        # crest = 10 / 4.47 ≈ 2.24
        assert result > 2.0

    def test_empty_raises(self):
        """빈 리스트는 ValueError"""
        with pytest.raises(ValueError):
            calculate_crest_factor([])


# =============================================================================
# pytest-randomly 관련 참고
# =============================================================================
# pytest-randomly가 설치되면 위의 모든 테스트가 랜덤 순서로 실행된다.
# 각 테스트가 독립적이므로 순서에 무관하게 통과해야 한다.
#
# 실행 예시:
#   pytest test_plugins_demo.py -v -p randomly
#   Using --randomly-seed=1234567
#
# 특정 시드로 재현:
#   pytest test_plugins_demo.py -v --randomly-seed=1234567

# =============================================================================
# pytest-cov 관련 참고
# =============================================================================
# pytest-cov가 설치되면 커버리지를 측정할 수 있다:
#   pytest test_plugins_demo.py --cov=src_performance_critical --cov-report=term-missing
#
# 출력 예시:
# Name                          Stmts   Miss  Cover   Missing
# -----------------------------------------------------------
# src_performance_critical.py      58      2    97%   45, 67
