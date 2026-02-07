"""
연습 30: 테스트 안티패턴 식별 및 수정

아래의 테스트에는 안티패턴이 포함되어 있습니다.
각 안티패턴을 식별하고 개선된 버전을 작성하세요.

실행 방법:
    pytest exercises/exercise_30.py -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_data_service import DataService


# =============================================================================
# 문제 1: 구현 결합 제거
# =============================================================================
# 아래 테스트는 내부 구현(_cache)에 의존합니다.
# 공개 인터페이스만 사용하도록 수정하세요.

class TestFix_구현결합:
    """TODO: 내부 구현에 의존하지 않도록 수정하세요."""

    def test_데이터_캐싱_동작(self):
        pytest.skip(
            "TODO: _cache에 직접 접근하지 않고 캐시 동작을 검증하세요.\n"
            "힌트: 같은 sensor_id로 두 번 호출하면 같은 결과가 나오는지 확인"
        )
        # 원래 안티패턴 코드:
        # service = DataService()
        # service.get_sensor_data("sensor-001")
        # assert "sensor-001" in service._cache  # 내부 구현에 의존!

        # 개선된 코드를 작성하세요:
        # service = DataService()
        # data1 = service.get_sensor_data("sensor-001")
        # data2 = service.get_sensor_data("sensor-001")
        # assert data1 == data2  # 캐시 동작을 공개 인터페이스로 검증


# =============================================================================
# 문제 2: 과도한 모킹 줄이기
# =============================================================================
# 아래 테스트는 모든 메서드를 모킹하여 실제 로직을 테스트하지 않습니다.
# 실제 로직이 실행되도록 수정하세요.

class TestFix_과도한모킹:
    """TODO: 불필요한 모킹을 제거하고 실제 로직을 테스트하세요."""

    def test_데이터_처리_실제_로직(self):
        pytest.skip(
            "TODO: 모킹 없이 process_data의 실제 로직을 테스트하세요.\n"
            "힌트: 직접 데이터 리스트를 전달하여 처리 결과를 검증"
        )
        # 원래 안티패턴 코드 (모든 것을 모킹):
        # monkeypatch.setattr(service, "process_data", lambda d: {"mean": 2})
        # result = service.process_data([1, 2, 3])
        # assert result == {"mean": 2}  # 모킹된 값만 확인

        # 개선된 코드를 작성하세요:
        # service = DataService()
        # result = service.process_data([100.0, 200.0, 300.0])
        # assert result["mean"] == 200.0  # 실제 계산 검증


# =============================================================================
# 문제 3: 여러 개념 분리
# =============================================================================
# 한 테스트에서 수집, 처리, 저장을 모두 검증합니다.
# 각각 분리된 테스트로 작성하세요.

class TestFix_개념분리:
    """TODO: 각 테스트가 하나의 개념만 검증하도록 분리하세요."""

    def test_데이터_수집_검증(self):
        pytest.skip("TODO: 데이터 수집만 검증하는 테스트를 작성하세요")
        # 힌트:
        # service = DataService()
        # data = service.get_sensor_data("sensor-001")
        # assert data is not None
        # assert len(data) > 0

    def test_데이터_처리_검증(self):
        pytest.skip("TODO: 데이터 처리만 검증하는 테스트를 작성하세요")

    def test_결과_저장_검증(self):
        pytest.skip("TODO: 결과 저장만 검증하는 테스트를 작성하세요")
