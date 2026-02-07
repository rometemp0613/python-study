"""
연습 문제 04: 풀이

테스트 구조와 fixture 활용 풀이.

실행 방법:
    pytest exercises/solution_04.py -v
"""

import pytest


# ============================================================
# 테스트 대상 함수들
# ============================================================

def create_maintenance_schedule(equipment_id, readings, threshold):
    """정비 일정을 생성한다."""
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
    """설비 건강도를 계산한다 (0~100%)."""
    if not readings:
        return 0

    opt_min, opt_max = optimal_range
    opt_center = (opt_min + opt_max) / 2
    opt_span = opt_max - opt_min

    avg = sum(readings) / len(readings)
    deviation = abs(avg - opt_center)

    if opt_min <= avg <= opt_max:
        health = 100
    else:
        health = max(0, 100 - (deviation - opt_span / 2) * 5)

    return round(health, 1)


# ============================================================
# fixture 정의 (풀이)
# ============================================================

@pytest.fixture
def sample_equipment():
    """테스트용 설비 정보를 제공한다."""
    return {
        "equipment_id": "MOTOR-001",
        "threshold": 80.0,
        "optimal_range": (20.0, 60.0),
        "location": "1공장 A라인",
    }


@pytest.fixture
def normal_readings():
    """정상 범위의 읽기 데이터를 제공한다."""
    return [25.0, 28.0, 30.0, 27.5, 26.0]


@pytest.fixture
def warning_readings():
    """주의 범위의 읽기 데이터를 제공한다 (임계값의 80~100%)."""
    return [60.0, 65.0, 68.0, 66.0, 64.0]


@pytest.fixture
def critical_readings():
    """위험 범위의 읽기 데이터를 제공한다."""
    return [75.0, 82.0, 90.0, 85.0, 88.0]


# ============================================================
# 테스트 코드 (풀이)
# ============================================================

class TestCreateMaintenanceSchedule:
    """정비 일정 생성 테스트"""

    def test_긴급정비_생성(self, sample_equipment, critical_readings):
        """임계값 이상이면 '긴급정비'를 반환해야 한다"""
        result = create_maintenance_schedule(
            sample_equipment["equipment_id"],
            critical_readings,
            sample_equipment["threshold"],
        )
        assert result["action"] == "긴급정비"
        assert result["priority"] == "높음"
        assert result["equipment_id"] == "MOTOR-001"

    def test_예방정비_생성(self, sample_equipment, warning_readings):
        """임계값의 80% 이상이면 '예방정비'를 반환해야 한다"""
        result = create_maintenance_schedule(
            sample_equipment["equipment_id"],
            warning_readings,
            sample_equipment["threshold"],
        )
        assert result["action"] == "예방정비"
        assert result["priority"] == "중간"

    def test_정상운전(self, sample_equipment, normal_readings):
        """임계값의 80% 미만이면 '정상운전'을 반환해야 한다"""
        result = create_maintenance_schedule(
            sample_equipment["equipment_id"],
            normal_readings,
            sample_equipment["threshold"],
        )
        assert result["action"] == "정상운전"
        assert result["priority"] == "낮음"

    def test_빈_데이터_예외(self, sample_equipment):
        """빈 데이터에 대해 ValueError가 발생해야 한다"""
        with pytest.raises(ValueError, match="비어있습니다"):
            create_maintenance_schedule(
                sample_equipment["equipment_id"],
                [],
                sample_equipment["threshold"],
            )

    def test_경계값_정확히_임계값(self, sample_equipment):
        """정확히 임계값이면 긴급정비"""
        result = create_maintenance_schedule(
            "MOTOR-001",
            [80.0],
            sample_equipment["threshold"],
        )
        assert result["action"] == "긴급정비"

    def test_경계값_80퍼센트(self, sample_equipment):
        """정확히 80%이면 예방정비"""
        threshold = sample_equipment["threshold"]  # 80.0
        result = create_maintenance_schedule(
            "MOTOR-001",
            [threshold * 0.8],  # 64.0
            threshold,
        )
        assert result["action"] == "예방정비"


class TestCalculateEquipmentHealth:
    """설비 건강도 계산 테스트"""

    def test_최적_범위_내(self, sample_equipment):
        """최적 범위 내의 값이면 건강도 100%"""
        readings = [30.0, 35.0, 40.0]
        health = calculate_equipment_health(
            readings, sample_equipment["optimal_range"]
        )
        assert health == 100

    def test_범위_밖_건강도_감소(self, sample_equipment):
        """최적 범위 밖이면 건강도가 감소해야 한다"""
        readings = [70.0, 75.0, 80.0]  # 최적 범위(20~60) 밖
        health = calculate_equipment_health(
            readings, sample_equipment["optimal_range"]
        )
        assert health < 100

    def test_빈_데이터_건강도_0(self, sample_equipment):
        """빈 데이터에 대해 건강도 0을 반환해야 한다"""
        health = calculate_equipment_health(
            [], sample_equipment["optimal_range"]
        )
        assert health == 0

    def test_건강도_범위(self, sample_equipment):
        """건강도는 항상 0~100 사이여야 한다"""
        # 극단적으로 높은 온도
        readings = [200.0, 250.0, 300.0]
        health = calculate_equipment_health(
            readings, sample_equipment["optimal_range"]
        )
        assert 0 <= health <= 100
