"""
테스트 안티패턴 예시와 개선 버전

각 안티패턴과 그에 대한 개선된 버전이 쌍으로 제시됩니다.
모든 테스트는 PASS하지만, 안티패턴 테스트는 설계상 문제가 있습니다.

실행 방법:
    pytest test_anti_patterns.py -v
"""

import pytest
from src_data_service import DataService


# =============================================================================
# 안티패턴 1: 구현 결합 (Implementation Coupling)
# =============================================================================

class TestAntiPattern_구현결합:
    """안티패턴: 내부 구현에 의존하는 테스트 (PASS하지만 나쁜 설계)"""

    def test_bad_내부캐시_직접접근(self):
        """
        안티패턴: private 속성(_cache)에 직접 접근
        → 캐시 구현이 변경되면 테스트가 깨짐
        """
        service = DataService()
        service.get_sensor_data("sensor-001")

        # 안티패턴: 내부 구현에 의존
        assert "sensor-001" in service._cache
        assert isinstance(service._cache["sensor-001"], list)


class TestImproved_동작테스트:
    """개선: 공개 인터페이스를 통해 동작을 검증"""

    def test_good_공개인터페이스_사용(self):
        """
        개선: 공개 메서드의 반환값으로 동작 검증
        → 내부 구현이 변경되어도 테스트 유지 가능
        """
        service = DataService()
        data = service.get_sensor_data("sensor-001")

        # 개선: 공개 인터페이스만 사용
        assert data is not None
        assert len(data) > 0
        assert all(isinstance(x, (int, float)) for x in data)

    def test_good_캐시_동작_검증(self):
        """
        개선: 캐시 동작을 공개 인터페이스로 검증
        (같은 데이터가 반환되는지 확인)
        """
        service = DataService()
        data1 = service.get_sensor_data("sensor-001")
        data2 = service.get_sensor_data("sensor-001")

        # 캐시가 동작하면 같은 객체가 반환됨
        assert data1 == data2


# =============================================================================
# 안티패턴 2: 과도한 모킹 (Excessive Mocking)
# =============================================================================

class TestAntiPattern_과도한모킹:
    """안티패턴: 모든 것을 모킹하여 실제 로직을 테스트하지 않음"""

    def test_bad_모든것을_모킹(self, monkeypatch):
        """
        안티패턴: 테스트 대상의 모든 메서드를 모킹
        → 실제로는 아무 로직도 테스트하지 않음
        """
        service = DataService()

        # 안티패턴: 모든 메서드를 모킹 - 실제 로직이 실행되지 않음
        monkeypatch.setattr(service, "get_sensor_data", lambda sid: [1, 2, 3])
        monkeypatch.setattr(service, "process_data", lambda d: {"mean": 2})
        monkeypatch.setattr(service, "save_results", lambda r, **kw: "result_001")

        data = service.get_sensor_data("sensor-001")
        result = service.process_data(data)
        result_id = service.save_results(result)

        # 모킹된 반환값만 확인 - 의미 없는 테스트
        assert data == [1, 2, 3]
        assert result == {"mean": 2}
        assert result_id == "result_001"


class TestImproved_적절한모킹:
    """개선: 외부 의존성만 모킹하고 내부 로직은 실제로 실행"""

    def test_good_실제로직_테스트(self):
        """
        개선: process_data의 실제 로직을 테스트
        (외부 의존성이 없으므로 모킹 불필요)
        """
        service = DataService()
        data = [100.0, 200.0, 300.0]

        result = service.process_data(data)

        # 실제 로직이 올바르게 동작하는지 검증
        assert result["mean"] == 200.0
        assert result["count"] == 3
        assert result["min"] == 100.0
        assert result["max"] == 300.0


# =============================================================================
# 안티패턴 3: 여러 개념 혼합 (God Test)
# =============================================================================

class TestAntiPattern_여러개념:
    """안티패턴: 한 테스트에서 너무 많은 것을 검증"""

    def test_bad_모든것을_한번에(self):
        """
        안티패턴: 데이터 수집, 처리, 저장, 조회를 한 테스트에서 모두 검증
        → 실패 시 어디가 문제인지 파악하기 어려움
        """
        service = DataService()

        # 데이터 수집
        data = service.get_sensor_data("sensor-001")
        assert data is not None
        assert len(data) > 0

        # 데이터 처리
        result = service.process_data(data)
        assert "mean" in result
        assert "std" in result
        assert result["count"] == len(data)

        # 결과 저장
        result_id = service.save_results(result, result_id="test_001")
        assert result_id == "test_001"

        # 결과 조회
        saved = service.get_saved_result("test_001")
        assert saved is not None
        assert saved["mean"] == result["mean"]


class TestImproved_개념분리:
    """개선: 각 테스트가 하나의 개념만 검증"""

    def test_good_데이터_수집(self):
        """데이터 수집만 검증"""
        service = DataService()
        data = service.get_sensor_data("sensor-001")
        assert data is not None
        assert len(data) > 0

    def test_good_데이터_처리(self):
        """데이터 처리만 검증"""
        service = DataService()
        data = [100.0, 200.0, 300.0]
        result = service.process_data(data)
        assert result["mean"] == 200.0
        assert result["count"] == 3

    def test_good_결과_저장_및_조회(self):
        """저장과 조회의 연결만 검증"""
        service = DataService()
        test_result = {"mean": 100.0, "std": 5.0}
        result_id = service.save_results(test_result, result_id="test_001")
        saved = service.get_saved_result(result_id)
        assert saved == test_result


# =============================================================================
# 안티패턴 4: 프레임워크 테스트
# =============================================================================

class TestAntiPattern_프레임워크테스트:
    """안티패턴: Python 내장 기능을 테스트"""

    def test_bad_파이썬_내장기능(self):
        """
        안티패턴: Python의 리스트, 딕셔너리 기능을 테스트
        → 이미 검증된 언어 기능을 다시 테스트하는 것은 낭비
        """
        # 리스트 기능 테스트 (불필요)
        data = [1, 2, 3]
        assert len(data) == 3
        assert sum(data) == 6

        # 딕셔너리 기능 테스트 (불필요)
        config = {"threshold": 100}
        assert "threshold" in config
        assert config["threshold"] == 100


class TestImproved_비즈니스로직:
    """개선: 자신의 비즈니스 로직을 테스트"""

    def test_good_이상치_감지_로직(self):
        """비즈니스 로직: 이상치 감지가 올바르게 동작하는지 검증"""
        service = DataService()
        # 이상치가 포함된 데이터
        data = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 500.0]
        result = service.process_data(data)

        assert result["anomaly_count"] >= 1
        assert 500.0 in result["anomalies"]


# =============================================================================
# 안티패턴 5: 검증 없는 테스트 (No Assertion)
# =============================================================================

class TestAntiPattern_검증없음:
    """안티패턴: assert가 없어서 항상 통과"""

    def test_bad_검증없는_실행(self):
        """
        안티패턴: 코드를 실행만 하고 결과를 검증하지 않음
        → 코드가 예외 없이 실행되기만 하면 통과
        """
        service = DataService()
        data = service.get_sensor_data("sensor-001")
        service.process_data(data)
        # assert 없음!

    def test_bad_약한_검증(self):
        """
        안티패턴: 너무 약한 검증으로 의미 없는 테스트
        """
        service = DataService()
        result = service.process_data([100.0, 200.0])
        assert result is not None  # 어떤 딕셔너리든 통과


class TestImproved_명확한검증:
    """개선: 명확하고 의미 있는 검증"""

    def test_good_처리결과_상세검증(self):
        """처리 결과의 구체적인 값을 검증"""
        service = DataService()
        result = service.process_data([100.0, 200.0, 300.0])

        assert result["mean"] == 200.0
        assert result["min"] == 100.0
        assert result["max"] == 300.0
        assert result["count"] == 3
        assert result["anomaly_count"] == 0

    def test_good_빈데이터_에러처리(self):
        """빈 데이터에 대한 에러 처리를 검증"""
        service = DataService()
        with pytest.raises(ValueError, match="빈 데이터"):
            service.process_data([])


# =============================================================================
# 안티패턴 6: 매직 넘버 / 불명확한 의도
# =============================================================================

class TestAntiPattern_매직넘버:
    """안티패턴: 의미 불명확한 매직 넘버 사용"""

    def test_bad_매직넘버(self):
        """
        안티패턴: 테스트 데이터와 기대값의 의미가 불명확
        """
        s = DataService()
        r = s.process_data([72.3, 74.1, 73.5, 75.0, 74.2])
        assert r["mean"] == pytest.approx(73.82, abs=0.01)
        assert r["count"] == 5


class TestImproved_명확한의도:
    """개선: 의미 있는 이름과 설명 사용"""

    def test_good_온도센서_평균계산(self):
        """온도 센서의 측정값 평균이 올바르게 계산되는지 검증"""
        # Arrange: 온도 센서 측정값 (섭씨)
        service = DataService()
        temperature_readings = [72.3, 74.1, 73.5, 75.0, 74.2]
        expected_mean = sum(temperature_readings) / len(temperature_readings)

        # Act
        result = service.process_data(temperature_readings)

        # Assert
        assert result["mean"] == pytest.approx(expected_mean, abs=0.01)
        assert result["count"] == len(temperature_readings)
