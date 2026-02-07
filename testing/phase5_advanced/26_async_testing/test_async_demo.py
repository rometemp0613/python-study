"""
비동기 코드 테스트 데모.

이 파일은 두 가지 방식으로 비동기 코드를 테스트한다:
1. asyncio.run() 사용 (pytest-asyncio 불필요)
2. @pytest.mark.asyncio 사용 (pytest-asyncio 필요, 별도 클래스)

실행 방법:
    pytest test_async_demo.py -v
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src_async_sensor import (
    fetch_sensor_data,
    collect_multiple_sensors,
    monitor_sensor,
    AsyncSensorCollector,
)


# =============================================================================
# asyncio.run() 사용 테스트 (pytest-asyncio 불필요)
# =============================================================================

class TestFetchSensorData:
    """단일 센서 데이터 수집 테스트 (동기 래퍼 사용)"""

    def test_fetch_returns_dict(self):
        """센서 데이터가 딕셔너리로 반환된다"""
        result = asyncio.run(fetch_sensor_data("VIB_001"))
        assert isinstance(result, dict)
        assert "sensor_id" in result
        assert "value" in result
        assert "status" in result

    def test_fetch_returns_correct_sensor_id(self):
        """반환된 센서 ID가 요청한 것과 일치한다"""
        result = asyncio.run(fetch_sensor_data("TEMP_001"))
        assert result["sensor_id"] == "TEMP_001"

    def test_fetch_status_ok(self):
        """정상 상태에서는 status가 ok"""
        result = asyncio.run(fetch_sensor_data("VIB_001"))
        assert result["status"] == "ok"


class TestFetchWithMock:
    """AsyncMock을 사용한 센서 데이터 모킹 테스트"""

    def test_mock_fetch_returns_expected_value(self):
        """모킹된 센서가 기대 값을 반환한다"""
        # AsyncMock 생성: 고정된 값 반환
        mock_fetch = AsyncMock(return_value={
            "sensor_id": "VIB_001",
            "value": 42.0,
            "status": "ok",
        })

        result = asyncio.run(mock_fetch("VIB_001"))
        assert result["value"] == 42.0
        mock_fetch.assert_called_once_with("VIB_001")

    def test_mock_fetch_side_effect(self):
        """모킹된 센서가 순차적으로 다른 값을 반환한다"""
        mock_fetch = AsyncMock(side_effect=[
            {"sensor_id": "VIB_001", "value": 10.0, "status": "ok"},
            {"sensor_id": "VIB_001", "value": 20.0, "status": "ok"},
            {"sensor_id": "VIB_001", "value": 30.0, "status": "ok"},
        ])

        async def run():
            results = []
            for _ in range(3):
                results.append(await mock_fetch("VIB_001"))
            return results

        results = asyncio.run(run())
        assert [r["value"] for r in results] == [10.0, 20.0, 30.0]

    def test_mock_fetch_raises_error(self):
        """모킹된 센서가 에러를 발생시킨다"""
        mock_fetch = AsyncMock(side_effect=ConnectionError("센서 연결 실패"))

        with pytest.raises(ConnectionError, match="연결 실패"):
            asyncio.run(mock_fetch("VIB_001"))


class TestCollectMultipleSensors:
    """여러 센서 동시 수집 테스트"""

    def test_collect_empty_list(self):
        """빈 센서 목록은 빈 결과"""
        result = asyncio.run(collect_multiple_sensors([]))
        assert result == []

    def test_collect_multiple_with_mock(self):
        """여러 센서를 동시에 수집 (모킹)"""
        mock_fetch = AsyncMock(side_effect=lambda sid: {
            "sensor_id": sid,
            "value": 42.0,
            "status": "ok",
        })

        result = asyncio.run(
            collect_multiple_sensors(
                ["VIB_001", "TEMP_001", "PRES_001"],
                fetch_func=mock_fetch,
            )
        )

        assert len(result) == 3
        sensor_ids = [r["sensor_id"] for r in result]
        assert "VIB_001" in sensor_ids
        assert "TEMP_001" in sensor_ids
        assert "PRES_001" in sensor_ids

    def test_collect_handles_errors(self):
        """일부 센서 에러 시 다른 센서는 정상 수집"""
        call_count = 0

        async def mock_fetch(sensor_id):
            nonlocal call_count
            call_count += 1
            if sensor_id == "BAD_001":
                raise ConnectionError("센서 연결 실패")
            return {"sensor_id": sensor_id, "value": 42.0, "status": "ok"}

        result = asyncio.run(
            collect_multiple_sensors(
                ["VIB_001", "BAD_001", "TEMP_001"],
                fetch_func=mock_fetch,
            )
        )

        assert len(result) == 3
        # 정상 센서
        assert result[0]["status"] == "ok"
        # 에러 센서
        assert result[1]["status"] == "error"
        assert "연결 실패" in result[1]["error"]
        # 정상 센서
        assert result[2]["status"] == "ok"


class TestMonitorSensor:
    """센서 모니터링 테스트"""

    def test_monitor_collects_data(self):
        """모니터링이 데이터를 수집한다"""
        mock_fetch = AsyncMock(return_value={
            "sensor_id": "VIB_001",
            "value": 42.0,
            "status": "ok",
        })

        readings = asyncio.run(
            monitor_sensor(
                "VIB_001",
                duration=0.25,
                interval=0.1,
                fetch_func=mock_fetch,
            )
        )

        # 0.25초 동안 0.1초 간격 → 약 2~3회 수집
        assert len(readings) >= 2
        assert all(r["sensor_id"] == "VIB_001" for r in readings)

    def test_monitor_handles_errors(self):
        """모니터링 중 에러 발생 시 기록하고 계속한다"""
        call_count = 0

        async def flaky_fetch(sensor_id):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise ConnectionError("일시적 에러")
            return {"sensor_id": sensor_id, "value": 42.0, "status": "ok"}

        readings = asyncio.run(
            monitor_sensor(
                "VIB_001",
                duration=0.25,
                interval=0.1,
                fetch_func=flaky_fetch,
            )
        )

        # 에러가 발생해도 모니터링은 계속된다
        statuses = [r["status"] for r in readings]
        assert "error" in statuses
        assert "ok" in statuses


class TestAsyncSensorCollector:
    """AsyncSensorCollector 클래스 테스트"""

    def test_register_sensor(self):
        """센서 등록"""
        collector = AsyncSensorCollector()
        collector.register_sensor("VIB_001")
        collector.register_sensor("TEMP_001")

        assert "VIB_001" in collector.registered_sensors
        assert "TEMP_001" in collector.registered_sensors
        assert len(collector.registered_sensors) == 2

    def test_register_duplicate_ignored(self):
        """중복 센서 등록은 무시된다"""
        collector = AsyncSensorCollector()
        collector.register_sensor("VIB_001")
        collector.register_sensor("VIB_001")

        assert len(collector.registered_sensors) == 1

    def test_collect_once_with_mock(self):
        """한 번 수집"""
        mock_fetch = AsyncMock(side_effect=lambda sid: {
            "sensor_id": sid,
            "value": 42.0,
            "status": "ok",
        })

        collector = AsyncSensorCollector(fetch_func=mock_fetch)
        collector.register_sensor("VIB_001")
        collector.register_sensor("TEMP_001")

        result = asyncio.run(collector.collect_once())

        assert "VIB_001" in result
        assert "TEMP_001" in result
        assert result["VIB_001"]["value"] == 42.0

    def test_collect_once_empty(self):
        """센서가 없을 때 빈 결과"""
        collector = AsyncSensorCollector()
        result = asyncio.run(collector.collect_once())
        assert result == {}

    def test_alert_callback(self):
        """임계값 초과 시 알림 콜백 호출"""
        mock_fetch = AsyncMock(return_value={
            "sensor_id": "VIB_001",
            "value": 15.0,  # 임계값(10) 초과
            "status": "ok",
        })

        alert_callback = AsyncMock()

        collector = AsyncSensorCollector(fetch_func=mock_fetch)
        collector.register_sensor("VIB_001", alert_threshold=10.0)
        collector.set_alert_callback(alert_callback)

        asyncio.run(collector.collect_once())

        # 알림 콜백이 호출되었는지 확인
        alert_callback.assert_called_once_with("VIB_001", 15.0, 10.0)

    def test_no_alert_below_threshold(self):
        """임계값 이하면 알림 없음"""
        mock_fetch = AsyncMock(return_value={
            "sensor_id": "VIB_001",
            "value": 5.0,  # 임계값(10) 이하
            "status": "ok",
        })

        alert_callback = AsyncMock()

        collector = AsyncSensorCollector(fetch_func=mock_fetch)
        collector.register_sensor("VIB_001", alert_threshold=10.0)
        collector.set_alert_callback(alert_callback)

        asyncio.run(collector.collect_once())

        # 알림 콜백이 호출되지 않아야 함
        alert_callback.assert_not_called()

    def test_get_statistics(self):
        """수집 통계 조회"""
        call_count = 0

        async def mock_fetch(sensor_id):
            nonlocal call_count
            call_count += 1
            return {
                "sensor_id": sensor_id,
                "value": float(call_count * 10),
                "status": "ok",
            }

        collector = AsyncSensorCollector(fetch_func=mock_fetch)
        collector.register_sensor("VIB_001")

        # 3번 수집
        async def collect_three():
            for _ in range(3):
                await collector.collect_once()

        asyncio.run(collect_three())

        stats = collector.get_statistics("VIB_001")
        assert stats["count"] == 3
        assert stats["min"] == 10.0
        assert stats["max"] == 30.0
        assert stats["mean"] == pytest.approx(20.0)

    def test_get_statistics_no_data(self):
        """데이터가 없을 때의 통계"""
        collector = AsyncSensorCollector()
        stats = collector.get_statistics("VIB_001")
        assert stats["count"] == 0
        assert stats["mean"] == 0.0

    def test_start_and_stop(self):
        """수집 시작/중지"""
        mock_fetch = AsyncMock(return_value={
            "sensor_id": "VIB_001",
            "value": 42.0,
            "status": "ok",
        })

        collector = AsyncSensorCollector(fetch_func=mock_fetch)
        collector.register_sensor("VIB_001")

        async def run_and_stop():
            # 별도 태스크로 수집 시작 (max_iterations=3)
            task = asyncio.create_task(
                collector.start(interval=0.05, max_iterations=3)
            )
            # 수집 완료 대기
            await task
            return collector.get_readings("VIB_001")

        readings = asyncio.run(run_and_stop())

        # 3회 반복 후 자동 종료
        assert len(readings) == 3
        assert collector.is_running is False

    def test_stop_during_collection(self):
        """수집 중 중지"""
        mock_fetch = AsyncMock(return_value={
            "sensor_id": "VIB_001",
            "value": 42.0,
            "status": "ok",
        })

        collector = AsyncSensorCollector(fetch_func=mock_fetch)
        collector.register_sensor("VIB_001")

        async def run_and_stop_early():
            task = asyncio.create_task(
                collector.start(interval=0.05, max_iterations=100)
            )
            # 0.15초 후 중지
            await asyncio.sleep(0.15)
            collector.stop()
            await task
            return collector.get_readings("VIB_001")

        readings = asyncio.run(run_and_stop_early())

        # 중지 전까지 수집된 데이터가 있어야 함
        assert len(readings) > 0
        assert len(readings) < 100  # max_iterations에 도달하지 않음
        assert collector.is_running is False


# =============================================================================
# pytest-asyncio 사용 테스트 (설치 시에만 실행)
# =============================================================================

# pytest-asyncio가 설치되어 있는지 확인
try:
    import pytest_asyncio
    HAS_PYTEST_ASYNCIO = True
except ImportError:
    HAS_PYTEST_ASYNCIO = False


@pytest.mark.skipif(
    not HAS_PYTEST_ASYNCIO,
    reason="pytest-asyncio가 설치되지 않음"
)
class TestWithPytestAsyncio:
    """
    pytest-asyncio를 사용하는 비동기 테스트.

    @pytest.mark.asyncio 데코레이터를 사용하면
    async def 테스트 함수를 직접 작성할 수 있다.
    """

    @pytest.mark.asyncio
    async def test_fetch_sensor_data(self):
        """비동기 테스트: 센서 데이터 수집"""
        result = await fetch_sensor_data("VIB_001")
        assert result["sensor_id"] == "VIB_001"
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_collect_multiple(self):
        """비동기 테스트: 여러 센서 동시 수집"""
        mock_fetch = AsyncMock(side_effect=lambda sid: {
            "sensor_id": sid,
            "value": 42.0,
            "status": "ok",
        })

        results = await collect_multiple_sensors(
            ["VIB_001", "TEMP_001"],
            fetch_func=mock_fetch,
        )

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_async_mock_usage(self):
        """비동기 테스트: AsyncMock 사용"""
        mock = AsyncMock(return_value={"value": 100.0})
        result = await mock()
        assert result["value"] == 100.0

    @pytest.mark.asyncio
    async def test_timeout(self):
        """비동기 테스트: 타임아웃"""
        async def slow_operation():
            await asyncio.sleep(10)  # 매우 느린 작업

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_operation(), timeout=0.1)

    @pytest.mark.asyncio
    async def test_collector_alert_async(self):
        """비동기 테스트: 알림 콜백 (async)"""
        mock_fetch = AsyncMock(return_value={
            "sensor_id": "VIB_001",
            "value": 20.0,
            "status": "ok",
        })

        alert_log = []

        async def on_alert(sensor_id, value, threshold):
            alert_log.append({
                "sensor_id": sensor_id,
                "value": value,
                "threshold": threshold,
            })

        collector = AsyncSensorCollector(fetch_func=mock_fetch)
        collector.register_sensor("VIB_001", alert_threshold=15.0)
        collector.set_alert_callback(on_alert)

        await collector.collect_once()

        assert len(alert_log) == 1
        assert alert_log[0]["sensor_id"] == "VIB_001"
        assert alert_log[0]["value"] == 20.0
