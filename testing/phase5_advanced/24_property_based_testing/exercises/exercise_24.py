"""
연습문제 24: Property-Based Testing (속성 기반 테스트)

이 연습에서는 함수의 불변 속성을 식별하고 테스트로 작성한다.
Hypothesis가 없어도 예제 기반으로 작성 가능하다.
TODO 부분을 채워서 테스트를 완성하라.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_data_transforms import (
    normalize,
    encode_sensor_type,
    decode_sensor_type,
    validate_reading,
    aggregate_readings,
    clamp,
    SENSOR_TYPE_MAP,
)


# =============================================================================
# 연습 1: validate_reading의 불변 속성
# =============================================================================

class TestValidateReadingProperties:
    """
    validate_reading() 함수의 불변 속성을 테스트하라.

    최소 3가지 속성을 검증해야 한다:
    1. is_valid == True이면 deviation == 0
    2. is_valid == False이면 deviation > 0
    3. 결과에는 항상 필수 키가 포함된다
    """

    def test_valid_implies_zero_deviation(self):
        """
        TODO: 유효한 값이면 deviation이 0인지 검증하라.

        힌트: 여러 범위 내 값으로 테스트
        """
        pytest.skip("TODO: valid → deviation==0 속성을 테스트하세요")

    def test_invalid_implies_positive_deviation(self):
        """
        TODO: 유효하지 않은 값이면 deviation이 양수인지 검증하라.

        힌트: 범위 밖의 값으로 테스트 (above, below 모두)
        """
        pytest.skip("TODO: invalid → deviation>0 속성을 테스트하세요")

    def test_result_always_has_required_keys(self):
        """
        TODO: 어떤 입력이든 결과에 필수 키가 있는지 검증하라.

        필수 키: "is_valid", "value", "deviation", "status"

        힌트: 여러 종류의 입력으로 테스트
        """
        pytest.skip("TODO: 필수 키 존재 속성을 테스트하세요")


# =============================================================================
# 연습 2: encode/decode 왕복 속성
# =============================================================================

class TestEncodeDecodeRoundtrip:
    """
    encode_sensor_type()과 decode_sensor_type()의
    왕복(roundtrip) 속성을 테스트하라.
    """

    def test_all_types_roundtrip(self):
        """
        TODO: 모든 센서 타입에 대해
        decode(encode(type)) == type을 검증하라.

        힌트: SENSOR_TYPE_MAP의 모든 키를 순회
        """
        pytest.skip("TODO: encode→decode 왕복을 테스트하세요")

    def test_all_codes_roundtrip(self):
        """
        TODO: 모든 센서 코드에 대해
        encode(decode(code)) == code를 검증하라.

        힌트: SENSOR_TYPE_MAP의 모든 값을 순회
        """
        pytest.skip("TODO: decode→encode 왕복을 테스트하세요")

    def test_encode_result_is_unique(self):
        """
        TODO: 서로 다른 센서 타입이 서로 다른 코드를 가지는지 검증하라.

        힌트: 모든 코드를 집합(set)에 넣고 길이 비교
        """
        pytest.skip("TODO: 인코딩 유일성을 테스트하세요")


# =============================================================================
# 연습 3: aggregate_readings의 동치 속성
# =============================================================================

class TestAggregateEquivalence:
    """
    aggregate_readings()의 동치(equivalence) 속성을 테스트하라.
    """

    def test_mean_consistency(self):
        """
        TODO: mean == sum / count 동치 속성을 검증하라.

        힌트: 여러 리스트로 테스트
        """
        pytest.skip("TODO: mean 동치 속성을 테스트하세요")

    def test_range_consistency(self):
        """
        TODO: range == max_val - min_val 동치 속성을 검증하라.

        힌트: 여러 리스트로 테스트
        """
        pytest.skip("TODO: range 동치 속성을 테스트하세요")

    def test_single_element(self):
        """
        TODO: 원소가 1개인 경우의 속성을 검증하라.
        - mean == sum == min_val == max_val == 그 값 자체
        - range == 0
        - count == 1
        """
        pytest.skip("TODO: 단일 원소 속성을 테스트하세요")
