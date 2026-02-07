"""
conftest.py - 07_fixtures 디렉토리의 공유 fixture

이 파일에 정의된 fixture는 같은 디렉토리와 하위 디렉토리의
모든 테스트에서 import 없이 사용할 수 있다.
"""

import pytest
from datetime import datetime, timedelta
from src_sensor_database import SensorDatabase, SensorReading


# ============================================================
# 기본 fixture: 센서 데이터베이스
# ============================================================

@pytest.fixture
def sensor_db():
    """
    각 테스트마다 새로운 센서 데이터베이스를 생성하고 정리하는 fixture.
    scope="function" (기본값) - 매 테스트 함수마다 새로 생성된다.
    """
    db = SensorDatabase()
    db.initialize()
    yield db       # 테스트에 db를 제공
    db.clear()     # 테스트 후 데이터 정리
    db.close()     # 연결 닫기


@pytest.fixture(scope="module")
def shared_sensor_db():
    """
    모듈(파일) 단위로 공유되는 센서 데이터베이스 fixture.
    같은 파일 내의 모든 테스트가 동일한 인스턴스를 공유한다.
    """
    db = SensorDatabase()
    db.initialize()
    yield db
    db.clear()
    db.close()


# ============================================================
# 샘플 데이터 fixture
# ============================================================

@pytest.fixture
def sample_readings():
    """미리 정의된 샘플 센서 읽기값 리스트"""
    base_time = datetime(2024, 1, 15, 10, 0, 0)
    return [
        SensorReading(
            sensor_id="TEMP-001",
            value=72.5,
            timestamp=base_time,
            unit="°C",
            status="normal",
        ),
        SensorReading(
            sensor_id="TEMP-001",
            value=85.0,
            timestamp=base_time + timedelta(minutes=5),
            unit="°C",
            status="warning",
        ),
        SensorReading(
            sensor_id="VIBR-002",
            value=3.2,
            timestamp=base_time + timedelta(minutes=10),
            unit="mm/s",
            status="normal",
        ),
        SensorReading(
            sensor_id="PRESS-003",
            value=150.0,
            timestamp=base_time + timedelta(minutes=15),
            unit="bar",
            status="critical",
        ),
    ]


@pytest.fixture
def populated_db(sensor_db, sample_readings):
    """
    샘플 데이터가 채워진 데이터베이스 fixture.
    sensor_db와 sample_readings fixture에 의존한다 (fixture 체이닝).
    """
    for reading in sample_readings:
        sensor_db.add_reading(
            sensor_id=reading.sensor_id,
            value=reading.value,
            unit=reading.unit,
            status=reading.status,
            timestamp=reading.timestamp,
        )
    return sensor_db


# ============================================================
# 팩토리 fixture
# ============================================================

@pytest.fixture
def make_reading():
    """
    센서 읽기값을 동적으로 생성하는 팩토리 fixture.
    테스트에서 다양한 매개변수로 데이터를 생성할 수 있다.
    """
    _counter = 0

    def _factory(
        sensor_id="TEMP-001",
        value=25.0,
        unit="°C",
        status="normal",
        timestamp=None,
    ):
        nonlocal _counter
        _counter += 1
        return SensorReading(
            sensor_id=sensor_id,
            value=value,
            timestamp=timestamp or datetime(2024, 1, 15, 10, _counter, 0),
            unit=unit,
            status=status,
        )

    return _factory


# ============================================================
# Parametrize된 fixture
# ============================================================

@pytest.fixture(params=[
    ("TEMP-001", "°C"),
    ("VIBR-002", "mm/s"),
    ("PRESS-003", "bar"),
], ids=["온도센서", "진동센서", "압력센서"])
def sensor_config(request):
    """
    여러 센서 설정으로 자동 반복 테스트되는 fixture.
    3가지 센서 타입에 대해 테스트가 각각 실행된다.
    """
    sensor_id, unit = request.param
    return {"sensor_id": sensor_id, "unit": unit}
