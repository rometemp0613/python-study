"""
솔루션 29: Flaky 테스트 수정하기

각 flaky 원인별로 수정된 안정적인 테스트입니다.

실행 방법:
    pytest exercises/solution_29.py -v
"""

import pytest
import math
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_sensor_monitor import SensorMonitor


# =============================================================================
# 솔루션 1: 시간 의존 → 고정 시간 주입
# =============================================================================

class TestFix_시간의존:
    """고정된 datetime을 사용하여 시간 의존성 제거"""

    def test_타임스탬프에_날짜포함(self):
        """고정 시간을 사용하여 항상 같은 결과를 보장"""
        # Arrange
        monitor = SensorMonitor()
        fixed_time = datetime(2024, 6, 15, 10, 30, 0)

        # Act
        result = monitor.format_timestamp(fixed_time)

        # Assert
        assert result == "2024-06-15 10:30:00"

    def test_자정_시간_포맷(self):
        """자정 시간도 올바르게 포맷되는지 확인"""
        monitor = SensorMonitor()
        midnight = datetime(2024, 1, 1, 0, 0, 0)

        result = monitor.format_timestamp(midnight)

        assert result == "2024-01-01 00:00:00"


# =============================================================================
# 솔루션 2: 부동소수점 → pytest.approx 사용
# =============================================================================

class TestFix_부동소수점:
    """pytest.approx를 사용하여 부동소수점 비교 문제 해결"""

    def test_센서_드리프트_계산(self):
        """pytest.approx로 드리프트 값 비교"""
        # Arrange
        monitor = SensorMonitor()
        readings = [100.0, 100.1, 100.2, 100.3, 100.4]

        # Act
        drift = monitor.calculate_drift(readings)

        # Assert: pytest.approx로 부동소수점 안전 비교
        assert drift == pytest.approx(0.1, abs=1e-10)

    def test_평균_계산(self):
        """pytest.approx로 평균값 비교"""
        # Arrange
        monitor = SensorMonitor()
        readings = [0.1, 0.2, 0.3]

        # Act
        stats = monitor.calculate_statistics(readings)

        # Assert: 부동소수점 안전 비교
        assert stats["mean"] == pytest.approx(0.2, abs=1e-5)

    def test_표준편차_계산(self):
        """표준편차도 approx로 비교"""
        monitor = SensorMonitor()
        readings = [10.0, 20.0, 30.0]

        stats = monitor.calculate_statistics(readings)

        expected_std = math.sqrt(200.0 / 3.0)
        assert stats["std"] == pytest.approx(expected_std, abs=1e-4)


# =============================================================================
# 솔루션 3: 랜덤 값 → 시드 고정
# =============================================================================

class TestFix_랜덤값:
    """시드를 고정하여 랜덤 값의 재현성 확보"""

    def test_센서_읽기_예측가능(self):
        """시드를 고정하면 항상 같은 결과를 얻을 수 있다"""
        # Arrange: 시드 고정
        monitor = SensorMonitor(seed=42)

        # Act
        reading = monitor.get_current_reading(base_value=100.0, noise_level=5.0)

        # Assert: 같은 시드로 생성한 결과와 동일해야 함
        monitor_same_seed = SensorMonitor(seed=42)
        expected = monitor_same_seed.get_current_reading(base_value=100.0, noise_level=5.0)
        assert reading == expected

    def test_여러_읽기_통계적_검증(self):
        """시드를 고정하고 통계적으로 검증"""
        # Arrange
        monitor = SensorMonitor(seed=12345)

        # Act: 많은 샘플 생성
        readings = [
            monitor.get_current_reading(base_value=100.0, noise_level=2.0)
            for _ in range(100)
        ]
        mean_reading = sum(readings) / len(readings)

        # Assert: 평균이 기대값에 가까움 (중심극한정리)
        assert mean_reading == pytest.approx(100.0, abs=1.0)
