"""
연습 29: Flaky 테스트 수정하기

아래의 flaky 테스트들을 안정적으로 통과하도록 수정하세요.
각 테스트에는 flaky한 이유와 힌트가 주석으로 제공됩니다.

실행 방법:
    pytest exercises/exercise_29.py -v
"""

import pytest
import math
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_sensor_monitor import SensorMonitor


# =============================================================================
# 문제 1: 시간 의존 flaky 테스트 수정
# =============================================================================

class TestFix_시간의존:
    """시간에 의존하는 flaky 테스트를 수정하세요."""

    def test_타임스탬프에_날짜포함(self):
        """
        문제: datetime.now()를 사용하여 시간에 따라 결과가 달라짐
        TODO: 고정된 datetime을 사용하도록 수정하세요
        """
        pytest.skip(
            "TODO: 고정된 datetime을 사용하여 수정하세요.\n"
            "힌트: fixed_time = datetime(2024, 6, 15, 10, 30, 0)"
        )
        # 원래 flaky 코드:
        # monitor = SensorMonitor()
        # result = monitor.format_timestamp(datetime.now())
        # assert "2024" in result

        # 수정된 코드를 작성하세요:
        # monitor = SensorMonitor()
        # fixed_time = datetime(2024, 6, 15, 10, 30, 0)
        # result = monitor.format_timestamp(fixed_time)
        # assert result == "2024-06-15 10:30:00"


# =============================================================================
# 문제 2: 부동소수점 비교 수정
# =============================================================================

class TestFix_부동소수점:
    """부동소수점 비교로 인한 flaky 테스트를 수정하세요."""

    def test_센서_드리프트_계산(self):
        """
        문제: 부동소수점 정확한 동등 비교로 실패할 수 있음
        TODO: pytest.approx를 사용하도록 수정하세요
        """
        pytest.skip(
            "TODO: pytest.approx를 사용하여 부동소수점 비교를 수정하세요.\n"
            "힌트: assert value == pytest.approx(expected, abs=1e-10)"
        )
        # 원래 flaky 코드:
        # monitor = SensorMonitor()
        # readings = [100.0, 100.1, 100.2, 100.3, 100.4]
        # drift = monitor.calculate_drift(readings)
        # assert drift == 0.1  # 부동소수점 오차!

    def test_평균_계산(self):
        """
        문제: 부동소수점 합산 후 정확한 비교
        TODO: pytest.approx를 사용하도록 수정하세요
        """
        pytest.skip(
            "TODO: 부동소수점 비교를 수정하세요.\n"
            "힌트: assert stats['mean'] == pytest.approx(expected, abs=1e-5)"
        )
        # 원래 flaky 코드:
        # monitor = SensorMonitor()
        # readings = [0.1, 0.2, 0.3]
        # stats = monitor.calculate_statistics(readings)
        # assert stats["mean"] == 0.2  # 0.19999... 가능


# =============================================================================
# 문제 3: 랜덤 값 의존 수정
# =============================================================================

class TestFix_랜덤값:
    """랜덤 값에 의존하는 flaky 테스트를 수정하세요."""

    def test_센서_읽기_예측가능(self):
        """
        문제: 매번 다른 랜덤 값이 생성됨
        TODO: 시드를 고정하여 결과를 예측 가능하게 만드세요
        """
        pytest.skip(
            "TODO: SensorMonitor의 seed 매개변수를 사용하여 랜덤을 고정하세요.\n"
            "힌트: monitor = SensorMonitor(seed=42)"
        )
        # 원래 flaky 코드:
        # monitor = SensorMonitor()
        # reading = monitor.get_current_reading(base_value=100.0)
        # assert 95.0 <= reading <= 105.0  # 가끔 범위 벗어남
