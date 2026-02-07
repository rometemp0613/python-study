"""
속성 기반 테스트 - Hypothesis 라이브러리 사용.

이 파일은 Hypothesis가 설치되어 있을 때만 실행된다.
설치되지 않은 경우 전체 파일이 skip된다.

설치 방법:
    pip install hypothesis

실행 방법:
    pytest test_property_hypothesis.py -v
    pytest test_property_hypothesis.py -v --hypothesis-show-statistics
"""

import pytest

# hypothesis가 설치되어 있지 않으면 이 파일 전체를 skip
hypothesis = pytest.importorskip("hypothesis", reason="hypothesis가 설치되지 않음")

from hypothesis import given, assume, settings
from hypothesis import strategies as st

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
# normalize() 속성 기반 테스트
# =============================================================================

class TestNormalizePropertyBased:
    """normalize() 속성 기반 테스트"""

    @given(
        st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=100,
        )
    )
    def test_result_in_zero_one_range(self, values):
        """속성: 결과의 모든 값은 0 이상 1 이하이다"""
        assume(min(values) != max(values))
        result = normalize(values)
        assert all(0.0 <= v <= 1.0 for v in result)

    @given(
        st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=100,
        )
    )
    def test_preserves_length(self, values):
        """속성: 결과 길이 == 입력 길이"""
        assume(min(values) != max(values))
        result = normalize(values)
        assert len(result) == len(values)

    @given(
        st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=100,
        )
    )
    def test_min_maps_to_zero(self, values):
        """속성: 최솟값은 0.0으로 매핑된다"""
        assume(min(values) != max(values))
        result = normalize(values)
        assert min(result) == pytest.approx(0.0, abs=1e-10)

    @given(
        st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=100,
        )
    )
    def test_max_maps_to_one(self, values):
        """속성: 최댓값은 1.0으로 매핑된다"""
        assume(min(values) != max(values))
        result = normalize(values)
        assert max(result) == pytest.approx(1.0, abs=1e-10)


# =============================================================================
# encode/decode 속성 기반 테스트
# =============================================================================

class TestEncodeDecodePropertyBased:
    """인코딩/디코딩 속성 기반 테스트"""

    @given(st.sampled_from(list(SENSOR_TYPE_MAP.keys())))
    def test_roundtrip_encode_decode(self, sensor_type):
        """왕복 속성: encode -> decode하면 원본과 동일"""
        code = encode_sensor_type(sensor_type)
        decoded = decode_sensor_type(code)
        assert decoded == sensor_type

    @given(st.sampled_from(list(SENSOR_TYPE_MAP.values())))
    def test_roundtrip_decode_encode(self, code):
        """왕복 속성: decode -> encode하면 원본과 동일"""
        sensor_type = decode_sensor_type(code)
        re_encoded = encode_sensor_type(sensor_type)
        assert re_encoded == code

    @given(st.sampled_from(list(SENSOR_TYPE_MAP.keys())))
    def test_encode_returns_positive_int(self, sensor_type):
        """속성: 인코딩 결과는 양의 정수"""
        code = encode_sensor_type(sensor_type)
        assert isinstance(code, int)
        assert code > 0


# =============================================================================
# validate_reading() 속성 기반 테스트
# =============================================================================

class TestValidateReadingPropertyBased:
    """validate_reading() 속성 기반 테스트"""

    @given(
        st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-1000, max_value=0, allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
    )
    def test_deviation_non_negative(self, value, min_val, max_val):
        """속성: deviation은 항상 0 이상"""
        assume(min_val <= max_val)
        result = validate_reading(value, min_val, max_val)
        assert result["deviation"] >= 0

    @given(
        st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-100, max_value=0, allow_nan=False, allow_infinity=False),
        st.floats(min_value=100, max_value=200, allow_nan=False, allow_infinity=False),
    )
    def test_in_range_is_valid(self, value, min_val, max_val):
        """속성: min <= value <= max이면 is_valid == True"""
        assume(min_val <= max_val)
        assume(min_val <= value <= max_val)
        result = validate_reading(value, min_val, max_val)
        assert result["is_valid"] is True
        assert result["status"] == "normal"


# =============================================================================
# aggregate_readings() 속성 기반 테스트
# =============================================================================

class TestAggregateReadingsPropertyBased:
    """aggregate_readings() 속성 기반 테스트"""

    @given(
        st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=100,
        )
    )
    def test_count_equals_length(self, readings):
        """속성: count == len(readings)"""
        result = aggregate_readings(readings)
        assert result["count"] == len(readings)

    @given(
        st.lists(
            st.floats(min_value=-1e4, max_value=1e4, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=100,
        )
    )
    def test_mean_equals_sum_div_count(self, readings):
        """동치 속성: mean == sum / count"""
        result = aggregate_readings(readings)
        assert result["mean"] == pytest.approx(
            result["sum"] / result["count"], rel=1e-9
        )

    @given(
        st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=100,
        )
    )
    def test_min_le_mean_le_max(self, readings):
        """속성: min <= mean <= max"""
        result = aggregate_readings(readings)
        assert result["min_val"] <= result["mean"] + 1e-10
        assert result["mean"] <= result["max_val"] + 1e-10

    @given(
        st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=100,
        )
    )
    def test_range_non_negative(self, readings):
        """속성: range >= 0"""
        result = aggregate_readings(readings)
        assert result["range"] >= -1e-10


# =============================================================================
# clamp() 속성 기반 테스트
# =============================================================================

class TestClampPropertyBased:
    """clamp() 속성 기반 테스트"""

    @given(
        st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-1000, max_value=0, allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
    )
    def test_result_in_range(self, value, min_val, max_val):
        """속성: 결과는 항상 [min_val, max_val] 범위"""
        assume(min_val <= max_val)
        result = clamp(value, min_val, max_val)
        assert min_val <= result <= max_val

    @given(
        st.floats(min_value=0, max_value=50, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-100, max_value=0, allow_nan=False, allow_infinity=False),
        st.floats(min_value=50, max_value=200, allow_nan=False, allow_infinity=False),
    )
    def test_idempotent(self, value, min_val, max_val):
        """멱등성 속성: clamp(clamp(x)) == clamp(x)"""
        assume(min_val <= max_val)
        once = clamp(value, min_val, max_val)
        twice = clamp(once, min_val, max_val)
        assert once == twice
