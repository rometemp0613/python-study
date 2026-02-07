"""
임계값 설정 테스트

monkeypatch.setenv()로 환경 변수를 테스트하고,
tmp_path로 설정 파일을 테스트하고,
datetime 모킹으로 시간 의존 코드를 테스트합니다.
"""
import json
import pytest
from datetime import datetime
from unittest.mock import patch

from src_threshold_config import ThresholdConfig


# ============================================================
# 기본 초기화 테스트
# ============================================================

class TestThresholdConfigInit:
    """설정 클래스 초기화 테스트"""

    def test_default_thresholds_loaded(self):
        """기본 임계값이 초기화되는지 확인"""
        config = ThresholdConfig()
        temp = config.get_threshold("temperature")
        assert temp["warning"] == 80.0
        assert temp["critical"] == 95.0

    def test_all_sensor_types_have_defaults(self):
        """모든 센서 타입에 기본 임계값이 있는지 확인"""
        config = ThresholdConfig()
        for sensor_type in ["temperature", "vibration", "current"]:
            threshold = config.get_threshold(sensor_type)
            assert "warning" in threshold
            assert "critical" in threshold

    def test_unknown_sensor_type_raises_key_error(self):
        """알 수 없는 센서 타입 조회 시 KeyError"""
        config = ThresholdConfig()
        with pytest.raises(KeyError, match="알 수 없는 센서 타입"):
            config.get_threshold("unknown_sensor")

    def test_default_alert_hours(self):
        """기본 알림 시간 설정 (항상 활성)"""
        config = ThresholdConfig()
        assert config.alert_start_hour == 0
        assert config.alert_end_hour == 24


# ============================================================
# 환경 변수 테스트 (monkeypatch)
# ============================================================

class TestLoadFromEnv:
    """환경 변수에서 설정 로드 테스트"""

    def test_load_temperature_from_env(self, monkeypatch):
        """온도 임계값을 환경 변수에서 로드"""
        monkeypatch.setenv("SENSOR_TEMP_WARNING", "75.0")
        monkeypatch.setenv("SENSOR_TEMP_CRITICAL", "90.0")

        config = ThresholdConfig()
        config.load_from_env()

        threshold = config.get_threshold("temperature")
        assert threshold["warning"] == 75.0
        assert threshold["critical"] == 90.0

    def test_load_vibration_from_env(self, monkeypatch):
        """진동 임계값을 환경 변수에서 로드"""
        monkeypatch.setenv("SENSOR_VIB_WARNING", "4.0")
        monkeypatch.setenv("SENSOR_VIB_CRITICAL", "8.0")

        config = ThresholdConfig()
        config.load_from_env()

        threshold = config.get_threshold("vibration")
        assert threshold["warning"] == 4.0
        assert threshold["critical"] == 8.0

    def test_partial_env_overrides(self, monkeypatch):
        """일부 환경 변수만 설정된 경우"""
        # warning만 설정, critical은 기본값 유지
        monkeypatch.setenv("SENSOR_TEMP_WARNING", "70.0")
        monkeypatch.delenv("SENSOR_TEMP_CRITICAL", raising=False)

        config = ThresholdConfig()
        config.load_from_env()

        threshold = config.get_threshold("temperature")
        assert threshold["warning"] == 70.0
        assert threshold["critical"] == 95.0  # 기본값 유지

    def test_env_not_set_uses_default(self, monkeypatch):
        """환경 변수가 없으면 기본값 사용"""
        # 모든 관련 환경 변수 제거
        for env_name in [
            "SENSOR_TEMP_WARNING", "SENSOR_TEMP_CRITICAL",
            "SENSOR_VIB_WARNING", "SENSOR_VIB_CRITICAL",
            "SENSOR_CURR_WARNING", "SENSOR_CURR_CRITICAL",
            "ALERT_START_HOUR", "ALERT_END_HOUR",
        ]:
            monkeypatch.delenv(env_name, raising=False)

        config = ThresholdConfig()
        config.load_from_env()

        # 기본값이 유지되어야 함
        assert config.get_threshold("temperature")["warning"] == 80.0

    def test_invalid_env_value_raises_error(self, monkeypatch):
        """숫자가 아닌 환경 변수 값 -> ValueError"""
        monkeypatch.setenv("SENSOR_TEMP_WARNING", "not_a_number")

        config = ThresholdConfig()
        with pytest.raises(ValueError, match="숫자로 변환"):
            config.load_from_env()

    def test_load_alert_hours_from_env(self, monkeypatch):
        """알림 시간을 환경 변수에서 로드"""
        monkeypatch.setenv("ALERT_START_HOUR", "8")
        monkeypatch.setenv("ALERT_END_HOUR", "22")

        config = ThresholdConfig()
        config.load_from_env()

        assert config.alert_start_hour == 8
        assert config.alert_end_hour == 22

    def test_invalid_alert_hour_raises_error(self, monkeypatch):
        """잘못된 알림 시간 값 -> ValueError"""
        monkeypatch.setenv("ALERT_START_HOUR", "abc")

        config = ThresholdConfig()
        with pytest.raises(ValueError, match="정수로 변환"):
            config.load_from_env()


# ============================================================
# 설정 파일 테스트 (tmp_path)
# ============================================================

class TestLoadFromFile:
    """JSON 설정 파일에서 설정 로드 테스트"""

    def test_load_valid_config(self, tmp_path):
        """유효한 설정 파일 로드"""
        config_data = {
            "thresholds": {
                "temperature": {"warning": 75.0, "critical": 90.0},
                "vibration": {"warning": 4.0, "critical": 8.0},
            },
            "alert_hours": {"start": 8, "end": 22},
        }

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data, indent=2))

        config = ThresholdConfig()
        config.load_from_file(str(config_file))

        assert config.get_threshold("temperature")["warning"] == 75.0
        assert config.get_threshold("vibration")["critical"] == 8.0
        assert config.alert_start_hour == 8
        assert config.alert_end_hour == 22

    def test_file_not_found(self):
        """설정 파일이 없을 때 FileNotFoundError"""
        config = ThresholdConfig()
        with pytest.raises(FileNotFoundError, match="설정 파일"):
            config.load_from_file("/nonexistent/config.json")

    def test_invalid_json(self, tmp_path):
        """잘못된 JSON 형식"""
        config_file = tmp_path / "bad_config.json"
        config_file.write_text("{invalid json content")

        config = ThresholdConfig()
        with pytest.raises(ValueError, match="JSON 파싱"):
            config.load_from_file(str(config_file))

    def test_non_numeric_threshold_in_file(self, tmp_path):
        """설정 파일의 임계값이 숫자가 아닌 경우"""
        config_data = {
            "thresholds": {
                "temperature": {"warning": "high", "critical": 90.0},
            },
        }

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        config = ThresholdConfig()
        with pytest.raises(ValueError, match="숫자여야"):
            config.load_from_file(str(config_file))

    def test_partial_config_file(self, tmp_path):
        """일부 설정만 포함된 파일"""
        config_data = {
            "thresholds": {
                "temperature": {"warning": 70.0, "critical": 85.0},
            },
            # vibration, current, alert_hours 없음
        }

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        config = ThresholdConfig()
        config.load_from_file(str(config_file))

        # temperature는 파일 값
        assert config.get_threshold("temperature")["warning"] == 70.0
        # vibration은 기본값 유지
        assert config.get_threshold("vibration")["warning"] == 5.0

    def test_custom_sensor_type_in_file(self, tmp_path):
        """설정 파일에 사용자 정의 센서 타입 추가"""
        config_data = {
            "thresholds": {
                "pressure": {"warning": 100.0, "critical": 150.0},
            },
        }

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        config = ThresholdConfig()
        config.load_from_file(str(config_file))

        pressure = config.get_threshold("pressure")
        assert pressure["warning"] == 100.0
        assert pressure["critical"] == 150.0


# ============================================================
# 설정 우선순위 테스트
# ============================================================

class TestConfigPriority:
    """설정 우선순위 테스트 (환경 변수 > 파일 > 기본값)"""

    def test_env_overrides_file(self, monkeypatch, tmp_path):
        """환경 변수가 설정 파일보다 우선"""
        config_data = {
            "thresholds": {
                "temperature": {"warning": 80.0, "critical": 95.0},
            },
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        # 환경 변수로 더 낮은 값 설정
        monkeypatch.setenv("SENSOR_TEMP_WARNING", "70.0")

        config = ThresholdConfig()
        config.load_from_file(str(config_file))
        config.load_from_env()  # 나중에 로드되어 덮어씀

        assert config.get_threshold("temperature")["warning"] == 70.0

    def test_file_overrides_default(self, tmp_path):
        """설정 파일이 기본값보다 우선"""
        config_data = {
            "thresholds": {
                "temperature": {"warning": 60.0, "critical": 75.0},
            },
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        config = ThresholdConfig()
        config.load_from_file(str(config_file))

        assert config.get_threshold("temperature")["warning"] == 60.0


# ============================================================
# 시간 의존 코드 테스트 (datetime 모킹)
# ============================================================

class TestIsAlertTime:
    """시간 기반 알림 활성화 테스트"""

    def test_alert_during_business_hours(self):
        """업무 시간(8~22시) 중 알림 활성화"""
        config = ThresholdConfig()
        config.alert_start_hour = 8
        config.alert_end_hour = 22

        # 오후 2시 (14시)로 시간 고정
        mock_now = datetime(2024, 1, 15, 14, 0, 0)
        with patch("src_threshold_config.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now

            assert config.is_alert_time() is True

    def test_alert_suppressed_at_night(self):
        """야간(22~8시)에는 알림 비활성화"""
        config = ThresholdConfig()
        config.alert_start_hour = 8
        config.alert_end_hour = 22

        # 새벽 3시로 시간 고정
        mock_now = datetime(2024, 1, 15, 3, 0, 0)
        with patch("src_threshold_config.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now

            assert config.is_alert_time() is False

    def test_alert_at_start_boundary(self):
        """알림 시작 시간 경계값"""
        config = ThresholdConfig()
        config.alert_start_hour = 8
        config.alert_end_hour = 22

        # 정확히 8시
        mock_now = datetime(2024, 1, 15, 8, 0, 0)
        with patch("src_threshold_config.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now

            assert config.is_alert_time() is True

    def test_alert_at_end_boundary(self):
        """알림 종료 시간 경계값"""
        config = ThresholdConfig()
        config.alert_start_hour = 8
        config.alert_end_hour = 22

        # 정확히 22시 -> 비활성 (< end_hour)
        mock_now = datetime(2024, 1, 15, 22, 0, 0)
        with patch("src_threshold_config.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now

            assert config.is_alert_time() is False

    def test_always_active_default(self):
        """기본 설정(0~24시)에서는 항상 활성"""
        config = ThresholdConfig()
        # 기본: start=0, end=24

        for hour in [0, 6, 12, 18, 23]:
            mock_now = datetime(2024, 1, 15, hour, 0, 0)
            with patch("src_threshold_config.datetime") as mock_dt:
                mock_dt.now.return_value = mock_now
                assert config.is_alert_time() is True, f"{hour}시에 활성이어야 합니다"

    def test_overnight_alert_hours(self):
        """자정을 넘는 알림 시간 (22시~6시)"""
        config = ThresholdConfig()
        config.alert_start_hour = 22
        config.alert_end_hour = 6

        # 23시 -> 활성
        mock_now = datetime(2024, 1, 15, 23, 0, 0)
        with patch("src_threshold_config.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            assert config.is_alert_time() is True

        # 3시 -> 활성
        mock_now = datetime(2024, 1, 15, 3, 0, 0)
        with patch("src_threshold_config.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            assert config.is_alert_time() is True

        # 12시 -> 비활성
        mock_now = datetime(2024, 1, 15, 12, 0, 0)
        with patch("src_threshold_config.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            assert config.is_alert_time() is False


# ============================================================
# check_value 테스트
# ============================================================

class TestCheckValue:
    """센서 값 상태 판정 테스트"""

    def test_normal_value(self):
        """정상 범위 값"""
        config = ThresholdConfig()
        assert config.check_value("temperature", 50.0) == "normal"

    def test_warning_value(self):
        """경고 범위 값"""
        config = ThresholdConfig()
        assert config.check_value("temperature", 85.0) == "warning"

    def test_critical_value(self):
        """위험 범위 값"""
        config = ThresholdConfig()
        assert config.check_value("temperature", 100.0) == "critical"

    def test_boundary_warning(self):
        """경고 경계값 (정확히 warning 임계값)"""
        config = ThresholdConfig()
        # 기본 temperature warning = 80.0
        assert config.check_value("temperature", 80.0) == "warning"

    def test_boundary_critical(self):
        """위험 경계값 (정확히 critical 임계값)"""
        config = ThresholdConfig()
        # 기본 temperature critical = 95.0
        assert config.check_value("temperature", 95.0) == "critical"

    def test_just_below_warning(self):
        """경고 임계값 바로 아래"""
        config = ThresholdConfig()
        assert config.check_value("temperature", 79.9) == "normal"
