"""
연습문제 26: 비동기 코드 테스트

이 연습에서는 비동기 함수와 클래스를 테스트한다.
asyncio.run()을 사용하므로 pytest-asyncio 없이도 실행 가능하다.
TODO 부분을 채워서 테스트를 완성하라.
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
# 연습 1: AsyncMock으로 센서 데이터 모킹
# =============================================================================

class TestAsyncMockExercise:
    """
    AsyncMock을 사용하여 센서 데이터 수집을 테스트하라.
    """

    def test_collect_with_custom_mock(self):
        """
        TODO: AsyncMock을 만들어 collect_multiple_sensors()를 테스트하라.

        요구사항:
        1. 센서 ID에 따라 다른 값을 반환하는 AsyncMock 작성
           - "TEMP_001" → value: 75.0
           - "VIB_001" → value: 8.5
           - "PRES_001" → value: 6.2
        2. 세 센서를 동시에 수집
        3. 각 센서의 값이 기대와 일치하는지 검증

        힌트:
        - AsyncMock의 side_effect에 함수를 전달
        - 센서 ID로 분기하여 다른 값 반환
        """
        pytest.skip("TODO: 센서별 다른 값을 반환하는 AsyncMock을 구현하세요")

    def test_collect_with_partial_failure(self):
        """
        TODO: 일부 센서만 에러가 발생하는 상황을 테스트하라.

        요구사항:
        1. "BAD_001"은 ConnectionError 발생
        2. 나머지 센서는 정상
        3. 에러 센서의 status가 "error"인지 확인
        4. 정상 센서의 value가 있는지 확인

        힌트:
        - AsyncMock의 side_effect에 조건부 함수 전달
        """
        pytest.skip("TODO: 부분 실패를 처리하는 테스트를 구현하세요")


# =============================================================================
# 연습 2: 타임아웃 테스트
# =============================================================================

class TestTimeoutExercise:
    """
    비동기 작업의 타임아웃을 테스트하라.
    """

    def test_slow_sensor_timeout(self):
        """
        TODO: 느린 센서에 타임아웃을 적용하여 테스트하라.

        요구사항:
        1. 2초 지연되는 AsyncMock 작성 (asyncio.sleep(2))
        2. 0.1초 타임아웃으로 asyncio.wait_for() 적용
        3. asyncio.TimeoutError가 발생하는지 확인

        힌트:
        - async def slow_fetch(sid): await asyncio.sleep(2); ...
        - asyncio.wait_for(coroutine, timeout=0.1)
        """
        pytest.skip("TODO: 타임아웃 테스트를 구현하세요")

    def test_fast_sensor_no_timeout(self):
        """
        TODO: 빠른 센서는 타임아웃 없이 정상 완료되는지 테스트하라.

        요구사항:
        1. 즉시 반환하는 AsyncMock 작성
        2. 1초 타임아웃으로 asyncio.wait_for() 적용
        3. 정상 결과를 반환하는지 확인
        """
        pytest.skip("TODO: 정상 타임아웃 테스트를 구현하세요")


# =============================================================================
# 연습 3: AsyncSensorCollector 클래스 테스트
# =============================================================================

class TestCollectorExercise:
    """
    AsyncSensorCollector 클래스를 종합적으로 테스트하라.
    """

    def test_collector_full_workflow(self):
        """
        TODO: 수집기의 전체 워크플로우를 테스트하라.

        워크플로우:
        1. 수집기 생성 (모킹된 fetch 함수 사용)
        2. 센서 2개 등록 (VIB_001: 임계값 10, TEMP_001: 임계값 80)
        3. 알림 콜백 설정 (AsyncMock 사용)
        4. 3회 수집 (collect_once를 3번 호출)
        5. 통계 확인 (count == 3)
        6. 임계값 초과 시 알림 콜백 호출 확인
        """
        pytest.skip("TODO: 수집기 전체 워크플로우를 테스트하세요")

    def test_collector_start_stop(self):
        """
        TODO: 수집기의 start/stop을 테스트하라.

        요구사항:
        1. start()로 수집 시작 (interval=0.05, max_iterations=5)
        2. 완료 후 수집된 데이터 수 확인
        3. is_running이 False인지 확인
        """
        pytest.skip("TODO: 수집기 시작/중지를 테스트하세요")
