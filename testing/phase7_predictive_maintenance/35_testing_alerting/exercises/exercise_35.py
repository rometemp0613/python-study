"""
연습 문제 35: 알람/알림 시스템 테스트

이 파일의 TODO를 완성하여 알람/알림 파이프라인을 테스트하세요.
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
    """
    알람 쿨다운 메커니즘을 테스트하세요.
    """

    def test_쿨다운_기간내_중복_방지(self, engine, base_time):
        """
        진동 센서 알람 규칙(threshold=10.0, cooldown=600초)을 추가하고:
        1. base_time에 값 15.0으로 첫 알람을 발생시킵니다
        2. 5분 후(base_time + 5분)에 같은 값으로 다시 확인합니다
        3. 첫 번째는 알람 발생, 두 번째는 쿨다운으로 알람 없음을 확인합니다

        힌트: AlertRule(sensor_type="vibration", threshold=10.0,
              severity="critical", cooldown_seconds=600)
        """
        pytest.skip("TODO: 쿨다운 기간 내 중복 알람이 차단되는지 확인하세요")

    def test_쿨다운_만료후_재발생(self, engine, base_time):
        """
        쿨다운 시간(600초) 이후에는 알람이 다시 발생하는지 테스트하세요.

        1. base_time에 첫 알람 발생
        2. base_time + 11분(660초) 후에 두 번째 확인
        3. 두 번째도 알람이 발생하는지 확인
        """
        pytest.skip("TODO: 쿨다운 만료 후 알람 재발생을 확인하세요")

    def test_다른_센서_독립적_쿨다운(self, engine, base_time):
        """
        온도와 진동 센서 규칙을 각각 추가하고:
        1. 온도 알람을 발생시킵니다
        2. 바로 직후에 진동 알람을 확인합니다
        3. 온도 쿨다운이 진동에 영향을 주지 않음을 확인합니다

        즉, 서로 다른 센서 타입은 독립적인 쿨다운을 가져야 합니다.
        """
        pytest.skip("TODO: 서로 다른 센서의 독립적 쿨다운을 확인하세요")


# ============================================================
# 연습 2: 심각도 기반 알림 라우팅 테스트
# ============================================================

class TestSeverityRouting:
    """
    모킹을 사용하여 심각도별 올바른 채널로 알림이 가는지 테스트하세요.
    """

    def test_warning_슬랙_이메일만_전송(self):
        """
        warning 심각도의 알람이 Slack과 Email로만 전송되고,
        SMS는 전송되지 않는지 테스트하세요.

        힌트:
        1. Mock()으로 email_sender, sms_sender, slack_sender를 만드세요
        2. NotificationDispatcher를 생성하세요
        3. severity="warning"인 AlertEvent를 만들어 dispatch()하세요
        4. mock_slack.send.assert_called_once()로 호출 확인
        5. mock_sms.send.assert_not_called()로 미호출 확인
        """
        pytest.skip("TODO: warning 심각도의 라우팅을 검증하세요")

    def test_critical_모든채널_전송(self):
        """
        critical 심각도의 알람이 Slack, Email, SMS 모두로 전송되는지
        테스트하세요.
        """
        pytest.skip("TODO: critical 심각도가 모든 채널로 전송되는지 확인하세요")

    def test_info_슬랙만_전송(self):
        """
        info 심각도의 알람이 Slack으로만 전송되고,
        Email과 SMS는 전송되지 않는지 테스트하세요.
        """
        pytest.skip("TODO: info 심각도가 Slack만으로 전송되는지 확인하세요")


# ============================================================
# 연습 3: 알람 파이프라인 통합 테스트
# ============================================================

class TestAlertPipelineIntegration:
    """
    AlertEngine + NotificationDispatcher 전체 파이프라인을 테스트하세요.
    """

    def test_임계값_초과시_알람_및_알림(self, base_time):
        """
        1. AlertEngine을 생성하고 온도 규칙을 추가합니다
           (threshold=80.0, severity="warning", cooldown=300초)
        2. Mock으로 전송자를 만들고 NotificationDispatcher를 생성합니다
        3. AlertPipeline을 생성합니다
        4. 온도 85.0으로 process_reading()을 호출합니다
        5. 결과가 None이 아니고, mock_email이 호출되었는지 확인합니다
        """
        pytest.skip("TODO: 전체 파이프라인을 구성하고 통합 테스트하세요")

    def test_정상값은_알림_없음(self, base_time):
        """
        임계값 이하의 정상 값(75.0)으로 process_reading()을 호출했을 때
        결과가 None이고, 어떤 알림도 전송되지 않았는지 테스트하세요.
        """
        pytest.skip("TODO: 정상 값에 대해 알림이 없는지 확인하세요")

    def test_연속_리딩_쿨다운_적용(self, base_time):
        """
        1. 첫 번째 리딩(85.0)에서 알람이 발생하는지 확인
        2. 1분 후 두 번째 리딩(90.0)에서 쿨다운으로 알람이 없는지 확인
        3. Email mock이 정확히 1번만 호출되었는지 확인
        """
        pytest.skip("TODO: 연속 리딩에서 쿨다운이 올바르게 적용되는지 확인하세요")
