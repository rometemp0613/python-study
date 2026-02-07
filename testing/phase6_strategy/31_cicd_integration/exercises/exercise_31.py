"""
연습 31: CI/CD 환경에서 실행되는 테스트 작성

CI/CD 파이프라인에서 실행될 테스트를 작성하세요.
pytest 마커를 사용하여 테스트를 분류하고,
JUnit XML 출력과 호환되는 테스트를 작성합니다.

실행 방법:
    pytest exercises/exercise_31.py -v
    pytest exercises/exercise_31.py -v --junitxml=results.xml
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
# 문제 1: 경계값 테스트 작성
# =============================================================================
# 센서 측정값 검증의 경계값을 테스트하세요.

class TestBoundaryValues:
    """경계값 테스트: 유효 범위의 경계에서의 동작을 검증"""

    def test_온도_하한_경계값(self):
        """온도의 유효 범위 하한(-50)에서의 동작을 테스트하세요."""
        pytest.skip(
            "TODO: -50.0은 유효, -50.1은 유효하지 않은지 확인하세요.\n"
            "힌트: assert validate_sensor_reading(-50.0, 'temperature') is True"
        )

    def test_온도_상한_경계값(self):
        """온도의 유효 범위 상한(500)에서의 동작을 테스트하세요."""
        pytest.skip(
            "TODO: 500.0은 유효, 500.1은 유효하지 않은지 확인하세요."
        )

    def test_압력_경계값(self):
        """압력의 유효 범위 경계에서의 동작을 테스트하세요."""
        pytest.skip(
            "TODO: 0.0과 1000.0은 유효, 범위 밖은 유효하지 않은지 확인하세요."
        )


# =============================================================================
# 문제 2: 매개변수화 테스트 작성
# =============================================================================
# pytest.mark.parametrize를 사용하여 건강 점수 계산을 테스트하세요.

class TestParametrized:
    """매개변수화 테스트: 다양한 입력에 대한 동작을 효율적으로 검증"""

    def test_건강점수_다양한_시나리오(self):
        """다양한 입력에 대해 건강 점수가 올바르게 계산되는지 테스트하세요."""
        pytest.skip(
            "TODO: parametrize를 사용하여 다양한 시나리오를 테스트하세요.\n"
            "힌트:\n"
            "@pytest.mark.parametrize('readings,baseline_mean,baseline_std,min_score,max_score', [\n"
            "    ([100.0, 100.0], 100.0, 5.0, 0.9, 1.0),  # 정상\n"
            "    ([120.0, 125.0], 100.0, 5.0, 0.0, 0.5),  # 악화\n"
            "])"
        )


# =============================================================================
# 문제 3: 유지보수 보고서 통합 테스트
# =============================================================================
# 실제 시나리오를 기반으로 보고서 생성을 테스트하세요.

class TestMaintenanceReport:
    """유지보수 보고서 통합 테스트"""

    def test_위험_장비_보고서(self):
        """위험 상태 장비의 보고서가 적절한 경고를 포함하는지 테스트하세요."""
        pytest.skip(
            "TODO: 기준선에서 크게 벗어난 데이터로 보고서를 생성하고\n"
            "상태가 'critical' 또는 'failure'인지 확인하세요.\n"
            "힌트:\n"
            "readings = [200.0, 210.0, 220.0]  # 기준선(100)에서 크게 벗어남\n"
            "report = generate_maintenance_report(\n"
            "    equipment_id='pump-danger',\n"
            "    readings=readings,\n"
            "    baseline_mean=100.0,\n"
            "    baseline_std=5.0\n"
            ")"
        )

    def test_보고서_권장_조치_포함(self):
        """보고서에 상태에 맞는 권장 조치가 포함되는지 테스트하세요."""
        pytest.skip(
            "TODO: 각 상태별 보고서에 적절한 recommendation이 포함되는지 확인하세요."
        )
