"""
conftest.py - 11_configuration 디렉토리의 프로그래밍 설정 예제

pytest hook 함수를 사용하여 설정을 프로그래밍 방식으로 구성한다.
이 파일에서 할 수 있는 것들:
- 커스텀 마커 동적 등록
- 테스트 수집 후 수정
- 커스텀 fixture 정의
- 보고서 커스터마이징
"""

import pytest


# ============================================================
# 1. pytest_configure: 설정 단계 hook
# ============================================================

def pytest_configure(config):
    """
    pytest 설정 단계에서 호출되는 hook.
    프로그래밍 방식으로 마커를 등록하거나 설정을 추가할 수 있다.
    """
    # 프로그래밍 방식으로 마커 등록
    config.addinivalue_line(
        "markers",
        "equipment(name): 특정 장비 관련 테스트를 표시하는 마커"
    )
    config.addinivalue_line(
        "markers",
        "priority(level): 테스트 우선순위를 지정하는 마커 (high, medium, low)"
    )


# ============================================================
# 2. pytest_collection_modifyitems: 테스트 수집 후 수정
# ============================================================

def pytest_collection_modifyitems(config, items):
    """
    테스트 수집 후 호출되는 hook.
    수집된 테스트를 수정하거나 순서를 변경할 수 있다.
    """
    for item in items:
        # "slow" 문자열이 테스트 이름에 포함되면 자동으로 slow 마커 부여
        if "slow" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)


# ============================================================
# 3. 공유 Fixture
# ============================================================

@pytest.fixture
def project_config():
    """예지보전 프로젝트의 기본 설정을 제공하는 fixture"""
    return {
        "project_name": "예지보전 모니터링 시스템",
        "version": "2.0.0",
        "environment": "test",
        "features": {
            "sensor_monitoring": True,
            "anomaly_detection": True,
            "predictive_maintenance": True,
            "cloud_sync": False,  # 테스트 환경에서는 비활성
        },
        "thresholds": {
            "temperature": {"warning": 80, "critical": 100},
            "vibration": {"warning": 7, "critical": 10},
        },
    }


@pytest.fixture
def test_environment():
    """테스트 환경 정보를 제공하는 fixture"""
    import sys
    import platform

    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "platform": platform.system(),
        "pytest_version": pytest.__version__,
    }
