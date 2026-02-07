"""
연습 문제 05: 예외와 에러 핸들링 테스트

장비 설정 검증 함수에 대한 예외 테스트를 작성하세요.
pytest.raises(), match, ExceptionInfo를 활용합니다.

실행 방법:
    pytest exercises/exercise_05.py -v
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
    """시스템 설정을 검증한다.

    Args:
        config: 설정 딕셔너리

    Returns:
        True (검증 통과)

    Raises:
        TypeError: config가 딕셔너리가 아닐 때
        MissingConfigError: 필수 키가 누락되었을 때
    """
    if not isinstance(config, dict):
        raise TypeError("설정은 딕셔너리여야 합니다")

    required_keys = ["temperature_threshold", "vibration_threshold", "sampling_interval"]
    missing = [k for k in required_keys if k not in config]

    if missing:
        raise MissingConfigError(missing)

    return True


def validate_threshold(param_name, value, min_val, max_val):
    """임계값이 유효 범위 내인지 검증한다.

    Args:
        param_name: 파라미터 이름
        value: 설정값
        min_val: 최소값
        max_val: 최대값

    Returns:
        True (검증 통과)

    Raises:
        InvalidThresholdError: 값이 유효 범위를 벗어날 때
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"'{param_name}' 값은 숫자여야 합니다")

    if value < min_val or value > max_val:
        raise InvalidThresholdError(param_name, value, (min_val, max_val))

    # 극단적인 값에 대한 경고
    range_span = max_val - min_val
    if value > min_val + range_span * 0.9:
        warnings.warn(
            f"'{param_name}' 값 {value}가 권장 범위의 상한에 근접",
            UserWarning,
        )

    return True


# ============================================================
# TODO: 아래에 테스트를 작성하세요
# ============================================================

class TestValidateConfig:
    """시스템 설정 검증 테스트"""

    def test_유효한_설정(self):
        """유효한 설정은 True를 반환해야 한다"""
        # TODO: 모든 필수 키가 있는 딕셔너리로 테스트
        pytest.skip("TODO: 유효한 설정 테스트를 구현하세요")

    def test_딕셔너리가_아닌_입력(self):
        """딕셔너리가 아닌 입력에 대해 TypeError 발생"""
        # TODO: pytest.raises(TypeError) 사용
        pytest.skip("TODO: 타입 에러 테스트를 구현하세요")

    def test_필수_키_누락(self):
        """필수 키가 누락되면 MissingConfigError 발생"""
        # TODO: pytest.raises와 match를 사용하세요
        # 힌트: 누락된 키 이름이 에러 메시지에 포함되는지 확인
        pytest.skip("TODO: 필수 키 누락 테스트를 구현하세요")

    def test_누락_키_목록_확인(self):
        """ExceptionInfo로 누락된 키 목록을 확인한다"""
        # TODO: exc_info.value.missing_keys를 확인하세요
        pytest.skip("TODO: 누락 키 목록 테스트를 구현하세요")


class TestValidateThreshold:
    """임계값 검증 테스트"""

    def test_유효한_임계값(self):
        """유효 범위 내의 값은 True를 반환해야 한다"""
        # TODO: validate_threshold("temperature", 80, 0, 200) 테스트
        pytest.skip("TODO: 유효한 임계값 테스트를 구현하세요")

    def test_범위_초과(self):
        """범위를 벗어난 값에 대해 InvalidThresholdError 발생"""
        # TODO: pytest.raises와 exc_info를 사용하여
        # param_name, value, valid_range 속성을 확인하세요
        pytest.skip("TODO: 범위 초과 테스트를 구현하세요")

    def test_상한_근접_경고(self):
        """상한에 근접한 값에 대해 경고 발생"""
        # TODO: pytest.warns(UserWarning) 사용
        # 힌트: 범위의 90% 이상인 값을 설정
        pytest.skip("TODO: 상한 근접 경고 테스트를 구현하세요")

    def test_타입_오류(self):
        """숫자가 아닌 값에 대해 TypeError 발생"""
        # TODO: 문자열 값으로 테스트
        pytest.skip("TODO: 타입 오류 테스트를 구현하세요")

    def test_예외_계층(self):
        """InvalidThresholdError가 ConfigError의 하위 클래스인지 확인"""
        # TODO: pytest.raises(ConfigError)로 InvalidThresholdError를 잡을 수 있는지
        pytest.skip("TODO: 예외 계층 테스트를 구현하세요")
