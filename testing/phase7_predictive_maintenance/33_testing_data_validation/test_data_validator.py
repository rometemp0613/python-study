"""
센서 데이터 유효성 검증 테스트 모듈

SensorDataValidator 클래스의 모든 검증 기능을 테스트합니다:
- 스키마 검증
- 물리적 범위 검증
- 시계열 갭 탐지
- 데이터 완전성 검증
- 단일 리딩 종합 검증
"""

import pytest
from datetime import datetime, timedelta
from src_data_validator import (
    SensorDataValidator,
    ValidationResult,
    SENSOR_RANGES,
)


# ============================================================
# 픽스처
# ============================================================

@pytest.fixture
def validator():
    """SensorDataValidator 인스턴스"""
    return SensorDataValidator()


@pytest.fixture
def valid_reading():
    """유효한 센서 리딩 데이터"""
    return {
        "timestamp": datetime(2024, 6, 15, 10, 30, 0),
        "sensor_type": "temperature",
        "value": 25.0,
    }


@pytest.fixture
def continuous_timestamps():
    """연속적인 1초 간격 타임스탬프 (60개)"""
    base = datetime(2024, 6, 15, 10, 0, 0)
    return [base + timedelta(seconds=i) for i in range(60)]


@pytest.fixture
def gapped_timestamps():
    """중간에 갭이 있는 타임스탬프"""
    base = datetime(2024, 6, 15, 10, 0, 0)
    # 0~9초: 정상
    ts = [base + timedelta(seconds=i) for i in range(10)]
    # 30~39초: 20초 갭 후 재개
    ts.extend([base + timedelta(seconds=30 + i) for i in range(10)])
    # 60~69초: 21초 갭 후 재개
    ts.extend([base + timedelta(seconds=60 + i) for i in range(10)])
    return ts


# ============================================================
# ValidationResult 테스트
# ============================================================

class TestValidationResult:
    """ValidationResult 데이터클래스 테스트"""

    def test_기본값_유효(self):
        """기본 생성 시 is_valid=True"""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_에러_추가(self):
        """에러를 추가하면 리스트에 포함됨"""
        result = ValidationResult(is_valid=False)
        result.errors.append("테스트 에러")
        assert len(result.errors) == 1
        assert result.errors[0] == "테스트 에러"

    def test_독립적인_인스턴스(self):
        """각 인스턴스는 독립적인 errors/warnings 리스트를 가짐"""
        result1 = ValidationResult()
        result2 = ValidationResult()
        result1.errors.append("에러1")

        assert len(result2.errors) == 0


# ============================================================
# 스키마 검증 테스트
# ============================================================

class TestValidateSchema:
    """스키마(컬럼/타입) 검증 테스트"""

    def test_유효한_스키마(self, validator):
        """모든 컬럼과 타입이 일치하는 경우"""
        data = {
            "timestamp": 1000.0,
            "temperature": 25.0,
            "vibration": 0.5,
        }
        expected = {
            "timestamp": float,
            "temperature": float,
            "vibration": float,
        }

        result = validator.validate_schema(data, expected)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_컬럼_누락(self, validator):
        """필수 컬럼이 누락된 경우"""
        data = {"timestamp": 1000.0}
        expected = {
            "timestamp": float,
            "temperature": float,
        }

        result = validator.validate_schema(data, expected)

        assert result.is_valid is False
        assert any("temperature" in e for e in result.errors)

    def test_타입_불일치(self, validator):
        """컬럼 타입이 예상과 다른 경우"""
        data = {
            "timestamp": 1000.0,
            "temperature": "hot",  # 문자열인데 float 기대
        }
        expected = {
            "timestamp": float,
            "temperature": float,
        }

        result = validator.validate_schema(data, expected)

        assert result.is_valid is False
        assert any("타입" in e for e in result.errors)

    def test_int값_float_기대시_경고(self, validator):
        """int 값이 float 타입으로 기대될 때 경고만 발생"""
        data = {"value": 25}  # int
        expected = {"value": float}

        result = validator.validate_schema(data, expected)

        # int → float는 자동 변환 가능하므로 에러가 아닌 경고
        assert result.is_valid is True
        assert len(result.warnings) > 0

    def test_추가_컬럼_경고(self, validator):
        """예상하지 않은 추가 컬럼이 있는 경우 경고"""
        data = {
            "timestamp": 1000.0,
            "extra_field": "unexpected",
        }
        expected = {"timestamp": float}

        result = validator.validate_schema(data, expected)

        assert result.is_valid is True
        assert any("예상하지 않은 컬럼" in w for w in result.warnings)

    def test_빈_데이터(self, validator):
        """빈 딕셔너리에 대해 필수 컬럼 누락 에러"""
        data = {}
        expected = {"timestamp": float}

        result = validator.validate_schema(data, expected)

        assert result.is_valid is False

    def test_빈_스키마(self, validator):
        """기대 스키마가 비어있으면 모든 데이터 유효"""
        data = {"anything": "value"}
        expected = {}

        result = validator.validate_schema(data, expected)

        assert result.is_valid is True


# ============================================================
# 물리적 범위 검증 테스트
# ============================================================

class TestValidateRange:
    """물리적 범위 검증 테스트"""

    def test_범위_내_값(self, validator):
        """모든 값이 범위 내인 경우"""
        values = [25.0, 30.0, 35.0, 40.0]
        result = validator.validate_range(values, -40.0, 200.0, "temperature")

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_범위_초과_값(self, validator):
        """범위를 벗어나는 값이 있는 경우"""
        values = [25.0, 300.0, 26.0]
        result = validator.validate_range(values, -40.0, 200.0, "temperature")

        assert result.is_valid is False
        assert any("300.0" in e for e in result.errors)

    def test_범위_미만_값(self, validator):
        """최소값 미만인 경우"""
        values = [25.0, -100.0, 26.0]
        result = validator.validate_range(values, -40.0, 200.0, "temperature")

        assert result.is_valid is False
        assert any("-100.0" in e for e in result.errors)

    def test_경계값_정확히_같은_경우(self, validator):
        """경계값과 정확히 같은 값은 유효"""
        values = [-40.0, 200.0]
        result = validator.validate_range(values, -40.0, 200.0, "temperature")

        assert result.is_valid is True

    def test_None_값_에러(self, validator):
        """None 값이 포함된 경우"""
        values = [25.0, None, 26.0]
        result = validator.validate_range(values, -40.0, 200.0, "temperature")

        assert result.is_valid is False
        assert any("None" in e for e in result.errors)

    def test_빈_값_리스트_경고(self, validator):
        """빈 리스트에 대해 경고"""
        result = validator.validate_range([], -40.0, 200.0, "temperature")

        assert result.is_valid is True  # 에러는 아니지만
        assert len(result.warnings) > 0  # 경고 발생

    def test_극한값_근접_경고(self, validator):
        """범위 내이지만 상한/하한에 근접한 값 경고"""
        # 상한 200에서 10% 이내 = 176 이상
        values = [190.0]
        result = validator.validate_range(values, -40.0, 200.0, "temperature")

        assert result.is_valid is True
        assert any("상한" in w for w in result.warnings)

    def test_진동_센서_범위(self, validator):
        """진동 센서 범위(0~50 mm/s) 검증"""
        values = [0.5, 1.2, 3.5, 10.0]
        result = validator.validate_range(values, 0.0, 50.0, "vibration")

        assert result.is_valid is True

    def test_여러_범위_초과_에러(self, validator):
        """여러 값이 범위를 벗어나는 경우 모든 에러 기록"""
        values = [-100.0, 25.0, 500.0]
        result = validator.validate_range(values, -40.0, 200.0, "temperature")

        assert result.is_valid is False
        assert len(result.errors) == 2  # -100.0과 500.0


# ============================================================
# 시계열 갭 탐지 테스트
# ============================================================

class TestDetectGaps:
    """시계열 갭 탐지 테스트"""

    def test_갭_없는_데이터(self, validator, continuous_timestamps):
        """연속적인 데이터에는 갭 없음"""
        gaps = validator.detect_gaps(continuous_timestamps, max_gap_seconds=5)
        assert len(gaps) == 0

    def test_갭_탐지(self, validator, gapped_timestamps):
        """20초 이상의 갭을 탐지"""
        gaps = validator.detect_gaps(gapped_timestamps, max_gap_seconds=5)

        # 10초→30초 갭과 39초→60초 갭, 총 2개
        assert len(gaps) == 2

    def test_갭_정보_구조(self, validator, gapped_timestamps):
        """갭 정보에 start, end, gap_seconds가 포함"""
        gaps = validator.detect_gaps(gapped_timestamps, max_gap_seconds=5)

        for gap in gaps:
            assert "start" in gap
            assert "end" in gap
            assert "gap_seconds" in gap
            assert isinstance(gap["start"], datetime)
            assert isinstance(gap["end"], datetime)
            assert gap["gap_seconds"] > 5

    def test_허용_갭_이내(self, validator):
        """허용 갭 이내의 간격은 갭으로 탐지하지 않음"""
        base = datetime(2024, 1, 1, 0, 0, 0)
        # 3초 간격 데이터
        ts = [base + timedelta(seconds=i * 3) for i in range(10)]

        gaps = validator.detect_gaps(ts, max_gap_seconds=5)
        assert len(gaps) == 0

    def test_단일_타임스탬프(self, validator):
        """타임스탬프가 1개면 갭 없음"""
        ts = [datetime(2024, 1, 1)]
        gaps = validator.detect_gaps(ts, max_gap_seconds=5)
        assert len(gaps) == 0

    def test_빈_타임스탬프(self, validator):
        """빈 리스트에 대해 갭 없음"""
        gaps = validator.detect_gaps([], max_gap_seconds=5)
        assert len(gaps) == 0

    def test_정확한_갭_크기(self, validator):
        """갭의 크기(초)가 정확한지 검증"""
        base = datetime(2024, 1, 1, 0, 0, 0)
        ts = [
            base,
            base + timedelta(seconds=1),
            base + timedelta(seconds=61),  # 60초 갭
        ]

        gaps = validator.detect_gaps(ts, max_gap_seconds=5)
        assert len(gaps) == 1
        assert gaps[0]["gap_seconds"] == pytest.approx(60.0)


# ============================================================
# 데이터 완전성 검증 테스트
# ============================================================

class TestValidateCompleteness:
    """데이터 완전성 비율 검증 테스트"""

    def test_완전한_데이터_100퍼센트(self, validator, continuous_timestamps):
        """1초 간격 60개 데이터 = 100% 완전"""
        completeness = validator.validate_completeness(
            continuous_timestamps, expected_interval=1
        )
        assert completeness == pytest.approx(100.0)

    def test_갭_있는_데이터_완전성(self, validator, gapped_timestamps):
        """갭이 있는 데이터의 완전성은 100% 미만"""
        completeness = validator.validate_completeness(
            gapped_timestamps, expected_interval=1
        )
        # 70초 범위에 30개 데이터 → 약 42%
        assert completeness < 100.0

    def test_반절_데이터_완전성(self, validator):
        """절반만 있는 데이터의 완전성 ≈ 50%"""
        base = datetime(2024, 1, 1, 0, 0, 0)
        # 10초 범위에 5개 데이터 (1초 간격 기대)
        ts = [base + timedelta(seconds=i * 2) for i in range(5)]
        # 범위: 0~8초, 예상 9개, 실제 5개

        completeness = validator.validate_completeness(
            ts, expected_interval=1
        )
        assert 50.0 <= completeness <= 60.0

    def test_데이터_부족_에러(self, validator):
        """타임스탬프 2개 미만이면 에러"""
        with pytest.raises(ValueError, match="최소 2개"):
            validator.validate_completeness(
                [datetime(2024, 1, 1)], expected_interval=1
            )

    def test_역순_타임스탬프_에러(self, validator):
        """역순 정렬된 타임스탬프에 대해 에러"""
        ts = [
            datetime(2024, 1, 1, 0, 0, 10),
            datetime(2024, 1, 1, 0, 0, 0),
        ]
        with pytest.raises(ValueError, match="시간순"):
            validator.validate_completeness(ts, expected_interval=1)


# ============================================================
# 단일 센서 리딩 검증 테스트
# ============================================================

class TestValidateSensorReading:
    """개별 센서 리딩의 종합 검증 테스트"""

    def test_유효한_리딩(self, validator, valid_reading):
        """모든 조건을 만족하는 유효한 리딩"""
        result = validator.validate_sensor_reading(valid_reading)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_필수_필드_누락_timestamp(self, validator):
        """timestamp 누락"""
        reading = {"sensor_type": "temperature", "value": 25.0}
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is False
        assert any("timestamp" in e for e in result.errors)

    def test_필수_필드_누락_sensor_type(self, validator):
        """sensor_type 누락"""
        reading = {
            "timestamp": datetime(2024, 1, 1),
            "value": 25.0,
        }
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is False
        assert any("sensor_type" in e for e in result.errors)

    def test_필수_필드_누락_value(self, validator):
        """value 누락"""
        reading = {
            "timestamp": datetime(2024, 1, 1),
            "sensor_type": "temperature",
        }
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is False
        assert any("value" in e for e in result.errors)

    def test_알수없는_센서_타입(self, validator):
        """등록되지 않은 센서 타입"""
        reading = {
            "timestamp": datetime(2024, 1, 1),
            "sensor_type": "unknown_sensor",
            "value": 10.0,
        }
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is False
        assert any("알 수 없는 센서" in e for e in result.errors)

    def test_온도_범위_초과(self, validator):
        """온도 값이 물리적 범위 초과"""
        reading = {
            "timestamp": datetime(2024, 1, 1),
            "sensor_type": "temperature",
            "value": 500.0,  # 200도 초과
        }
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is False
        assert any("범위" in e for e in result.errors)

    def test_진동_음수값(self, validator):
        """진동 값이 음수 (물리적 불가)"""
        reading = {
            "timestamp": datetime(2024, 1, 1),
            "sensor_type": "vibration",
            "value": -5.0,
        }
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is False

    def test_유효한_압력_리딩(self, validator):
        """유효한 압력 센서 리딩"""
        reading = {
            "timestamp": datetime(2024, 1, 1),
            "sensor_type": "pressure",
            "value": 100.0,
        }
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is True

    def test_잘못된_timestamp_타입(self, validator):
        """timestamp가 datetime이 아닌 경우"""
        reading = {
            "timestamp": "2024-01-01",  # 문자열
            "sensor_type": "temperature",
            "value": 25.0,
        }
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is False
        assert any("datetime" in e for e in result.errors)

    def test_잘못된_value_타입(self, validator):
        """value가 숫자가 아닌 경우"""
        reading = {
            "timestamp": datetime(2024, 1, 1),
            "sensor_type": "temperature",
            "value": "hot",
        }
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is False
        assert any("숫자" in e for e in result.errors)

    @pytest.mark.parametrize("sensor_type,valid_value", [
        ("temperature", 25.0),
        ("vibration", 5.0),
        ("pressure", 100.0),
        ("current", 50.0),
        ("rpm", 3000.0),
    ])
    def test_모든_센서_타입_유효값(self, validator, sensor_type, valid_value):
        """모든 센서 타입에 대해 유효한 값으로 통과"""
        reading = {
            "timestamp": datetime(2024, 1, 1),
            "sensor_type": sensor_type,
            "value": valid_value,
        }
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is True

    @pytest.mark.parametrize("sensor_type,invalid_value", [
        ("temperature", -50.0),     # -40 미만
        ("vibration", 100.0),       # 50 초과
        ("pressure", -10.0),        # 0 미만
        ("current", 600.0),         # 500 초과
        ("rpm", -100.0),            # 0 미만
    ])
    def test_모든_센서_타입_범위초과(self, validator, sensor_type, invalid_value):
        """모든 센서 타입에 대해 범위 초과 값은 실패"""
        reading = {
            "timestamp": datetime(2024, 1, 1),
            "sensor_type": sensor_type,
            "value": invalid_value,
        }
        result = validator.validate_sensor_reading(reading)

        assert result.is_valid is False


# ============================================================
# SENSOR_RANGES 상수 테스트
# ============================================================

class TestSensorRanges:
    """SENSOR_RANGES 딕셔너리 구조 테스트"""

    def test_필수_센서_타입_등록(self):
        """필수 센서 타입이 모두 등록되어 있는지 확인"""
        required_types = ["temperature", "vibration", "pressure", "current", "rpm"]
        for sensor_type in required_types:
            assert sensor_type in SENSOR_RANGES

    def test_각_센서_범위_구조(self):
        """각 센서 범위에 min, max, unit이 있는지 확인"""
        for sensor_type, range_info in SENSOR_RANGES.items():
            assert "min" in range_info, f"{sensor_type}에 min 없음"
            assert "max" in range_info, f"{sensor_type}에 max 없음"
            assert "unit" in range_info, f"{sensor_type}에 unit 없음"
            assert range_info["min"] < range_info["max"], \
                f"{sensor_type}: min({range_info['min']}) >= max({range_info['max']})"
