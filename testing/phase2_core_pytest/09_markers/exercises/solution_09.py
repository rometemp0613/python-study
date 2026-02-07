"""
연습 문제 09 풀이: Markers - 테스트 마커

각 연습의 풀이를 확인하세요.
"""

import sys
import pytest
import os

# 상위 디렉토리의 모듈을 import하기 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_equipment_monitor import EquipmentMonitor


# ============================================================
# 연습 1 풀이: skipif 활용
# ============================================================

@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="Python 3.9 미만에서는 지원하지 않는 기능"
)
def test_modern_python_feature():
    """Python 3.9+ 기능 테스트 - dict 합병 연산자 사용"""
    # Python 3.9+ 의 dict 합병 연산자 |
    defaults = {"temperature": 0.0, "vibration": 0.0}
    updates = {"temperature": 75.5}
    merged = defaults | updates
    assert merged["temperature"] == 75.5
    assert merged["vibration"] == 0.0


# ============================================================
# 연습 2 풀이: 커스텀 마커로 장비별 분류
# ============================================================

@pytest.mark.motor
def test_motor_status():
    """모터 상태 확인 테스트"""
    monitor = EquipmentMonitor()
    monitor.register_equipment("MOTOR-001", "1번 모터")
    monitor.update_sensor_data("MOTOR-001", temperature=65.0, vibration=3.0)
    status = monitor.get_status("MOTOR-001")
    assert status.status == "running"
    assert status.temperature == 65.0


@pytest.mark.pump
def test_pump_status():
    """펌프 상태 확인 테스트"""
    monitor = EquipmentMonitor()
    monitor.register_equipment("PUMP-001", "1번 펌프")
    monitor.update_sensor_data("PUMP-001", temperature=85.0, vibration=6.0)
    status = monitor.get_status("PUMP-001")
    assert status.status == "warning"  # 온도 80 초과


@pytest.mark.conveyor
def test_conveyor_status():
    """컨베이어 상태 확인 테스트"""
    monitor = EquipmentMonitor()
    monitor.register_equipment("CONV-001", "1번 컨베이어")
    monitor.update_sensor_data("CONV-001", temperature=40.0, vibration=2.0)
    status = monitor.get_status("CONV-001")
    assert status.status == "running"


# ============================================================
# 연습 3 풀이: 마커 조합
# ============================================================

@pytest.mark.slow
@pytest.mark.sensor
def test_slow_sensor_diagnostics():
    """느린 센서 진단 테스트 (slow + sensor)"""
    monitor = EquipmentMonitor()
    monitor.register_equipment("DIAG-001", "진단 대상 장비")
    monitor.update_sensor_data("DIAG-001", temperature=75.0, vibration=5.0)

    result = monitor.run_full_diagnostics("DIAG-001")
    assert result["equipment_id"] == "DIAG-001"
    assert result["temperature_check"] is True
    assert result["vibration_check"] is True
    assert result["overall_health"] == "good"


@pytest.mark.xfail(reason="예지보전 알고리즘 미구현 - 향후 개발 예정")
def test_predictive_maintenance():
    """예지보전 알고리즘 테스트 (미구현 - xfail)"""
    monitor = EquipmentMonitor()
    monitor.register_equipment("PRED-001", "예측 대상 장비")

    # 아직 predict_failure 메서드가 구현되지 않음
    prediction = monitor.predict_failure("PRED-001")  # AttributeError 발생
    assert prediction["probability"] > 0.5
