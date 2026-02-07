"""
연습문제 24 정답: Property-Based Testing

각 연습의 완성된 풀이. 예제 기반으로 속성을 검증한다.
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
# 연습 1 정답: validate_reading의 불변 속성
# =============================================================================

class TestValidateReadingProperties:
    """validate_reading() 함수의 불변 속성 테스트"""

    def test_valid_implies_zero_deviation(self):
        """속성: is_valid == True → deviation == 0"""
        # 다양한 범위 내 값으로 테스트
        test_cases = [
            (50.0, 0.0, 100.0),     # 중간값
            (0.0, 0.0, 100.0),      # 경계: 최솟값
            (100.0, 0.0, 100.0),    # 경계: 최댓값
            (-5.0, -10.0, 10.0),    # 음수 포함
            (0.0, 0.0, 0.0),        # 범위가 0인 경우
        ]
        for value, min_val, max_val in test_cases:
            result = validate_reading(value, min_val, max_val)
            if result["is_valid"]:
                assert result["deviation"] == 0.0, (
                    f"is_valid=True인데 deviation={result['deviation']}"
                    f" (value={value}, range=[{min_val}, {max_val}])"
                )

    def test_invalid_implies_positive_deviation(self):
        """속성: is_valid == False → deviation > 0"""
        test_cases = [
            (-5.0, 0.0, 100.0),    # 하한 미만
            (105.0, 0.0, 100.0),   # 상한 초과
            (-100.0, -50.0, 50.0), # 큰 이탈
            (200.0, 0.0, 10.0),    # 매우 큰 이탈
        ]
        for value, min_val, max_val in test_cases:
            result = validate_reading(value, min_val, max_val)
            if not result["is_valid"]:
                assert result["deviation"] > 0, (
                    f"is_valid=False인데 deviation={result['deviation']}"
                    f" (value={value}, range=[{min_val}, {max_val}])"
                )

    def test_result_always_has_required_keys(self):
        """속성: 결과에 항상 필수 키가 존재한다"""
        required_keys = {"is_valid", "value", "deviation", "status"}

        test_cases = [
            (50.0, 0.0, 100.0),    # 정상
            (-5.0, 0.0, 100.0),    # 하한 미만
            (150.0, 0.0, 100.0),   # 상한 초과
            (0.0, 0.0, 0.0),       # 경계
        ]
        for value, min_val, max_val in test_cases:
            result = validate_reading(value, min_val, max_val)
            assert required_keys.issubset(result.keys()), (
                f"필수 키 누락: {required_keys - result.keys()}"
            )


# =============================================================================
# 연습 2 정답: encode/decode 왕복 속성
# =============================================================================

class TestEncodeDecodeRoundtrip:
    """encode/decode 왕복 속성 테스트"""

    def test_all_types_roundtrip(self):
        """모든 센서 타입: decode(encode(type)) == type"""
        for sensor_type in SENSOR_TYPE_MAP.keys():
            code = encode_sensor_type(sensor_type)
            decoded = decode_sensor_type(code)
            assert decoded == sensor_type, (
                f"왕복 실패: {sensor_type} → {code} → {decoded}"
            )

    def test_all_codes_roundtrip(self):
        """모든 센서 코드: encode(decode(code)) == code"""
        for code in SENSOR_TYPE_MAP.values():
            sensor_type = decode_sensor_type(code)
            re_encoded = encode_sensor_type(sensor_type)
            assert re_encoded == code, (
                f"왕복 실패: {code} → {sensor_type} → {re_encoded}"
            )

    def test_encode_result_is_unique(self):
        """서로 다른 센서 타입은 서로 다른 코드를 가진다"""
        codes = set()
        for sensor_type in SENSOR_TYPE_MAP.keys():
            code = encode_sensor_type(sensor_type)
            assert code not in codes, (
                f"중복 코드 발견: {sensor_type} → {code}"
            )
            codes.add(code)

        # 코드 수와 타입 수가 동일해야 한다
        assert len(codes) == len(SENSOR_TYPE_MAP)


# =============================================================================
# 연습 3 정답: aggregate_readings의 동치 속성
# =============================================================================

class TestAggregateEquivalence:
    """aggregate_readings() 동치 속성 테스트"""

    def test_mean_consistency(self):
        """동치 속성: mean == sum / count"""
        test_lists = [
            [1.0, 2.0, 3.0],
            [10.0, 20.0, 30.0, 40.0, 50.0],
            [-5.0, 0.0, 5.0],
            [100.0],
            [1.5, 2.5, 3.5, 4.5],
        ]
        for readings in test_lists:
            result = aggregate_readings(readings)
            expected_mean = result["sum"] / result["count"]
            assert result["mean"] == pytest.approx(expected_mean), (
                f"mean 불일치: {result['mean']} != {expected_mean}"
                f" (readings={readings})"
            )

    def test_range_consistency(self):
        """동치 속성: range == max_val - min_val"""
        test_lists = [
            [1.0, 5.0, 3.0],
            [-10.0, 10.0],
            [7.0, 7.0, 7.0],
            [0.0, 100.0, 50.0],
        ]
        for readings in test_lists:
            result = aggregate_readings(readings)
            expected_range = result["max_val"] - result["min_val"]
            assert result["range"] == pytest.approx(expected_range), (
                f"range 불일치: {result['range']} != {expected_range}"
            )

    def test_single_element(self):
        """단일 원소: mean == sum == min == max == 그 값"""
        test_values = [0.0, 42.0, -7.5, 100.0]
        for val in test_values:
            result = aggregate_readings([val])
            assert result["count"] == 1
            assert result["sum"] == pytest.approx(val)
            assert result["mean"] == pytest.approx(val)
            assert result["min_val"] == pytest.approx(val)
            assert result["max_val"] == pytest.approx(val)
            assert result["range"] == pytest.approx(0.0)
