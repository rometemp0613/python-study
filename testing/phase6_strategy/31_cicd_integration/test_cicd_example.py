"""
CI/CD용 테스트 파일

CI 파이프라인에서 실행되는 테스트입니다.
JUnit XML 출력과 호환되며, 마커를 사용하여 테스트를 분류합니다.

실행 방법:
    # 일반 실행
    pytest test_cicd_example.py -v

    # JUnit XML 출력
    pytest test_cicd_example.py -v --junitxml=test-results.xml

    # 커버리지와 함께
    pytest test_cicd_example.py --cov=src_cicd_example --cov-report=term-missing

    # 특정 마커만 실행
    pytest test_cicd_example.py -v -m unit
    pytest test_cicd_example.py -v -m "not slow"
"""

import pytest
from src_cicd_example import (
    validate_sensor_reading,
    calculate_health_score,
    classify_equipment_status,
    generate_maintenance_report,
    batch_validate_readings,
)


# =============================================================================
# 단위 테스트: 센서 측정값 검증
# =============================================================================

class TestValidateSensorReading:
    """센서 측정값 유효성 검증 테스트"""

    def test_유효한_온도값(self):
        """정상 범위의 온도값은 유효해야 한다."""
        assert validate_sensor_reading(25.0, "temperature") is True
        assert validate_sensor_reading(0.0, "temperature") is True
        assert validate_sensor_reading(500.0, "temperature") is True

    def test_유효하지_않은_온도값(self):
        """범위를 벗어나는 온도값은 유효하지 않아야 한다."""
        assert validate_sensor_reading(-100.0, "temperature") is False
        assert validate_sensor_reading(600.0, "temperature") is False

    def test_유효한_압력값(self):
        """정상 범위의 압력값은 유효해야 한다."""
        assert validate_sensor_reading(500.0, "pressure") is True
        assert validate_sensor_reading(0.0, "pressure") is True

    def test_유효한_진동값(self):
        """정상 범위의 진동값은 유효해야 한다."""
        assert validate_sensor_reading(5.0, "vibration") is True

    def test_알수없는_센서종류_에러(self):
        """알 수 없는 센서 종류는 ValueError를 발생시켜야 한다."""
        with pytest.raises(ValueError, match="알 수 없는 센서 종류"):
            validate_sensor_reading(25.0, "unknown_sensor")

    @pytest.mark.parametrize("value,sensor_type,expected", [
        (25.0, "temperature", True),
        (-100.0, "temperature", False),
        (500.0, "pressure", True),
        (-1.0, "pressure", False),
        (50.0, "vibration", True),
        (200.0, "vibration", False),
    ])
    def test_다양한_센서값_매개변수화(self, value, sensor_type, expected):
        """매개변수화된 테스트로 다양한 입력 검증"""
        assert validate_sensor_reading(value, sensor_type) == expected


# =============================================================================
# 단위 테스트: 건강 점수 계산
# =============================================================================

class TestCalculateHealthScore:
    """장비 건강 점수 계산 테스트"""

    def test_정상_건강_점수(self):
        """기준선과 동일한 측정값은 높은 건강 점수를 반환해야 한다."""
        readings = [100.0, 100.0, 100.0]
        score = calculate_health_score(readings, baseline_mean=100.0, baseline_std=5.0)
        assert score == pytest.approx(1.0, abs=0.01)

    def test_악화된_건강_점수(self):
        """기준선에서 벗어난 측정값은 낮은 건강 점수를 반환해야 한다."""
        readings = [120.0, 125.0, 130.0]  # 기준선(100)에서 크게 벗어남
        score = calculate_health_score(readings, baseline_mean=100.0, baseline_std=5.0)
        assert score < 0.5

    def test_빈_리스트_에러(self):
        """빈 리스트는 ValueError를 발생시켜야 한다."""
        with pytest.raises(ValueError, match="비어 있습니다"):
            calculate_health_score([], baseline_mean=100.0, baseline_std=5.0)

    def test_기준선_표준편차_0_에러(self):
        """기준선 표준편차가 0이면 ValueError를 발생시켜야 한다."""
        with pytest.raises(ValueError, match="0보다 커야"):
            calculate_health_score([100.0], baseline_mean=100.0, baseline_std=0.0)

    def test_건강점수_범위(self):
        """건강 점수는 항상 0.0~1.0 사이여야 한다."""
        # 매우 큰 편차
        readings = [1000.0, 1000.0]
        score = calculate_health_score(readings, baseline_mean=100.0, baseline_std=5.0)
        assert 0.0 <= score <= 1.0


# =============================================================================
# 단위 테스트: 장비 상태 분류
# =============================================================================

class TestClassifyEquipmentStatus:
    """장비 상태 분류 테스트"""

    @pytest.mark.parametrize("score,expected_status", [
        (1.0, "good"),
        (0.8, "good"),
        (0.79, "warning"),
        (0.5, "warning"),
        (0.49, "critical"),
        (0.2, "critical"),
        (0.19, "failure"),
        (0.0, "failure"),
    ])
    def test_점수별_상태분류(self, score, expected_status):
        """건강 점수에 따라 올바른 상태가 반환되어야 한다."""
        assert classify_equipment_status(score) == expected_status


# =============================================================================
# 통합 테스트: 유지보수 보고서 생성
# =============================================================================

class TestGenerateMaintenanceReport:
    """유지보수 보고서 생성 통합 테스트"""

    def test_정상_장비_보고서(self):
        """정상 장비의 보고서는 'good' 상태여야 한다."""
        readings = [100.0, 101.0, 99.0, 100.5, 99.5]
        report = generate_maintenance_report(
            equipment_id="pump-001",
            readings=readings,
            baseline_mean=100.0,
            baseline_std=5.0,
        )

        assert report["equipment_id"] == "pump-001"
        assert report["status"] == "good"
        assert report["health_score"] > 0.8
        assert report["reading_count"] == 5
        assert "정상 운전" in report["recommendation"]

    def test_경고_장비_보고서(self):
        """기준선에서 벗어난 장비의 보고서는 'warning' 이상이어야 한다."""
        readings = [115.0, 118.0, 116.0, 117.0]
        report = generate_maintenance_report(
            equipment_id="motor-002",
            readings=readings,
            baseline_mean=100.0,
            baseline_std=5.0,
        )

        assert report["equipment_id"] == "motor-002"
        assert report["status"] in ["warning", "critical"]
        assert "recommendation" in report

    def test_보고서_필수_필드(self):
        """보고서에 필수 필드가 포함되어야 한다."""
        readings = [100.0, 100.0]
        report = generate_maintenance_report(
            equipment_id="test-001",
            readings=readings,
            baseline_mean=100.0,
            baseline_std=5.0,
        )

        required_fields = [
            "equipment_id", "health_score", "status",
            "current_mean", "current_std",
            "baseline_mean", "baseline_std",
            "reading_count", "recommendation",
        ]
        for field in required_fields:
            assert field in report, f"필수 필드 누락: {field}"


# =============================================================================
# 단위 테스트: 일괄 검증
# =============================================================================

class TestBatchValidateReadings:
    """일괄 센서 검증 테스트"""

    def test_모두_유효한_경우(self):
        """모든 측정값이 유효한 경우"""
        readings = [
            ("temp-001", 25.0, "temperature"),
            ("press-001", 500.0, "pressure"),
            ("vib-001", 5.0, "vibration"),
        ]

        result = batch_validate_readings(readings)

        assert len(result["valid"]) == 3
        assert len(result["invalid"]) == 0

    def test_일부_유효하지_않은_경우(self):
        """일부 측정값이 유효하지 않은 경우"""
        readings = [
            ("temp-001", 25.0, "temperature"),    # 유효
            ("temp-002", 600.0, "temperature"),   # 범위 초과
        ]

        result = batch_validate_readings(readings)

        assert len(result["valid"]) == 1
        assert len(result["invalid"]) == 1

    def test_알수없는_센서종류_처리(self):
        """알 수 없는 센서 종류도 정상 처리되어야 한다."""
        readings = [
            ("unknown-001", 25.0, "unknown_type"),
        ]

        result = batch_validate_readings(readings)

        assert len(result["invalid"]) == 1
        assert "알 수 없는 센서 종류" in result["invalid"][0]["reason"]
