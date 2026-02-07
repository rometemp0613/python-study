"""
연습 문제 07: Fixture 심화

아래 TODO를 완성하여 fixture 관련 테스트를 작성하세요.
pytest.skip()을 제거하고 코드를 구현하세요.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# 상위 디렉토리의 모듈을 import하기 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_sensor_database import SensorDatabase, SensorReading


# ============================================================
# 연습 1: yield fixture 작성
# ============================================================

@pytest.fixture
def equipment_db():
    """
    TODO: 장비 데이터베이스 yield fixture를 작성하세요.

    요구사항:
    1. SensorDatabase를 생성하고 초기화한다
    2. 초기 데이터로 "MOTOR-001" 센서에 값 50.0을 추가한다
    3. yield로 db를 테스트에 전달한다
    4. 정리 단계에서 clear()와 close()를 호출한다
    """
    pytest.skip("TODO: yield fixture를 구현하세요")


def test_equipment_db_has_initial_data(equipment_db):
    """장비 DB에 초기 데이터가 있는지 확인"""
    pytest.skip("TODO: equipment_db fixture의 초기 데이터를 확인하세요")


def test_equipment_db_can_add_more(equipment_db):
    """장비 DB에 추가 데이터를 넣을 수 있는지 확인"""
    pytest.skip("TODO: equipment_db에 새 데이터를 추가하고 확인하세요")


# ============================================================
# 연습 2: factory fixture 작성
# ============================================================

@pytest.fixture
def create_equipment_reading():
    """
    TODO: 장비 센서 읽기값을 생성하는 팩토리 fixture를 작성하세요.

    요구사항:
    - 기본값: sensor_id="MOTOR-001", value=0.0, status="normal"
    - 내부 함수 _create(**kwargs)를 반환
    - SensorReading 객체를 생성하여 반환
    - timestamp는 자동 생성 (datetime.now())
    """
    pytest.skip("TODO: factory fixture를 구현하세요")


def test_factory_creates_normal_reading(create_equipment_reading):
    """팩토리로 정상 읽기값 생성"""
    pytest.skip("TODO: 기본값으로 생성된 읽기값을 확인하세요")


def test_factory_creates_critical_reading(create_equipment_reading):
    """팩토리로 위험 읽기값 생성"""
    pytest.skip("TODO: status='critical'로 생성된 읽기값을 확인하세요")


# ============================================================
# 연습 3: fixture 의존성 체인 작성
# ============================================================

@pytest.fixture
def base_db():
    """
    TODO: 기본 데이터베이스 fixture를 작성하세요.
    SensorDatabase를 생성, 초기화, yield, 정리(clear+close)
    """
    pytest.skip("TODO: base_db fixture를 구현하세요")


@pytest.fixture
def db_with_temperature_data(base_db):
    """
    TODO: base_db에 온도 센서 데이터를 추가하는 fixture를 작성하세요.

    요구사항:
    - "TEMP-001" 센서에 다음 값 추가: 20.0, 22.0, 24.0, 26.0, 28.0
    - base_db를 반환
    """
    pytest.skip("TODO: 온도 데이터가 채워진 db fixture를 구현하세요")


@pytest.fixture
def db_with_all_data(db_with_temperature_data):
    """
    TODO: db_with_temperature_data에 진동 센서 데이터를 추가하는 fixture를 작성하세요.

    요구사항:
    - "VIBR-002" 센서에 다음 값 추가: 1.0, 2.0, 3.0
    - db_with_temperature_data를 반환
    """
    pytest.skip("TODO: 모든 센서 데이터가 채워진 db fixture를 구현하세요")


def test_chain_temperature_average(db_with_temperature_data):
    """의존성 체인: 온도 데이터의 평균값 확인"""
    pytest.skip("TODO: TEMP-001의 평균이 24.0인지 확인하세요")


def test_chain_all_sensors(db_with_all_data):
    """의존성 체인: 모든 센서가 등록되었는지 확인"""
    pytest.skip("TODO: TEMP-001과 VIBR-002가 모두 있는지 확인하세요")


def test_chain_vibration_count(db_with_all_data):
    """의존성 체인: 진동 센서 데이터 개수 확인"""
    pytest.skip("TODO: VIBR-002의 읽기값이 3개인지 확인하세요")
