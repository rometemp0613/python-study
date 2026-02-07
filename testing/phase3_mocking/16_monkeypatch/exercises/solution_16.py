"""
연습 문제 16 풀이: Monkeypatch

monkeypatch를 사용한 환경 변수, 클래스 속성,
딕셔너리 조작 풀이입니다.
"""

import pytest
import sys
import os

# 상위 디렉토리의 모듈을 임포트하기 위한 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src_sensor_config import (
    SensorConfig,
    SENSOR_THRESHOLDS,
    DATABASE_CONFIG,
    analyze_sensor_reading,
    get_config_summary,
)


# ============================================================
# 연습 1 풀이: 환경 변수로 API 설정 변경
# ============================================================

class TestExercise1:
    """monkeypatch.setenv()로 환경 변수를 설정하여 테스트"""

    def test_custom_api_settings(self, monkeypatch):
        """API URL과 키를 환경 변수로 설정"""
        monkeypatch.setenv("SENSOR_API_URL", "http://test-api:3000")
        monkeypatch.setenv("SENSOR_API_KEY", "my-test-key")

        config = SensorConfig()

        assert config.api_url == "http://test-api:3000"
        assert config.api_key == "my-test-key"

    def test_database_url_with_env_vars(self, monkeypatch):
        """환경 변수로 데이터베이스 URL을 구성"""
        monkeypatch.setenv("DB_HOST", "test-db")
        monkeypatch.setenv("DB_PORT", "5433")
        monkeypatch.setenv("DB_NAME", "test_sensors")
        monkeypatch.setenv("DB_USER", "tester")

        url = SensorConfig.get_database_url()

        assert url == "postgresql://tester@test-db:5433/test_sensors"

    def test_default_values_without_env(self, monkeypatch):
        """환경 변수가 없을 때 기본값이 사용된다"""
        monkeypatch.delenv("SENSOR_API_URL", raising=False)
        monkeypatch.delenv("SENSOR_API_KEY", raising=False)

        config = SensorConfig()

        assert config.api_url == "http://localhost:8080"
        assert config.api_key == ""


# ============================================================
# 연습 2 풀이: 클래스 속성 패치
# ============================================================

class TestExercise2:
    """monkeypatch.setattr()로 클래스 속성을 변경하여 테스트"""

    def test_custom_collection_interval(self, monkeypatch):
        """수집 주기를 5초로 변경"""
        # 환경 변수가 우선하므로 먼저 제거
        monkeypatch.delenv("SENSOR_INTERVAL", raising=False)
        monkeypatch.setattr(SensorConfig, "DEFAULT_INTERVAL", 5)

        assert SensorConfig.get_interval() == 5

    def test_env_overrides_class_attribute(self, monkeypatch):
        """환경 변수가 클래스 속성보다 우선한다"""
        # 클래스 속성 변경
        monkeypatch.setattr(SensorConfig, "DEFAULT_INTERVAL", 5)

        # 환경 변수 설정 (이것이 우선)
        monkeypatch.setenv("SENSOR_INTERVAL", "15")

        # 환경 변수 값이 반환됨
        assert SensorConfig.get_interval() == 15


# ============================================================
# 연습 3 풀이: 설정 딕셔너리 조작
# ============================================================

class TestExercise3:
    """monkeypatch.setitem()으로 딕셔너리를 변경하여 테스트"""

    def test_lower_temperature_threshold(self, monkeypatch):
        """온도 임계값을 낮추면 정상 범위 데이터도 경고가 된다"""
        monkeypatch.setitem(SENSOR_THRESHOLDS, "temperature_warning", 50.0)

        result = analyze_sensor_reading(
            temperature=55.0, vibration=2.0, pressure=5.0
        )

        assert result["status"] == "경고"
        assert any("온도 경고" in w for w in result["warnings"])

    def test_all_thresholds_critical(self, monkeypatch):
        """모든 임계값을 매우 낮게 설정하면 위험 상태가 된다"""
        # 모든 critical 임계값을 매우 낮게 설정
        monkeypatch.setitem(SENSOR_THRESHOLDS, "temperature_critical", 20.0)
        monkeypatch.setitem(SENSOR_THRESHOLDS, "vibration_critical", 1.0)
        monkeypatch.setitem(SENSOR_THRESHOLDS, "pressure_critical", 3.0)

        result = analyze_sensor_reading(
            temperature=25.0, vibration=2.0, pressure=5.0
        )

        assert result["status"] == "위험"
        assert len(result["warnings"]) == 3

    def test_thresholds_restored(self):
        """이전 테스트의 변경이 복원되었다"""
        # monkeypatch에 의해 원래 값이 복원되어 있어야 함
        assert SENSOR_THRESHOLDS["temperature_warning"] == 80.0
        assert SENSOR_THRESHOLDS["temperature_critical"] == 100.0
        assert SENSOR_THRESHOLDS["vibration_warning"] == 5.0
        assert SENSOR_THRESHOLDS["vibration_critical"] == 10.0
        assert SENSOR_THRESHOLDS["pressure_warning"] == 8.0
        assert SENSOR_THRESHOLDS["pressure_critical"] == 12.0
