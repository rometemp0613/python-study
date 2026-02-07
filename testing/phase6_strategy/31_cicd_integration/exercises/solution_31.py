"""
솔루션 31: CI/CD 환경에서 실행되는 테스트

경계값 테스트, 매개변수화 테스트, 통합 테스트의 완성된 솔루션입니다.

실행 방법:
    pytest exercises/solution_31.py -v
    pytest exercises/solution_31.py -v --junitxml=results.xml
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_cicd_example import (
    validate_sensor_reading,
    calculate_health_score,
    classify_equipment_status,
    generate_maintenance_report,
    batch_validate_readings,
)


# =============================================================================
# 솔루션 1: 경계값 테스트
# =============================================================================

class TestBoundaryValues:
    """경계값 테스트: 유효 범위의 경계에서의 동작을 검증"""

    def test_온도_하한_경계값(self):
        """온도의 유효 범위 하한(-50)에서의 동작"""
        # 경계 안쪽: 유효
        assert validate_sensor_reading(-50.0, "temperature") is True
        # 경계 바깥: 유효하지 않음
        assert validate_sensor_reading(-50.1, "temperature") is False

    def test_온도_상한_경계값(self):
        """온도의 유효 범위 상한(500)에서의 동작"""
        # 경계 안쪽: 유효
        assert validate_sensor_reading(500.0, "temperature") is True
        # 경계 바깥: 유효하지 않음
        assert validate_sensor_reading(500.1, "temperature") is False

    def test_압력_경계값(self):
        """압력의 유효 범위 경계에서의 동작"""
        # 하한 경계
        assert validate_sensor_reading(0.0, "pressure") is True
        assert validate_sensor_reading(-0.1, "pressure") is False
        # 상한 경계
        assert validate_sensor_reading(1000.0, "pressure") is True
        assert validate_sensor_reading(1000.1, "pressure") is False

    def test_진동_경계값(self):
        """진동의 유효 범위 경계에서의 동작"""
        assert validate_sensor_reading(0.0, "vibration") is True
        assert validate_sensor_reading(100.0, "vibration") is True
        assert validate_sensor_reading(100.1, "vibration") is False


# =============================================================================
# 솔루션 2: 매개변수화 테스트
# =============================================================================

class TestParametrized:
    """매개변수화 테스트: 다양한 입력에 대한 동작을 효율적으로 검증"""

    @pytest.mark.parametrize("readings,baseline_mean,baseline_std,min_score,max_score", [
        # 정상: 기준선과 동일한 값
        ([100.0, 100.0, 100.0], 100.0, 5.0, 0.9, 1.0),
        # 약간 악화: 기준선에서 약간 벗어남
        ([110.0, 112.0, 108.0], 100.0, 5.0, 0.5, 0.8),
        # 심각하게 악화: 기준선에서 크게 벗어남
        ([130.0, 135.0, 125.0], 100.0, 5.0, 0.0, 0.3),
    ])
    def test_건강점수_다양한_시나리오(self, readings, baseline_mean,
                                   baseline_std, min_score, max_score):
        """다양한 입력에 대해 건강 점수가 예상 범위 내에 있어야 한다."""
        score = calculate_health_score(readings, baseline_mean, baseline_std)
        assert min_score <= score <= max_score, (
            f"건강 점수 {score}이 예상 범위 [{min_score}, {max_score}]을 벗어남"
        )

    @pytest.mark.parametrize("score,expected_status", [
        (1.0, "good"),
        (0.85, "good"),
        (0.8, "good"),
        (0.79, "warning"),
        (0.65, "warning"),
        (0.5, "warning"),
        (0.49, "critical"),
        (0.3, "critical"),
        (0.2, "critical"),
        (0.19, "failure"),
        (0.1, "failure"),
        (0.0, "failure"),
    ])
    def test_상태분류_매개변수화(self, score, expected_status):
        """각 점수에 대해 올바른 상태가 반환되어야 한다."""
        assert classify_equipment_status(score) == expected_status


# =============================================================================
# 솔루션 3: 유지보수 보고서 통합 테스트
# =============================================================================

class TestMaintenanceReport:
    """유지보수 보고서 통합 테스트"""

    def test_위험_장비_보고서(self):
        """위험 상태 장비의 보고서가 적절한 경고를 포함해야 한다."""
        # Arrange: 기준선에서 크게 벗어난 데이터
        readings = [200.0, 210.0, 220.0]

        # Act
        report = generate_maintenance_report(
            equipment_id="pump-danger",
            readings=readings,
            baseline_mean=100.0,
            baseline_std=5.0,
        )

        # Assert
        assert report["equipment_id"] == "pump-danger"
        assert report["status"] in ["critical", "failure"]
        assert report["health_score"] < 0.5

    def test_보고서_권장_조치_포함(self):
        """각 상태별 보고서에 적절한 권장 조치가 포함되어야 한다."""
        test_cases = [
            # (readings, baseline_mean, baseline_std, expected_keyword)
            ([100.0, 100.0], 100.0, 5.0, "정상 운전"),
            ([200.0, 200.0], 100.0, 5.0, "점검"),
        ]

        for readings, mean, std, keyword in test_cases:
            report = generate_maintenance_report(
                equipment_id="test",
                readings=readings,
                baseline_mean=mean,
                baseline_std=std,
            )
            assert keyword in report["recommendation"], (
                f"상태 '{report['status']}'의 권장 조치에 '{keyword}'가 포함되어야 함. "
                f"실제: '{report['recommendation']}'"
            )

    def test_정상_장비_보고서(self):
        """정상 장비는 'good' 상태이고 정상 운전 권장"""
        readings = [100.0, 99.5, 100.5, 100.0]
        report = generate_maintenance_report(
            equipment_id="pump-healthy",
            readings=readings,
            baseline_mean=100.0,
            baseline_std=5.0,
        )

        assert report["status"] == "good"
        assert report["health_score"] >= 0.8
        assert "정상 운전" in report["recommendation"]

    def test_일괄_검증_통합(self):
        """일괄 검증이 유효/무효를 올바르게 분류해야 한다."""
        readings = [
            ("temp-001", 25.0, "temperature"),     # 유효
            ("temp-002", 600.0, "temperature"),    # 범위 초과
            ("press-001", 500.0, "pressure"),      # 유효
            ("unknown", 10.0, "unknown_type"),     # 알 수 없는 센서
        ]

        result = batch_validate_readings(readings)

        assert len(result["valid"]) == 2
        assert len(result["invalid"]) == 2
