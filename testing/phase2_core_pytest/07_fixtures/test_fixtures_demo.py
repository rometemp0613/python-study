"""
Fixture 심화 데모 테스트

다양한 fixture 패턴을 실제로 시연한다:
1. 스코프별 동작 확인
2. yield fixture를 통한 정리(teardown)
3. factory fixture로 동적 데이터 생성
4. parametrized fixture로 여러 시나리오 자동 테스트
5. autouse fixture
6. fixture 의존성 체인
"""

import pytest
from datetime import datetime, timedelta
from src_sensor_database import SensorDatabase, SensorReading


# ============================================================
# 1. 기본 Fixture 사용 (conftest.py에서 가져옴)
# ============================================================

class TestBasicFixtures:
    """conftest.py에 정의된 기본 fixture 사용 예제"""

    def test_sensor_db_is_initialized(self, sensor_db):
        """sensor_db fixture가 초기화된 상태로 제공되는지 확인"""
        assert sensor_db.is_initialized

    def test_sensor_db_is_empty(self, sensor_db):
        """각 테스트마다 빈 DB가 제공되는지 확인"""
        assert sensor_db.get_all_sensor_ids() == []

    def test_add_and_retrieve(self, sensor_db):
        """데이터 추가 후 조회가 되는지 확인"""
        sensor_db.add_reading("TEMP-001", 25.0, unit="°C")
        readings = sensor_db.get_readings("TEMP-001")
        assert len(readings) == 1
        assert readings[0].value == 25.0


# ============================================================
# 2. Fixture 스코프 시연
# ============================================================

# 스코프별 fixture를 로컬에 정의하여 동작을 명확히 보여줌
_function_call_count = 0
_module_call_count = 0


@pytest.fixture
def function_scoped_counter():
    """function 스코프: 매 테스트마다 새로 생성"""
    global _function_call_count
    _function_call_count += 1
    return _function_call_count


@pytest.fixture(scope="module")
def module_scoped_db():
    """module 스코프: 이 파일 내 모든 테스트가 공유"""
    db = SensorDatabase()
    db.initialize()
    yield db
    db.close()


class TestScopeDemo:
    """fixture 스코프에 따른 동작 차이를 시연"""

    def test_function_scope_a(self, function_scoped_counter):
        """function 스코프 fixture는 매번 새 값을 제공"""
        assert isinstance(function_scoped_counter, int)

    def test_function_scope_b(self, function_scoped_counter):
        """function 스코프 fixture는 매번 새 값을 제공"""
        assert isinstance(function_scoped_counter, int)

    def test_module_scope_a(self, module_scoped_db):
        """module 스코프 fixture는 같은 인스턴스를 공유"""
        module_scoped_db.add_reading("SCOPE-TEST", 1.0)
        assert module_scoped_db.count_readings("SCOPE-TEST") >= 1

    def test_module_scope_b(self, module_scoped_db):
        """module 스코프: 이전 테스트의 데이터가 남아있음"""
        # module 스코프이므로 test_module_scope_a에서 추가한 데이터가 남아있다
        count = module_scoped_db.count_readings("SCOPE-TEST")
        assert count >= 1


# ============================================================
# 3. Yield Fixture (설정과 정리)
# ============================================================

@pytest.fixture
def tracked_db():
    """
    설정과 정리를 추적하는 yield fixture.
    yield 이전: 설정 코드
    yield: 테스트에 값 전달
    yield 이후: 정리 코드 (테스트 성공/실패 무관하게 실행)
    """
    # === 설정 (Setup) ===
    db = SensorDatabase()
    db.initialize()
    db.add_reading("SETUP-SENSOR", 100.0)

    yield db

    # === 정리 (Teardown) ===
    db.clear()
    db.close()


def test_yield_fixture_cleanup(tracked_db):
    """yield fixture가 설정 데이터를 포함하는지 확인"""
    # 설정 단계에서 추가한 데이터 확인
    assert tracked_db.count_readings("SETUP-SENSOR") == 1

    # 추가 데이터 입력
    tracked_db.add_reading("TEST-SENSOR", 50.0)
    assert tracked_db.count_readings("TEST-SENSOR") == 1
    # 테스트 종료 후 정리 코드가 실행됨


def test_yield_fixture_fresh_state(tracked_db):
    """각 테스트마다 새로운 tracked_db가 제공되는지 확인"""
    # 이전 테스트의 "TEST-SENSOR" 데이터가 없어야 함
    assert tracked_db.count_readings("TEST-SENSOR") == 0
    # 설정 단계의 데이터는 있어야 함
    assert tracked_db.count_readings("SETUP-SENSOR") == 1


# ============================================================
# 4. Factory Fixture
# ============================================================

class TestFactoryFixture:
    """팩토리 fixture를 사용한 동적 데이터 생성 시연"""

    def test_factory_creates_default(self, make_reading):
        """기본값으로 센서 읽기값 생성"""
        reading = make_reading()
        assert reading.sensor_id == "TEMP-001"
        assert reading.value == 25.0
        assert reading.status == "normal"

    def test_factory_creates_custom(self, make_reading):
        """사용자 지정 값으로 센서 읽기값 생성"""
        reading = make_reading(
            sensor_id="VIBR-002",
            value=8.5,
            unit="mm/s",
            status="warning"
        )
        assert reading.sensor_id == "VIBR-002"
        assert reading.value == 8.5
        assert reading.status == "warning"

    def test_factory_multiple_readings(self, make_reading, sensor_db):
        """팩토리로 여러 데이터를 생성하여 DB에 추가"""
        # 정상 데이터 5개 생성
        for i in range(5):
            r = make_reading(value=20.0 + i)
            sensor_db.add_reading(r.sensor_id, r.value, r.unit, r.status)

        assert sensor_db.count_readings("TEMP-001") == 5
        avg = sensor_db.get_average("TEMP-001")
        assert avg == 22.0  # (20+21+22+23+24) / 5

    def test_factory_mixed_statuses(self, make_reading):
        """다양한 상태의 데이터를 생성하여 분류 테스트"""
        readings = [
            make_reading(value=25.0, status="normal"),
            make_reading(value=80.0, status="warning"),
            make_reading(value=95.0, status="critical"),
        ]

        critical_count = sum(1 for r in readings if r.is_critical())
        warning_count = sum(1 for r in readings if r.is_warning())

        assert critical_count == 1
        assert warning_count == 1


# ============================================================
# 5. Parametrized Fixture (conftest.py의 sensor_config 사용)
# ============================================================

class TestParametrizedFixture:
    """parametrize된 fixture로 여러 센서 타입 자동 테스트"""

    def test_sensor_id_format(self, sensor_config):
        """센서 ID 형식이 올바른지 확인 (3가지 센서에 대해 각각 실행)"""
        sensor_id = sensor_config["sensor_id"]
        parts = sensor_id.split("-")
        assert len(parts) == 2
        assert parts[1].isdigit()

    def test_sensor_has_unit(self, sensor_config):
        """각 센서에 단위가 지정되어 있는지 확인"""
        assert len(sensor_config["unit"]) > 0

    def test_add_reading_with_config(self, sensor_db, sensor_config):
        """센서 설정으로 데이터를 추가하고 조회"""
        sensor_db.add_reading(
            sensor_id=sensor_config["sensor_id"],
            value=50.0,
            unit=sensor_config["unit"],
        )
        readings = sensor_db.get_readings(sensor_config["sensor_id"])
        assert len(readings) == 1
        assert readings[0].unit == sensor_config["unit"]


# ============================================================
# 6. Autouse Fixture
# ============================================================

# 테스트 실행 시간을 자동 기록하는 autouse fixture 예제
_test_timestamps = []


@pytest.fixture(autouse=True)
def record_test_time():
    """
    autouse=True: 모든 테스트에 자동 적용.
    명시적으로 요청하지 않아도 매 테스트 전후에 실행된다.
    """
    start = datetime.now()
    yield
    end = datetime.now()
    _test_timestamps.append((start, end))


def test_autouse_runs_automatically():
    """autouse fixture는 인자로 요청하지 않아도 실행된다"""
    # record_test_time이 자동으로 실행되어 타임스탬프가 기록됨
    assert len(_test_timestamps) > 0


# ============================================================
# 7. Fixture 의존성 체인 (conftest.py의 populated_db 사용)
# ============================================================

class TestFixtureDependencyChain:
    """fixture 의존성 체인 시연: sensor_db → populated_db"""

    def test_populated_db_has_data(self, populated_db):
        """populated_db는 sample_readings의 데이터를 포함"""
        all_ids = populated_db.get_all_sensor_ids()
        assert "TEMP-001" in all_ids
        assert "VIBR-002" in all_ids
        assert "PRESS-003" in all_ids

    def test_populated_db_reading_count(self, populated_db):
        """각 센서의 읽기값 개수 확인"""
        # TEMP-001은 2개 (normal + warning)
        assert populated_db.count_readings("TEMP-001") == 2
        # VIBR-002는 1개
        assert populated_db.count_readings("VIBR-002") == 1

    def test_populated_db_average(self, populated_db):
        """populated_db의 평균값 계산"""
        avg = populated_db.get_average("TEMP-001")
        assert avg == pytest.approx(78.75)  # (72.5 + 85.0) / 2

    def test_populated_db_status_filter(self, populated_db):
        """상태별 필터링이 올바르게 동작하는지 확인"""
        criticals = populated_db.get_readings_by_status("critical")
        assert len(criticals) == 1
        assert criticals[0].sensor_id == "PRESS-003"

    def test_populated_db_min_max(self, populated_db):
        """최솟값/최댓값 조회"""
        result = populated_db.get_min_max("TEMP-001")
        assert result is not None
        min_val, max_val = result
        assert min_val == 72.5
        assert max_val == 85.0
