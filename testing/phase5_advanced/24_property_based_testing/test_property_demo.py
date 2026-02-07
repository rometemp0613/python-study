"""
속성 기반 테스트 데모.

이 파일에는 예제 기반 테스트만 포함한다 (항상 실행).
Hypothesis 기반 속성 테스트는 test_property_hypothesis.py에 있다.

실행 방법:
    pytest test_property_demo.py -v
"""

import pytest
import math

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
# 예제 기반 테스트 (항상 실행)
# =============================================================================

class TestNormalizeExampleBased:
    """normalize() 예제 기반 테스트"""

    def test_basic_normalization(self):
        """기본 정규화 검증"""
        result = normalize([1.0, 2.0, 3.0])
        assert result == [pytest.approx(0.0), pytest.approx(0.5), pytest.approx(1.0)]

    def test_negative_values(self):
        """음수 포함 정규화"""
        result = normalize([-10.0, 0.0, 10.0])
        assert result == [pytest.approx(0.0), pytest.approx(0.5), pytest.approx(1.0)]

    def test_result_range(self):
        """결과가 0~1 범위인지 검증"""
        result = normalize([5.0, 1.0, 3.0, 9.0, 7.0])
        assert all(0.0 <= v <= 1.0 for v in result)

    def test_preserves_length(self):
        """입력과 출력 길이가 동일"""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        result = normalize(values)
        assert len(result) == len(values)

    def test_preserves_order(self):
        """순서 관계 보존"""
        values = [3.0, 1.0, 4.0, 1.5, 9.0]
        result = normalize(values)
        # 원본에서 a < b이면 정규화 후에도 a < b
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                if values[i] < values[j]:
                    assert result[i] < result[j]
                elif values[i] > values[j]:
                    assert result[i] > result[j]

    def test_min_maps_to_zero(self):
        """최솟값은 0.0"""
        result = normalize([5.0, 3.0, 8.0, 1.0, 6.0])
        assert min(result) == pytest.approx(0.0)

    def test_max_maps_to_one(self):
        """최댓값은 1.0"""
        result = normalize([5.0, 3.0, 8.0, 1.0, 6.0])
        assert max(result) == pytest.approx(1.0)

    def test_too_few_values(self):
        """값이 2개 미만이면 에러"""
        with pytest.raises(ValueError, match="최소 2개"):
            normalize([1.0])

    def test_all_same_values(self):
        """모든 값이 같으면 에러"""
        with pytest.raises(ValueError, match="동일하면"):
            normalize([5.0, 5.0, 5.0])


class TestEncodeDecodeExampleBased:
    """인코딩/디코딩 예제 기반 테스트"""

    def test_encode_temperature(self):
        """온도 센서 인코딩"""
        assert encode_sensor_type("temperature") == 1

    def test_decode_temperature(self):
        """온도 센서 코드 디코딩"""
        assert decode_sensor_type(1) == "temperature"

    def test_roundtrip(self):
        """모든 센서 타입의 왕복 테스트"""
        for sensor_type in SENSOR_TYPE_MAP:
            code = encode_sensor_type(sensor_type)
            decoded = decode_sensor_type(code)
            assert decoded == sensor_type

    def test_encode_unknown(self):
        """알 수 없는 센서 타입"""
        with pytest.raises(ValueError, match="알 수 없는 센서 타입"):
            encode_sensor_type("unknown")

    def test_decode_unknown(self):
        """알 수 없는 코드"""
        with pytest.raises(ValueError, match="알 수 없는 센서 코드"):
            decode_sensor_type(999)


class TestValidateReadingExampleBased:
    """validate_reading() 예제 기반 테스트"""

    def test_valid_reading(self):
        """유효 범위 내 값"""
        result = validate_reading(50.0, 0.0, 100.0)
        assert result["is_valid"] is True
        assert result["deviation"] == 0.0
        assert result["status"] == "normal"

    def test_below_range(self):
        """하한 미만"""
        result = validate_reading(-5.0, 0.0, 100.0)
        assert result["is_valid"] is False
        assert result["deviation"] == pytest.approx(5.0)
        assert result["status"] == "below_range"

    def test_above_range(self):
        """상한 초과"""
        result = validate_reading(105.0, 0.0, 100.0)
        assert result["is_valid"] is False
        assert result["deviation"] == pytest.approx(5.0)
        assert result["status"] == "above_range"

    def test_boundary_min(self):
        """경계값: 최솟값"""
        result = validate_reading(0.0, 0.0, 100.0)
        assert result["is_valid"] is True

    def test_boundary_max(self):
        """경계값: 최댓값"""
        result = validate_reading(100.0, 0.0, 100.0)
        assert result["is_valid"] is True

    def test_invalid_range(self):
        """최솟값 > 최댓값"""
        with pytest.raises(ValueError, match="최소값"):
            validate_reading(50.0, 100.0, 0.0)


class TestAggregateReadingsExampleBased:
    """aggregate_readings() 예제 기반 테스트"""

    def test_basic_aggregation(self):
        """기본 집계"""
        result = aggregate_readings([1.0, 2.0, 3.0, 4.0, 5.0])
        assert result["count"] == 5
        assert result["sum"] == pytest.approx(15.0)
        assert result["mean"] == pytest.approx(3.0)
        assert result["min_val"] == pytest.approx(1.0)
        assert result["max_val"] == pytest.approx(5.0)
        assert result["range"] == pytest.approx(4.0)

    def test_mean_equals_sum_div_count(self):
        """mean == sum / count 검증"""
        result = aggregate_readings([10.0, 20.0, 30.0])
        assert result["mean"] == pytest.approx(result["sum"] / result["count"])

    def test_empty_raises(self):
        """빈 리스트"""
        with pytest.raises(ValueError, match="빈 측정값"):
            aggregate_readings([])


class TestClampExampleBased:
    """clamp() 예제 기반 테스트"""

    def test_within_range(self):
        """범위 내 값은 변경 없음"""
        assert clamp(5.0, 0.0, 10.0) == 5.0

    def test_below_min(self):
        """하한 미만 → 하한으로 제한"""
        assert clamp(-5.0, 0.0, 10.0) == 0.0

    def test_above_max(self):
        """상한 초과 → 상한으로 제한"""
        assert clamp(15.0, 0.0, 10.0) == 10.0

    def test_invalid_range(self):
        """최솟값 > 최댓값"""
        with pytest.raises(ValueError):
            clamp(5.0, 10.0, 0.0)
