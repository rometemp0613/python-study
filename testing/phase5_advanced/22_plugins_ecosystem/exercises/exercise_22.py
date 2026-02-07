"""
연습문제 22: pytest 플러그인 생태계

이 연습에서는 플러그인을 활용한 테스트를 작성한다.
TODO 부분을 채워서 테스트를 완성하라.
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
# 연습 1: 타임아웃이 있는 성능 테스트
# =============================================================================

class TestTimeoutExercise:
    """
    타임아웃을 활용한 성능 보장 테스트를 작성하라.

    pytest-timeout이 없어도 수동으로 시간을 측정하여
    성능 요구사항을 검증할 수 있다.
    """

    def test_large_dataset_rms_within_timeout(self):
        """
        TODO: 100,000개 데이터 포인트의 RMS 계산이
        1초 이내에 완료되는지 검증하라.

        힌트:
        - time.perf_counter()로 시작/종료 시간 측정
        - 큰 데이터셋 생성: list(range(100000))
        - assert로 소요 시간 검증
        """
        pytest.skip("TODO: 타임아웃 성능 테스트를 구현하세요")

    def test_batch_processing_scales_linearly(self):
        """
        TODO: 센서 수가 2배가 되면 처리 시간도 대략 2배가 되는지
        (선형 확장성) 검증하라.

        힌트:
        - 센서 10개 처리 시간 측정
        - 센서 20개 처리 시간 측정
        - 비율이 1.5~2.5 범위인지 확인
        """
        pytest.skip("TODO: 선형 확장성 테스트를 구현하세요")


# =============================================================================
# 연습 2: 벤치마크 스타일 테스트
# =============================================================================

class TestBenchmarkExercise:
    """
    수동 벤치마크 테스트를 작성하라.

    pytest-benchmark가 없어도 반복 실행으로
    안정적인 성능 측정이 가능하다.
    """

    def test_moving_average_vs_simple_mean(self):
        """
        TODO: moving_average(window=전체길이)와
        단순 평균(sum/len)의 결과가 같고,
        각각의 실행 시간을 비교하라.

        힌트:
        - values = [float(i) for i in range(1000)]
        - moving_average(values, window=len(values))의 결과 검증
        - 각각 1000회 실행 시간 측정 후 비교
        """
        pytest.skip("TODO: 벤치마크 비교 테스트를 구현하세요")

    def test_detect_peaks_performance_profile(self):
        """
        TODO: 데이터 크기별 피크 감지 성능을 프로파일링하라.

        힌트:
        - 크기 100, 1000, 10000의 데이터 생성
        - 각 크기에서 100회 실행 시간 측정
        - 크기가 10배 증가할 때 시간도 약 10배 증가하는지 확인
        """
        pytest.skip("TODO: 성능 프로파일링 테스트를 구현하세요")


# =============================================================================
# 연습 3: 플러그인 설정 (개념 문제)
# =============================================================================

class TestPluginConfigExercise:
    """
    플러그인 설정에 대한 이해도를 테스트한다.
    """

    def test_understand_pyproject_config(self):
        """
        TODO: 아래 pyproject.toml 설정이 하는 일을 주석으로 설명하고,
        각 설정 값이 올바른지 assert로 검증하라.

        설정:
            addopts = "--cov=src --cov-fail-under=80 --timeout=30 -n auto"

        힌트:
        - config 딕셔너리의 각 항목이 맞는지 확인
        - 각 플러그인의 역할을 주석으로 작성
        """
        pytest.skip("TODO: 플러그인 설정 이해 테스트를 구현하세요")
