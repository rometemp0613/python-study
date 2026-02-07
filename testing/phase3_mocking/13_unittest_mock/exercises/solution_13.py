"""
연습 문제 13 풀이: unittest.mock 심화

Mock의 다양한 기능을 활용한 풀이입니다.
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
# 연습 1 풀이: side_effect로 온도 상승 시뮬레이션
# ============================================================

class TestExercise1:
    """side_effect를 사용하여 센서 데이터 시나리오를 시뮬레이션"""

    def test_temperature_rising_scenario(self):
        """온도가 점점 상승하는 시나리오를 시뮬레이션"""
        mock_api = Mock(spec=SensorAPI)

        # 온도가 점점 상승하는 3개의 데이터
        mock_api.fetch_reading.side_effect = [
            {"temperature": 70.0, "vibration": 2.0, "pressure": 5.0},
            {"temperature": 80.0, "vibration": 2.0, "pressure": 5.0},
            {"temperature": 95.0, "vibration": 2.0, "pressure": 5.0},
        ]

        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)

        # 3번 수집
        r1 = collector.collect_single("S-01")
        r2 = collector.collect_single("S-02")
        r3 = collector.collect_single("S-03")

        # 온도 상승 확인
        assert r1.temperature == 70.0
        assert r2.temperature == 80.0
        assert r3.temperature == 95.0

        # 3번 호출 확인
        assert mock_api.fetch_reading.call_count == 3

    def test_connection_failure_recovery(self):
        """연결 실패 후 복구되는 시나리오"""
        mock_api = Mock(spec=SensorAPI)

        # 처음 2번 실패, 3번째 성공
        mock_api.fetch_reading.side_effect = [
            ConnectionError("1차 연결 실패"),
            ConnectionError("2차 연결 실패"),
            {"temperature": 75.0, "vibration": 2.0, "pressure": 5.0},
        ]

        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)
        result = collector.collect_with_retry("SENSOR-01", max_retries=3)

        # 최종적으로 성공
        assert result is not None
        assert result.temperature == 75.0

        # 3번 호출됨 (2번 실패 + 1번 성공)
        assert mock_api.fetch_reading.call_count == 3


# ============================================================
# 연습 2 풀이: spec으로 안전한 목 만들기
# ============================================================

class TestExercise2:
    """spec과 create_autospec 활용"""

    def test_spec_prevents_typo(self):
        """spec이 오타를 방지한다"""
        mock_api = Mock(spec=SensorAPI)

        # 존재하는 메서드는 정상 동작
        mock_api.fetch_reading.return_value = {
            "temperature": 70.0, "vibration": 2.0, "pressure": 5.0
        }
        result = mock_api.fetch_reading("SENSOR-01")
        assert result["temperature"] == 70.0

        # 존재하지 않는 메서드 접근 시 AttributeError 발생
        with pytest.raises(AttributeError):
            _ = mock_api.fetch_rading  # 오타: 'e' 누락

        with pytest.raises(AttributeError):
            _ = mock_api.nonexistent_method

    def test_autospec_validates_arguments(self):
        """create_autospec이 인자 개수를 검증한다"""
        mock_api = create_autospec(SensorAPI)

        # 올바른 인자로 호출
        mock_api.fetch_reading("SENSOR-01")  # 성공

        # 잘못된 인자 개수로 호출
        with pytest.raises(TypeError):
            mock_api.fetch_reading()  # 인자 부족

        with pytest.raises(TypeError):
            mock_api.fetch_reading("S-01", "extra")  # 인자 초과


# ============================================================
# 연습 3 풀이: 호출 패턴 검증
# ============================================================

class TestExercise3:
    """assert_has_calls로 호출 패턴을 검증"""

    def test_multiple_sensors_call_order(self):
        """여러 센서 수집 시 API 호출 순서를 검증"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.return_value = {
            "temperature": 70.0, "vibration": 2.0, "pressure": 5.0
        }

        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)
        result = collector.collect_multiple(
            ["PUMP-01", "MOTOR-02", "VALVE-03"]
        )

        # 3번 호출 확인
        assert mock_api.fetch_reading.call_count == 3

        # 호출 순서 검증
        mock_api.fetch_reading.assert_has_calls([
            call("PUMP-01"),
            call("MOTOR-02"),
            call("VALVE-03"),
        ])

        # 저장소에도 3번 저장되었는지 확인
        assert mock_store.save.call_count == 3

        # 모든 센서 수집 성공 확인
        assert result.successful == 3

    def test_invalid_data_not_saved(self):
        """유효하지 않은 데이터는 저장되지 않는다"""
        mock_api = Mock(spec=SensorAPI)
        # 온도 250도: 유효 범위(200도) 초과
        mock_api.fetch_reading.return_value = {
            "temperature": 250.0, "vibration": 2.0, "pressure": 5.0
        }

        mock_store = Mock(spec=DataStore)

        collector = SensorCollector(api=mock_api, store=mock_store)
        reading = collector.collect_single("SENSOR-01")

        # 유효하지 않은 데이터
        assert reading.is_valid is False

        # 저장이 호출되지 않았는지 확인
        mock_store.save.assert_not_called()
