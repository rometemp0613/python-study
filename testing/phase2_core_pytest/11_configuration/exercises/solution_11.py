"""
연습 문제 11 풀이: pytest 설정 (Configuration)

각 연습의 풀이를 확인하세요.
"""

import pytest
import sys
import os

# conftest.py의 fixture를 사용하기 위해 상위 디렉토리를 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ============================================================
# 연습 1 풀이: 설정 검증 테스트
# ============================================================

def test_project_config_has_required_keys(project_config):
    """project_config fixture에 필수 키가 있는지 확인"""
    # 1. 최상위 필수 키 확인
    assert "project_name" in project_config
    assert "version" in project_config
    assert "environment" in project_config

    # 2. features 딕셔너리에 sensor_monitoring 키 확인
    assert "features" in project_config
    assert "sensor_monitoring" in project_config["features"]

    # 3. thresholds 딕셔너리에 temperature와 vibration 키 확인
    assert "thresholds" in project_config
    assert "temperature" in project_config["thresholds"]
    assert "vibration" in project_config["thresholds"]


def test_environment_meets_requirements(test_environment):
    """테스트 환경이 최소 요구사항을 충족하는지 확인"""
    # 1. Python 버전 3.9 이상 확인
    major, minor = test_environment["python_version"].split(".")
    assert int(major) >= 3
    assert int(minor) >= 9

    # 2. pytest 버전 문자열이 비어있지 않은지 확인
    assert len(test_environment["pytest_version"]) > 0


# ============================================================
# 연습 2 풀이: 마커 활용 테스트
# ============================================================

@pytest.mark.smoke
def test_basic_arithmetic_smoke():
    """스모크 테스트: 기본 산술 연산이 작동하는지 확인"""
    assert 2 + 2 == 4
    assert 10 - 3 == 7
    assert 4 * 5 == 20
    assert 10 / 2 == 5.0


@pytest.mark.equipment(name="pump")
def test_pump_equipment():
    """equipment 마커를 사용한 펌프 테스트"""
    # 간단한 펌프 상태 시뮬레이션
    pump_status = {
        "id": "PUMP-001",
        "pressure": 120.0,
        "flow_rate": 50.0,
        "status": "running",
    }
    assert pump_status["status"] == "running"
    assert pump_status["pressure"] > 0


# ============================================================
# 연습 3 풀이: 설정 기반 조건부 테스트
# ============================================================

def test_cloud_sync_disabled_in_test(project_config):
    """테스트 환경에서 cloud_sync가 비활성화되어 있는지 확인"""
    # 1. cloud_sync가 False인지 확인
    assert project_config["features"]["cloud_sync"] is False

    # 2. 환경이 "test"인지 확인
    assert project_config["environment"] == "test"
