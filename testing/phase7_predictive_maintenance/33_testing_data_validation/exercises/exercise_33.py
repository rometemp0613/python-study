"""
연습 문제 33: 데이터 유효성 검증 테스트

이 파일의 TODO를 완성하여 데이터 유효성 검증 로직을 테스트하세요.
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
    """
    여러 센서의 데이터를 한번에 검증하는 테스트를 작성하세요.
    """

    def test_온도_진동_압력_스키마_유효(self, validator):
        """
        온도, 진동, 압력 센서 데이터가 모두 올바른 스키마를 가지는지 테스트하세요.

        데이터: {"timestamp": 1000.0, "temperature": 25.0,
                "vibration": 0.5, "pressure": 100.0}
        기대 스키마: 모든 값이 float 타입
        """
        pytest.skip("TODO: validate_schema()로 다중 센서 스키마를 검증하세요")

    def test_일부_센서_누락_감지(self, validator):
        """
        pressure 컬럼이 누락된 데이터를 감지하는 테스트를 작성하세요.

        데이터: {"timestamp": 1000.0, "temperature": 25.0}
        기대 스키마: timestamp, temperature, pressure 모두 필요
        """
        pytest.skip("TODO: 누락된 컬럼이 에러로 보고되는지 확인하세요")


# ============================================================
# 연습 2: 시계열 갭 탐지 및 완전성 검증
# ============================================================

class TestTimeSeriesQuality:
    """
    시계열 데이터의 갭과 완전성을 검증하는 테스트를 작성하세요.
    """

    def test_30분_데이터_갭_탐지(self, validator):
        """
        30분 동안 1초 간격으로 수집된 데이터에서,
        중간에 5분 갭이 있는 경우를 탐지하세요.

        구성:
        - 0~600초 (10분): 1초 간격 정상 데이터
        - 600~900초 (5분): 갭 (데이터 없음)
        - 900~1800초 (15분): 1초 간격 정상 데이터

        max_gap_seconds=10으로 설정
        """
        pytest.skip("TODO: detect_gaps()로 5분 갭을 탐지하세요")

    def test_데이터_완전성_95퍼센트_이상(self, validator):
        """
        5% 이하의 데이터가 누락된 경우 완전성이 95% 이상인지 확인하세요.

        힌트: 100초 범위에 96개 이상의 1초 간격 데이터를 만드세요.
        """
        pytest.skip("TODO: validate_completeness()가 95 이상을 반환하는지 확인하세요")


# ============================================================
# 연습 3: 복합 센서 리딩 검증
# ============================================================

class TestSensorReadingValidation:
    """
    단일 센서 리딩의 종합 검증 테스트를 작성하세요.
    """

    def test_유효한_RPM_리딩(self, validator):
        """
        유효한 RPM 센서 리딩이 통과하는지 테스트하세요.

        리딩: timestamp=현재시각, sensor_type="rpm", value=3000.0
        """
        pytest.skip("TODO: validate_sensor_reading()으로 유효한 RPM 리딩을 검증하세요")

    def test_전류_센서_범위_초과(self, validator):
        """
        전류(current) 센서 값이 물리적 범위(0~500A)를 초과할 때
        is_valid=False가 되는지 테스트하세요.

        리딩: value=600.0 (500A 초과)
        """
        pytest.skip("TODO: 범위 초과 시 is_valid가 False인지 확인하세요")

    def test_필수_필드_모두_누락(self, validator):
        """
        빈 딕셔너리로 validate_sensor_reading()을 호출했을 때
        모든 필수 필드에 대한 에러가 발생하는지 테스트하세요.
        """
        pytest.skip("TODO: 빈 딕셔너리로 3개 필수 필드 누락 에러를 확인하세요")
