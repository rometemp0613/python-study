"""
연습 문제 35 풀이: 알람/알림 시스템 테스트

각 테스트의 완성된 풀이입니다.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
import sys
import os

# 부모 디렉토리의 모듈을 임포트하기 위한 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_alert_pipeline import (
    AlertRule,
    AlertEvent,
    AlertEngine,
    NotificationDispatcher,
    AlertPipeline,
)


@pytest.fixture
def engine():
    """AlertEngine 인스턴스"""
    return AlertEngine()


@pytest.fixture
def base_time():
    """테스트 기준 시각"""
    return datetime(2024, 6, 15, 10, 0, 0)


# ============================================================
# 연습 1: 쿨다운 메커니즘 테스트
# ============================================================

class TestCooldownMechanism:
    """알람 쿨다운 메커니즘 테스트"""

    def test_쿨다운_기간내_중복_방지(self, engine, base_time):
        """쿨다운 기간 내 중복 알람 차단"""
        # 준비: 진동 센서 규칙 추가
        engine.add_rule(AlertRule(
            sensor_type="vibration",
            threshold=10.0,
            severity="critical",
            cooldown_seconds=600,
        ))

        # 실행: 첫 번째 알람
        alert1 = engine.check_reading("vibration", 15.0, base_time)
        # 5분 후 두 번째 시도 (쿨다운 10분 내)
        alert2 = engine.check_reading(
            "vibration", 15.0, base_time + timedelta(minutes=5)
        )

        # 검증
        assert alert1 is not None, "첫 번째 알람은 발생해야 합니다"
        assert alert2 is None, "쿨다운 중 두 번째 알람은 차단되어야 합니다"

    def test_쿨다운_만료후_재발생(self, engine, base_time):
        """쿨다운 만료 후 알람 재발생"""
        # 준비
        engine.add_rule(AlertRule(
            sensor_type="vibration",
            threshold=10.0,
            severity="critical",
            cooldown_seconds=600,
        ))

        # 실행
        alert1 = engine.check_reading("vibration", 15.0, base_time)
        # 11분 후 (쿨다운 10분 만료)
        alert2 = engine.check_reading(
            "vibration", 15.0, base_time + timedelta(minutes=11)
        )

        # 검증
        assert alert1 is not None, "첫 번째 알람 발생"
        assert alert2 is not None, "쿨다운 만료 후 알람 재발생"

    def test_다른_센서_독립적_쿨다운(self, engine, base_time):
        """서로 다른 센서의 독립적 쿨다운"""
        # 준비
        engine.add_rule(AlertRule(
            sensor_type="temperature",
            threshold=80.0,
            severity="warning",
            cooldown_seconds=300,
        ))
        engine.add_rule(AlertRule(
            sensor_type="vibration",
            threshold=10.0,
            severity="critical",
            cooldown_seconds=600,
        ))

        # 실행
        alert_temp = engine.check_reading("temperature", 85.0, base_time)
        # 바로 직후 진동 센서 확인
        alert_vib = engine.check_reading(
            "vibration", 15.0, base_time + timedelta(seconds=1)
        )

        # 검증: 온도 쿨다운이 진동에 영향 없음
        assert alert_temp is not None, "온도 알람 발생"
        assert alert_vib is not None, "진동 알람도 독립적으로 발생해야 함"


# ============================================================
# 연습 2: 심각도 기반 알림 라우팅 테스트
# ============================================================

class TestSeverityRouting:
    """심각도별 알림 채널 라우팅 검증"""

    def test_warning_슬랙_이메일만_전송(self):
        """warning → Slack + Email, SMS 미전송"""
        # 준비: 모킹된 전송자
        mock_email = Mock()
        mock_sms = Mock()
        mock_slack = Mock()

        dispatcher = NotificationDispatcher(
            email_sender=mock_email,
            sms_sender=mock_sms,
            slack_sender=mock_slack,
        )

        alert = AlertEvent(
            timestamp=datetime.now(),
            sensor_type="temperature",
            value=85.0,
            severity="warning",
            message="온도 경고",
        )

        # 실행
        channels = dispatcher.dispatch(alert)

        # 검증
        assert "slack" in channels
        assert "email" in channels
        assert "sms" not in channels
        mock_slack.send.assert_called_once()
        mock_email.send.assert_called_once()
        mock_sms.send.assert_not_called()

    def test_critical_모든채널_전송(self):
        """critical → Slack + Email + SMS"""
        # 준비
        mock_email = Mock()
        mock_sms = Mock()
        mock_slack = Mock()

        dispatcher = NotificationDispatcher(
            email_sender=mock_email,
            sms_sender=mock_sms,
            slack_sender=mock_slack,
        )

        alert = AlertEvent(
            timestamp=datetime.now(),
            sensor_type="vibration",
            value=15.0,
            severity="critical",
            message="진동 위험",
        )

        # 실행
        channels = dispatcher.dispatch(alert)

        # 검증
        assert channels == ["slack", "email", "sms"]
        mock_slack.send.assert_called_once()
        mock_email.send.assert_called_once()
        mock_sms.send.assert_called_once()

    def test_info_슬랙만_전송(self):
        """info → Slack만"""
        # 준비
        mock_email = Mock()
        mock_sms = Mock()
        mock_slack = Mock()

        dispatcher = NotificationDispatcher(
            email_sender=mock_email,
            sms_sender=mock_sms,
            slack_sender=mock_slack,
        )

        alert = AlertEvent(
            timestamp=datetime.now(),
            sensor_type="pressure",
            value=550.0,
            severity="info",
            message="압력 정보",
        )

        # 실행
        channels = dispatcher.dispatch(alert)

        # 검증
        assert channels == ["slack"]
        mock_slack.send.assert_called_once()
        mock_email.send.assert_not_called()
        mock_sms.send.assert_not_called()


# ============================================================
# 연습 3: 알람 파이프라인 통합 테스트
# ============================================================

class TestAlertPipelineIntegration:
    """전체 파이프라인 통합 테스트"""

    def test_임계값_초과시_알람_및_알림(self, base_time):
        """전체 파이프라인: 임계값 초과 → 알람 → 알림"""
        # 준비
        engine = AlertEngine()
        engine.add_rule(AlertRule(
            sensor_type="temperature",
            threshold=80.0,
            severity="warning",
            cooldown_seconds=300,
        ))

        mock_email = Mock()
        mock_sms = Mock()
        mock_slack = Mock()

        dispatcher = NotificationDispatcher(
            email_sender=mock_email,
            sms_sender=mock_sms,
            slack_sender=mock_slack,
        )

        pipeline = AlertPipeline(engine=engine, dispatcher=dispatcher)

        # 실행
        result = pipeline.process_reading("temperature", 85.0, base_time)

        # 검증
        assert result is not None
        assert result["alert"].sensor_type == "temperature"
        assert "email" in result["channels"]
        mock_email.send.assert_called_once()

    def test_정상값은_알림_없음(self, base_time):
        """정상 값에 대해 알림 없음"""
        # 준비
        engine = AlertEngine()
        engine.add_rule(AlertRule(
            sensor_type="temperature",
            threshold=80.0,
            severity="warning",
            cooldown_seconds=300,
        ))

        mock_email = Mock()
        mock_sms = Mock()
        mock_slack = Mock()

        dispatcher = NotificationDispatcher(
            email_sender=mock_email,
            sms_sender=mock_sms,
            slack_sender=mock_slack,
        )

        pipeline = AlertPipeline(engine=engine, dispatcher=dispatcher)

        # 실행
        result = pipeline.process_reading("temperature", 75.0, base_time)

        # 검증
        assert result is None
        mock_email.send.assert_not_called()
        mock_slack.send.assert_not_called()

    def test_연속_리딩_쿨다운_적용(self, base_time):
        """연속 리딩에서 쿨다운 적용"""
        # 준비
        engine = AlertEngine()
        engine.add_rule(AlertRule(
            sensor_type="temperature",
            threshold=80.0,
            severity="warning",
            cooldown_seconds=300,
        ))

        mock_email = Mock()
        mock_sms = Mock()
        mock_slack = Mock()

        dispatcher = NotificationDispatcher(
            email_sender=mock_email,
            sms_sender=mock_sms,
            slack_sender=mock_slack,
        )

        pipeline = AlertPipeline(engine=engine, dispatcher=dispatcher)

        # 실행: 첫 리딩 (알람 발생)
        result1 = pipeline.process_reading("temperature", 85.0, base_time)
        # 1분 후 두 번째 리딩 (쿨다운 중)
        result2 = pipeline.process_reading(
            "temperature", 90.0, base_time + timedelta(minutes=1)
        )

        # 검증
        assert result1 is not None, "첫 리딩은 알람 발생"
        assert result2 is None, "두 번째 리딩은 쿨다운으로 알람 없음"
        # Email은 정확히 1번만 호출
        mock_email.send.assert_called_once()
