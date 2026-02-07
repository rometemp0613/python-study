"""
연습문제 26 정답: 비동기 코드 테스트

각 연습의 완성된 풀이.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_async_sensor import (
    fetch_sensor_data,
    collect_multiple_sensors,
    monitor_sensor,
    AsyncSensorCollector,
)


# =============================================================================
# 연습 1 정답: AsyncMock으로 센서 데이터 모킹
# =============================================================================

class TestAsyncMockSolution:
    """AsyncMock을 사용한 센서 데이터 모킹"""

    def test_collect_with_custom_mock(self):
        """센서별 다른 값을 반환하는 모킹 테스트"""
        # 센서 ID에 따라 다른 값을 반환하는 mock 함수
        sensor_values = {
            "TEMP_001": 75.0,
            "VIB_001": 8.5,
            "PRES_001": 6.2,
        }

        async def mock_fetch(sensor_id):
            return {
                "sensor_id": sensor_id,
                "value": sensor_values.get(sensor_id, 0.0),
                "status": "ok",
            }

        mock = AsyncMock(side_effect=mock_fetch)

        # 세 센서 동시 수집
        result = asyncio.run(
            collect_multiple_sensors(
                ["TEMP_001", "VIB_001", "PRES_001"],
                fetch_func=mock,
            )
        )

        # 결과 검증
        assert len(result) == 3

        # 각 센서의 값 확인
        result_map = {r["sensor_id"]: r["value"] for r in result}
        assert result_map["TEMP_001"] == 75.0
        assert result_map["VIB_001"] == 8.5
        assert result_map["PRES_001"] == 6.2

    def test_collect_with_partial_failure(self):
        """일부 센서 에러 시 나머지는 정상 수집"""

        async def mock_fetch(sensor_id):
            if sensor_id == "BAD_001":
                raise ConnectionError("센서 연결 실패")
            return {
                "sensor_id": sensor_id,
                "value": 42.0,
                "status": "ok",
            }

        mock = AsyncMock(side_effect=mock_fetch)

        result = asyncio.run(
            collect_multiple_sensors(
                ["VIB_001", "BAD_001", "TEMP_001"],
                fetch_func=mock,
            )
        )

        assert len(result) == 3

        # VIB_001: 정상
        assert result[0]["status"] == "ok"
        assert result[0]["value"] == 42.0

        # BAD_001: 에러
        assert result[1]["status"] == "error"
        assert "연결 실패" in result[1]["error"]
        assert result[1]["value"] is None

        # TEMP_001: 정상
        assert result[2]["status"] == "ok"
        assert result[2]["value"] == 42.0


# =============================================================================
# 연습 2 정답: 타임아웃 테스트
# =============================================================================

class TestTimeoutSolution:
    """비동기 타임아웃 테스트"""

    def test_slow_sensor_timeout(self):
        """느린 센서에 타임아웃 적용"""

        async def slow_fetch(sensor_id):
            """2초 지연되는 느린 센서"""
            await asyncio.sleep(2)
            return {"sensor_id": sensor_id, "value": 42.0, "status": "ok"}

        async def run():
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    slow_fetch("VIB_001"),
                    timeout=0.1,  # 0.1초 제한
                )

        asyncio.run(run())

    def test_fast_sensor_no_timeout(self):
        """빠른 센서는 타임아웃 없이 정상 완료"""
        mock_fetch = AsyncMock(return_value={
            "sensor_id": "VIB_001",
            "value": 42.0,
            "status": "ok",
        })

        async def run():
            result = await asyncio.wait_for(
                mock_fetch("VIB_001"),
                timeout=1.0,  # 1초 제한 (충분히 넉넉)
            )
            return result

        result = asyncio.run(run())
        assert result["value"] == 42.0
        assert result["status"] == "ok"


# =============================================================================
# 연습 3 정답: AsyncSensorCollector 전체 워크플로우
# =============================================================================

class TestCollectorSolution:
    """AsyncSensorCollector 종합 테스트"""

    def test_collector_full_workflow(self):
        """수집기 전체 워크플로우"""
        # VIB_001은 임계값(10) 초과, TEMP_001은 임계값(80) 이하
        async def mock_fetch(sensor_id):
            values = {
                "VIB_001": 15.0,  # 임계값 10 초과 → 알림
                "TEMP_001": 65.0,  # 임계값 80 이하 → 알림 없음
            }
            return {
                "sensor_id": sensor_id,
                "value": values.get(sensor_id, 0.0),
                "status": "ok",
            }

        mock = AsyncMock(side_effect=mock_fetch)
        alert_callback = AsyncMock()

        # 1. 수집기 생성
        collector = AsyncSensorCollector(fetch_func=mock)

        # 2. 센서 등록 (임계값 포함)
        collector.register_sensor("VIB_001", alert_threshold=10.0)
        collector.register_sensor("TEMP_001", alert_threshold=80.0)

        # 3. 알림 콜백 설정
        collector.set_alert_callback(alert_callback)

        # 4. 3회 수집
        async def collect_three():
            for _ in range(3):
                await collector.collect_once()

        asyncio.run(collect_three())

        # 5. 통계 확인
        vib_stats = collector.get_statistics("VIB_001")
        assert vib_stats["count"] == 3
        assert vib_stats["mean"] == pytest.approx(15.0)

        temp_stats = collector.get_statistics("TEMP_001")
        assert temp_stats["count"] == 3
        assert temp_stats["mean"] == pytest.approx(65.0)

        # 6. 알림 콜백: VIB_001만 3회 호출 (매번 임계값 초과)
        assert alert_callback.call_count == 3
        # 모든 호출이 VIB_001에 대한 것인지 확인
        for call in alert_callback.call_args_list:
            assert call.args[0] == "VIB_001"
            assert call.args[1] == 15.0
            assert call.args[2] == 10.0

    def test_collector_start_stop(self):
        """수집기 시작/중지"""
        mock_fetch = AsyncMock(return_value={
            "sensor_id": "VIB_001",
            "value": 42.0,
            "status": "ok",
        })

        collector = AsyncSensorCollector(fetch_func=mock_fetch)
        collector.register_sensor("VIB_001")

        async def run():
            # max_iterations=5로 자동 종료
            await collector.start(interval=0.05, max_iterations=5)
            return collector.get_readings("VIB_001")

        readings = asyncio.run(run())

        # 5회 수집 완료
        assert len(readings) == 5

        # 수집기가 중지됨
        assert collector.is_running is False

        # 통계 확인
        stats = collector.get_statistics("VIB_001")
        assert stats["count"] == 5
        assert stats["mean"] == pytest.approx(42.0)
