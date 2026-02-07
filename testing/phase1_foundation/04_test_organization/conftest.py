"""
conftest.py - 공유 fixture 정의

이 파일에 정의된 fixture는 같은 디렉토리와 하위 디렉토리의
모든 테스트에서 import 없이 사용할 수 있다.
"""

import pytest


@pytest.fixture
def sample_sensor_data():
    """테스트용 센서 데이터를 제공한다.

    단일 센서의 읽기 데이터를 딕셔너리 형태로 반환한다.
    """
    return {
        "sensor_id": "TEMP-001",
        "sensor_type": "temperature",
        "readings": [25.0, 25.5, 26.0, 25.8, 25.2, 24.9, 25.3],
        "unit": "celsius",
        "location": "모터 A",
        "timestamp": "2024-01-15T10:00:00",
    }


@pytest.fixture
def sample_multi_sensor_data():
    """테스트용 다중 센서 데이터를 제공한다.

    여러 센서의 읽기 데이터를 리스트 형태로 반환한다.
    """
    return [
        {
            "sensor_id": "TEMP-001",
            "sensor_type": "temperature",
            "readings": [25.0, 25.5, 26.0],
            "unit": "celsius",
            "location": "모터 A",
        },
        {
            "sensor_id": "VIB-001",
            "sensor_type": "vibration",
            "readings": [2.1, 2.3, 2.0],
            "unit": "mm/s",
            "location": "모터 A",
        },
        {
            "sensor_id": "PRESS-001",
            "sensor_type": "pressure",
            "readings": [14.5, 14.7, 14.6],
            "unit": "psi",
            "location": "배관 B",
        },
    ]


@pytest.fixture
def sample_config():
    """테스트용 시스템 설정을 제공한다.

    예지보전 시스템의 기본 설정값을 딕셔너리로 반환한다.
    """
    return {
        "temperature_threshold": 80.0,
        "vibration_threshold": 7.1,
        "pressure_threshold": 100.0,
        "sampling_interval_seconds": 60,
        "alert_email": "operator@factory.com",
        "data_retention_days": 365,
        "anomaly_detection": {
            "method": "zscore",
            "threshold_multiplier": 2.0,
        },
    }


@pytest.fixture
def empty_readings():
    """빈 읽기 데이터를 제공한다 (엣지 케이스 테스트용)."""
    return {
        "sensor_id": "TEMP-999",
        "sensor_type": "temperature",
        "readings": [],
        "unit": "celsius",
        "location": "테스트",
    }
