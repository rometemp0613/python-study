"""
연습 문제 04: 테스트 구조와 fixture 활용

fixture를 정의하고 테스트에서 활용하는 연습을 합니다.
체계적인 네이밍과 클래스 구조를 따라 테스트를 작성하세요.

실행 방법:
    pytest exercises/exercise_04.py -v
"""

import pytest


# ============================================================
# 테스트 대상 함수들
# ============================================================

def create_maintenance_schedule(equipment_id, readings, threshold):
    """정비 일정을 생성한다.

    최근 읽기 값이 임계값의 80% 이상이면 "예방정비",
    임계값 이상이면 "긴급정비"를 반환한다.

    Args:
        equipment_id: 설비 ID
        readings: 최근 읽기 값 리스트
        threshold: 임계값

    Returns:
        딕셔너리: {"equipment_id": ..., "action": ..., "priority": ...}

    Raises:
        ValueError: readings가 비어있을 때
    """
    if not readings:
        raise ValueError("읽기 값이 비어있습니다")

    max_reading = max(readings)

    if max_reading >= threshold:
        return {
            "equipment_id": equipment_id,
            "action": "긴급정비",
            "priority": "높음",
            "max_reading": max_reading,
        }
    elif max_reading >= threshold * 0.8:
        return {
            "equipment_id": equipment_id,
            "action": "예방정비",
            "priority": "중간",
            "max_reading": max_reading,
        }
    else:
        return {
            "equipment_id": equipment_id,
            "action": "정상운전",
            "priority": "낮음",
            "max_reading": max_reading,
        }


def calculate_equipment_health(readings, optimal_range):
    """설비 건강도를 계산한다 (0~100%).

    최근 읽기 값이 최적 범위에 얼마나 가까운지 기반으로 계산한다.

    Args:
        readings: 최근 읽기 값 리스트
        optimal_range: 최적 범위 튜플 (min, max)

    Returns:
        건강도 (0~100)
    """
    if not readings:
        return 0

    opt_min, opt_max = optimal_range
    opt_center = (opt_min + opt_max) / 2
    opt_span = opt_max - opt_min

    avg = sum(readings) / len(readings)
    deviation = abs(avg - opt_center)

    # 최적 범위 내이면 100%, 범위 밖이면 거리에 따라 감소
    if opt_min <= avg <= opt_max:
        health = 100
    else:
        health = max(0, 100 - (deviation - opt_span / 2) * 5)

    return round(health, 1)


# ============================================================
# TODO: fixture를 정의하세요
# ============================================================

@pytest.fixture
def sample_equipment():
    """테스트용 설비 정보를 제공한다."""
    # TODO: 설비 정보 딕셔너리를 반환하세요
    # 힌트: {"equipment_id": "MOTOR-001", "threshold": 80.0, ...}
    pytest.skip("TODO: fixture를 구현하세요")


@pytest.fixture
def normal_readings():
    """정상 범위의 읽기 데이터를 제공한다."""
    # TODO: 정상 범위의 온도 리스트를 반환하세요
    pytest.skip("TODO: fixture를 구현하세요")


@pytest.fixture
def critical_readings():
    """위험 범위의 읽기 데이터를 제공한다."""
    # TODO: 임계값 이상의 온도 리스트를 반환하세요
    pytest.skip("TODO: fixture를 구현하세요")


# ============================================================
# TODO: 테스트를 작성하세요
# ============================================================

class TestCreateMaintenanceSchedule:
    """정비 일정 생성 테스트"""

    def test_긴급정비_생성(self):
        """임계값 이상이면 '긴급정비'를 반환해야 한다"""
        # TODO: 높은 온도 데이터로 테스트
        pytest.skip("TODO: 긴급정비 테스트를 구현하세요")

    def test_예방정비_생성(self):
        """임계값의 80% 이상이면 '예방정비'를 반환해야 한다"""
        # TODO: 임계값의 80~100% 범위 데이터로 테스트
        pytest.skip("TODO: 예방정비 테스트를 구현하세요")

    def test_정상운전(self):
        """임계값의 80% 미만이면 '정상운전'을 반환해야 한다"""
        # TODO: 낮은 온도 데이터로 테스트
        pytest.skip("TODO: 정상운전 테스트를 구현하세요")

    def test_빈_데이터_예외(self):
        """빈 데이터에 대해 ValueError가 발생해야 한다"""
        # TODO: pytest.raises 사용
        pytest.skip("TODO: 빈 데이터 예외 테스트를 구현하세요")


class TestCalculateEquipmentHealth:
    """설비 건강도 계산 테스트"""

    def test_최적_범위_내(self):
        """최적 범위 내의 값이면 건강도 100%"""
        # TODO: 최적 범위 내의 데이터로 테스트
        pytest.skip("TODO: 최적 범위 건강도 테스트를 구현하세요")

    def test_범위_밖_건강도_감소(self):
        """최적 범위 밖이면 건강도가 감소해야 한다"""
        # TODO: 최적 범위 밖의 데이터로 테스트
        pytest.skip("TODO: 건강도 감소 테스트를 구현하세요")

    def test_빈_데이터_건강도_0(self):
        """빈 데이터에 대해 건강도 0을 반환해야 한다"""
        # TODO: 빈 리스트로 테스트
        pytest.skip("TODO: 빈 데이터 건강도 테스트를 구현하세요")
