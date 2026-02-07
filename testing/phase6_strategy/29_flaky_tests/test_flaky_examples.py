"""
Flaky 테스트 예시: 원래 flaky했던 테스트와 수정된 버전

각 테스트에는 원래의 flaky 버전(주석)과 수정된 버전이 있습니다.
모든 테스트는 안정적으로 PASS합니다.

실행 방법:
    pytest test_flaky_examples.py -v
"""

import math
import pytest
from datetime import datetime
from src_sensor_monitor import SensorMonitor


# =============================================================================
# 원인 1: 현재 시간(datetime) 의존
# =============================================================================

class TestFixed_시간의존:
    """시간 의존 flaky 테스트의 수정 예시"""

    # -------------------------------------------------------------------------
    # 원래 flaky 버전 (주석 처리):
    # def test_타임스탬프_포맷_flaky(self):
    #     """문제: datetime.now()에 의존하여 결과가 매번 달라짐"""
    #     monitor = SensorMonitor()
    #     result = monitor.format_timestamp(datetime.now())
    #     # 현재 연도에 의존 - 연도가 바뀌면 실패
    #     assert "2024" in result
    #     # 초 단위가 일치해야 함 - 실행 시점에 따라 달라질 수 있음
    #     expected = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     assert result == expected  # 밀리초 차이로 실패 가능
    # -------------------------------------------------------------------------

    def test_타임스탬프_포맷_fixed(self):
        """수정: 고정된 datetime을 사용하여 결과를 예측 가능하게 만듦"""
        monitor = SensorMonitor()
        fixed_time = datetime(2024, 6, 15, 10, 30, 45)

        result = monitor.format_timestamp(fixed_time)

        assert result == "2024-06-15 10:30:45"

    def test_다양한_시간_포맷(self):
        """수정: 여러 고정 시간으로 포맷 검증"""
        monitor = SensorMonitor()

        # 자정
        assert monitor.format_timestamp(datetime(2024, 1, 1, 0, 0, 0)) == "2024-01-01 00:00:00"
        # 연말
        assert monitor.format_timestamp(datetime(2024, 12, 31, 23, 59, 59)) == "2024-12-31 23:59:59"


# =============================================================================
# 원인 2: 부동소수점 비교
# =============================================================================

class TestFixed_부동소수점:
    """부동소수점 비교 flaky 테스트의 수정 예시"""

    # -------------------------------------------------------------------------
    # 원래 flaky 버전 (주석 처리):
    # def test_드리프트_계산_flaky(self):
    #     """문제: 부동소수점 정확한 동등 비교"""
    #     monitor = SensorMonitor()
    #     readings = [100.0, 100.1, 100.2, 100.3, 100.4]
    #     drift = monitor.calculate_drift(readings)
    #     assert drift == 0.1  # 부동소수점 오차로 실패할 수 있음
    # -------------------------------------------------------------------------

    def test_드리프트_계산_fixed(self):
        """수정: pytest.approx로 허용 오차 비교"""
        monitor = SensorMonitor()
        readings = [100.0, 100.1, 100.2, 100.3, 100.4]

        drift = monitor.calculate_drift(readings)

        assert drift == pytest.approx(0.1, abs=1e-10)

    # -------------------------------------------------------------------------
    # 원래 flaky 버전 (주석 처리):
    # def test_통계_계산_flaky(self):
    #     """문제: 부동소수점 합산 후 정확한 비교"""
    #     monitor = SensorMonitor()
    #     readings = [0.1, 0.2, 0.3]
    #     stats = monitor.calculate_statistics(readings)
    #     assert stats["mean"] == 0.2  # 0.19999... 가능
    # -------------------------------------------------------------------------

    def test_통계_계산_fixed(self):
        """수정: pytest.approx 사용"""
        monitor = SensorMonitor()
        readings = [0.1, 0.2, 0.3]

        stats = monitor.calculate_statistics(readings)

        assert stats["mean"] == pytest.approx(0.2, abs=1e-5)

    def test_임계값_비교_마진(self):
        """수정: 마진 값 비교 시 approx 사용"""
        monitor = SensorMonitor()

        result = monitor.check_threshold(100.3, 100.0)

        assert result["exceeded"] is True
        assert result["margin"] == pytest.approx(0.3, abs=1e-5)


# =============================================================================
# 원인 3: 랜덤 값 의존
# =============================================================================

class TestFixed_랜덤값:
    """랜덤 값 의존 flaky 테스트의 수정 예시"""

    # -------------------------------------------------------------------------
    # 원래 flaky 버전 (주석 처리):
    # def test_센서_읽기_flaky(self):
    #     """문제: 랜덤 노이즈로 결과가 매번 달라짐"""
    #     monitor = SensorMonitor()
    #     reading = monitor.get_current_reading(base_value=100.0)
    #     assert 95.0 <= reading <= 105.0  # 가끔 범위를 벗어남
    # -------------------------------------------------------------------------

    def test_센서_읽기_시드_고정(self):
        """수정: 랜덤 시드를 고정하여 결과를 예측 가능하게 만듦"""
        monitor = SensorMonitor(seed=42)

        reading = monitor.get_current_reading(base_value=100.0, noise_level=5.0)

        # 시드가 고정되어 항상 같은 값을 반환
        assert isinstance(reading, float)
        # 첫 번째 호출 결과가 항상 동일
        monitor2 = SensorMonitor(seed=42)
        reading2 = monitor2.get_current_reading(base_value=100.0, noise_level=5.0)
        assert reading == reading2

    def test_센서_읽기_범위_넓힘(self):
        """수정: 충분히 넓은 범위로 확인 (통계적 접근)"""
        monitor = SensorMonitor(seed=12345)

        readings = [
            monitor.get_current_reading(base_value=100.0, noise_level=2.0)
            for _ in range(100)
        ]

        mean_reading = sum(readings) / len(readings)
        # 100개의 평균은 100에 가까워야 함 (중심극한정리)
        assert mean_reading == pytest.approx(100.0, abs=1.0)


# =============================================================================
# 원인 4: 테스트 오염 (Test Pollution)
# =============================================================================

class TestFixed_테스트오염:
    """테스트 오염 flaky 테스트의 수정 예시"""

    # -------------------------------------------------------------------------
    # 원래 flaky 버전 (주석 처리):
    # 모듈 수준 변수 공유로 인한 테스트 오염
    # _shared_readings = []
    #
    # def test_데이터_추가_flaky(self):
    #     _shared_readings.append(100.0)
    #     assert len(_shared_readings) == 1  # 순서에 따라 다를 수 있음
    #
    # def test_빈_리스트_확인_flaky(self):
    #     assert len(_shared_readings) == 0  # 위 테스트 후에는 실패
    # -------------------------------------------------------------------------

    def test_독립적_데이터_추가(self):
        """수정: 각 테스트에서 로컬 변수 사용"""
        local_readings = []
        local_readings.append(100.0)
        assert len(local_readings) == 1

    def test_독립적_빈_리스트(self):
        """수정: 다른 테스트에 의존하지 않음"""
        local_readings = []
        assert len(local_readings) == 0


# =============================================================================
# 원인 5: 순서/정렬 의존
# =============================================================================

class TestFixed_순서의존:
    """순서 의존 flaky 테스트의 수정 예시"""

    # -------------------------------------------------------------------------
    # 원래 flaky 버전 (주석 처리):
    # def test_센서_분류_flaky(self):
    #     """문제: 세트의 순서에 의존"""
    #     categories = set()
    #     monitor = SensorMonitor()
    #     for value in [50, 80, 120]:
    #         cat = monitor.classify_reading(value, (60, 100), (40, 110))
    #         categories.add(cat)
    #     result = list(categories)
    #     assert result == ["warning", "normal", "critical"]  # 순서 보장 안됨
    # -------------------------------------------------------------------------

    def test_센서_분류_fixed(self):
        """수정: 순서에 의존하지 않는 검증 방법 사용"""
        categories = set()
        monitor = SensorMonitor()

        for value in [50, 80, 120]:
            cat = monitor.classify_reading(value, (60, 100), (40, 110))
            categories.add(cat)

        # 세트의 포함 여부로 검증 (순서 무관)
        assert "normal" in categories
        assert "warning" in categories
        assert "critical" in categories
        assert len(categories) == 3

    def test_통계_결과_키_확인(self):
        """수정: 딕셔너리 키 존재 여부로 검증"""
        monitor = SensorMonitor()
        stats = monitor.calculate_statistics([10.0, 20.0, 30.0])

        # 키 존재 여부로 확인 (순서 무관)
        expected_keys = {"mean", "std", "min", "max", "count"}
        assert set(stats.keys()) == expected_keys


# =============================================================================
# 종합: 실제 센서 시나리오
# =============================================================================

class TestFixed_종합시나리오:
    """종합적인 flaky 테스트 수정 예시"""

    def test_센서_모니터링_안정적(self):
        """모든 flaky 원인을 제거한 안정적인 테스트"""
        # 시드 고정으로 랜덤 제거
        monitor = SensorMonitor(sensor_id="temp-001", seed=42)

        # 고정된 데이터 사용 (랜덤 대신)
        readings = [72.0, 74.5, 73.2, 75.1, 74.8]

        # 통계 계산 - approx로 부동소수점 처리
        stats = monitor.calculate_statistics(readings)
        assert stats["mean"] == pytest.approx(73.92, abs=0.01)
        assert stats["count"] == 5

        # 드리프트 계산 - approx로 부동소수점 처리
        drift = monitor.calculate_drift(readings)
        assert isinstance(drift, float)

        # 고정 시간 사용
        fixed_time = datetime(2024, 3, 15, 14, 30, 0)
        timestamp = monitor.format_timestamp(fixed_time)
        assert timestamp == "2024-03-15 14:30:00"

        # 임계값 비교 - 명확한 값 사용
        result = monitor.check_threshold(75.0, 80.0)
        assert result["exceeded"] is False
        assert result["status"] == "normal"
