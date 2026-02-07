"""
센서 데이터 검증 모듈 테스트

pytest.raises(), match, ExceptionInfo, pytest.warns() 활용 예제.
"""

import pytest
from src_sensor_validator import (
    SensorError,
    SensorDataError,
    SensorRangeError,
    SensorTimeoutError,
    validate_sensor_data,
    validate_temperature_reading,
    validate_readings_batch,
    check_sensor_connection,
)


# ============================================================
# 커스텀 예외 클래스 테스트
# ============================================================

class TestCustomExceptions:
    """커스텀 예외 클래스 구조 테스트"""

    def test_예외_계층_구조(self):
        """모든 센서 예외가 SensorError를 상속하는지 확인"""
        assert issubclass(SensorDataError, SensorError)
        assert issubclass(SensorRangeError, SensorError)
        assert issubclass(SensorTimeoutError, SensorError)

    def test_예외_계층_구조_Exception(self):
        """SensorError가 Exception을 상속하는지 확인"""
        assert issubclass(SensorError, Exception)

    def test_SensorDataError_속성(self):
        """SensorDataError의 속성이 올바르게 설정되는지 확인"""
        error = SensorDataError("TEMP-001", "데이터 오류", "E001")
        assert error.sensor_id == "TEMP-001"
        assert error.error_code == "E001"
        assert "TEMP-001" in str(error)
        assert "E001" in str(error)

    def test_SensorRangeError_속성(self):
        """SensorRangeError의 속성이 올바르게 설정되는지 확인"""
        error = SensorRangeError("TEMP-001", 250, (-50, 200))
        assert error.sensor_id == "TEMP-001"
        assert error.value == 250
        assert error.valid_range == (-50, 200)
        assert "250" in str(error)

    def test_SensorTimeoutError_속성(self):
        """SensorTimeoutError의 속성이 올바르게 설정되는지 확인"""
        error = SensorTimeoutError("TEMP-001", 5.0)
        assert error.sensor_id == "TEMP-001"
        assert error.timeout_seconds == 5.0
        assert "타임아웃" in str(error)


# ============================================================
# validate_sensor_data 테스트
# ============================================================

class TestValidateSensorData:
    """센서 데이터 구조 검증 테스트"""

    def test_유효한_데이터(self):
        """유효한 데이터는 True를 반환해야 한다"""
        data = {
            "sensor_id": "TEMP-001",
            "sensor_type": "temperature",
            "readings": [25.0, 26.0],
        }
        assert validate_sensor_data(data) is True

    def test_필수_필드_누락_sensor_id(self):
        """sensor_id 누락 시 SensorDataError 발생"""
        data = {"sensor_type": "temperature", "readings": []}
        with pytest.raises(SensorDataError, match="sensor_id"):
            validate_sensor_data(data)

    def test_필수_필드_누락_readings(self):
        """readings 누락 시 SensorDataError 발생"""
        data = {"sensor_id": "TEMP-001", "sensor_type": "temperature"}
        with pytest.raises(SensorDataError, match="readings"):
            validate_sensor_data(data)

    def test_readings_타입_오류(self):
        """readings가 리스트가 아니면 SensorDataError 발생"""
        data = {
            "sensor_id": "TEMP-001",
            "sensor_type": "temperature",
            "readings": "not_a_list",
        }
        with pytest.raises(SensorDataError, match="리스트"):
            validate_sensor_data(data)

    def test_딕셔너리가_아닌_입력(self):
        """딕셔너리가 아닌 입력에 대해 TypeError 발생"""
        with pytest.raises(TypeError, match="딕셔너리"):
            validate_sensor_data("not_a_dict")

        with pytest.raises(TypeError):
            validate_sensor_data([1, 2, 3])

    def test_에러_코드_확인(self):
        """ExceptionInfo를 통해 에러 코드 확인"""
        data = {"sensor_type": "temperature", "readings": []}

        with pytest.raises(SensorDataError) as exc_info:
            validate_sensor_data(data)

        # ExceptionInfo 객체에서 예외 속성 접근
        assert exc_info.value.error_code == "E001"
        assert exc_info.type == SensorDataError


# ============================================================
# validate_temperature_reading 테스트
# ============================================================

class TestValidateTemperatureReading:
    """온도 읽기 값 범위 검증 테스트"""

    def test_유효한_온도(self):
        """유효한 온도는 True를 반환해야 한다"""
        assert validate_temperature_reading("TEMP-001", 25.0) is True
        assert validate_temperature_reading("TEMP-001", -50) is True
        assert validate_temperature_reading("TEMP-001", 200) is True

    def test_범위_초과_양수(self):
        """최대 온도 초과 시 SensorRangeError 발생"""
        with pytest.raises(SensorRangeError) as exc_info:
            validate_temperature_reading("TEMP-001", 250)

        assert exc_info.value.sensor_id == "TEMP-001"
        assert exc_info.value.value == 250
        assert exc_info.value.valid_range == (-50, 200)

    def test_범위_초과_음수(self):
        """최소 온도 미만 시 SensorRangeError 발생"""
        with pytest.raises(SensorRangeError, match="범위"):
            validate_temperature_reading("TEMP-001", -100)

    def test_사용자_정의_범위(self):
        """사용자가 지정한 범위로 검증"""
        # 좁은 범위로 검증
        with pytest.raises(SensorRangeError):
            validate_temperature_reading("TEMP-001", 50, min_temp=0, max_temp=40)

    def test_타입_오류(self):
        """숫자가 아닌 값에 대해 TypeError 발생"""
        with pytest.raises(TypeError, match="숫자"):
            validate_temperature_reading("TEMP-001", "hot")

    def test_상위_예외로_잡기(self):
        """SensorRangeError를 SensorError로도 잡을 수 있다"""
        with pytest.raises(SensorError):
            validate_temperature_reading("TEMP-001", 500)


# ============================================================
# validate_readings_batch 테스트
# ============================================================

class TestValidateReadingsBatch:
    """읽기 값 묶음 검증 테스트"""

    def test_유효한_데이터_묶음(self):
        """유효한 데이터는 그대로 반환되어야 한다"""
        readings = [25.0, 30.0, 35.0, 40.0]
        result = validate_readings_batch("TEMP-001", readings)
        assert result == [25.0, 30.0, 35.0, 40.0]

    def test_빈_읽기_값_예외(self):
        """빈 리스트에 대해 SensorDataError 발생"""
        with pytest.raises(SensorDataError) as exc_info:
            validate_readings_batch("TEMP-001", [])

        assert exc_info.value.error_code == "E003"

    def test_크게_벗어난_값_예외(self):
        """범위를 크게 벗어난 값에 대해 SensorRangeError 발생"""
        # 유효 범위: (-50, 200), 범위폭: 250
        # 200 + 250 = 450 초과 시 에러
        with pytest.raises(SensorRangeError):
            validate_readings_batch("TEMP-001", [25.0, 500.0])

    def test_약간_벗어난_값_경고(self):
        """범위를 약간 벗어난 값에 대해 경고 발생"""
        # 210은 범위를 약간 벗어남 (경고만 발생)
        with pytest.warns(UserWarning, match="벗어남"):
            result = validate_readings_batch("TEMP-001", [25.0, 210.0])

        # 벗어난 값은 제외됨
        assert result == [25.0]

    def test_숫자가_아닌_값_예외(self):
        """숫자가 아닌 값에 대해 SensorDataError 발생"""
        with pytest.raises(SensorDataError) as exc_info:
            validate_readings_batch("TEMP-001", [25.0, "invalid", 30.0])

        assert exc_info.value.error_code == "E004"


# ============================================================
# check_sensor_connection 테스트
# ============================================================

class TestCheckSensorConnection:
    """센서 연결 확인 테스트"""

    def test_정상_연결(self):
        """응답 시간이 빠르면 'connected' 반환"""
        result = check_sensor_connection("TEMP-001", response_time=1.0)
        assert result == "connected"

    def test_타임아웃(self):
        """응답 시간이 타임아웃을 초과하면 SensorTimeoutError 발생"""
        with pytest.raises(SensorTimeoutError) as exc_info:
            check_sensor_connection("TEMP-001", response_time=10.0)

        assert exc_info.value.sensor_id == "TEMP-001"
        assert exc_info.value.timeout_seconds == 5.0
        assert "타임아웃" in str(exc_info.value)

    def test_사용자_정의_타임아웃(self):
        """사용자 지정 타임아웃으로 판단"""
        # 타임아웃을 2초로 설정
        with pytest.raises(SensorTimeoutError):
            check_sensor_connection("TEMP-001", response_time=3.0, timeout=2.0)

    def test_연결_불안정_경고(self):
        """응답이 느리면 경고 발생"""
        # timeout=5.0 의 80% = 4.0, 4.5 > 4.0 이므로 경고 발생
        with pytest.warns(UserWarning, match="불안정"):
            check_sensor_connection("TEMP-001", response_time=4.5)

    def test_타임아웃_경계값(self):
        """정확히 타임아웃과 같으면 정상 (> 기준)"""
        # 5.0 > 5.0*0.8(=4.0) 이므로 경고는 발생하지만 타임아웃은 아님
        with pytest.warns(UserWarning, match="불안정"):
            result = check_sensor_connection("TEMP-001", response_time=5.0)
        assert result == "connected"
