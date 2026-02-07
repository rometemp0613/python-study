"""
알람/알림 파이프라인 테스트 모듈

전체 알람 시스템을 테스트합니다:
- AlertEngine: 임계값 판정, 쿨다운, 억제
- NotificationDispatcher: 심각도 기반 알림 라우팅
- AlertPipeline: 전체 파이프라인 통합
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, call
from src_alert_pipeline import (
    AlertRule,
    AlertEvent,
    AlertEngine,
    NotificationDispatcher,
    AlertPipeline,
)


# ============================================================
# 픽스처
# ============================================================

@pytest.fixture
def engine():
    """AlertEngine 인스턴스"""
    return AlertEngine()


@pytest.fixture
def temperature_rule():
    """온도 센서 경고 규칙"""
    return AlertRule(
        sensor_type="temperature",
        threshold=80.0,
        severity="warning",
        cooldown_seconds=300,  # 5분
    )


@pytest.fixture
def vibration_rule():
    """진동 센서 위험 규칙"""
    return AlertRule(
        sensor_type="vibration",
        threshold=10.0,
        severity="critical",
        cooldown_seconds=600,  # 10분
    )


@pytest.fixture
def pressure_rule():
    """압력 센서 정보 규칙"""
    return AlertRule(
        sensor_type="pressure",
        threshold=500.0,
        severity="info",
        cooldown_seconds=120,  # 2분
    )


@pytest.fixture
def engine_with_rules(engine, temperature_rule, vibration_rule, pressure_rule):
    """규칙이 설정된 AlertEngine"""
    engine.add_rule(temperature_rule)
    engine.add_rule(vibration_rule)
    engine.add_rule(pressure_rule)
    return engine


@pytest.fixture
def mock_email():
    """모킹된 이메일 전송자"""
    return Mock()


@pytest.fixture
def mock_sms():
    """모킹된 SMS 전송자"""
    return Mock()


@pytest.fixture
def mock_slack():
    """모킹된 Slack 전송자"""
    return Mock()


@pytest.fixture
def dispatcher(mock_email, mock_sms, mock_slack):
    """모킹된 전송자를 가진 NotificationDispatcher"""
    return NotificationDispatcher(
        email_sender=mock_email,
        sms_sender=mock_sms,
        slack_sender=mock_slack,
    )


@pytest.fixture
def pipeline(engine_with_rules, dispatcher):
    """전체 AlertPipeline"""
    return AlertPipeline(engine=engine_with_rules, dispatcher=dispatcher)


@pytest.fixture
def base_time():
    """테스트 기준 시각"""
    return datetime(2024, 6, 15, 10, 0, 0)


# ============================================================
# AlertRule 데이터클래스 테스트
# ============================================================

class TestAlertRule:
    """AlertRule 데이터클래스 테스트"""

    def test_규칙_생성(self, temperature_rule):
        """AlertRule 인스턴스 생성 및 속성 확인"""
        assert temperature_rule.sensor_type == "temperature"
        assert temperature_rule.threshold == 80.0
        assert temperature_rule.severity == "warning"
        assert temperature_rule.cooldown_seconds == 300


# ============================================================
# AlertEvent 데이터클래스 테스트
# ============================================================

class TestAlertEvent:
    """AlertEvent 데이터클래스 테스트"""

    def test_이벤트_생성(self):
        """AlertEvent 인스턴스 생성"""
        event = AlertEvent(
            timestamp=datetime(2024, 1, 1),
            sensor_type="temperature",
            value=85.0,
            severity="warning",
            message="온도 경고",
        )
        assert event.sensor_type == "temperature"
        assert event.value == 85.0
        assert event.alert_id is not None  # 자동 생성된 ID

    def test_고유_ID_생성(self):
        """각 이벤트는 고유한 ID를 가짐"""
        event1 = AlertEvent(
            timestamp=datetime(2024, 1, 1),
            sensor_type="temperature",
            value=85.0,
            severity="warning",
            message="경고1",
        )
        event2 = AlertEvent(
            timestamp=datetime(2024, 1, 1),
            sensor_type="temperature",
            value=85.0,
            severity="warning",
            message="경고2",
        )
        assert event1.alert_id != event2.alert_id


# ============================================================
# AlertEngine - 임계값 판정 테스트
# ============================================================

class TestAlertEngineThreshold:
    """알람 엔진의 임계값 기반 판정 테스트"""

    def test_임계값_초과시_알람_발생(self, engine_with_rules, base_time):
        """값이 임계값을 초과하면 알람 발생"""
        alert = engine_with_rules.check_reading(
            "temperature", 85.0, base_time
        )

        assert alert is not None
        assert alert.sensor_type == "temperature"
        assert alert.value == 85.0
        assert alert.severity == "warning"

    def test_임계값_미만시_알람_없음(self, engine_with_rules, base_time):
        """값이 임계값 미만이면 알람 없음"""
        alert = engine_with_rules.check_reading(
            "temperature", 75.0, base_time
        )

        assert alert is None

    def test_임계값_정확히_같으면_알람_없음(self, engine_with_rules, base_time):
        """값이 임계값과 정확히 같으면 알람 없음 (초과만 해당)"""
        alert = engine_with_rules.check_reading(
            "temperature", 80.0, base_time
        )

        assert alert is None

    def test_규칙없는_센서_알람_없음(self, engine_with_rules, base_time):
        """규칙이 없는 센서 타입은 항상 알람 없음"""
        alert = engine_with_rules.check_reading(
            "humidity", 99.0, base_time
        )

        assert alert is None

    def test_알람_메시지_포함(self, engine_with_rules, base_time):
        """알람 이벤트에 의미 있는 메시지가 포함"""
        alert = engine_with_rules.check_reading(
            "temperature", 85.0, base_time
        )

        assert "temperature" in alert.message
        assert "85.0" in alert.message
        assert "80.0" in alert.message


# ============================================================
# AlertEngine - 쿨다운 테스트
# ============================================================

class TestAlertEngineCooldown:
    """알람 엔진의 쿨다운 메커니즘 테스트"""

    def test_쿨다운_기간내_중복_알람_방지(self, engine_with_rules, base_time):
        """쿨다운 기간 내 동일 센서 알람 방지"""
        # 첫 번째 알람
        alert1 = engine_with_rules.check_reading(
            "temperature", 85.0, base_time
        )
        assert alert1 is not None

        # 1분 후 (쿨다운 5분 내)
        alert2 = engine_with_rules.check_reading(
            "temperature", 90.0, base_time + timedelta(minutes=1)
        )
        assert alert2 is None

    def test_쿨다운_만료후_알람_재발생(self, engine_with_rules, base_time):
        """쿨다운 만료 후 알람 재발생"""
        # 첫 번째 알람
        alert1 = engine_with_rules.check_reading(
            "temperature", 85.0, base_time
        )
        assert alert1 is not None

        # 6분 후 (쿨다운 5분 만료)
        alert2 = engine_with_rules.check_reading(
            "temperature", 85.0, base_time + timedelta(minutes=6)
        )
        assert alert2 is not None

    def test_서로다른_센서_독립적_쿨다운(self, engine_with_rules, base_time):
        """서로 다른 센서 타입은 독립적인 쿨다운을 가짐"""
        # 온도 알람
        alert_temp = engine_with_rules.check_reading(
            "temperature", 85.0, base_time
        )
        assert alert_temp is not None

        # 바로 뒤에 진동 알람 (온도 쿨다운에 영향 없음)
        alert_vib = engine_with_rules.check_reading(
            "vibration", 15.0, base_time + timedelta(seconds=1)
        )
        assert alert_vib is not None

    def test_쿨다운_경계값(self, engine_with_rules, base_time):
        """쿨다운 시간 정확히 만료 직전/직후"""
        # 첫 번째 알람
        engine_with_rules.check_reading("temperature", 85.0, base_time)

        # 정확히 5분(300초) - 쿨다운 내
        alert_at_boundary = engine_with_rules.check_reading(
            "temperature", 85.0,
            base_time + timedelta(seconds=299)
        )
        assert alert_at_boundary is None

        # 5분 이후 - 쿨다운 만료
        alert_after = engine_with_rules.check_reading(
            "temperature", 85.0,
            base_time + timedelta(seconds=301)
        )
        assert alert_after is not None


# ============================================================
# AlertEngine - 억제(Suppression) 테스트
# ============================================================

class TestAlertEngineSuppression:
    """알람 억제 기능 테스트"""

    def test_억제중_알람_차단(self, engine_with_rules, base_time):
        """억제 중에는 임계값 초과해도 알람 없음"""
        engine_with_rules.suppress_alert("temperature", duration=1800)

        alert = engine_with_rules.check_reading(
            "temperature", 95.0, base_time
        )

        assert alert is None

    def test_억제_미설정_센서_정상_동작(self, engine_with_rules, base_time):
        """억제가 설정되지 않은 센서는 정상 동작"""
        engine_with_rules.suppress_alert("temperature", duration=1800)

        # 진동 센서는 억제되지 않음
        alert = engine_with_rules.check_reading(
            "vibration", 15.0, base_time
        )

        assert alert is not None

    def test_억제_해제후_알람_재작동(self, engine_with_rules, base_time):
        """억제 해제 후 알람이 다시 작동"""
        engine_with_rules.suppress_alert("temperature", duration=1800)

        # 억제 해제
        engine_with_rules.clear_suppression("temperature")

        alert = engine_with_rules.check_reading(
            "temperature", 85.0, base_time
        )

        assert alert is not None


# ============================================================
# AlertEngine - 활성 알람 목록 테스트
# ============================================================

class TestActiveAlerts:
    """활성 알람 목록 관련 테스트"""

    def test_활성_알람_추가(self, engine_with_rules, base_time):
        """발생한 알람이 활성 목록에 추가됨"""
        engine_with_rules.check_reading("temperature", 85.0, base_time)

        alerts = engine_with_rules.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0].sensor_type == "temperature"

    def test_여러_알람_활성_목록(self, engine_with_rules, base_time):
        """여러 센서의 알람이 모두 활성 목록에 포함"""
        engine_with_rules.check_reading("temperature", 85.0, base_time)
        engine_with_rules.check_reading(
            "vibration", 15.0, base_time + timedelta(seconds=1)
        )

        alerts = engine_with_rules.get_active_alerts()
        assert len(alerts) == 2

    def test_초기_활성_알람_비어있음(self, engine_with_rules):
        """초기 상태에서 활성 알람 없음"""
        alerts = engine_with_rules.get_active_alerts()
        assert len(alerts) == 0


# ============================================================
# NotificationDispatcher - 심각도 기반 라우팅 테스트
# ============================================================

class TestNotificationDispatcherRouting:
    """심각도 기반 알림 라우팅 테스트"""

    def test_info_슬랙만(self, dispatcher, mock_email, mock_sms, mock_slack):
        """info 심각도: Slack만 전송"""
        alert = AlertEvent(
            timestamp=datetime.now(),
            sensor_type="pressure",
            value=550.0,
            severity="info",
            message="압력 정보",
        )

        channels = dispatcher.dispatch(alert)

        assert channels == ["slack"]
        mock_slack.send.assert_called_once()
        mock_email.send.assert_not_called()
        mock_sms.send.assert_not_called()

    def test_warning_슬랙_이메일(self, dispatcher, mock_email, mock_sms, mock_slack):
        """warning 심각도: Slack + Email 전송"""
        alert = AlertEvent(
            timestamp=datetime.now(),
            sensor_type="temperature",
            value=85.0,
            severity="warning",
            message="온도 경고",
        )

        channels = dispatcher.dispatch(alert)

        assert "slack" in channels
        assert "email" in channels
        assert "sms" not in channels
        mock_slack.send.assert_called_once()
        mock_email.send.assert_called_once()
        mock_sms.send.assert_not_called()

    def test_critical_모든채널(self, dispatcher, mock_email, mock_sms, mock_slack):
        """critical 심각도: Slack + Email + SMS 전송"""
        alert = AlertEvent(
            timestamp=datetime.now(),
            sensor_type="vibration",
            value=15.0,
            severity="critical",
            message="진동 위험",
        )

        channels = dispatcher.dispatch(alert)

        assert "slack" in channels
        assert "email" in channels
        assert "sms" in channels
        mock_slack.send.assert_called_once()
        mock_email.send.assert_called_once()
        mock_sms.send.assert_called_once()

    @pytest.mark.parametrize("severity,expected_channels", [
        ("info", ["slack"]),
        ("warning", ["slack", "email"]),
        ("critical", ["slack", "email", "sms"]),
    ])
    def test_심각도별_채널_매핑(self, severity, expected_channels):
        """파라미터화된 심각도 → 채널 매핑 테스트"""
        mock_email = Mock()
        mock_sms = Mock()
        mock_slack = Mock()
        disp = NotificationDispatcher(
            email_sender=mock_email,
            sms_sender=mock_sms,
            slack_sender=mock_slack,
        )

        alert = AlertEvent(
            timestamp=datetime.now(),
            sensor_type="test",
            value=100.0,
            severity=severity,
            message="테스트",
        )

        channels = disp.dispatch(alert)
        assert channels == expected_channels


# ============================================================
# NotificationDispatcher - 전송 기록 테스트
# ============================================================

class TestDispatchHistory:
    """알림 전송 기록 테스트"""

    def test_전송기록_저장(self, dispatcher):
        """알림 전송 후 기록이 저장됨"""
        alert = AlertEvent(
            timestamp=datetime.now(),
            sensor_type="temperature",
            value=85.0,
            severity="warning",
            message="테스트",
        )

        dispatcher.dispatch(alert)

        history = dispatcher.get_dispatch_history()
        assert len(history) == 1
        assert history[0]["severity"] == "warning"
        assert "slack" in history[0]["channels"]
        assert "email" in history[0]["channels"]

    def test_여러번_전송_기록_누적(self, dispatcher):
        """여러 번 전송하면 기록이 누적됨"""
        for i in range(3):
            alert = AlertEvent(
                timestamp=datetime.now(),
                sensor_type="temperature",
                value=85.0 + i,
                severity="warning",
                message=f"테스트 {i}",
            )
            dispatcher.dispatch(alert)

        history = dispatcher.get_dispatch_history()
        assert len(history) == 3

    def test_초기_기록_비어있음(self, dispatcher):
        """초기 상태에서 전송 기록 없음"""
        history = dispatcher.get_dispatch_history()
        assert len(history) == 0


# ============================================================
# NotificationDispatcher - 전송 메시지 내용 테스트
# ============================================================

class TestDispatchMessage:
    """전송된 메시지 내용 테스트"""

    def test_슬랙에_전달된_메시지(self, dispatcher, mock_slack):
        """Slack에 올바른 메시지가 전달되었는지 확인"""
        alert = AlertEvent(
            timestamp=datetime.now(),
            sensor_type="temperature",
            value=85.0,
            severity="info",
            message="온도 경고: 85.0도",
        )

        dispatcher.dispatch(alert)

        mock_slack.send.assert_called_once_with("온도 경고: 85.0도")


# ============================================================
# AlertPipeline - 통합 테스트
# ============================================================

class TestAlertPipeline:
    """전체 파이프라인 통합 테스트"""

    def test_임계값_초과_전체_파이프라인(self, pipeline, base_time, mock_email, mock_slack):
        """임계값 초과 → 알람 → 알림 전송 전체 흐름"""
        result = pipeline.process_reading("temperature", 85.0, base_time)

        assert result is not None
        assert result["alert"].sensor_type == "temperature"
        assert "slack" in result["channels"]
        assert "email" in result["channels"]
        mock_email.send.assert_called_once()
        mock_slack.send.assert_called_once()

    def test_임계값_미만_파이프라인(self, pipeline, base_time, mock_email, mock_slack):
        """임계값 미만이면 파이프라인 결과 None"""
        result = pipeline.process_reading("temperature", 75.0, base_time)

        assert result is None
        mock_email.send.assert_not_called()
        mock_slack.send.assert_not_called()

    def test_쿨다운중_파이프라인(self, pipeline, base_time, mock_email):
        """쿨다운 중에는 알림 전송 없음"""
        # 첫 알람
        pipeline.process_reading("temperature", 85.0, base_time)
        mock_email.reset_mock()

        # 쿨다운 중 두 번째 리딩
        result = pipeline.process_reading(
            "temperature", 90.0, base_time + timedelta(minutes=1)
        )

        assert result is None
        mock_email.send.assert_not_called()

    def test_critical_알람_전체_채널_전송(
        self, pipeline, base_time, mock_email, mock_sms, mock_slack
    ):
        """critical 알람은 모든 채널로 전송"""
        result = pipeline.process_reading("vibration", 15.0, base_time)

        assert result is not None
        assert result["alert"].severity == "critical"
        mock_slack.send.assert_called_once()
        mock_email.send.assert_called_once()
        mock_sms.send.assert_called_once()

    def test_연속_다른센서_리딩(self, pipeline, base_time, mock_email):
        """다른 센서의 연속 리딩은 각각 독립적으로 처리"""
        # 온도 알람
        result1 = pipeline.process_reading("temperature", 85.0, base_time)
        assert result1 is not None

        # 진동 알람 (온도 쿨다운에 영향 없음)
        result2 = pipeline.process_reading(
            "vibration", 15.0, base_time + timedelta(seconds=1)
        )
        assert result2 is not None

    def test_정상_리딩_연속처리(self, pipeline, base_time, mock_email, mock_slack):
        """정상 리딩은 아무 처리 없이 None 반환"""
        for i in range(10):
            result = pipeline.process_reading(
                "temperature", 70.0 + i,
                base_time + timedelta(seconds=i)
            )
            assert result is None

        mock_email.send.assert_not_called()
        mock_slack.send.assert_not_called()
