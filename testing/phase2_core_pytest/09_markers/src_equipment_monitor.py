"""
장비 모니터링 모듈

공장 설비의 상태를 모니터링하고 분석하는 기능을 제공한다.
일부 함수는 실행 시간이 오래 걸리거나(slow) 외부 시스템 연동이 필요(integration)하다.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class EquipmentStatus:
    """장비 상태 정보"""
    equipment_id: str        # 장비 식별자
    name: str                # 장비 이름
    status: str              # 상태: "running", "idle", "warning", "error", "maintenance"
    temperature: float = 0.0 # 온도 (°C)
    vibration: float = 0.0   # 진동 (mm/s)
    runtime_hours: float = 0.0  # 가동 시간 (시간)
    last_maintenance: Optional[datetime] = None  # 최근 정비 일시


class EquipmentMonitor:
    """
    장비 모니터링 시스템

    장비 상태를 추적하고 분석하는 기능을 제공한다.
    """

    def __init__(self):
        """모니터 초기화"""
        self._equipment: dict[str, EquipmentStatus] = {}

    def register_equipment(self, equipment_id: str, name: str) -> EquipmentStatus:
        """
        새 장비를 등록한다.

        Args:
            equipment_id: 장비 고유 식별자
            name: 장비 이름

        Returns:
            등록된 EquipmentStatus

        Raises:
            ValueError: 이미 등록된 장비 ID일 때
        """
        if equipment_id in self._equipment:
            raise ValueError(f"이미 등록된 장비입니다: {equipment_id}")

        status = EquipmentStatus(
            equipment_id=equipment_id,
            name=name,
            status="idle",
        )
        self._equipment[equipment_id] = status
        return status

    def get_status(self, equipment_id: str) -> EquipmentStatus:
        """장비 상태를 조회한다"""
        if equipment_id not in self._equipment:
            raise KeyError(f"등록되지 않은 장비입니다: {equipment_id}")
        return self._equipment[equipment_id]

    def update_sensor_data(self, equipment_id: str,
                           temperature: float = None,
                           vibration: float = None) -> EquipmentStatus:
        """
        장비 센서 데이터를 업데이트한다.

        Args:
            equipment_id: 장비 식별자
            temperature: 온도 값 (None이면 변경 안 함)
            vibration: 진동 값 (None이면 변경 안 함)

        Returns:
            업데이트된 EquipmentStatus
        """
        status = self.get_status(equipment_id)

        if temperature is not None:
            status.temperature = temperature
        if vibration is not None:
            status.vibration = vibration

        # 자동 상태 판단
        status.status = self._evaluate_status(status)
        return status

    def _evaluate_status(self, status: EquipmentStatus) -> str:
        """센서 데이터 기반 장비 상태 평가"""
        if status.temperature > 100 or status.vibration > 10:
            return "error"
        elif status.temperature > 80 or status.vibration > 7:
            return "warning"
        elif status.temperature > 0 or status.vibration > 0:
            return "running"
        else:
            return "idle"

    def check_maintenance_needed(self, equipment_id: str,
                                 max_runtime_hours: float = 1000) -> bool:
        """
        정비가 필요한지 확인한다.

        Args:
            equipment_id: 장비 식별자
            max_runtime_hours: 최대 가동 시간

        Returns:
            True면 정비 필요
        """
        status = self.get_status(equipment_id)
        return status.runtime_hours >= max_runtime_hours

    def get_all_equipment(self) -> list[EquipmentStatus]:
        """모든 등록된 장비 목록을 반환한다"""
        return list(self._equipment.values())

    def get_equipment_by_status(self, target_status: str) -> list[EquipmentStatus]:
        """특정 상태의 장비 목록을 반환한다"""
        return [
            eq for eq in self._equipment.values()
            if eq.status == target_status
        ]

    # === 느린 작업 (slow 마커 대상) ===

    def run_full_diagnostics(self, equipment_id: str) -> dict:
        """
        전체 진단 실행 (시간이 오래 걸리는 작업).
        실제로는 여러 센서를 순차 점검한다.

        이 함수는 테스트에서 "slow" 마커로 표시될 수 있다.
        """
        status = self.get_status(equipment_id)

        # 시뮬레이션: 실제로는 오래 걸리지만 테스트용으로 간소화
        diagnostics = {
            "equipment_id": equipment_id,
            "temperature_check": status.temperature < 100,
            "vibration_check": status.vibration < 10,
            "overall_health": "good" if status.status in ("running", "idle") else "poor",
            "recommendations": [],
        }

        if status.temperature > 80:
            diagnostics["recommendations"].append("냉각 시스템 점검 권장")
        if status.vibration > 7:
            diagnostics["recommendations"].append("베어링 점검 권장")
        if status.runtime_hours > 800:
            diagnostics["recommendations"].append("정기 정비 시기 도래")

        return diagnostics

    def generate_monthly_report(self, equipment_ids: list[str]) -> dict:
        """
        월간 보고서 생성 (여러 장비를 분석하므로 느림).
        "slow" 마커 대상.
        """
        report = {
            "total_equipment": len(equipment_ids),
            "status_summary": {},
            "maintenance_needed": [],
        }

        for eq_id in equipment_ids:
            try:
                status = self.get_status(eq_id)
                report["status_summary"][eq_id] = status.status
                if self.check_maintenance_needed(eq_id):
                    report["maintenance_needed"].append(eq_id)
            except KeyError:
                report["status_summary"][eq_id] = "not_found"

        return report

    # === 외부 시스템 연동 (integration 마커 대상) ===

    def send_alert(self, equipment_id: str, message: str) -> dict:
        """
        알림 전송 (외부 시스템 연동).
        실제로는 이메일/SMS/Slack 등으로 전송.
        테스트에서는 "integration" 마커로 표시.
        """
        status = self.get_status(equipment_id)
        # 시뮬레이션: 실제 외부 호출 대신 결과를 반환
        return {
            "sent": True,
            "equipment_id": equipment_id,
            "message": message,
            "status_at_alert": status.status,
        }

    def sync_to_cloud(self, equipment_id: str) -> dict:
        """
        클라우드에 데이터 동기화 (외부 시스템 연동).
        "integration" 마커 대상.
        """
        status = self.get_status(equipment_id)
        return {
            "synced": True,
            "equipment_id": equipment_id,
            "data_size_bytes": 1024,
            "cloud_status": "uploaded",
        }
