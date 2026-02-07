"""
연습 27: TDD로 RUL(잔여 수명) 추정기 만들기

TDD 방식으로 장비의 잔여 수명(Remaining Useful Life)을 추정하는 클래스를 구현하세요.

RUL 추정기 요구사항:
1. 장비의 건강 지표(health_index) 시계열을 입력받는다 (0.0~1.0, 1.0이 정상)
2. 건강 지표가 시간에 따라 감소하는 추세를 계산한다 (선형 회귀)
3. 건강 지표가 임계값(기본 0.3)에 도달하는 시점을 예측한다
4. 잔여 수명을 시간 단위로 반환한다

TDD 사이클을 따라 아래 테스트를 작성하고, RULEstimator를 구현하세요.

실행 방법:
    pytest exercises/exercise_27.py -v
"""

import pytest


# =============================================================================
# TDD 사이클 1: 빈 추정기 생성
# =============================================================================

class TestRULEstimator_사이클1:
    """사이클 1: 추정기 생성"""

    def test_새로운_추정기_생성(self):
        """추정기를 생성할 수 있어야 한다."""
        pytest.skip("TODO: RULEstimator를 생성하고 데이터 개수가 0인지 확인하세요")
        # 힌트:
        # estimator = RULEstimator()
        # assert estimator.get_data_count() == 0


# =============================================================================
# TDD 사이클 2: 건강 지표 추가
# =============================================================================

class TestRULEstimator_사이클2:
    """사이클 2: 건강 지표 데이터 추가"""

    def test_건강_지표_추가(self):
        """건강 지표 데이터를 추가할 수 있어야 한다."""
        pytest.skip("TODO: add_health_index(value)로 데이터를 추가하고 개수를 확인하세요")
        # 힌트:
        # estimator = RULEstimator()
        # estimator.add_health_index(0.95)
        # assert estimator.get_data_count() == 1

    def test_유효하지_않은_건강_지표_거부(self):
        """0.0~1.0 범위를 벗어나는 값은 거부해야 한다."""
        pytest.skip("TODO: 범위 밖의 값(1.5, -0.1)을 넣으면 ValueError가 발생하는지 확인하세요")
        # 힌트:
        # estimator = RULEstimator()
        # with pytest.raises(ValueError):
        #     estimator.add_health_index(1.5)


# =============================================================================
# TDD 사이클 3: 감소 추세 계산
# =============================================================================

class TestRULEstimator_사이클3:
    """사이클 3: 감소 추세(기울기) 계산"""

    def test_감소_추세_계산(self):
        """건강 지표의 감소 기울기를 계산할 수 있어야 한다."""
        pytest.skip("TODO: 감소하는 데이터를 넣고 기울기가 음수인지 확인하세요")
        # 힌트:
        # estimator = RULEstimator()
        # # 시간 단위로 감소하는 건강 지표
        # for v in [1.0, 0.9, 0.8, 0.7, 0.6]:
        #     estimator.add_health_index(v)
        # slope = estimator.get_degradation_rate()
        # assert slope < 0  # 감소 추세
        # assert abs(slope - (-0.1)) < 0.001

    def test_데이터_부족시_에러(self):
        """데이터가 2개 미만이면 추세를 계산할 수 없다."""
        pytest.skip("TODO: 데이터가 1개일 때 get_degradation_rate() 호출 시 ValueError 확인")


# =============================================================================
# TDD 사이클 4: 잔여 수명 추정
# =============================================================================

class TestRULEstimator_사이클4:
    """사이클 4: RUL 추정"""

    def test_잔여_수명_추정(self):
        """잔여 수명을 시간 단위로 추정할 수 있어야 한다."""
        pytest.skip("TODO: 감소하는 데이터로 RUL을 추정하세요")
        # 힌트:
        # estimator = RULEstimator(failure_threshold=0.3)
        # # 매 시간 0.1씩 감소: 1.0, 0.9, 0.8, 0.7, 0.6
        # for v in [1.0, 0.9, 0.8, 0.7, 0.6]:
        #     estimator.add_health_index(v)
        # # 현재 0.6에서 0.3까지: 0.3/0.1 = 3시간
        # rul = estimator.estimate_rul()
        # assert abs(rul - 3.0) < 0.1

    def test_건강한_장비_RUL(self):
        """건강 지표가 증가하거나 안정적이면 RUL은 None이어야 한다."""
        pytest.skip("TODO: 안정적이거나 증가하는 데이터에 대해 RUL이 None인지 확인하세요")
        # 힌트:
        # estimator = RULEstimator()
        # for v in [0.9, 0.9, 0.9, 0.9]:
        #     estimator.add_health_index(v)
        # assert estimator.estimate_rul() is None  # 감소 추세 없음


# =============================================================================
# RUL 추정기 구현 (여기에 구현하세요)
# =============================================================================

# TODO: RULEstimator 클래스를 구현하세요
# class RULEstimator:
#     def __init__(self, failure_threshold=0.3):
#         ...
#     def add_health_index(self, value):
#         ...
#     def get_data_count(self):
#         ...
#     def get_degradation_rate(self):
#         ...
#     def estimate_rul(self):
#         ...
