"""
pytest 설정 데모 테스트

설정이 올바르게 적용되는지 확인하는 테스트:
1. conftest.py에서 정의한 fixture 사용
2. 마커 등록 확인
3. 설정 효과 시연
"""

import pytest
import sys


# ============================================================
# 1. 기본 설정 확인 테스트
# ============================================================

class TestBasicConfiguration:
    """기본 설정이 올바르게 적용되는지 확인"""

    def test_project_config_available(self, project_config):
        """conftest.py의 project_config fixture가 사용 가능한지 확인"""
        assert project_config["project_name"] == "예지보전 모니터링 시스템"
        assert project_config["version"] == "2.0.0"
        assert project_config["environment"] == "test"

    def test_features_in_config(self, project_config):
        """프로젝트 기능 설정 확인"""
        features = project_config["features"]
        assert features["sensor_monitoring"] is True
        assert features["anomaly_detection"] is True
        assert features["cloud_sync"] is False  # 테스트 환경에서 비활성

    def test_thresholds_in_config(self, project_config):
        """임계값 설정 확인"""
        thresholds = project_config["thresholds"]
        assert thresholds["temperature"]["warning"] == 80
        assert thresholds["temperature"]["critical"] == 100
        assert thresholds["vibration"]["warning"] == 7


# ============================================================
# 2. 환경 정보 테스트
# ============================================================

class TestEnvironment:
    """테스트 환경 정보 확인"""

    def test_environment_fixture(self, test_environment):
        """test_environment fixture에서 환경 정보 확인"""
        assert "python_version" in test_environment
        assert "platform" in test_environment
        assert "pytest_version" in test_environment

    def test_python_version_sufficient(self, test_environment):
        """Python 버전이 최소 요구사항을 충족하는지 확인"""
        major, minor = test_environment["python_version"].split(".")
        assert int(major) >= 3
        assert int(minor) >= 9  # Python 3.9 이상 필요


# ============================================================
# 3. 커스텀 마커 테스트
# ============================================================

@pytest.mark.config
class TestMarkerConfiguration:
    """마커 등록 및 사용 테스트"""

    def test_config_marker_applied(self):
        """config 마커가 적용된 테스트"""
        # pyproject.toml에 등록된 config 마커 사용
        assert True

    @pytest.mark.smoke
    def test_smoke_marker_applied(self):
        """smoke 마커가 적용된 테스트"""
        assert True

    @pytest.mark.sensor
    def test_sensor_marker_applied(self):
        """sensor 마커가 적용된 테스트"""
        assert True


# ============================================================
# 4. conftest.py hook으로 등록된 마커 테스트
# ============================================================

@pytest.mark.equipment(name="motor")
def test_motor_equipment_marker():
    """conftest.py에서 프로그래밍 등록된 equipment 마커 사용"""
    assert True


@pytest.mark.priority(level="high")
def test_high_priority_marker():
    """conftest.py에서 프로그래밍 등록된 priority 마커 사용"""
    assert True


# ============================================================
# 5. 설정에 의한 경고 필터링 테스트
# ============================================================

class TestWarningFilters:
    """filterwarnings 설정 효과 확인"""

    def test_no_deprecation_warning(self):
        """DeprecationWarning이 필터링되는지 확인"""
        import warnings
        # pyproject.toml에서 DeprecationWarning을 ignore로 설정했으므로
        # 이 경고는 테스트 실패를 일으키지 않음
        warnings.warn("이전 API 사용", DeprecationWarning)
        assert True

    def test_normal_operation(self):
        """일반적인 테스트가 정상 동작하는지 확인"""
        result = 2 + 2
        assert result == 4


# ============================================================
# 6. addopts 효과 시연
# ============================================================

class TestAddoptsEffect:
    """addopts 설정 효과 확인"""

    def test_verbose_output(self):
        """
        -v 옵션이 적용되어 이 테스트 이름이 상세히 표시된다.
        test_config_demo.py::TestAddoptsEffect::test_verbose_output
        """
        assert True

    def test_short_traceback(self):
        """
        --tb=short 옵션이 적용되어 실패 시 짧은 트레이스백이 표시된다.
        이 테스트는 성공하므로 트레이스백이 표시되지 않는다.
        """
        value = 42
        assert value == 42

    def test_summary_report(self):
        """
        -ra 옵션이 적용되어 실패/건너뜀 테스트가 요약 표시된다.
        """
        assert True


# ============================================================
# 7. testpaths 설정 확인
# ============================================================

class TestTestpaths:
    """testpaths 설정이 올바르게 적용되는지 확인"""

    def test_this_file_is_discovered(self):
        """이 테스트 파일이 발견되어 실행된다 (testpaths가 올바르게 설정됨)"""
        assert True

    def test_test_file_naming(self):
        """test_ 접두사가 있는 파일만 수집되는지 확인"""
        # python_files = ["test_*.py"] 설정에 의해 test_로 시작하는 파일만 수집
        import os
        current_file = os.path.basename(__file__)
        assert current_file.startswith("test_")
