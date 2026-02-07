"""
연습 문제 05: 풀이

장비 설정 검증 함수에 대한 예외 테스트 풀이.

실행 방법:
    pytest exercises/solution_05.py -v
"""

import pytest
import warnings


# ============================================================
# 커스텀 예외 클래스
# ============================================================

class ConfigError(Exception):
    """설정 관련 기본 예외"""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class InvalidThresholdError(ConfigError):
    """잘못된 임계값 설정"""

    def __init__(self, param_name, value, valid_range):
        self.param_name = param_name
        self.value = value
        self.valid_range = valid_range
        message = (
            f"임계값 '{param_name}'의 값 {value}가 "
            f"유효 범위 {valid_range}를 벗어남"
        )
        super().__init__(message)


class MissingConfigError(ConfigError):
    """필수 설정 누락"""

    def __init__(self, missing_keys):
        self.missing_keys = missing_keys
        message = f"필수 설정이 누락됨: {', '.join(missing_keys)}"
        super().__init__(message)


# ============================================================
# 테스트 대상 함수들
# ============================================================

def validate_config(config):
    """시스템 설정을 검증한다."""
    if not isinstance(config, dict):
        raise TypeError("설정은 딕셔너리여야 합니다")

    required_keys = ["temperature_threshold", "vibration_threshold", "sampling_interval"]
    missing = [k for k in required_keys if k not in config]

    if missing:
        raise MissingConfigError(missing)

    return True


def validate_threshold(param_name, value, min_val, max_val):
    """임계값이 유효 범위 내인지 검증한다."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"'{param_name}' 값은 숫자여야 합니다")

    if value < min_val or value > max_val:
        raise InvalidThresholdError(param_name, value, (min_val, max_val))

    range_span = max_val - min_val
    if value > min_val + range_span * 0.9:
        warnings.warn(
            f"'{param_name}' 값 {value}가 권장 범위의 상한에 근접",
            UserWarning,
        )

    return True


# ============================================================
# 테스트 코드 (풀이)
# ============================================================

class TestValidateConfig:
    """시스템 설정 검증 테스트"""

    def test_유효한_설정(self):
        """유효한 설정은 True를 반환해야 한다"""
        config = {
            "temperature_threshold": 80.0,
            "vibration_threshold": 7.1,
            "sampling_interval": 60,
        }
        assert validate_config(config) is True

    def test_딕셔너리가_아닌_입력(self):
        """딕셔너리가 아닌 입력에 대해 TypeError 발생"""
        with pytest.raises(TypeError, match="딕셔너리"):
            validate_config("not_a_dict")

        with pytest.raises(TypeError):
            validate_config([1, 2, 3])

        with pytest.raises(TypeError):
            validate_config(None)

    def test_필수_키_누락(self):
        """필수 키가 누락되면 MissingConfigError 발생"""
        config = {"temperature_threshold": 80.0}  # 나머지 키 누락

        with pytest.raises(MissingConfigError, match="누락"):
            validate_config(config)

    def test_누락_키_목록_확인(self):
        """ExceptionInfo로 누락된 키 목록을 확인한다"""
        config = {"temperature_threshold": 80.0}

        with pytest.raises(MissingConfigError) as exc_info:
            validate_config(config)

        # 누락된 키 목록 확인
        missing = exc_info.value.missing_keys
        assert "vibration_threshold" in missing
        assert "sampling_interval" in missing
        assert len(missing) == 2

    def test_빈_딕셔너리(self):
        """빈 딕셔너리는 모든 필수 키가 누락됨"""
        with pytest.raises(MissingConfigError) as exc_info:
            validate_config({})

        assert len(exc_info.value.missing_keys) == 3

    def test_예외_메시지에_키_이름_포함(self):
        """에러 메시지에 누락된 키 이름이 포함되어야 한다"""
        with pytest.raises(MissingConfigError, match="vibration_threshold"):
            validate_config({"temperature_threshold": 80.0, "sampling_interval": 60})


class TestValidateThreshold:
    """임계값 검증 테스트"""

    def test_유효한_임계값(self):
        """유효 범위 내의 값은 True를 반환해야 한다"""
        assert validate_threshold("temperature", 80, 0, 200) is True
        assert validate_threshold("vibration", 7.1, 0, 50) is True
        assert validate_threshold("pressure", 14.7, 0, 100) is True

    def test_경계값(self):
        """경계값도 유효하다"""
        assert validate_threshold("temperature", 0, 0, 200) is True
        assert validate_threshold("temperature", 200, 0, 200) is True

    def test_범위_초과_상한(self):
        """상한을 초과한 값에 대해 InvalidThresholdError 발생"""
        with pytest.raises(InvalidThresholdError) as exc_info:
            validate_threshold("temperature", 250, 0, 200)

        assert exc_info.value.param_name == "temperature"
        assert exc_info.value.value == 250
        assert exc_info.value.valid_range == (0, 200)

    def test_범위_초과_하한(self):
        """하한 미만의 값에 대해 InvalidThresholdError 발생"""
        with pytest.raises(InvalidThresholdError) as exc_info:
            validate_threshold("temperature", -10, 0, 200)

        assert exc_info.value.value == -10

    def test_상한_근접_경고(self):
        """상한에 근접한 값에 대해 경고 발생"""
        # 범위 0~200, 90% = 180 이상이면 경고
        with pytest.warns(UserWarning, match="상한에 근접"):
            validate_threshold("temperature", 190, 0, 200)

    def test_타입_오류(self):
        """숫자가 아닌 값에 대해 TypeError 발생"""
        with pytest.raises(TypeError, match="숫자"):
            validate_threshold("temperature", "hot", 0, 200)

    def test_예외_계층(self):
        """InvalidThresholdError가 ConfigError의 하위 클래스인지 확인"""
        # 상위 예외 클래스로도 잡을 수 있다
        with pytest.raises(ConfigError):
            validate_threshold("temperature", 250, 0, 200)

    def test_에러_메시지_내용(self):
        """에러 메시지에 파라미터 이름과 값이 포함되어야 한다"""
        with pytest.raises(InvalidThresholdError, match="temperature"):
            validate_threshold("temperature", 250, 0, 200)

        with pytest.raises(InvalidThresholdError, match="250"):
            validate_threshold("temperature", 250, 0, 200)
