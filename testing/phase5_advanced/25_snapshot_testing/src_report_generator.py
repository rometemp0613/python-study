"""
리포트 생성 모듈.

공장 설비의 센서 데이터, 알림, 유지보수 스케줄에 대한
구조화된 리포트를 생성하는 함수들을 포함한다.

이 모듈의 출력은 구조화되어 있어 스냅샷 테스트에 적합하다.
"""

from typing import List, Dict, Any, Optional
import math


def generate_sensor_report(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    센서 데이터에 대한 요약 리포트를 생성한다.

    Args:
        sensor_data: 센서 데이터 딕셔너리
            {
                "sensor_id": str,
                "sensor_type": str,
                "values": List[float],
                "unit": str,
                "location": str,
            }

    Returns:
        요약 리포트 딕셔너리:
        {
            "sensor_id": str,
            "sensor_type": str,
            "location": str,
            "statistics": {
                "count": int,
                "mean": float,
                "std_dev": float,
                "min": float,
                "max": float,
                "range": float,
            },
            "status": str,
            "unit": str,
        }
    """
    values = sensor_data.get("values", [])

    if not values:
        return {
            "sensor_id": sensor_data.get("sensor_id", "unknown"),
            "sensor_type": sensor_data.get("sensor_type", "unknown"),
            "location": sensor_data.get("location", "unknown"),
            "statistics": {
                "count": 0,
                "mean": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
                "range": 0.0,
            },
            "status": "no_data",
            "unit": sensor_data.get("unit", ""),
        }

    count = len(values)
    mean = sum(values) / count
    variance = sum((v - mean) ** 2 for v in values) / count
    std_dev = math.sqrt(variance)
    min_val = min(values)
    max_val = max(values)

    # 상태 판정 (변동계수 기반)
    if count < 2:
        status = "insufficient_data"
    elif std_dev / abs(mean) > 0.5 if mean != 0 else std_dev > 0:
        status = "unstable"
    elif std_dev / abs(mean) > 0.2 if mean != 0 else False:
        status = "variable"
    else:
        status = "stable"

    return {
        "sensor_id": sensor_data.get("sensor_id", "unknown"),
        "sensor_type": sensor_data.get("sensor_type", "unknown"),
        "location": sensor_data.get("location", "unknown"),
        "statistics": {
            "count": count,
            "mean": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "range": round(max_val - min_val, 2),
        },
        "status": status,
        "unit": sensor_data.get("unit", ""),
    }


def generate_alert_summary(alerts: List[Dict[str, Any]]) -> str:
    """
    알림 목록에 대한 요약 텍스트를 생성한다.

    Args:
        alerts: 알림 리스트
            각 항목: {
                "equipment_id": str,
                "alert_type": str ("critical", "warning", "info"),
                "message": str,
            }

    Returns:
        포맷된 요약 문자열
    """
    if not alerts:
        return "=== 알림 요약 ===\n활성 알림 없음\n=================="

    # 유형별 분류
    critical = [a for a in alerts if a.get("alert_type") == "critical"]
    warning = [a for a in alerts if a.get("alert_type") == "warning"]
    info = [a for a in alerts if a.get("alert_type") == "info"]

    lines = ["=== 알림 요약 ==="]
    lines.append(f"총 알림: {len(alerts)}건")
    lines.append(f"  - 위험: {len(critical)}건")
    lines.append(f"  - 경고: {len(warning)}건")
    lines.append(f"  - 정보: {len(info)}건")
    lines.append("")

    # 위험 알림 상세
    if critical:
        lines.append("[위험 알림]")
        for alert in critical:
            lines.append(
                f"  * [{alert['equipment_id']}] {alert['message']}"
            )
        lines.append("")

    # 경고 알림 상세
    if warning:
        lines.append("[경고 알림]")
        for alert in warning:
            lines.append(
                f"  * [{alert['equipment_id']}] {alert['message']}"
            )
        lines.append("")

    # 정보 알림 상세
    if info:
        lines.append("[정보 알림]")
        for alert in info:
            lines.append(
                f"  * [{alert['equipment_id']}] {alert['message']}"
            )
        lines.append("")

    lines.append("==================")

    return "\n".join(lines)


def generate_maintenance_schedule(
    equipment_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    설비 목록에 대한 유지보수 스케줄을 생성한다.

    각 설비의 상태와 마지막 점검일을 기반으로
    다음 점검 계획을 수립한다.

    Args:
        equipment_list: 설비 정보 리스트
            각 항목: {
                "equipment_id": str,
                "name": str,
                "status": str ("normal", "caution", "warning", "danger"),
                "last_maintenance_days_ago": int,
                "maintenance_interval_days": int,
            }

    Returns:
        유지보수 스케줄 리스트:
        [{
            "equipment_id": str,
            "name": str,
            "priority": str ("urgent", "scheduled", "routine", "deferred"),
            "days_until_maintenance": int,
            "action": str,
        }]
    """
    schedule = []

    for eq in equipment_list:
        equipment_id = eq["equipment_id"]
        name = eq["name"]
        status = eq["status"]
        days_ago = eq.get("last_maintenance_days_ago", 0)
        interval = eq.get("maintenance_interval_days", 90)

        # 유지보수까지 남은 일수
        days_remaining = interval - days_ago

        # 우선순위 결정
        if status in ("danger", "critical"):
            priority = "urgent"
            action = "즉시 점검 필요"
            days_until = 0
        elif status == "warning" or days_remaining <= 0:
            priority = "scheduled"
            action = "점검 예약 필요"
            days_until = max(0, days_remaining)
        elif days_remaining <= interval * 0.2:
            # 잔여 기간이 20% 이하
            priority = "routine"
            action = "정기 점검 예정"
            days_until = days_remaining
        else:
            priority = "deferred"
            action = "다음 정기 점검까지 대기"
            days_until = days_remaining

        schedule.append({
            "equipment_id": equipment_id,
            "name": name,
            "priority": priority,
            "days_until_maintenance": days_until,
            "action": action,
        })

    # 우선순위 순으로 정렬
    priority_order = {"urgent": 0, "scheduled": 1, "routine": 2, "deferred": 3}
    schedule.sort(key=lambda x: priority_order.get(x["priority"], 99))

    return schedule
