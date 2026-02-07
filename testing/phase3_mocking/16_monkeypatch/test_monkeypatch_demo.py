"""
Monkeypatch 데모

monkeypatch.setattr(), setenv(), delenv(),
setitem(), delitem() 등의 사용법을 보여주는 예제입니다.
"""

import pytest
import os
from src_sensor_config import (
    SensorConfig,
    SENSOR_THRESHOLDS,
    DATABASE_CONFIG,
    analyze_sensor_reading,
    get_config_summary,
)


# ============================================================
# 1. monkeypatch.setenv() - 환경 변수 설정
# ============================================================

class TestSetEnv:
    """환경 변수를 설정하여 설정을 변경하는 테스트"""

    def test_custom_api_url(self, monkeypatch):
        """환경 변수로 API URL을 변경한다"""
        monkeypatch.setenv("SENSOR_API_URL", "http://test-server:9090")

        config = SensorConfig()
        assert config.api_url == "http://test-server:9090"

    def test_api_key_from_env(self, monkeypatch):
        """환경 변수에서 API 키를 읽는다"""
        monkeypatch.setenv("SENSOR_API_KEY", "test-key-12345")

        config = SensorConfig()
        assert config.api_key == "test-key-12345"

    def test_debug_mode_enabled(self, monkeypatch):
        """환경 변수로 디버그 모드를 활성화한다"""
        monkeypatch.setenv("DEBUG", "true")

        config = SensorConfig()
        assert config.debug_mode is True

    def test_debug_mode_disabled(self, monkeypatch):
        """디버그 모드가 비활성화된 경우"""
        monkeypatch.setenv("DEBUG", "false")

        config = SensorConfig()
        assert config.debug_mode is False

    def test_custom_interval_from_env(self, monkeypatch):
        """환경 변수로 수집 주기를 변경한다"""
        monkeypatch.setenv("SENSOR_INTERVAL", "10")

        interval = SensorConfig.get_interval()
        assert interval == 10

    def test_custom_timeout_from_env(self, monkeypatch):
        """환경 변수로 타임아웃을 변경한다"""
        monkeypatch.setenv("SENSOR_TIMEOUT", "5")

        timeout = SensorConfig.get_timeout()
        assert timeout == 5

    def test_database_url_from_env(self, monkeypatch):
        """환경 변수로 데이터베이스 연결 정보를 변경한다"""
        monkeypatch.setenv("DB_HOST", "test-db")
        monkeypatch.setenv("DB_PORT", "5433")
        monkeypatch.setenv("DB_NAME", "test_sensor")
        monkeypatch.setenv("DB_USER", "test_user")

        url = SensorConfig.get_database_url()
        assert url == "postgresql://test_user@test-db:5433/test_sensor"


# ============================================================
# 2. monkeypatch.delenv() - 환경 변수 삭제
# ============================================================

class TestDelEnv:
    """환경 변수를 삭제하여 기본값 동작을 테스트"""

    def test_default_api_url_when_env_not_set(self, monkeypatch):
        """환경 변수가 없으면 기본 URL을 사용한다"""
        monkeypatch.delenv("SENSOR_API_URL", raising=False)

        config = SensorConfig()
        assert config.api_url == "http://localhost:8080"

    def test_default_interval_when_env_not_set(self, monkeypatch):
        """환경 변수가 없으면 클래스 기본값을 사용한다"""
        monkeypatch.delenv("SENSOR_INTERVAL", raising=False)

        interval = SensorConfig.get_interval()
        assert interval == SensorConfig.DEFAULT_INTERVAL


# ============================================================
# 3. monkeypatch.setattr() - 클래스 속성 변경
# ============================================================

class TestSetAttr:
    """클래스 속성을 변경하는 테스트"""

    def test_change_default_interval(self, monkeypatch):
        """기본 수집 주기를 변경한다"""
        monkeypatch.delenv("SENSOR_INTERVAL", raising=False)
        monkeypatch.setattr(SensorConfig, "DEFAULT_INTERVAL", 5)

        assert SensorConfig.get_interval() == 5

    def test_change_default_timeout(self, monkeypatch):
        """기본 타임아웃을 변경한다"""
        monkeypatch.delenv("SENSOR_TIMEOUT", raising=False)
        monkeypatch.setattr(SensorConfig, "DEFAULT_TIMEOUT", 10)

        assert SensorConfig.get_timeout() == 10

    def test_change_max_retries(self, monkeypatch):
        """최대 재시도 횟수를 변경한다"""
        monkeypatch.setattr(SensorConfig, "MAX_RETRIES", 5)

        assert SensorConfig.MAX_RETRIES == 5

    def test_change_batch_size(self, monkeypatch):
        """배치 크기를 변경한다"""
        monkeypatch.setattr(SensorConfig, "DEFAULT_BATCH_SIZE", 50)

        assert SensorConfig.DEFAULT_BATCH_SIZE == 50

    def test_replace_function_with_lambda(self, monkeypatch):
        """os.path.exists를 대체하여 항상 True를 반환하게 한다"""
        monkeypatch.setattr(os.path, "exists", lambda path: True)

        assert os.path.exists("/this/path/does/not/exist") is True

    def test_values_restored_after_test(self):
        """이전 테스트의 monkeypatch 변경이 복원되었는지 확인"""
        # 위의 테스트에서 변경한 값들이 원래대로 복원되었어야 함
        assert SensorConfig.DEFAULT_INTERVAL == 60
        assert SensorConfig.DEFAULT_TIMEOUT == 30
        assert SensorConfig.MAX_RETRIES == 3
        assert SensorConfig.DEFAULT_BATCH_SIZE == 100


# ============================================================
# 4. monkeypatch.setitem() / delitem() - 딕셔너리 변경
# ============================================================

class TestSetItem:
    """딕셔너리 항목을 변경하는 테스트"""

    def test_change_temperature_threshold(self, monkeypatch):
        """온도 임계값을 변경한다"""
        monkeypatch.setitem(SENSOR_THRESHOLDS, "temperature_warning", 60.0)
        monkeypatch.setitem(SENSOR_THRESHOLDS, "temperature_critical", 80.0)

        # 변경된 임계값으로 분석
        result = analyze_sensor_reading(
            temperature=65.0, vibration=2.0, pressure=5.0
        )
        assert result["status"] == "경고"  # 원래는 정상이었을 값

    def test_change_vibration_threshold(self, monkeypatch):
        """진동 임계값을 변경한다"""
        monkeypatch.setitem(SENSOR_THRESHOLDS, "vibration_warning", 3.0)

        result = analyze_sensor_reading(
            temperature=25.0, vibration=4.0, pressure=5.0
        )
        assert result["status"] == "경고"

    def test_change_database_config(self, monkeypatch):
        """데이터베이스 설정을 변경한다"""
        monkeypatch.setitem(DATABASE_CONFIG, "host", "test-db-host")
        monkeypatch.setitem(DATABASE_CONFIG, "port", 15432)

        assert DATABASE_CONFIG["host"] == "test-db-host"
        assert DATABASE_CONFIG["port"] == 15432

    def test_thresholds_restored_after_test(self):
        """이전 테스트의 딕셔너리 변경이 복원되었는지 확인"""
        assert SENSOR_THRESHOLDS["temperature_warning"] == 80.0
        assert SENSOR_THRESHOLDS["temperature_critical"] == 100.0
        assert SENSOR_THRESHOLDS["vibration_warning"] == 5.0


class TestDelItem:
    """딕셔너리 항목을 삭제하는 테스트"""

    def test_delete_threshold_entry(self, monkeypatch):
        """임계값 항목을 삭제하여 KeyError 발생을 확인한다"""
        monkeypatch.delitem(SENSOR_THRESHOLDS, "pressure_warning")

        assert "pressure_warning" not in SENSOR_THRESHOLDS

    def test_threshold_restored_after_delete(self):
        """삭제된 항목이 복원되었는지 확인"""
        assert "pressure_warning" in SENSOR_THRESHOLDS
        assert SENSOR_THRESHOLDS["pressure_warning"] == 8.0


# ============================================================
# 5. monkeypatch.chdir() - 작업 디렉토리 변경
# ============================================================

class TestChdir:
    """작업 디렉토리를 변경하는 테스트"""

    def test_change_working_directory(self, monkeypatch, tmp_path):
        """작업 디렉토리를 임시 디렉토리로 변경한다"""
        monkeypatch.chdir(tmp_path)

        assert os.getcwd() == str(tmp_path)

    def test_working_directory_restored(self):
        """작업 디렉토리가 원래대로 복원되었는지 확인"""
        # tmp_path가 아닌 원래 디렉토리에 있어야 함
        cwd = os.getcwd()
        assert "tmp" not in cwd or "pytest" not in cwd


# ============================================================
# 6. 종합 예제: 테스트 환경 전체 설정
# ============================================================

class TestFullConfiguration:
    """여러 monkeypatch를 조합한 종합 테스트"""

    def test_complete_test_environment(self, monkeypatch):
        """
        테스트 환경 전체를 설정한다.

        환경 변수, 클래스 속성, 딕셔너리를 모두 변경하여
        완전히 격리된 테스트 환경을 구성합니다.
        """
        # 환경 변수 설정
        monkeypatch.setenv("SENSOR_API_URL", "http://test:8080")
        monkeypatch.setenv("SENSOR_API_KEY", "test-key")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.delenv("SENSOR_INTERVAL", raising=False)
        monkeypatch.delenv("SENSOR_TIMEOUT", raising=False)

        # 클래스 속성 변경
        monkeypatch.setattr(SensorConfig, "DEFAULT_INTERVAL", 10)
        monkeypatch.setattr(SensorConfig, "DEFAULT_TIMEOUT", 5)

        # 딕셔너리 변경
        monkeypatch.setitem(SENSOR_THRESHOLDS, "temperature_warning", 50.0)

        # 종합 설정 확인
        summary = get_config_summary()

        assert summary["api_url"] == "http://test:8080"
        assert summary["debug_mode"] is True
        assert summary["interval"] == 10
        assert summary["timeout"] == 5
        assert summary["thresholds"]["temperature_warning"] == 50.0

    def test_isolation_from_previous_test(self):
        """이전 테스트의 변경이 모두 복원되었는지 확인"""
        # 모든 변경이 복원되어야 함
        assert SensorConfig.DEFAULT_INTERVAL == 60
        assert SensorConfig.DEFAULT_TIMEOUT == 30
        assert SENSOR_THRESHOLDS["temperature_warning"] == 80.0
