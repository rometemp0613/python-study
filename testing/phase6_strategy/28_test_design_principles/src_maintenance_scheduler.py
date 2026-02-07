"""
유지보수 스케줄러 모듈

공장 장비의 유지보수 일정을 관리합니다.
우선순위 기반 스케줄링과 기한 초과 관리 기능을 제공합니다.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional
import uuid


# 우선순위별 기본 유지보수 주기 (일)
PRIORITY_INTERVALS = {
    "critical": 1,   # 긴급: 1일 이내
    "high": 7,       # 높음: 1주 이내
    "medium": 30,    # 중간: 1개월 이내
    "low": 90,       # 낮음: 3개월 이내
}

# 유효한 우선순위 목록
VALID_PRIORITIES = list(PRIORITY_INTERVALS.keys())


class MaintenanceScheduler:
    """
    유지보수 스케줄러

    장비별 유지보수 일정을 관리합니다.
    우선순위에 따라 적절한 날짜에 유지보수를 예약하고,
    기한이 초과된 유지보수를 추적합니다.
    """

    def __init__(self, today: Optional[date] = None):
        """
        스케줄러를 초기화합니다.

        Args:
            today: 현재 날짜 (테스트를 위한 주입, 기본값: 오늘)
        """
        self._today = today or date.today()
        self._schedules: List[Dict] = []

    def schedule_maintenance(
        self,
        equipment_id: str,
        priority: str,
        scheduled_date: Optional[date] = None,
    ) -> str:
        """
        유지보수를 스케줄링합니다.

        Args:
            equipment_id: 장비 ID
            priority: 우선순위 ("critical", "high", "medium", "low")
            scheduled_date: 예약 날짜 (기본값: 우선순위에 따라 자동 설정)

        Returns:
            유지보수 ID

        Raises:
            ValueError: 유효하지 않은 우선순위
        """
        if priority not in VALID_PRIORITIES:
            raise ValueError(
                f"유효하지 않은 우선순위: {priority}. "
                f"유효한 값: {VALID_PRIORITIES}"
            )

        if scheduled_date is None:
            interval = PRIORITY_INTERVALS[priority]
            scheduled_date = self._today + timedelta(days=interval)

        maintenance_id = str(uuid.uuid4())[:8]

        self._schedules.append({
            "id": maintenance_id,
            "equipment_id": equipment_id,
            "priority": priority,
            "scheduled_date": scheduled_date,
            "status": "scheduled",
        })

        return maintenance_id

    def get_next_maintenance(self, equipment_id: str) -> Optional[Dict]:
        """
        특정 장비의 다음 예정 유지보수를 반환합니다.

        가장 이른 날짜의 예정된 유지보수를 반환합니다.

        Args:
            equipment_id: 장비 ID

        Returns:
            유지보수 정보 딕셔너리 또는 None
        """
        scheduled = [
            s for s in self._schedules
            if s["equipment_id"] == equipment_id and s["status"] == "scheduled"
        ]

        if not scheduled:
            return None

        # 가장 이른 날짜 반환
        return min(scheduled, key=lambda s: s["scheduled_date"])

    def cancel_maintenance(self, maintenance_id: str) -> bool:
        """
        예정된 유지보수를 취소합니다.

        Args:
            maintenance_id: 유지보수 ID

        Returns:
            취소 성공 여부
        """
        for schedule in self._schedules:
            if schedule["id"] == maintenance_id and schedule["status"] == "scheduled":
                schedule["status"] = "cancelled"
                return True
        return False

    def get_overdue_maintenances(self) -> List[Dict]:
        """
        기한이 초과된 유지보수 목록을 반환합니다.

        Returns:
            기한 초과 유지보수 리스트
        """
        overdue = [
            s for s in self._schedules
            if s["status"] == "scheduled" and s["scheduled_date"] < self._today
        ]

        # 우선순위별 정렬 (critical > high > medium > low)
        priority_order = {p: i for i, p in enumerate(VALID_PRIORITIES)}
        overdue.sort(key=lambda s: priority_order.get(s["priority"], 99))

        return overdue

    def get_all_scheduled(self, equipment_id: Optional[str] = None) -> List[Dict]:
        """
        예정된 모든 유지보수를 반환합니다.

        Args:
            equipment_id: 필터링할 장비 ID (None이면 전체)

        Returns:
            유지보수 리스트
        """
        scheduled = [s for s in self._schedules if s["status"] == "scheduled"]

        if equipment_id:
            scheduled = [s for s in scheduled if s["equipment_id"] == equipment_id]

        return scheduled

    def complete_maintenance(self, maintenance_id: str) -> bool:
        """
        유지보수를 완료 처리합니다.

        Args:
            maintenance_id: 유지보수 ID

        Returns:
            완료 처리 성공 여부
        """
        for schedule in self._schedules:
            if schedule["id"] == maintenance_id and schedule["status"] == "scheduled":
                schedule["status"] = "completed"
                schedule["completed_date"] = self._today
                return True
        return False
