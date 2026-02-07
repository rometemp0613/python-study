"""
알람/알림 파이프라인 모듈

센서 리딩을 받아 임계값을 확인하고, 알람을 발생시키며,
적절한 채널로 알림을 보내는 파이프라인을 구현합니다.

구성:
- AlertRule: 알람 규칙 정의
- AlertEvent: 발생한 알람 이벤트
- AlertEngine: 알람 판정 (임계값, 쿨다운, 억제)
- NotificationDispatcher: 심각도 기반 알림 전송
- AlertPipeline: 전체 흐름 통합

외부 라이브러리 없이 Python 표준 라이브러리만 사용합니다.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Protocol
import uuid


@dataclass
class AlertRule:
    """
    알람 규칙 정의

    Attributes:
        sensor_type: 센서 타입 (예: "temperature", "vibration")
        threshold: 알람 발생 임계값
        severity: 심각도 ("info", "warning", "critical")
        cooldown_seconds: 동일 센서 재알람까지 대기 시간 (초)
    """
    sensor_type: str
    threshold: float
    severity: str
    cooldown_seconds: int


@dataclass
class AlertEvent:
    """
    발생한 알람 이벤트

    Attributes:
        alert_id: 고유 식별자
        timestamp: 알람 발생 시각
        sensor_type: 센서 타입
        value: 측정값
        severity: 심각도
        message: 알람 메시지
    """
    timestamp: datetime
    sensor_type: str
    value: float
    severity: str
    message: str
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


class AlertEngine:
    """
    알람 판정 엔진

    센서 리딩을 받아 규칙에 따라 알람을 발생시킵니다.
    쿨다운과 억제 메커니즘으로 알람 폭풍을 방지합니다.
    """

    def __init__(self):
        """알람 엔진 초기화"""
        # 센서 타입별 알람 규칙
        self._rules: Dict[str, AlertRule] = {}
        # 센서 타입별 마지막 알람 발생 시각 (쿨다운용)
        self._last_alert_time: Dict[str, datetime] = {}
        # 현재 활성 알람 목록
        self._active_alerts: List[AlertEvent] = []
        # 억제 중인 센서 타입과 만료 시각
        self._suppressions: Dict[str, datetime] = {}

    def add_rule(self, rule: AlertRule) -> None:
        """
        알람 규칙을 추가합니다.

        같은 sensor_type의 기존 규칙이 있으면 덮어씁니다.

        Args:
            rule: 추가할 알람 규칙
        """
        self._rules[rule.sensor_type] = rule

    def check_reading(
        self,
        sensor_type: str,
        value: float,
        timestamp: datetime,
    ) -> Optional[AlertEvent]:
        """
        센서 리딩을 확인하고 필요시 알람을 발생시킵니다.

        알람 발생 조건:
        1. 해당 센서 타입에 대한 규칙이 있어야 함
        2. 값이 임계값을 초과해야 함
        3. 쿨다운 기간이 아니어야 함
        4. 억제 중이 아니어야 함

        Args:
            sensor_type: 센서 타입
            value: 측정값
            timestamp: 측정 시각

        Returns:
            AlertEvent 또는 None (알람이 발생하지 않으면)
        """
        # 규칙 확인
        if sensor_type not in self._rules:
            return None

        rule = self._rules[sensor_type]

        # 임계값 확인
        if value <= rule.threshold:
            return None

        # 억제 확인
        if self._is_suppressed(sensor_type, timestamp):
            return None

        # 쿨다운 확인
        if self._is_in_cooldown(sensor_type, timestamp):
            return None

        # 알람 생성
        alert = AlertEvent(
            timestamp=timestamp,
            sensor_type=sensor_type,
            value=value,
            severity=rule.severity,
            message=(
                f"[{rule.severity.upper()}] {sensor_type} 센서 값 {value}이(가) "
                f"임계값 {rule.threshold}을(를) 초과했습니다"
            ),
        )

        # 상태 업데이트
        self._last_alert_time[sensor_type] = timestamp
        self._active_alerts.append(alert)

        return alert

    def get_active_alerts(self) -> List[AlertEvent]:
        """
        현재 활성 알람 목록을 반환합니다.

        Returns:
            활성 AlertEvent 리스트
        """
        return list(self._active_alerts)

    def suppress_alert(
        self,
        sensor_type: str,
        duration: int,
    ) -> None:
        """
        특정 센서 타입의 알람을 일시적으로 억제합니다.

        유지보수 중, 테스트 중 등의 상황에서 사용합니다.

        Args:
            sensor_type: 억제할 센서 타입
            duration: 억제 기간 (초)
        """
        expiry = datetime.now() + timedelta(seconds=duration)
        self._suppressions[sensor_type] = expiry

    def clear_suppression(self, sensor_type: str) -> None:
        """
        특정 센서 타입의 억제를 해제합니다.

        Args:
            sensor_type: 해제할 센서 타입
        """
        if sensor_type in self._suppressions:
            del self._suppressions[sensor_type]

    def _is_in_cooldown(
        self, sensor_type: str, current_time: datetime
    ) -> bool:
        """
        해당 센서 타입이 쿨다운 기간인지 확인합니다.

        Args:
            sensor_type: 센서 타입
            current_time: 현재 시각

        Returns:
            쿨다운 중이면 True
        """
        if sensor_type not in self._last_alert_time:
            return False

        rule = self._rules.get(sensor_type)
        if rule is None:
            return False

        elapsed = (current_time - self._last_alert_time[sensor_type]).total_seconds()
        return elapsed < rule.cooldown_seconds

    def _is_suppressed(
        self, sensor_type: str, current_time: datetime
    ) -> bool:
        """
        해당 센서 타입이 억제 중인지 확인합니다.

        억제가 만료되었으면 자동으로 해제합니다.

        Args:
            sensor_type: 센서 타입
            current_time: 현재 시각

        Returns:
            억제 중이면 True
        """
        if sensor_type not in self._suppressions:
            return False

        expiry = self._suppressions[sensor_type]
        if current_time >= expiry:
            # 억제 만료 → 자동 해제
            del self._suppressions[sensor_type]
            return False

        return True


class NotificationDispatcher:
    """
    알림 디스패처

    심각도에 따라 적절한 채널로 알림을 전송합니다.

    라우팅 규칙:
    - info: Slack만
    - warning: Slack + Email
    - critical: Slack + Email + SMS
    """

    def __init__(self, email_sender, sms_sender, slack_sender):
        """
        알림 디스패처 초기화 (의존성 주입)

        Args:
            email_sender: 이메일 전송 객체 (send(message) 메서드 필요)
            sms_sender: SMS 전송 객체 (send(message) 메서드 필요)
            slack_sender: Slack 전송 객체 (send(message) 메서드 필요)
        """
        self._email_sender = email_sender
        self._sms_sender = sms_sender
        self._slack_sender = slack_sender
        self._dispatch_history: List[Dict[str, Any]] = []

    def dispatch(self, alert_event: AlertEvent) -> List[str]:
        """
        알람 이벤트를 적절한 채널로 전송합니다.

        Args:
            alert_event: 전송할 알람 이벤트

        Returns:
            전송된 채널 이름 리스트 (예: ["slack", "email"])
        """
        channels_sent = []
        message = alert_event.message

        # 심각도에 따른 라우팅
        severity = alert_event.severity.lower()

        if severity in ("info", "warning", "critical"):
            self._slack_sender.send(message)
            channels_sent.append("slack")

        if severity in ("warning", "critical"):
            self._email_sender.send(message)
            channels_sent.append("email")

        if severity == "critical":
            self._sms_sender.send(message)
            channels_sent.append("sms")

        # 전송 기록 저장
        self._dispatch_history.append({
            "alert_id": alert_event.alert_id,
            "timestamp": alert_event.timestamp,
            "severity": alert_event.severity,
            "channels": channels_sent,
            "message": message,
        })

        return channels_sent

    def get_dispatch_history(self) -> List[Dict[str, Any]]:
        """
        전송 기록을 반환합니다.

        Returns:
            전송 기록 리스트
        """
        return list(self._dispatch_history)


class AlertPipeline:
    """
    알람 파이프라인

    AlertEngine과 NotificationDispatcher를 연결하여
    센서 리딩을 받아 알람 발생 및 알림 전송까지의 전체 흐름을 처리합니다.
    """

    def __init__(self, engine: AlertEngine, dispatcher: NotificationDispatcher):
        """
        파이프라인 초기화

        Args:
            engine: 알람 판정 엔진
            dispatcher: 알림 디스패처
        """
        self._engine = engine
        self._dispatcher = dispatcher

    def process_reading(
        self,
        sensor_type: str,
        value: float,
        timestamp: datetime,
    ) -> Optional[Dict[str, Any]]:
        """
        센서 리딩을 처리합니다.

        1. AlertEngine으로 알람 판정
        2. 알람이 발생하면 NotificationDispatcher로 알림 전송

        Args:
            sensor_type: 센서 타입
            value: 측정값
            timestamp: 측정 시각

        Returns:
            처리 결과 딕셔너리 (알람이 발생한 경우) 또는 None
        """
        # 알람 판정
        alert = self._engine.check_reading(sensor_type, value, timestamp)

        if alert is None:
            return None

        # 알림 전송
        channels = self._dispatcher.dispatch(alert)

        return {
            "alert": alert,
            "channels": channels,
            "timestamp": timestamp,
        }
