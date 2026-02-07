"""
연습 문제 09: Markers - 테스트 마커

아래 TODO를 완성하여 마커 관련 테스트를 작성하세요.
pytest.skip()을 제거하고 코드를 구현하세요.
"""

import sys
import pytest
import os

# 상위 디렉토리의 모듈을 import하기 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_equipment_monitor import EquipmentMonitor


# ============================================================
# 연습 1: skipif 활용
# ============================================================
# Python 버전에 따라 조건부로 건너뛰는 테스트를 작성하세요.

# TODO: Python 3.9 미만에서는 건너뛰는 skipif 마커를 추가하세요.
def test_modern_python_feature():
    """Python 3.9+ 기능 테스트"""
    pytest.skip("TODO: @pytest.mark.skipif를 사용하여 조건부 skip을 구현하세요")


# ============================================================
# 연습 2: 커스텀 마커로 장비별 분류
# ============================================================
# motor, pump, conveyor 마커를 사용하여 장비별 테스트를 작성하세요.

# TODO: @pytest.mark.motor 마커를 추가하세요.
def test_motor_status():
    """모터 상태 확인 테스트"""
    pytest.skip("TODO: motor 마커를 추가하고 모터 등록/상태 확인 테스트를 작성하세요")


# TODO: @pytest.mark.pump 마커를 추가하세요.
def test_pump_status():
    """펌프 상태 확인 테스트"""
    pytest.skip("TODO: pump 마커를 추가하고 펌프 등록/상태 확인 테스트를 작성하세요")


# TODO: @pytest.mark.conveyor 마커를 추가하세요.
def test_conveyor_status():
    """컨베이어 상태 확인 테스트"""
    pytest.skip("TODO: conveyor 마커를 추가하고 컨베이어 등록/상태 확인 테스트를 작성하세요")


# ============================================================
# 연습 3: 마커 조합
# ============================================================
# 여러 마커를 조합하여 테스트를 작성하세요.

# TODO: slow와 sensor 마커를 모두 적용한 테스트를 작성하세요.
def test_slow_sensor_diagnostics():
    """느린 센서 진단 테스트 (slow + sensor)"""
    pytest.skip("TODO: slow + sensor 마커를 추가하고 전체 진단 테스트를 작성하세요")


# TODO: xfail 마커를 사용하여 미구현 기능 테스트를 작성하세요.
def test_predictive_maintenance():
    """예지보전 알고리즘 테스트 (미구현 - xfail)"""
    pytest.skip("TODO: xfail 마커를 추가하고 미구현 기능 테스트를 작성하세요")
