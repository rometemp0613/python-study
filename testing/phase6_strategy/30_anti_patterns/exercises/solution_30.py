"""
솔루션 30: 테스트 안티패턴 수정

안티패턴을 제거하고 좋은 설계 원칙을 적용한 테스트입니다.

실행 방법:
    pytest exercises/solution_30.py -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_data_service import DataService


# =============================================================================
# 솔루션 1: 구현 결합 제거 → 동작 기반 테스트
# =============================================================================

class TestFix_구현결합:
    """동작 기반으로 캐싱을 검증 (내부 구현에 의존하지 않음)"""

    def test_데이터_캐싱_동작(self):
        """같은 sensor_id로 두 번 호출하면 같은 결과를 반환해야 한다."""
        # Arrange
        service = DataService()

        # Act: 같은 sensor_id로 두 번 호출
        data1 = service.get_sensor_data("sensor-001")
        data2 = service.get_sensor_data("sensor-001")

        # Assert: 캐시 동작을 공개 인터페이스로 검증
        assert data1 == data2
        assert len(data1) > 0

    def test_캐시_초기화_동작(self):
        """캐시를 초기화하면 데이터를 다시 가져와야 한다."""
        # Arrange
        service = DataService()
        data_before = service.get_sensor_data("sensor-001")

        # Act: 캐시 초기화
        service.clear_cache()
        data_after = service.get_sensor_data("sensor-001")

        # Assert: 동일한 데이터가 다시 생성됨 (결정론적 생성)
        assert data_before == data_after


# =============================================================================
# 솔루션 2: 과도한 모킹 제거 → 실제 로직 테스트
# =============================================================================

class TestFix_과도한모킹:
    """실제 로직이 실행되는 테스트"""

    def test_데이터_처리_실제_로직(self):
        """process_data의 실제 계산 로직을 검증한다."""
        # Arrange
        service = DataService()
        test_data = [100.0, 200.0, 300.0]

        # Act: 실제 로직 실행 (모킹 없음)
        result = service.process_data(test_data)

        # Assert: 실제 계산 결과 검증
        assert result["mean"] == 200.0
        assert result["min"] == 100.0
        assert result["max"] == 300.0
        assert result["count"] == 3

    def test_이상치_감지_실제_로직(self):
        """이상치 감지 로직이 실제로 동작하는지 검증"""
        # Arrange
        service = DataService()
        # 정상 데이터 + 극단적 이상치
        data_with_anomaly = [100.0, 100.0, 100.0, 100.0, 100.0, 500.0]

        # Act
        result = service.process_data(data_with_anomaly)

        # Assert
        assert result["anomaly_count"] >= 1
        assert 500.0 in result["anomalies"]

    def test_빈데이터_에러(self):
        """빈 데이터에 대한 에러 처리를 검증"""
        service = DataService()
        with pytest.raises(ValueError, match="빈 데이터"):
            service.process_data([])


# =============================================================================
# 솔루션 3: 개념 분리 → 하나의 테스트 = 하나의 개념
# =============================================================================

class TestFix_개념분리:
    """각 테스트가 하나의 개념만 검증"""

    def test_데이터_수집_검증(self):
        """센서 데이터 수집이 올바르게 동작하는지 검증"""
        # Arrange
        service = DataService()

        # Act
        data = service.get_sensor_data("sensor-001")

        # Assert
        assert data is not None
        assert len(data) > 0
        assert all(isinstance(x, (int, float)) for x in data)

    def test_데이터_처리_검증(self):
        """데이터 처리가 올바른 통계를 반환하는지 검증"""
        # Arrange
        service = DataService()
        input_data = [100.0, 200.0, 300.0]

        # Act
        result = service.process_data(input_data)

        # Assert
        assert result["mean"] == 200.0
        assert result["count"] == 3
        assert "std" in result

    def test_결과_저장_검증(self):
        """결과 저장 및 조회가 올바르게 동작하는지 검증"""
        # Arrange
        service = DataService()
        test_result = {"mean": 100.0, "std": 5.0, "count": 10}

        # Act
        result_id = service.save_results(test_result, result_id="test_001")
        saved = service.get_saved_result(result_id)

        # Assert
        assert result_id == "test_001"
        assert saved == test_result

    def test_전체_파이프라인_통합(self):
        """전체 분석 파이프라인이 올바르게 동작하는지 검증"""
        # Arrange
        service = DataService()

        # Act
        analysis = service.run_analysis("sensor-001")

        # Assert: 최종 결과 구조만 검증
        assert analysis["sensor_id"] == "sensor-001"
        assert "result_id" in analysis
        assert "summary" in analysis
        assert "mean" in analysis["summary"]
        assert "std" in analysis["summary"]
