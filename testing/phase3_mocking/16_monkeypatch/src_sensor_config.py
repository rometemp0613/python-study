"""
센서 설정 모듈

환경 변수, 설정 딕셔너리, 클래스 속성 등에서
설정을 읽어오는 기능을 제공합니다.
monkeypatch 학습을 위한 소스 코드입니다.
"""

import os
from typing import Optional


# ============================================================
# 모듈 수준 설정 딕셔너리
# ============================================================

SENSOR_THRESHOLDS = {
    "temperature_warning": 80.0,
    "temperature_critical": 100.0,
    "vibration_warning": 5.0,
    "vibration_critical": 10.0,
    "pressure_warning": 8.0,
    "pressure_critical": 12.0,
}

DATABASE_CONFIG = {
    "host": "production-db.factory.com",
    "port": 5432,
    "database": "sensor_data",
    "username": "app_user",
}


# ============================================================
# 센서 설정 클래스
# ============================================================

class SensorConfig:
    """
    센서 설정 관리 클래스

    환경 변수, 클래스 속성, 딕셔너리에서
    설정을 읽어오는 기능을 제공합니다.
    """

    # 클래스 속성 (기본값)
    DEFAULT_INTERVAL = 60          # 데이터 수집 주기 (초)
    DEFAULT_TIMEOUT = 30           # API 타임아웃 (초)
    DEFAULT_BATCH_SIZE = 100       # 배치 처리 크기
    MAX_RETRIES = 3                # 최대 재시도 횟수

    def __init__(self):
        """환경 변수에서 설정을 로드한다"""
        self._api_url = os.environ.get(
            "SENSOR_API_URL", "http://localhost:8080"
        )
        self._api_key = os.environ.get("SENSOR_API_KEY", "")
        self._debug_mode = os.environ.get("DEBUG", "false").lower() == "true"

    @property
    def api_url(self) -> str:
        """센서 API URL을 반환한다"""
        return self._api_url

    @property
    def api_key(self) -> str:
        """센서 API 키를 반환한다"""
        return self._api_key

    @property
    def debug_mode(self) -> bool:
        """디버그 모드 여부를 반환한다"""
        return self._debug_mode

    @classmethod
    def get_interval(cls) -> int:
        """데이터 수집 주기를 반환한다"""
        # 환경 변수가 있으면 우선 사용
        env_interval = os.environ.get("SENSOR_INTERVAL")
        if env_interval:
            return int(env_interval)
        return cls.DEFAULT_INTERVAL

    @classmethod
    def get_timeout(cls) -> int:
        """API 타임아웃을 반환한다"""
        env_timeout = os.environ.get("SENSOR_TIMEOUT")
        if env_timeout:
            return int(env_timeout)
        return cls.DEFAULT_TIMEOUT

    @staticmethod
    def get_database_url() -> str:
        """데이터베이스 연결 URL을 생성한다"""
        host = os.environ.get("DB_HOST", DATABASE_CONFIG["host"])
        port = os.environ.get("DB_PORT", str(DATABASE_CONFIG["port"]))
        db = os.environ.get("DB_NAME", DATABASE_CONFIG["database"])
        user = os.environ.get("DB_USER", DATABASE_CONFIG["username"])

        return f"postgresql://{user}@{host}:{port}/{db}"


# ============================================================
# 상태 분석 함수
# ============================================================

def analyze_sensor_reading(temperature: float,
                           vibration: float,
                           pressure: float) -> dict:
    """
    센서 데이터를 분석하여 상태를 반환한다.

    SENSOR_THRESHOLDS 딕셔너리의 임계값을 사용합니다.
    """
    status = "정상"
    warnings = []

    # 온도 확인
    if temperature >= SENSOR_THRESHOLDS["temperature_critical"]:
        status = "위험"
        warnings.append(f"온도 위험: {temperature}°C")
    elif temperature >= SENSOR_THRESHOLDS["temperature_warning"]:
        status = "경고"
        warnings.append(f"온도 경고: {temperature}°C")

    # 진동 확인
    if vibration >= SENSOR_THRESHOLDS["vibration_critical"]:
        status = "위험"
        warnings.append(f"진동 위험: {vibration}mm/s")
    elif vibration >= SENSOR_THRESHOLDS["vibration_warning"]:
        if status != "위험":
            status = "경고"
        warnings.append(f"진동 경고: {vibration}mm/s")

    # 압력 확인
    if pressure >= SENSOR_THRESHOLDS["pressure_critical"]:
        status = "위험"
        warnings.append(f"압력 위험: {pressure}bar")
    elif pressure >= SENSOR_THRESHOLDS["pressure_warning"]:
        if status != "위험":
            status = "경고"
        warnings.append(f"압력 경고: {pressure}bar")

    return {
        "status": status,
        "warnings": warnings,
        "data": {
            "temperature": temperature,
            "vibration": vibration,
            "pressure": pressure,
        }
    }


def get_config_summary() -> dict:
    """현재 설정 요약을 반환한다"""
    config = SensorConfig()
    return {
        "api_url": config.api_url,
        "debug_mode": config.debug_mode,
        "interval": SensorConfig.get_interval(),
        "timeout": SensorConfig.get_timeout(),
        "database_url": SensorConfig.get_database_url(),
        "thresholds": dict(SENSOR_THRESHOLDS),
    }
