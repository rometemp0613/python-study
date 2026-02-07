"""
연습 문제 33 풀이: 데이터 유효성 검증 테스트

각 테스트의 완성된 풀이입니다.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# 부모 디렉토리의 모듈을 임포트하기 위한 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_data_validator import SensorDataValidator, SENSOR_RANGES


@pytest.fixture
def validator():
    """SensorDataValidator 인스턴스"""
    return SensorDataValidator()


# ============================================================
# 연습 1: 다중 센서 스키마 검증
# ============================================================

class TestMultiSensorSchema:
    """여러 센서의 데이터 스키마 검증"""

    def test_온도_진동_압력_스키마_유효(self, validator):
        """온도, 진동, 압력 센서 데이터의 스키마가 유효한지 테스트"""
        # 준비
        data = {
            "timestamp": 1000.0,
            "temperature": 25.0,
            "vibration": 0.5,
            "pressure": 100.0,
        }
        expected = {
            "timestamp": float,
            "temperature": float,
            "vibration": float,
            "pressure": float,
        }

        # 실행
        result = validator.validate_schema(data, expected)

        # 검증
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_일부_센서_누락_감지(self, validator):
        """pressure 컬럼이 누락된 데이터 감지"""
        # 준비
        data = {
            "timestamp": 1000.0,
            "temperature": 25.0,
        }
        expected = {
            "timestamp": float,
            "temperature": float,
            "pressure": float,
        }

        # 실행
        result = validator.validate_schema(data, expected)

        # 검증
        assert result.is_valid is False
        assert any("pressure" in e for e in result.errors)


# ============================================================
# 연습 2: 시계열 갭 탐지 및 완전성 검증
# ============================================================

class TestTimeSeriesQuality:
    """시계열 데이터 갭 및 완전성 검증"""

    def test_30분_데이터_갭_탐지(self, validator):
        """30분 데이터에서 5분 갭을 탐지"""
        # 준비: 0~600초(10분) 정상 + 900~1800초(15분) 정상
        base = datetime(2024, 6, 15, 10, 0, 0)
        timestamps = []

        # 처음 10분 (0~600초)
        for i in range(601):
            timestamps.append(base + timedelta(seconds=i))

        # 5분 갭 후 15분 (900~1800초)
        for i in range(901):
            timestamps.append(base + timedelta(seconds=900 + i))

        # 실행
        gaps = validator.detect_gaps(timestamps, max_gap_seconds=10)

        # 검증: 600초와 900초 사이에 300초(5분) 갭
        assert len(gaps) == 1
        assert gaps[0]["gap_seconds"] == pytest.approx(300.0, abs=1.0)

    def test_데이터_완전성_95퍼센트_이상(self, validator):
        """데이터 완전성이 95% 이상인지 확인"""
        # 준비: 100초 범위에 97개 데이터 (약 97% 완전)
        base = datetime(2024, 6, 15, 10, 0, 0)
        timestamps = []
        skip_indices = {20, 50, 80}  # 3개만 누락

        for i in range(100):
            if i not in skip_indices:
                timestamps.append(base + timedelta(seconds=i))

        # 실행
        completeness = validator.validate_completeness(
            timestamps, expected_interval=1
        )

        # 검증
        assert completeness >= 95.0


# ============================================================
# 연습 3: 복합 센서 리딩 검증
# ============================================================

class TestSensorReadingValidation:
    """단일 센서 리딩의 종합 검증"""

    def test_유효한_RPM_리딩(self, validator):
        """유효한 RPM 센서 리딩 통과 테스트"""
        # 준비
        reading = {
            "timestamp": datetime.now(),
            "sensor_type": "rpm",
            "value": 3000.0,
        }

        # 실행
        result = validator.validate_sensor_reading(reading)

        # 검증
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_전류_센서_범위_초과(self, validator):
        """전류 센서 값 범위 초과(>500A) 감지"""
        # 준비
        reading = {
            "timestamp": datetime.now(),
            "sensor_type": "current",
            "value": 600.0,
        }

        # 실행
        result = validator.validate_sensor_reading(reading)

        # 검증
        assert result.is_valid is False
        assert any("범위" in e for e in result.errors)

    def test_필수_필드_모두_누락(self, validator):
        """빈 딕셔너리로 모든 필수 필드 누락 에러 확인"""
        # 준비
        reading = {}

        # 실행
        result = validator.validate_sensor_reading(reading)

        # 검증
        assert result.is_valid is False
        assert len(result.errors) == 3  # timestamp, sensor_type, value
        assert any("timestamp" in e for e in result.errors)
        assert any("sensor_type" in e for e in result.errors)
        assert any("value" in e for e in result.errors)
