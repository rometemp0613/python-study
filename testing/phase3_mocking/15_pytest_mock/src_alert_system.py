"""
설비 알림 시스템 모듈

센서 데이터를 기반으로 이상을 감지하고,
알림을 발송하며 이력을 저장하는 기능을 제공합니다.
pytest-mock 학습을 위한 소스 코드입니다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ============================================================
# 의존성 인터페이스
# ============================================================

class NotificationService:
    """
    알림 발송 서비스

    이메일, SMS, 슬랙 등 다양한 채널로 알림을 발송합니다.
    실제로는 외부 API를 호출합니다.
    """

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """이메일 알림을 발송한다"""
        raise NotImplementedError("실제 이메일 서비스 연결 필요")

    def send_sms(self, phone: str, message: str) -> bool:
        """SMS 알림을 발송한다"""
        raise NotImplementedError("실제 SMS 서비스 연결 필요")

    def send_slack(self, channel: str, message: str) -> bool:
        """슬랙 메시지를 발송한다"""
        raise NotImplementedError("실제 슬랙 서비스 연결 필요")


class AlertRepository:
    """
    알림 이력 저장소

    발송된 알림의 이력을 데이터베이스에 저장합니다.
    """

    def save(self, alert_record: dict) -> str:
        """알림 이력을 저장하고 ID를 반환한다"""
        raise NotImplementedError("실제 데이터베이스 연결 필요")

    def get_recent(self, equipment_id: str, count: int = 10) -> list:
        """최근 알림 이력을 조회한다"""
        raise NotImplementedError("실제 데이터베이스 연결 필요")

    def count_by_level(self, equipment_id: str, level: str) -> int:
        """특정 수준의 알림 횟수를 조회한다"""
        raise NotImplementedError("실제 데이터베이스 연결 필요")


class ThresholdConfig:
    """
    임계값 설정 관리

    설비별 임계값을 관리합니다.
    실제로는 설정 파일이나 DB에서 로드합니다.
    """

    def get_threshold(self, equipment_id: str, metric: str) -> float:
        """설비별 임계값을 조회한다"""
        raise NotImplementedError("실제 설정 저장소 연결 필요")

    def get_all_thresholds(self, equipment_id: str) -> dict:
        """설비의 모든 임계값을 조회한다"""
        raise NotImplementedError("실제 설정 저장소 연결 필요")


# ============================================================
# 데이터 클래스
# ============================================================

@dataclass
class AlertRecord:
    """알림 기록"""
    equipment_id: str
    alert_level: str      # "info", "warning", "critical"
    message: str
    sensor_data: dict
    timestamp: datetime = field(default_factory=datetime.now)
    notified: bool = False


# ============================================================
# 메인 알림 시스템
# ============================================================

class AlertSystem:
    """
    설비 알림 시스템

    센서 데이터를 분석하여 이상을 감지하고,
    적절한 수준의 알림을 발송합니다.
    """

    # 기본 임계값 (ThresholdConfig를 사용할 수 없을 때의 폴백)
    DEFAULT_THRESHOLDS = {
        "temperature": {"warning": 80.0, "critical": 100.0},
        "vibration": {"warning": 5.0, "critical": 10.0},
        "pressure": {"warning": 8.0, "critical": 12.0},
    }

    def __init__(self,
                 notification_service: NotificationService,
                 alert_repository: AlertRepository,
                 threshold_config: Optional[ThresholdConfig] = None):
        self._notifier = notification_service
        self._repository = alert_repository
        self._config = threshold_config

    def evaluate_sensor_data(self, equipment_id: str,
                             sensor_data: dict) -> str:
        """
        센서 데이터를 평가하여 알림 수준을 결정한다.

        Returns:
            str: "normal", "warning", "critical"
        """
        thresholds = self._get_thresholds(equipment_id)

        for metric, value in sensor_data.items():
            if metric not in thresholds:
                continue

            if value >= thresholds[metric]["critical"]:
                return "critical"
            elif value >= thresholds[metric]["warning"]:
                # 다른 메트릭에서 critical이 없는지 계속 확인
                continue_checking = True
                for other_metric, other_value in sensor_data.items():
                    if other_metric in thresholds:
                        if other_value >= thresholds[other_metric]["critical"]:
                            return "critical"

                return "warning"

        return "normal"

    def process_reading(self, equipment_id: str,
                        sensor_data: dict,
                        notify_email: str = None,
                        notify_phone: str = None) -> dict:
        """
        센서 데이터를 처리하고 필요시 알림을 발송한다.

        Args:
            equipment_id: 설비 ID
            sensor_data: 센서 데이터 딕셔너리
            notify_email: 알림 이메일 (선택)
            notify_phone: 알림 전화번호 (선택)

        Returns:
            dict: 처리 결과
        """
        alert_level = self.evaluate_sensor_data(equipment_id, sensor_data)

        result = {
            "equipment_id": equipment_id,
            "alert_level": alert_level,
            "notified": False,
            "record_id": None,
        }

        # 경고 이상이면 알림 발송
        if alert_level in ("warning", "critical"):
            message = self._build_alert_message(
                equipment_id, alert_level, sensor_data
            )

            # 이메일 알림
            if notify_email:
                subject = f"[{alert_level.upper()}] 설비 {equipment_id}"
                self._notifier.send_email(notify_email, subject, message)
                result["notified"] = True

            # SMS 알림 (critical일 때만)
            if notify_phone and alert_level == "critical":
                sms_msg = f"[긴급] {equipment_id} 위험 상태 감지"
                self._notifier.send_sms(notify_phone, sms_msg)

            # 알림 이력 저장
            record = {
                "equipment_id": equipment_id,
                "alert_level": alert_level,
                "message": message,
                "sensor_data": sensor_data,
                "timestamp": datetime.now().isoformat(),
            }
            record_id = self._repository.save(record)
            result["record_id"] = record_id

        return result

    def get_alert_summary(self, equipment_id: str) -> dict:
        """
        설비의 알림 요약을 조회한다.

        Returns:
            dict: {"warning_count": int, "critical_count": int, "recent": list}
        """
        warning_count = self._repository.count_by_level(
            equipment_id, "warning"
        )
        critical_count = self._repository.count_by_level(
            equipment_id, "critical"
        )
        recent = self._repository.get_recent(equipment_id, count=5)

        return {
            "equipment_id": equipment_id,
            "warning_count": warning_count,
            "critical_count": critical_count,
            "recent_alerts": recent,
        }

    def _get_thresholds(self, equipment_id: str) -> dict:
        """설비별 임계값을 가져온다 (설정이 없으면 기본값 사용)"""
        if self._config:
            try:
                return self._config.get_all_thresholds(equipment_id)
            except Exception:
                pass  # 설정 조회 실패 시 기본값 사용

        return self.DEFAULT_THRESHOLDS

    def _build_alert_message(self, equipment_id: str,
                             level: str,
                             sensor_data: dict) -> str:
        """알림 메시지를 생성한다"""
        lines = [
            f"설비 {equipment_id}에서 {level} 수준의 이상이 감지되었습니다.",
            "",
            "센서 데이터:",
        ]
        for metric, value in sensor_data.items():
            lines.append(f"  - {metric}: {value}")

        return "\n".join(lines)
