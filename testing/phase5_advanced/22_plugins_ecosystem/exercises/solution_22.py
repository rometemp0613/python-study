"""
연습문제 22 정답: pytest 플러그인 생태계

각 연습의 완성된 풀이.
"""

import time
import math
import pytest
import sys
import os

# 소스 모듈 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_performance_critical import (
    calculate_rms,
    detect_peaks,
    moving_average,
    batch_process_sensors,
    calculate_crest_factor,
)


# =============================================================================
# 연습 1 정답: 타임아웃이 있는 성능 테스트
# =============================================================================

class TestTimeoutSolution:
    """타임아웃을 활용한 성능 보장 테스트"""

    def test_large_dataset_rms_within_timeout(self):
        """100,000개 데이터 포인트의 RMS 계산이 1초 이내에 완료되는지 검증"""
        # 큰 데이터셋 생성
        values = list(range(100000))

        # 시간 측정 시작
        start = time.perf_counter()
        result = calculate_rms(values)
        elapsed = time.perf_counter() - start

        # 결과 검증
        assert result > 0, "RMS 결과가 양수여야 한다"

        # 성능 요구사항: 1초 이내
        assert elapsed < 1.0, (
            f"RMS 계산이 너무 느립니다: {elapsed:.3f}초 (제한: 1.0초)"
        )

    def test_batch_processing_scales_linearly(self):
        """센서 수가 2배가 되면 처리 시간도 대략 2배가 되는지 검증"""

        def create_sensor_data(count):
            """센서 데이터를 생성하는 헬퍼 함수"""
            return [
                {
                    "sensor_id": f"sensor_{i}",
                    "values": [float(j) for j in range(100)],
                    "threshold": 80.0,
                }
                for i in range(count)
            ]

        # 10개 센서 처리 시간 측정
        data_small = create_sensor_data(10)
        start = time.perf_counter()
        for _ in range(50):  # 반복으로 측정 정밀도 향상
            batch_process_sensors(data_small)
        time_small = time.perf_counter() - start

        # 20개 센서 처리 시간 측정
        data_large = create_sensor_data(20)
        start = time.perf_counter()
        for _ in range(50):
            batch_process_sensors(data_large)
        time_large = time.perf_counter() - start

        # 선형 확장성 검증: 비율이 1.0~3.0 범위 (여유 있게)
        # 완벽한 선형이면 2.0이지만, 오버헤드 때문에 범위를 넓게 설정
        if time_small > 0:
            ratio = time_large / time_small
            assert 1.0 <= ratio <= 3.0, (
                f"선형 확장성 위반: 비율={ratio:.2f} "
                f"(10개: {time_small:.4f}초, 20개: {time_large:.4f}초)"
            )


# =============================================================================
# 연습 2 정답: 벤치마크 스타일 테스트
# =============================================================================

class TestBenchmarkSolution:
    """수동 벤치마크 테스트"""

    def test_moving_average_vs_simple_mean(self):
        """이동 평균(전체 윈도우)과 단순 평균 비교"""
        values = [float(i) for i in range(1000)]

        # 결과 비교: 윈도우=전체길이면 결과는 하나, 전체 평균과 동일
        ma_result = moving_average(values, window=len(values))
        simple_mean = sum(values) / len(values)
        assert ma_result[0] == pytest.approx(simple_mean)

        # 이동 평균 실행 시간
        start = time.perf_counter()
        for _ in range(100):
            moving_average(values, window=len(values))
        ma_time = time.perf_counter() - start

        # 단순 평균 실행 시간
        start = time.perf_counter()
        for _ in range(100):
            sum(values) / len(values)
        simple_time = time.perf_counter() - start

        # 단순 평균이 이동 평균보다 빠를 것으로 예상 (출력으로 확인)
        print(f"\n이동 평균 (100회): {ma_time:.4f}초")
        print(f"단순 평균 (100회): {simple_time:.4f}초")
        print(f"이동 평균이 {ma_time / max(simple_time, 1e-9):.1f}배 느림")

    def test_detect_peaks_performance_profile(self):
        """데이터 크기별 피크 감지 성능 프로파일링"""
        sizes = [100, 1000, 10000]
        times = {}

        for size in sizes:
            # 데이터 생성: 10%가 피크인 패턴
            values = [float(i % 100) for i in range(size)]

            # 100회 실행 시간 측정
            start = time.perf_counter()
            for _ in range(100):
                detect_peaks(values, threshold=90.0)
            elapsed = time.perf_counter() - start

            times[size] = elapsed
            print(f"\n크기 {size:>6}: {elapsed:.4f}초 (100회)")

        # 크기가 10배 증가할 때 시간 비율 확인
        # O(n) 알고리즘이므로 대략 10배 증가해야 한다
        if times[100] > 0:
            ratio_1 = times[1000] / times[100]
            ratio_2 = times[10000] / times[1000]
            print(f"\n100→1000 비율: {ratio_1:.1f}x")
            print(f"1000→10000 비율: {ratio_2:.1f}x")

            # 범위를 넓게 설정 (시스템 부하에 따라 변동)
            assert ratio_1 < 50, f"100→1000 확장 비율이 비정상: {ratio_1:.1f}x"
            assert ratio_2 < 50, f"1000→10000 확장 비율이 비정상: {ratio_2:.1f}x"


# =============================================================================
# 연습 3 정답: 플러그인 설정
# =============================================================================

class TestPluginConfigSolution:
    """플러그인 설정에 대한 이해도 테스트"""

    def test_understand_pyproject_config(self):
        """pyproject.toml 플러그인 설정 이해도 검증"""

        # pyproject.toml 설정을 파싱한 결과
        config = {
            # pytest-cov: 테스트 커버리지 측정 대상 디렉토리
            "cov_target": "src",
            # pytest-cov: 최소 커버리지 퍼센트 (미달 시 테스트 실패)
            "cov_fail_under": 80,
            # pytest-timeout: 각 테스트의 최대 실행 시간 (초)
            "timeout": 30,
            # pytest-xdist: 병렬 실행 워커 수 ("auto"는 CPU 코어 수)
            "parallel": "auto",
        }

        # 각 설정이 올바른지 검증
        # 커버리지 대상은 문자열
        assert isinstance(config["cov_target"], str)
        assert config["cov_target"] == "src"

        # 커버리지 임계값은 0~100 사이
        assert 0 <= config["cov_fail_under"] <= 100
        assert config["cov_fail_under"] == 80

        # 타임아웃은 양수
        assert config["timeout"] > 0
        assert config["timeout"] == 30

        # 병렬 설정은 "auto" 또는 숫자
        assert config["parallel"] in ("auto",) or isinstance(config["parallel"], int)
