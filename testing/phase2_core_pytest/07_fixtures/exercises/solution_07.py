"""
연습 문제 07 풀이: Fixture 심화

각 연습의 풀이를 확인하세요.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# 상위 디렉토리의 모듈을 import하기 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_sensor_database import SensorDatabase, SensorReading


# ============================================================
# 연습 1 풀이: yield fixture 작성
# ============================================================

@pytest.fixture
def equipment_db():
    """
    장비 데이터베이스 yield fixture.
    설정 단계에서 DB를 초기화하고 초기 데이터를 추가한다.
    정리 단계에서 데이터를 삭제하고 연결을 닫는다.
    """
    # 설정
    db = SensorDatabase()
    db.initialize()
    db.add_reading("MOTOR-001", 50.0)

    yield db  # 테스트에 전달

    # 정리
    db.clear()
    db.close()


def test_equipment_db_has_initial_data(equipment_db):
    """장비 DB에 초기 데이터가 있는지 확인"""
    readings = equipment_db.get_readings("MOTOR-001")
    assert len(readings) == 1
    assert readings[0].value == 50.0


def test_equipment_db_can_add_more(equipment_db):
    """장비 DB에 추가 데이터를 넣을 수 있는지 확인"""
    equipment_db.add_reading("MOTOR-001", 55.0)
    readings = equipment_db.get_readings("MOTOR-001")
    assert len(readings) == 2  # 초기 1개 + 추가 1개


# ============================================================
# 연습 2 풀이: factory fixture 작성
# ============================================================

@pytest.fixture
def create_equipment_reading():
    """
    장비 센서 읽기값을 생성하는 팩토리 fixture.
    다양한 매개변수로 SensorReading을 동적 생성한다.
    """
    def _create(sensor_id="MOTOR-001", value=0.0, status="normal",
                unit="", timestamp=None):
        return SensorReading(
            sensor_id=sensor_id,
            value=value,
            timestamp=timestamp or datetime.now(),
            unit=unit,
            status=status,
        )
    return _create


def test_factory_creates_normal_reading(create_equipment_reading):
    """팩토리로 정상 읽기값 생성"""
    reading = create_equipment_reading()
    assert reading.sensor_id == "MOTOR-001"
    assert reading.value == 0.0
    assert reading.status == "normal"
    assert not reading.is_critical()


def test_factory_creates_critical_reading(create_equipment_reading):
    """팩토리로 위험 읽기값 생성"""
    reading = create_equipment_reading(
        sensor_id="TEMP-001",
        value=120.0,
        status="critical",
    )
    assert reading.sensor_id == "TEMP-001"
    assert reading.value == 120.0
    assert reading.is_critical()


# ============================================================
# 연습 3 풀이: fixture 의존성 체인 작성
# ============================================================

@pytest.fixture
def base_db():
    """기본 데이터베이스 fixture: 생성, 초기화, 정리"""
    db = SensorDatabase()
    db.initialize()
    yield db
    db.clear()
    db.close()


@pytest.fixture
def db_with_temperature_data(base_db):
    """base_db에 온도 센서 데이터를 추가하는 fixture"""
    for value in [20.0, 22.0, 24.0, 26.0, 28.0]:
        base_db.add_reading("TEMP-001", value, unit="°C")
    return base_db


@pytest.fixture
def db_with_all_data(db_with_temperature_data):
    """db_with_temperature_data에 진동 센서 데이터를 추가하는 fixture"""
    for value in [1.0, 2.0, 3.0]:
        db_with_temperature_data.add_reading("VIBR-002", value, unit="mm/s")
    return db_with_temperature_data


def test_chain_temperature_average(db_with_temperature_data):
    """의존성 체인: 온도 데이터의 평균값 확인"""
    avg = db_with_temperature_data.get_average("TEMP-001")
    assert avg == pytest.approx(24.0)  # (20+22+24+26+28) / 5


def test_chain_all_sensors(db_with_all_data):
    """의존성 체인: 모든 센서가 등록되었는지 확인"""
    all_ids = db_with_all_data.get_all_sensor_ids()
    assert "TEMP-001" in all_ids
    assert "VIBR-002" in all_ids


def test_chain_vibration_count(db_with_all_data):
    """의존성 체인: 진동 센서 데이터 개수 확인"""
    count = db_with_all_data.count_readings("VIBR-002")
    assert count == 3
