"""
연습 문제 20 풀이: 설정과 환경 테스트
"""
import json
import pytest
from datetime import datetime
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src_threshold_config import ThresholdConfig


# ============================================================
# 연습 1: 환경 변수 기반 설정 테스트
# ============================================================

class TestEnvVariables:
    """monkeypatch를 활용한 환경 변수 테스트"""

    def test_all_env_vars_set(self, monkeypatch):
        """모든 센서의 환경 변수가 설정된 경우"""
        # 모든 센서 타입의 환경 변수 설정
        monkeypatch.setenv("SENSOR_TEMP_WARNING", "70.0")
        monkeypatch.setenv("SENSOR_TEMP_CRITICAL", "85.0")
        monkeypatch.setenv("SENSOR_VIB_WARNING", "3.0")
        monkeypatch.setenv("SENSOR_VIB_CRITICAL", "7.0")
        monkeypatch.setenv("SENSOR_CURR_WARNING", "12.0")
        monkeypatch.setenv("SENSOR_CURR_CRITICAL", "18.0")

        config = ThresholdConfig()
        config.load_from_env()

        assert config.get_threshold("temperature")["warning"] == 70.0
        assert config.get_threshold("temperature")["critical"] == 85.0
        assert config.get_threshold("vibration")["warning"] == 3.0
        assert config.get_threshold("vibration")["critical"] == 7.0
        assert config.get_threshold("current")["warning"] == 12.0
        assert config.get_threshold("current")["critical"] == 18.0

    def test_no_env_vars_set(self, monkeypatch):
        """환경 변수가 하나도 설정되지 않은 경우"""
        # 모든 관련 환경 변수 제거
        env_vars = [
            "SENSOR_TEMP_WARNING", "SENSOR_TEMP_CRITICAL",
            "SENSOR_VIB_WARNING", "SENSOR_VIB_CRITICAL",
            "SENSOR_CURR_WARNING", "SENSOR_CURR_CRITICAL",
            "ALERT_START_HOUR", "ALERT_END_HOUR",
        ]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

        config = ThresholdConfig()
        config.load_from_env()

        # 기본값이 유지되어야 함
        assert config.get_threshold("temperature")["warning"] == 80.0
        assert config.get_threshold("temperature")["critical"] == 95.0
        assert config.get_threshold("vibration")["warning"] == 5.0

    def test_invalid_env_value(self, monkeypatch):
        """잘못된 환경 변수 값 처리"""
        monkeypatch.setenv("SENSOR_VIB_WARNING", "high")

        config = ThresholdConfig()
        with pytest.raises(ValueError, match="숫자로 변환"):
            config.load_from_env()


# ============================================================
# 연습 2: 설정 파일 테스트
# ============================================================

class TestConfigFile:
    """tmp_path를 활용한 설정 파일 테스트"""

    def test_valid_config_file(self, tmp_path):
        """유효한 설정 파일 로드"""
        config_data = {
            "thresholds": {
                "temperature": {"warning": 65.0, "critical": 80.0},
                "vibration": {"warning": 3.5, "critical": 7.0},
            },
            "alert_hours": {"start": 9, "end": 21},
        }

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data, indent=2))

        config = ThresholdConfig()
        config.load_from_file(str(config_file))

        assert config.get_threshold("temperature")["warning"] == 65.0
        assert config.get_threshold("temperature")["critical"] == 80.0
        assert config.get_threshold("vibration")["warning"] == 3.5
        assert config.alert_start_hour == 9
        assert config.alert_end_hour == 21

    def test_empty_json_file(self, tmp_path):
        """빈 JSON 객체 ({}) 파일"""
        config_file = tmp_path / "empty.json"
        config_file.write_text("{}")

        config = ThresholdConfig()
        config.load_from_file(str(config_file))

        # 기본값이 유지되어야 함
        assert config.get_threshold("temperature")["warning"] == 80.0
        assert config.get_threshold("vibration")["critical"] == 10.0

    def test_malformed_json(self, tmp_path):
        """잘못된 JSON 형식 파일"""
        config_file = tmp_path / "bad.json"
        config_file.write_text("{ this is not valid json }")

        config = ThresholdConfig()
        with pytest.raises(ValueError, match="JSON 파싱"):
            config.load_from_file(str(config_file))


# ============================================================
# 연습 3: 시간 의존 로직 테스트
# ============================================================

class TestTimeDependentLogic:
    """datetime 모킹을 활용한 시간 의존 코드 테스트"""

    def test_midday_alert_active(self):
        """정오(12시)에 알림이 활성인지 테스트"""
        config = ThresholdConfig()
        config.alert_start_hour = 8
        config.alert_end_hour = 22

        mock_now = datetime(2024, 6, 15, 12, 0, 0)
        with patch("src_threshold_config.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now

            assert config.is_alert_time() is True

    def test_midnight_alert_inactive(self):
        """자정(0시)에 알림이 비활성인지 테스트"""
        config = ThresholdConfig()
        config.alert_start_hour = 8
        config.alert_end_hour = 22

        mock_now = datetime(2024, 6, 15, 0, 0, 0)
        with patch("src_threshold_config.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now

            assert config.is_alert_time() is False

    def test_check_value_with_custom_threshold(self):
        """사용자 정의 임계값으로 상태 판정"""
        config = ThresholdConfig()
        config.thresholds["temperature"] = {
            "warning": 50.0,
            "critical": 70.0,
        }

        assert config.check_value("temperature", 45.0) == "normal"
        assert config.check_value("temperature", 60.0) == "warning"
        assert config.check_value("temperature", 75.0) == "critical"
