"""
솔루션 27: TDD로 RUL(잔여 수명) 추정기 만들기

이 솔루션은 TDD 사이클을 따라 단계적으로 구현되었습니다.

실행 방법:
    pytest exercises/solution_27.py -v
"""

import pytest
from typing import List, Optional


# =============================================================================
# RUL 추정기 구현
# =============================================================================

class RULEstimator:
    """
    장비 잔여 수명(Remaining Useful Life) 추정기

    건강 지표(health_index)의 시계열 데이터를 기반으로
    선형 회귀를 통해 장비의 잔여 수명을 추정합니다.

    Args:
        failure_threshold: 고장 임계값 (기본값: 0.3)
    """

    def __init__(self, failure_threshold: float = 0.3):
        """추정기를 초기화합니다."""
        self._health_indices: List[float] = []
        self._failure_threshold = failure_threshold

    def add_health_index(self, value: float) -> None:
        """
        건강 지표를 추가합니다.

        Args:
            value: 건강 지표 (0.0 ~ 1.0)

        Raises:
            ValueError: 값이 0.0~1.0 범위를 벗어나는 경우
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"숫자 타입이 필요합니다: {type(value).__name__}")

        if value < 0.0 or value > 1.0:
            raise ValueError(
                f"건강 지표는 0.0~1.0 범위여야 합니다. 입력값: {value}"
            )

        self._health_indices.append(float(value))

    def get_data_count(self) -> int:
        """현재까지 추가된 데이터의 개수를 반환합니다."""
        return len(self._health_indices)

    def get_degradation_rate(self) -> float:
        """
        건강 지표의 감소율(기울기)을 계산합니다.

        단순 선형 회귀를 사용하여 시간에 따른 감소 추세를 계산합니다.
        시간 단위: 데이터 포인트 간격 = 1 시간

        Returns:
            시간당 건강 지표 변화율 (감소 시 음수)

        Raises:
            ValueError: 데이터가 2개 미만인 경우
        """
        n = len(self._health_indices)
        if n < 2:
            raise ValueError("추세 계산에는 최소 2개의 데이터가 필요합니다.")

        # 단순 선형 회귀: y = ax + b
        # x = [0, 1, 2, ..., n-1] (시간)
        # y = health_indices
        x_values = list(range(n))
        y_values = self._health_indices

        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

        # 기울기 계산
        numerator = sum(
            (x - x_mean) * (y - y_mean)
            for x, y in zip(x_values, y_values)
        )
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    def estimate_rul(self) -> Optional[float]:
        """
        잔여 수명을 시간 단위로 추정합니다.

        현재 건강 지표와 감소율을 기반으로
        임계값에 도달하는 시점을 계산합니다.

        Returns:
            잔여 수명 (시간), 감소 추세가 없으면 None

        Raises:
            ValueError: 데이터가 2개 미만인 경우
        """
        if len(self._health_indices) < 2:
            raise ValueError("RUL 추정에는 최소 2개의 데이터가 필요합니다.")

        rate = self.get_degradation_rate()

        # 감소 추세가 없으면 (기울기가 0 이상) 고장 예측 불가
        if rate >= 0:
            return None

        # 현재 건강 지표 (마지막 값)
        current_health = self._health_indices[-1]

        # 이미 임계값 이하인 경우
        if current_health <= self._failure_threshold:
            return 0.0

        # 잔여 수명 = (현재값 - 임계값) / |감소율|
        rul = (current_health - self._failure_threshold) / abs(rate)
        return rul


# =============================================================================
# TDD 사이클 1: 빈 추정기 생성
# =============================================================================

class TestRULEstimator_사이클1:
    """사이클 1: 추정기 생성"""

    def test_새로운_추정기_생성(self):
        """추정기를 생성할 수 있어야 한다."""
        estimator = RULEstimator()
        assert estimator.get_data_count() == 0


# =============================================================================
# TDD 사이클 2: 건강 지표 추가
# =============================================================================

class TestRULEstimator_사이클2:
    """사이클 2: 건강 지표 데이터 추가"""

    def test_건강_지표_추가(self):
        """건강 지표 데이터를 추가할 수 있어야 한다."""
        estimator = RULEstimator()
        estimator.add_health_index(0.95)
        assert estimator.get_data_count() == 1

    def test_여러_건강_지표_추가(self):
        """여러 건강 지표를 추가할 수 있어야 한다."""
        estimator = RULEstimator()
        estimator.add_health_index(0.95)
        estimator.add_health_index(0.90)
        estimator.add_health_index(0.85)
        assert estimator.get_data_count() == 3

    def test_유효하지_않은_건강_지표_거부_상한(self):
        """1.0을 초과하는 값은 거부해야 한다."""
        estimator = RULEstimator()
        with pytest.raises(ValueError, match="0.0~1.0"):
            estimator.add_health_index(1.5)

    def test_유효하지_않은_건강_지표_거부_하한(self):
        """0.0 미만의 값은 거부해야 한다."""
        estimator = RULEstimator()
        with pytest.raises(ValueError):
            estimator.add_health_index(-0.1)

    def test_경계값_허용(self):
        """0.0과 1.0은 유효한 값이다."""
        estimator = RULEstimator()
        estimator.add_health_index(0.0)
        estimator.add_health_index(1.0)
        assert estimator.get_data_count() == 2


# =============================================================================
# TDD 사이클 3: 감소 추세 계산
# =============================================================================

class TestRULEstimator_사이클3:
    """사이클 3: 감소 추세(기울기) 계산"""

    def test_일정한_감소_추세(self):
        """매 시간 0.1씩 감소하는 경우 기울기는 -0.1이어야 한다."""
        estimator = RULEstimator()
        for v in [1.0, 0.9, 0.8, 0.7, 0.6]:
            estimator.add_health_index(v)

        slope = estimator.get_degradation_rate()
        assert slope < 0  # 감소 추세
        assert abs(slope - (-0.1)) < 0.001

    def test_안정적인_추세(self):
        """변화가 없으면 기울기는 0에 가까워야 한다."""
        estimator = RULEstimator()
        for v in [0.8, 0.8, 0.8, 0.8]:
            estimator.add_health_index(v)

        slope = estimator.get_degradation_rate()
        assert abs(slope) < 0.001

    def test_데이터_부족시_에러(self):
        """데이터가 2개 미만이면 에러가 발생해야 한다."""
        estimator = RULEstimator()
        estimator.add_health_index(0.9)
        with pytest.raises(ValueError, match="최소 2개"):
            estimator.get_degradation_rate()


# =============================================================================
# TDD 사이클 4: 잔여 수명 추정
# =============================================================================

class TestRULEstimator_사이클4:
    """사이클 4: RUL 추정"""

    def test_잔여_수명_추정(self):
        """감소하는 데이터로 잔여 수명을 추정한다."""
        estimator = RULEstimator(failure_threshold=0.3)
        # 매 시간 0.1씩 감소: 1.0 → 0.9 → 0.8 → 0.7 → 0.6
        for v in [1.0, 0.9, 0.8, 0.7, 0.6]:
            estimator.add_health_index(v)

        # 현재 0.6, 임계값 0.3, 감소율 0.1/시간
        # RUL = (0.6 - 0.3) / 0.1 = 3.0 시간
        rul = estimator.estimate_rul()
        assert rul is not None
        assert abs(rul - 3.0) < 0.1

    def test_빠른_열화_짧은_RUL(self):
        """빠르게 감소하면 RUL이 짧아야 한다."""
        estimator = RULEstimator(failure_threshold=0.3)
        # 매 시간 0.2씩 감소
        for v in [1.0, 0.8, 0.6, 0.4]:
            estimator.add_health_index(v)

        # 현재 0.4, 임계값 0.3, 감소율 0.2/시간
        # RUL = (0.4 - 0.3) / 0.2 = 0.5 시간
        rul = estimator.estimate_rul()
        assert rul is not None
        assert abs(rul - 0.5) < 0.1

    def test_건강한_장비_RUL_없음(self):
        """감소 추세가 없으면 RUL은 None이어야 한다."""
        estimator = RULEstimator()
        for v in [0.9, 0.9, 0.9, 0.9]:
            estimator.add_health_index(v)

        assert estimator.estimate_rul() is None

    def test_이미_임계값_이하(self):
        """이미 임계값 이하면 RUL은 0이어야 한다."""
        estimator = RULEstimator(failure_threshold=0.3)
        for v in [0.5, 0.4, 0.3, 0.2]:
            estimator.add_health_index(v)

        rul = estimator.estimate_rul()
        assert rul == 0.0

    def test_데이터_부족시_에러(self):
        """데이터가 2개 미만이면 에러가 발생해야 한다."""
        estimator = RULEstimator()
        estimator.add_health_index(0.9)
        with pytest.raises(ValueError):
            estimator.estimate_rul()
