"""
정비 리포트 생성 모듈

설비 상태를 분석하고 정비 리포트를 생성합니다.
datetime, 설정 딕셔너리, 외부 서비스 등
패칭이 필요한 의존성을 포함합니다.
"""

from datetime import datetime, timedelta
from typing import Optional


# ============================================================
# 설정 딕셔너리 (모듈 수준)
# ============================================================

MAINTENANCE_CONFIG = {
    "temperature_threshold": 80.0,    # 온도 경고 임계값 (섭씨)
    "vibration_threshold": 5.0,       # 진동 경고 임계값 (mm/s)
    "pressure_threshold": 8.0,        # 압력 경고 임계값 (bar)
    "check_interval_hours": 24,       # 점검 주기 (시간)
    "report_recipients": ["admin@factory.com"],
    "company_name": "스마트팩토리 주식회사",
}


# ============================================================
# 외부 서비스 (패칭 대상)
# ============================================================

class NotificationClient:
    """
    외부 알림 서비스 클라이언트

    실제로는 HTTP API를 호출하여 알림을 발송합니다.
    테스트에서는 패치하여 대체합니다.
    """

    def send_alert(self, recipient: str, message: str) -> bool:
        """알림을 발송한다 (실제로는 API 호출)"""
        raise NotImplementedError("실제 알림 서비스 연결 필요")

    def send_report(self, recipient: str, report: str) -> bool:
        """리포트를 이메일로 발송한다"""
        raise NotImplementedError("실제 이메일 서비스 연결 필요")


# ============================================================
# 헬퍼 함수
# ============================================================

def get_current_time() -> datetime:
    """현재 시각을 반환한다 (테스트 시 패치하기 쉽도록 별도 함수로 분리)"""
    return datetime.now()


def calculate_next_check(last_check: datetime) -> datetime:
    """다음 점검 일시를 계산한다"""
    interval = MAINTENANCE_CONFIG["check_interval_hours"]
    return last_check + timedelta(hours=interval)


# ============================================================
# 메인 리포터 클래스
# ============================================================

class MaintenanceReporter:
    """
    정비 리포트 생성기

    설비 상태 데이터를 받아 리포트를 생성하고,
    필요시 알림을 발송합니다.
    """

    def __init__(self, notification_client: Optional[NotificationClient] = None):
        self._client = notification_client or NotificationClient()

    def generate_report(self, equipment_id: str,
                        sensor_data: dict) -> dict:
        """
        설비 정비 리포트를 생성한다.

        Args:
            equipment_id: 설비 ID
            sensor_data: {"temperature": float, "vibration": float, "pressure": float}

        Returns:
            dict: 리포트 정보
        """
        now = get_current_time()
        status = self._evaluate_status(sensor_data)
        warnings = self._check_thresholds(sensor_data)

        report = {
            "equipment_id": equipment_id,
            "report_date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "report_year": now.year,
            "report_month": now.month,
            "status": status,
            "warnings": warnings,
            "sensor_data": sensor_data,
            "company": MAINTENANCE_CONFIG["company_name"],
            "next_check": calculate_next_check(now).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

        return report

    def generate_and_send_report(self, equipment_id: str,
                                 sensor_data: dict) -> dict:
        """리포트를 생성하고 경고가 있으면 알림을 발송한다"""
        report = self.generate_report(equipment_id, sensor_data)

        if report["warnings"]:
            for recipient in MAINTENANCE_CONFIG["report_recipients"]:
                message = self._format_alert(report)
                self._client.send_alert(recipient, message)

        return report

    def send_periodic_report(self, equipment_id: str,
                             sensor_data: dict) -> dict:
        """정기 리포트를 생성하고 발송한다"""
        report = self.generate_report(equipment_id, sensor_data)

        for recipient in MAINTENANCE_CONFIG["report_recipients"]:
            report_text = self._format_report(report)
            self._client.send_report(recipient, report_text)

        return report

    def _evaluate_status(self, sensor_data: dict) -> str:
        """센서 데이터를 기반으로 상태를 평가한다"""
        temp = sensor_data.get("temperature", 0)
        vibration = sensor_data.get("vibration", 0)
        pressure = sensor_data.get("pressure", 0)

        temp_thresh = MAINTENANCE_CONFIG["temperature_threshold"]
        vib_thresh = MAINTENANCE_CONFIG["vibration_threshold"]
        pres_thresh = MAINTENANCE_CONFIG["pressure_threshold"]

        if temp > temp_thresh * 1.5 or vibration > vib_thresh * 2:
            return "위험"
        elif (temp > temp_thresh or vibration > vib_thresh
              or pressure > pres_thresh):
            return "경고"
        else:
            return "정상"

    def _check_thresholds(self, sensor_data: dict) -> list:
        """임계값 초과 항목을 확인한다"""
        warnings = []

        temp = sensor_data.get("temperature", 0)
        vibration = sensor_data.get("vibration", 0)
        pressure = sensor_data.get("pressure", 0)

        if temp > MAINTENANCE_CONFIG["temperature_threshold"]:
            warnings.append(
                f"온도 초과: {temp}°C "
                f"(임계값: {MAINTENANCE_CONFIG['temperature_threshold']}°C)"
            )

        if vibration > MAINTENANCE_CONFIG["vibration_threshold"]:
            warnings.append(
                f"진동 초과: {vibration}mm/s "
                f"(임계값: {MAINTENANCE_CONFIG['vibration_threshold']}mm/s)"
            )

        if pressure > MAINTENANCE_CONFIG["pressure_threshold"]:
            warnings.append(
                f"압력 초과: {pressure}bar "
                f"(임계값: {MAINTENANCE_CONFIG['pressure_threshold']}bar)"
            )

        return warnings

    def _format_alert(self, report: dict) -> str:
        """알림 메시지를 포맷한다"""
        lines = [
            f"[경고] 설비 {report['equipment_id']} 이상 감지",
            f"일시: {report['report_date']}",
            f"상태: {report['status']}",
            "",
            "경고 사항:",
        ]
        for warning in report["warnings"]:
            lines.append(f"  - {warning}")

        return "\n".join(lines)

    def _format_report(self, report: dict) -> str:
        """리포트 텍스트를 포맷한다"""
        lines = [
            f"=== 정비 리포트 ===",
            f"회사: {report['company']}",
            f"설비: {report['equipment_id']}",
            f"일시: {report['report_date']}",
            f"상태: {report['status']}",
            f"다음 점검: {report['next_check']}",
        ]
        return "\n".join(lines)
