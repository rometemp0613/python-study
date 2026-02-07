"""
연습 문제 13: unittest.mock 심화

Mock의 다양한 기능을 활용하여
센서 데이터 수집기를 테스트하세요.
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, create_autospec, call

# 상위 디렉토리의 모듈을 임포트하기 위한 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src_sensor_collector import (
    SensorAPI, SensorCollector, DataStore,
    SensorReading, CollectionResult,
)


# ============================================================
# 연습 1: side_effect로 온도 상승 시뮬레이션
# ============================================================

class TestExercise1:
    """side_effect를 사용하여 센서 데이터 시나리오를 시뮬레이션"""

    def test_temperature_rising_scenario(self):
        """온도가 점점 상승하는 시나리오를 시뮬레이션하세요"""
        pytest.skip("TODO: side_effect로 온도 상승 시나리오를 구현하세요")
        # TODO:
        # 1. Mock(spec=SensorAPI)로 mock_api 생성
        # 2. fetch_reading의 side_effect에 3개의 딕셔너리 리스트 설정
        #    - 온도: 70, 80, 95 (점점 상승)
        #    - 진동/압력: 일정 (2.0, 5.0)
        # 3. Mock(spec=DataStore)로 mock_store 생성 (save → True)
        # 4. SensorCollector로 3번 collect_single 호출
        # 5. 세 번째 읽기의 온도가 95인지 확인

    def test_connection_failure_recovery(self):
        """연결 실패 후 복구되는 시나리오를 테스트하세요"""
        pytest.skip("TODO: side_effect로 실패→실패→성공 시나리오를 구현하세요")
        # TODO:
        # 1. side_effect에 [ConnectionError, ConnectionError, 정상데이터] 설정
        # 2. collect_with_retry(sensor_id, max_retries=3) 호출
        # 3. 결과가 None이 아닌지 확인
        # 4. fetch_reading이 3번 호출되었는지 확인


# ============================================================
# 연습 2: spec으로 안전한 목 만들기
# ============================================================

class TestExercise2:
    """spec과 create_autospec 활용"""

    def test_spec_prevents_typo(self):
        """spec이 오타를 방지하는 것을 확인하세요"""
        pytest.skip("TODO: spec=SensorAPI인 Mock을 만들고 오타 감지를 테스트하세요")
        # TODO:
        # 1. Mock(spec=SensorAPI) 생성
        # 2. 존재하는 메서드 호출은 성공하는지 확인
        # 3. 존재하지 않는 메서드 접근 시 AttributeError 발생 확인
        #    - pytest.raises(AttributeError) 사용

    def test_autospec_validates_arguments(self):
        """create_autospec이 인자 개수를 검증하는 것을 확인하세요"""
        pytest.skip("TODO: create_autospec으로 시그니처 검증을 테스트하세요")
        # TODO:
        # 1. create_autospec(SensorAPI) 생성
        # 2. 올바른 인자로 호출 시 성공
        # 3. 잘못된 인자 개수로 호출 시 TypeError 발생 확인


# ============================================================
# 연습 3: 호출 패턴 검증
# ============================================================

class TestExercise3:
    """assert_has_calls로 호출 패턴을 검증"""

    def test_multiple_sensors_call_order(self):
        """여러 센서 수집 시 API 호출 순서를 검증하세요"""
        pytest.skip("TODO: assert_has_calls로 호출 순서를 검증하세요")
        # TODO:
        # 1. mock_api의 fetch_reading이 고정 데이터를 반환하도록 설정
        # 2. collect_multiple(["PUMP-01", "MOTOR-02", "VALVE-03"]) 호출
        # 3. fetch_reading이 3번 호출되었는지 확인 (call_count)
        # 4. assert_has_calls로 호출 순서 검증:
        #    [call("PUMP-01"), call("MOTOR-02"), call("VALVE-03")]
        # 5. 각 센서에 대해 store.save도 호출되었는지 확인

    def test_invalid_data_not_saved(self):
        """유효하지 않은 데이터는 저장되지 않음을 검증하세요"""
        pytest.skip("TODO: 범위 밖 데이터가 저장되지 않는 것을 검증하세요")
        # TODO:
        # 1. 온도 250도(범위 밖)인 데이터를 반환하도록 설정
        # 2. collect_single 호출
        # 3. reading.is_valid가 False인지 확인
        # 4. store.save가 호출되지 않았는지 확인 (assert_not_called)
