"""
unittest.mock 종합 데모

Mock, MagicMock, return_value, side_effect, spec,
assertion 메서드 등을 활용한 테스트 예제입니다.
"""

import pytest
from unittest.mock import (
    Mock, MagicMock, create_autospec,
    PropertyMock, sentinel, call, patch,
)
from src_sensor_collector import (
    SensorAPI, SensorCollector, DataStore,
    SensorReading, CollectionResult,
)


# ============================================================
# 1. Mock vs MagicMock
# ============================================================

class TestMockVsMagicMock:
    """Mock과 MagicMock의 차이를 보여주는 테스트"""

    def test_mock_creates_attributes_dynamically(self):
        """Mock은 속성과 메서드를 동적으로 생성한다"""
        mock = Mock()

        # 존재하지 않는 속성/메서드도 에러 없이 접근 가능
        assert mock.any_attribute is not None
        assert mock.any_method() is not None

        # 중첩 속성도 자동 생성
        assert mock.a.b.c is not None

    def test_magicmock_supports_magic_methods(self):
        """MagicMock은 매직 메서드를 지원한다"""
        magic = MagicMock()

        # __len__, __bool__, __str__ 등이 자동 지원됨
        assert len(magic) == 0
        assert bool(magic) is True
        assert str(magic) is not None

        # __getitem__도 지원
        result = magic[0]
        assert result is not None

    def test_magicmock_as_context_manager(self):
        """MagicMock은 컨텍스트 매니저로 사용 가능하다"""
        magic = MagicMock()

        # __enter__와 __exit__이 자동 지원됨
        with magic as m:
            m.do_something()

        magic.__enter__.assert_called_once()
        magic.__exit__.assert_called_once()


# ============================================================
# 2. return_value 활용
# ============================================================

class TestReturnValue:
    """return_value를 활용한 테스트"""

    def test_simple_return_value(self):
        """간단한 반환값 설정"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.return_value = {
            "temperature": 75.5,
            "vibration": 3.2,
            "pressure": 6.1
        }

        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)
        reading = collector.collect_single("SENSOR-01")

        assert reading.temperature == 75.5
        assert reading.vibration == 3.2

    def test_chained_return_value(self):
        """체인된 호출의 반환값 설정"""
        mock = Mock()
        # get_client().connect().fetch()의 반환값 설정
        mock.get_client.return_value.connect.return_value.fetch.return_value = {
            "data": [1, 2, 3]
        }

        result = mock.get_client().connect().fetch()
        assert result["data"] == [1, 2, 3]


# ============================================================
# 3. side_effect 활용
# ============================================================

class TestSideEffect:
    """side_effect의 다양한 사용법"""

    def test_sequential_return_values(self):
        """side_effect 리스트로 순차 반환"""
        mock_api = Mock(spec=SensorAPI)

        # 센서 데이터가 점점 상승하는 시나리오
        mock_api.fetch_reading.side_effect = [
            {"temperature": 70.0, "vibration": 2.0, "pressure": 5.0},
            {"temperature": 75.0, "vibration": 2.5, "pressure": 5.5},
            {"temperature": 82.0, "vibration": 3.0, "pressure": 6.0},
        ]

        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)

        # 순차적으로 다른 값을 반환
        r1 = collector.collect_single("S-01")
        r2 = collector.collect_single("S-02")
        r3 = collector.collect_single("S-03")

        assert r1.temperature == 70.0
        assert r2.temperature == 75.0
        assert r3.temperature == 82.0

    def test_side_effect_exception(self):
        """side_effect로 예외 발생 시뮬레이션"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.side_effect = ConnectionError(
            "센서 게이트웨이 연결 실패"
        )

        mock_store = Mock(spec=DataStore)

        collector = SensorCollector(api=mock_api, store=mock_store)

        with pytest.raises(ConnectionError, match="센서 게이트웨이"):
            collector.collect_single("SENSOR-01")

    def test_side_effect_mixed(self):
        """성공과 실패를 섞은 시나리오"""
        mock_api = Mock(spec=SensorAPI)

        # 첫 번째: 성공, 두 번째: 실패, 세 번째: 성공
        mock_api.fetch_reading.side_effect = [
            {"temperature": 70.0, "vibration": 2.0, "pressure": 5.0},
            ConnectionError("일시적 연결 오류"),
            {"temperature": 72.0, "vibration": 2.1, "pressure": 5.1},
        ]

        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)

        result = collector.collect_multiple(["S-01", "S-02", "S-03"])

        assert result.successful == 2
        assert result.failed == 1
        assert "일시적 연결 오류" in result.errors[0]

    def test_side_effect_function(self):
        """side_effect로 대체 함수 사용"""
        mock_api = Mock(spec=SensorAPI)

        # 센서 ID에 따라 다른 데이터를 반환하는 함수
        def fake_fetch(sensor_id):
            sensor_data = {
                "TEMP-01": {"temperature": 25.0, "vibration": 1.0, "pressure": 3.0},
                "TEMP-02": {"temperature": 85.0, "vibration": 6.0, "pressure": 7.0},
            }
            if sensor_id not in sensor_data:
                raise ValueError(f"알 수 없는 센서: {sensor_id}")
            return sensor_data[sensor_id]

        mock_api.fetch_reading.side_effect = fake_fetch
        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)

        r1 = collector.collect_single("TEMP-01")
        assert r1.temperature == 25.0

        r2 = collector.collect_single("TEMP-02")
        assert r2.temperature == 85.0

    def test_retry_with_side_effect(self):
        """재시도 로직 테스트: 처음 2번 실패 후 성공"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.side_effect = [
            ConnectionError("1차 실패"),
            ConnectionError("2차 실패"),
            {"temperature": 75.0, "vibration": 2.0, "pressure": 5.0},
        ]

        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)
        result = collector.collect_with_retry("SENSOR-01", max_retries=3)

        assert result is not None
        assert result.temperature == 75.0
        assert mock_api.fetch_reading.call_count == 3

    def test_all_retries_fail(self):
        """모든 재시도가 실패하면 None을 반환한다"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.side_effect = ConnectionError("연결 불가")

        mock_store = Mock(spec=DataStore)

        collector = SensorCollector(api=mock_api, store=mock_store)
        result = collector.collect_with_retry("SENSOR-01", max_retries=3)

        assert result is None
        assert mock_api.fetch_reading.call_count == 3


# ============================================================
# 4. Assertion 메서드
# ============================================================

class TestAssertionMethods:
    """다양한 assertion 메서드 사용법"""

    def test_assert_called_once(self):
        """정확히 1번 호출되었는지 검증"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.return_value = {
            "temperature": 70.0, "vibration": 2.0, "pressure": 5.0
        }
        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)
        collector.collect_single("SENSOR-01")

        # API가 정확히 1번 호출되었는지 검증
        mock_api.fetch_reading.assert_called_once()
        mock_api.fetch_reading.assert_called_once_with("SENSOR-01")

    def test_assert_called_with_specific_args(self):
        """특정 인자로 호출되었는지 검증"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.get_sensor_status.return_value = "active"

        collector = SensorCollector(api=mock_api, store=Mock(spec=DataStore))
        collector.check_sensor_health("SENSOR-42")

        mock_api.get_sensor_status.assert_called_with("SENSOR-42")

    def test_assert_not_called(self):
        """유효하지 않은 데이터는 저장하지 않는다"""
        mock_api = Mock(spec=SensorAPI)
        # 범위 밖의 데이터 (온도 300도 → 유효하지 않음)
        mock_api.fetch_reading.return_value = {
            "temperature": 300.0, "vibration": 2.0, "pressure": 5.0
        }

        mock_store = Mock(spec=DataStore)

        collector = SensorCollector(api=mock_api, store=mock_store)
        reading = collector.collect_single("SENSOR-01")

        # 유효하지 않은 데이터는 저장하지 않아야 함
        assert reading.is_valid is False
        mock_store.save.assert_not_called()

    def test_call_count_and_call_args_list(self):
        """여러 센서 수집 시 호출 횟수와 인자 목록 검증"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.return_value = {
            "temperature": 70.0, "vibration": 2.0, "pressure": 5.0
        }
        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)
        collector.collect_multiple(["S-01", "S-02", "S-03"])

        # 3번 호출되었는지 확인
        assert mock_api.fetch_reading.call_count == 3

        # 각 호출의 인자 확인
        expected_calls = [
            call("S-01"),
            call("S-02"),
            call("S-03"),
        ]
        mock_api.fetch_reading.assert_has_calls(expected_calls)

    def test_assert_any_call(self):
        """특정 인자로의 호출이 있었는지 확인"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.return_value = {
            "temperature": 70.0, "vibration": 2.0, "pressure": 5.0
        }
        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)
        collector.collect_multiple(["S-01", "S-02", "S-03"])

        # "S-02"로 호출된 적이 있는지 확인
        mock_api.fetch_reading.assert_any_call("S-02")


# ============================================================
# 5. spec과 autospec
# ============================================================

class TestSpecAndAutospec:
    """spec과 autospec으로 안전한 목 객체 만들기"""

    def test_spec_catches_typos(self):
        """spec은 오타를 감지한다"""
        mock_api = Mock(spec=SensorAPI)

        # 존재하는 메서드는 정상 동작
        mock_api.fetch_reading.return_value = {
            "temperature": 70.0, "vibration": 2.0, "pressure": 5.0
        }

        # 존재하지 않는 메서드는 AttributeError 발생
        with pytest.raises(AttributeError):
            mock_api.fetch_rading  # 오타! 'e' 누락

    def test_create_autospec_validates_signatures(self):
        """create_autospec은 메서드 시그니처까지 검증한다"""
        mock_api = create_autospec(SensorAPI)

        # 올바른 시그니처로 호출
        mock_api.fetch_reading("SENSOR-01")

        # 잘못된 인자 개수로 호출하면 TypeError 발생
        with pytest.raises(TypeError):
            mock_api.fetch_reading("SENSOR-01", "extra_arg")

    def test_spec_with_instance(self):
        """인스턴스를 spec으로 사용할 수도 있다"""
        # 참고: SensorAPI는 __init__에서 예외를 발생시키지 않으므로
        # 여기서는 클래스를 spec으로 사용
        mock_api = Mock(spec=SensorAPI)

        # spec에 정의된 메서드만 사용 가능
        assert hasattr(mock_api, 'fetch_reading')
        assert hasattr(mock_api, 'connect')
        assert not hasattr(mock_api, 'nonexistent_method')


# ============================================================
# 6. PropertyMock
# ============================================================

class TestPropertyMock:
    """PropertyMock을 활용한 프로퍼티 테스트"""

    def test_property_mock_basic(self):
        """PropertyMock으로 프로퍼티 값을 설정한다"""
        mock_api = Mock(spec=SensorAPI)

        # connection_status 프로퍼티를 목킹
        type(mock_api).connection_status = PropertyMock(
            return_value="connected"
        )

        assert mock_api.connection_status == "connected"

    def test_property_mock_side_effect(self):
        """PropertyMock에 side_effect로 변화하는 값 설정"""
        mock_api = Mock(spec=SensorAPI)

        # 연결 상태가 변화하는 시나리오
        type(mock_api).connection_status = PropertyMock(
            side_effect=["connecting", "connected", "disconnected"]
        )

        assert mock_api.connection_status == "connecting"
        assert mock_api.connection_status == "connected"
        assert mock_api.connection_status == "disconnected"


# ============================================================
# 7. sentinel
# ============================================================

class TestSentinel:
    """sentinel을 활용한 고유 객체 테스트"""

    def test_sentinel_as_unique_marker(self):
        """sentinel로 고유한 테스트 객체를 생성한다"""
        mock_store = Mock(spec=DataStore)
        mock_store.get_latest.return_value = sentinel.latest_reading

        # 반환값이 정확히 같은 sentinel 객체인지 확인
        result = mock_store.get_latest("SENSOR-01")
        assert result is sentinel.latest_reading

    def test_sentinel_in_data_flow(self):
        """sentinel로 데이터가 올바르게 전달되는지 검증"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.return_value = {
            "temperature": 70.0,
            "vibration": 2.0,
            "pressure": 5.0
        }

        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)
        reading = collector.collect_single("SENSOR-01")

        # save가 SensorReading 객체로 호출되었는지 확인
        mock_store.save.assert_called_once()
        saved_reading = mock_store.save.call_args[0][0]
        assert isinstance(saved_reading, SensorReading)
        assert saved_reading.sensor_id == "SENSOR-01"


# ============================================================
# 8. 종합 예제: 수집 결과 검증
# ============================================================

class TestCollectionResult:
    """수집 결과의 다양한 시나리오 테스트"""

    def test_full_collection_success(self):
        """모든 센서 수집 성공 시나리오"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.return_value = {
            "temperature": 70.0, "vibration": 2.0, "pressure": 5.0
        }
        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)
        result = collector.collect_multiple(["S-01", "S-02"])

        assert result.total_sensors == 2
        assert result.successful == 2
        assert result.failed == 0
        assert result.success_rate == 100.0

    def test_partial_collection_failure(self):
        """일부 센서 수집 실패 시나리오"""
        mock_api = Mock(spec=SensorAPI)
        mock_api.fetch_reading.side_effect = [
            {"temperature": 70.0, "vibration": 2.0, "pressure": 5.0},
            ConnectionError("S-02 연결 실패"),
            {"temperature": 72.0, "vibration": 2.1, "pressure": 5.1},
        ]
        mock_store = Mock(spec=DataStore)
        mock_store.save.return_value = True

        collector = SensorCollector(api=mock_api, store=mock_store)
        result = collector.collect_multiple(["S-01", "S-02", "S-03"])

        assert result.successful == 2
        assert result.failed == 1
        assert pytest.approx(result.success_rate, abs=0.1) == 66.7
        assert len(result.errors) == 1
