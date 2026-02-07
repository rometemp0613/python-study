"""
설비 상태 분류 모듈.

공장 설비의 센서 데이터(온도, 진동, 압력)를 기반으로
설비 상태를 분류하고, 유지보수 우선순위를 결정하며,
비상 정지 여부를 판단하는 로직을 포함한다.

이 모듈은 다양한 분기(if/elif/else)를 포함하여
커버리지 분석 학습에 적합하다.
"""

from typing import List, Dict, Optional, Tuple


def classify_status(
    temp: float,
    vibration: float,
    pressure: float
) -> str:
    """
    설비 상태를 분류한다.

    세 가지 센서 값(온도, 진동, 압력)을 종합하여
    설비의 현재 상태를 판정한다.

    Args:
        temp: 온도 (섭씨). 정상 범위: 20~80
        vibration: 진동 (mm/s). 정상 범위: 0~10
        pressure: 압력 (bar). 정상 범위: 1~10

    Returns:
        상태 문자열: "normal", "caution", "warning", "danger", "critical"
    """
    # 입력값 유효성 검사
    if temp < -50 or temp > 500:
        raise ValueError(f"비정상 온도 값: {temp}")
    if vibration < 0:
        raise ValueError(f"진동은 음수일 수 없습니다: {vibration}")
    if pressure < 0:
        raise ValueError(f"압력은 음수일 수 없습니다: {pressure}")

    # 위험 점수 계산
    danger_score = 0

    # 온도 기반 점수
    if temp > 120:
        danger_score += 3  # 극고온
    elif temp > 100:
        danger_score += 2  # 고온
    elif temp > 80:
        danger_score += 1  # 주의 온도
    elif temp < 0:
        danger_score += 1  # 저온 주의

    # 진동 기반 점수
    if vibration > 20:
        danger_score += 3  # 극심한 진동
    elif vibration > 15:
        danger_score += 2  # 높은 진동
    elif vibration > 10:
        danger_score += 1  # 주의 진동

    # 압력 기반 점수
    if pressure > 15:
        danger_score += 3  # 극고압
    elif pressure > 12:
        danger_score += 2  # 고압
    elif pressure > 10:
        danger_score += 1  # 주의 압력
    elif pressure < 1:
        danger_score += 1  # 저압 주의

    # 점수 기반 상태 분류
    if danger_score >= 7:
        return "critical"
    elif danger_score >= 5:
        return "danger"
    elif danger_score >= 3:
        return "warning"
    elif danger_score >= 1:
        return "caution"
    else:
        return "normal"


def get_maintenance_priority(status: str) -> Dict[str, any]:
    """
    설비 상태에 따른 유지보수 우선순위를 반환한다.

    Args:
        status: 설비 상태 ("normal", "caution", "warning", "danger", "critical")

    Returns:
        우선순위 정보 딕셔너리:
        {
            "priority": int (1=최우선, 5=최하위),
            "action": str (권장 조치),
            "max_response_hours": int (최대 대응 시간)
        }
    """
    priority_map = {
        "critical": {
            "priority": 1,
            "action": "즉시 정지 및 긴급 점검",
            "max_response_hours": 1,
        },
        "danger": {
            "priority": 2,
            "action": "가동 중단 예약 및 점검 준비",
            "max_response_hours": 4,
        },
        "warning": {
            "priority": 3,
            "action": "모니터링 강화 및 점검 계획 수립",
            "max_response_hours": 24,
        },
        "caution": {
            "priority": 4,
            "action": "정기 점검 시 추가 확인",
            "max_response_hours": 72,
        },
        "normal": {
            "priority": 5,
            "action": "정기 점검 유지",
            "max_response_hours": 168,  # 1주
        },
    }

    if status not in priority_map:
        raise ValueError(f"알 수 없는 상태: {status}")

    return priority_map[status]


def should_shutdown(readings_history: List[Dict[str, float]]) -> Tuple[bool, str]:
    """
    과거 측정 이력을 기반으로 설비 정지 여부를 판단한다.

    여러 조건을 복합적으로 검토하여 비상 정지가 필요한지 결정한다.
    각 조건은 독립적으로 정지를 트리거할 수 있다.

    Args:
        readings_history: 측정 이력 리스트
            각 항목: {"temp": float, "vibration": float, "pressure": float}

    Returns:
        (정지 여부, 사유) 튜플
    """
    # 이력이 없으면 판단 불가
    if not readings_history:
        return False, "측정 이력 없음"

    # 조건 1: 최근 측정값이 극한 범위인 경우 즉시 정지
    latest = readings_history[-1]
    if latest.get("temp", 0) > 150:
        return True, "극고온 감지 (150도 초과)"
    if latest.get("vibration", 0) > 30:
        return True, "극심한 진동 감지 (30mm/s 초과)"
    if latest.get("pressure", 0) > 20:
        return True, "극고압 감지 (20bar 초과)"

    # 이력이 충분하지 않으면 추세 분석 불가
    if len(readings_history) < 3:
        return False, "이력 부족으로 추세 분석 불가"

    # 조건 2: 최근 3회 연속 위험 범위인 경우
    recent_three = readings_history[-3:]
    consecutive_danger = all(
        r.get("temp", 0) > 100 or r.get("vibration", 0) > 20
        for r in recent_three
    )
    if consecutive_danger:
        return True, "3회 연속 위험 범위"

    # 조건 3: 온도 급상승 (직전 대비 50% 이상 증가)
    if len(readings_history) >= 2:
        prev_temp = readings_history[-2].get("temp", 0)
        curr_temp = latest.get("temp", 0)
        if prev_temp > 0 and curr_temp > prev_temp * 1.5:
            return True, f"온도 급상승 ({prev_temp}→{curr_temp})"

    # 조건 4: 진동 추세 지속 증가 (5회 연속 증가)
    if len(readings_history) >= 5:
        recent_five = readings_history[-5:]
        vibrations = [r.get("vibration", 0) for r in recent_five]
        is_increasing = all(
            vibrations[i] < vibrations[i + 1]
            for i in range(len(vibrations) - 1)
        )
        if is_increasing and vibrations[-1] > 15:
            return True, "진동 5회 연속 증가 (15mm/s 초과)"

    # 모든 조건을 통과하면 정지 불필요
    return False, "정상 범위"


def calculate_health_score(
    temp: float,
    vibration: float,
    pressure: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    설비 건강 점수를 0~100 범위로 계산한다.

    각 센서 값을 정상 범위 대비 비율로 환산하고,
    가중치를 적용하여 종합 건강 점수를 산출한다.

    Args:
        temp: 온도
        vibration: 진동
        pressure: 압력
        weights: 가중치 딕셔너리 (기본: 동일 가중치)

    Returns:
        건강 점수 (0~100, 100이 최상)
    """
    if weights is None:
        weights = {"temp": 1.0, "vibration": 1.0, "pressure": 1.0}

    # 각 센서의 정상 범위 정의
    normal_ranges = {
        "temp": (20, 80),       # 정상 온도 범위
        "vibration": (0, 10),   # 정상 진동 범위
        "pressure": (1, 10),    # 정상 압력 범위
    }

    scores = {}

    # 온도 점수
    t_min, t_max = normal_ranges["temp"]
    if t_min <= temp <= t_max:
        scores["temp"] = 100.0
    elif temp < t_min:
        scores["temp"] = max(0, 100 - (t_min - temp) * 5)
    else:
        scores["temp"] = max(0, 100 - (temp - t_max) * 2)

    # 진동 점수
    v_min, v_max = normal_ranges["vibration"]
    if v_min <= vibration <= v_max:
        scores["vibration"] = 100.0
    else:
        scores["vibration"] = max(0, 100 - (vibration - v_max) * 5)

    # 압력 점수
    p_min, p_max = normal_ranges["pressure"]
    if p_min <= pressure <= p_max:
        scores["pressure"] = 100.0
    elif pressure < p_min:
        scores["pressure"] = max(0, 100 - (p_min - pressure) * 20)
    else:
        scores["pressure"] = max(0, 100 - (pressure - p_max) * 10)

    # 가중 평균 계산
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(
        scores[key] * weights.get(key, 0)
        for key in scores
    )

    return round(weighted_sum / total_weight, 1)
