"""
연습 문제 11: pytest 설정 (Configuration)

아래 TODO를 완성하여 설정 관련 테스트를 작성하세요.
pytest.skip()을 제거하고 코드를 구현하세요.
"""

import pytest
import sys


# ============================================================
# 연습 1: 설정 검증 테스트
# ============================================================

def test_project_config_has_required_keys(project_config):
    """
    TODO: project_config fixture에 필수 키가 있는지 확인하세요.

    요구사항:
    1. project_config에 "project_name", "version", "environment" 키가 있는지 확인
    2. "features" 딕셔너리에 "sensor_monitoring" 키가 있는지 확인
    3. "thresholds" 딕셔너리에 "temperature"와 "vibration" 키가 있는지 확인
    """
    pytest.skip("TODO: project_config의 필수 키를 검증하세요")


def test_environment_meets_requirements(test_environment):
    """
    TODO: 테스트 환경이 최소 요구사항을 충족하는지 확인하세요.

    요구사항:
    1. Python 버전이 3.9 이상인지 확인
    2. pytest 버전 문자열이 비어있지 않은지 확인
    """
    pytest.skip("TODO: 환경 요구사항을 검증하세요")


# ============================================================
# 연습 2: 마커 활용 테스트
# ============================================================

# TODO: @pytest.mark.smoke 마커를 추가하세요.
def test_basic_arithmetic_smoke():
    """
    TODO: 스모크 테스트를 작성하세요.
    시스템의 가장 기본적인 동작(산술 연산)이 작동하는지 확인합니다.
    """
    pytest.skip("TODO: smoke 마커를 추가하고 기본 산술 테스트를 작성하세요")


# TODO: @pytest.mark.equipment(name="pump") 마커를 추가하세요.
def test_pump_equipment():
    """
    TODO: equipment 마커를 사용한 펌프 테스트를 작성하세요.
    conftest.py에서 프로그래밍 방식으로 등록된 마커입니다.
    """
    pytest.skip("TODO: equipment 마커를 추가하고 펌프 테스트를 작성하세요")


# ============================================================
# 연습 3: 설정 기반 조건부 테스트
# ============================================================

def test_cloud_sync_disabled_in_test(project_config):
    """
    TODO: 테스트 환경에서 cloud_sync가 비활성화되어 있는지 확인하세요.

    요구사항:
    1. project_config의 features에서 cloud_sync 값을 확인
    2. 테스트 환경에서는 False여야 함
    3. environment 키가 "test"인지도 확인
    """
    pytest.skip("TODO: 테스트 환경 설정을 검증하세요")
