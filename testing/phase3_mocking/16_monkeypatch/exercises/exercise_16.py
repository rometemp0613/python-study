"""
연습 문제 16: Monkeypatch

monkeypatch를 사용하여 환경 변수, 클래스 속성,
딕셔너리 항목을 변경하고 테스트하세요.
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
# 연습 1: 환경 변수로 API 설정 변경
# ============================================================

class TestExercise1:
    """monkeypatch.setenv()로 환경 변수를 설정하여 테스트"""

    def test_custom_api_settings(self, monkeypatch):
        """API URL과 키를 환경 변수로 설정하세요"""
        pytest.skip("TODO: setenv로 API 설정을 변경하고 확인하세요")
        # TODO:
        # 1. monkeypatch.setenv("SENSOR_API_URL", "http://test-api:3000")
        # 2. monkeypatch.setenv("SENSOR_API_KEY", "my-test-key")
        # 3. SensorConfig() 생성
        # 4. config.api_url이 "http://test-api:3000"인지 확인
        # 5. config.api_key가 "my-test-key"인지 확인

    def test_database_url_with_env_vars(self, monkeypatch):
        """환경 변수로 데이터베이스 URL을 구성하세요"""
        pytest.skip("TODO: DB 관련 환경 변수를 설정하고 URL을 확인하세요")
        # TODO:
        # 1. monkeypatch.setenv("DB_HOST", "test-db")
        # 2. monkeypatch.setenv("DB_PORT", "5433")
        # 3. monkeypatch.setenv("DB_NAME", "test_sensors")
        # 4. monkeypatch.setenv("DB_USER", "tester")
        # 5. SensorConfig.get_database_url() 호출
        # 6. 결과가 "postgresql://tester@test-db:5433/test_sensors"인지 확인

    def test_default_values_without_env(self, monkeypatch):
        """환경 변수가 없을 때 기본값이 사용되는지 확인하세요"""
        pytest.skip("TODO: 환경 변수를 삭제하고 기본값을 확인하세요")
        # TODO:
        # 1. monkeypatch.delenv("SENSOR_API_URL", raising=False)
        # 2. monkeypatch.delenv("SENSOR_API_KEY", raising=False)
        # 3. SensorConfig() 생성
        # 4. config.api_url이 "http://localhost:8080"인지 확인
        # 5. config.api_key가 ""(빈 문자열)인지 확인


# ============================================================
# 연습 2: 클래스 속성 패치
# ============================================================

class TestExercise2:
    """monkeypatch.setattr()로 클래스 속성을 변경하여 테스트"""

    def test_custom_collection_interval(self, monkeypatch):
        """수집 주기를 5초로 변경하세요"""
        pytest.skip("TODO: DEFAULT_INTERVAL을 변경하고 get_interval 결과를 확인하세요")
        # TODO:
        # 1. monkeypatch.delenv("SENSOR_INTERVAL", raising=False)
        # 2. monkeypatch.setattr(SensorConfig, "DEFAULT_INTERVAL", 5)
        # 3. SensorConfig.get_interval() == 5 확인

    def test_env_overrides_class_attribute(self, monkeypatch):
        """환경 변수가 클래스 속성보다 우선하는지 확인하세요"""
        pytest.skip("TODO: 환경 변수와 클래스 속성을 모두 설정하고 우선순위를 확인하세요")
        # TODO:
        # 1. monkeypatch.setattr(SensorConfig, "DEFAULT_INTERVAL", 5)
        # 2. monkeypatch.setenv("SENSOR_INTERVAL", "15")
        # 3. SensorConfig.get_interval() == 15 확인 (환경 변수가 우선)


# ============================================================
# 연습 3: 설정 딕셔너리 조작
# ============================================================

class TestExercise3:
    """monkeypatch.setitem()으로 딕셔너리를 변경하여 테스트"""

    def test_lower_temperature_threshold(self, monkeypatch):
        """온도 임계값을 낮추고 경고 발생을 확인하세요"""
        pytest.skip("TODO: 온도 임계값을 낮추고 analyze_sensor_reading 결과를 확인하세요")
        # TODO:
        # 1. monkeypatch.setitem(SENSOR_THRESHOLDS, "temperature_warning", 50.0)
        # 2. analyze_sensor_reading(temperature=55.0, vibration=2.0, pressure=5.0) 호출
        # 3. result["status"]가 "경고"인지 확인
        # 4. warnings에 "온도 경고"가 포함되어 있는지 확인

    def test_all_thresholds_critical(self, monkeypatch):
        """모든 임계값을 매우 낮게 설정하여 위험 상태를 테스트하세요"""
        pytest.skip("TODO: 모든 임계값을 낮추고 위험 상태를 확인하세요")
        # TODO:
        # 1. 온도, 진동, 압력의 critical 임계값을 모두 낮게 설정
        # 2. analyze_sensor_reading 호출
        # 3. status가 "위험"인지 확인
        # 4. warnings에 3개 항목이 있는지 확인

    def test_thresholds_restored(self):
        """이전 테스트의 변경이 복원되었는지 확인하세요"""
        pytest.skip("TODO: SENSOR_THRESHOLDS의 원래 값이 복원되었는지 확인하세요")
        # TODO:
        # 1. SENSOR_THRESHOLDS["temperature_warning"] == 80.0 확인
        # 2. SENSOR_THRESHOLDS["vibration_warning"] == 5.0 확인
