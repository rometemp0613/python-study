"""
conftest.py - 09_markers 디렉토리의 공유 설정

커스텀 마커 등록 및 공유 fixture를 정의한다.
"""

import pytest
from src_equipment_monitor import EquipmentMonitor


# ============================================================
# 공유 Fixture
# ============================================================

@pytest.fixture
def monitor():
    """기본 장비 모니터 인스턴스"""
    return EquipmentMonitor()


@pytest.fixture
def monitor_with_equipment():
    """장비가 등록된 모니터 인스턴스"""
    mon = EquipmentMonitor()
    mon.register_equipment("MOTOR-001", "1번 모터")
    mon.register_equipment("PUMP-001", "1번 펌프")
    mon.register_equipment("CONV-001", "1번 컨베이어")
    return mon


@pytest.fixture
def monitor_with_data():
    """센서 데이터가 포함된 모니터 인스턴스"""
    mon = EquipmentMonitor()

    # 장비 등록
    mon.register_equipment("MOTOR-001", "1번 모터")
    mon.register_equipment("PUMP-001", "1번 펌프")
    mon.register_equipment("CONV-001", "1번 컨베이어")

    # 센서 데이터 업데이트
    mon.update_sensor_data("MOTOR-001", temperature=75.0, vibration=5.0)
    mon.update_sensor_data("PUMP-001", temperature=90.0, vibration=8.5)
    mon.update_sensor_data("CONV-001", temperature=45.0, vibration=2.0)

    return mon
