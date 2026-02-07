"""
연습 문제 15 풀이: pytest-mock 플러그인 (unittest.mock으로 구현)

AlertSystem의 다양한 동작을 테스트한 풀이입니다.
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch, call

# 상위 디렉토리의 모듈을 임포트하기 위한 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src_alert_system import (
    AlertSystem,
    NotificationService,
    AlertRepository,
    ThresholdConfig,
)


# ============================================================
# 공통 픽스처
# ============================================================

@pytest.fixture
def mock_notifier():
    """알림 서비스 Mock"""
    mock = Mock(spec=NotificationService)
    mock.send_email.return_value = True
    mock.send_sms.return_value = True
    return mock


@pytest.fixture
def mock_repository():
    """알림 저장소 Mock"""
    mock = Mock(spec=AlertRepository)
    mock.save.return_value = "ALERT-001"
    return mock


@pytest.fixture
def mock_config():
    """임계값 설정 Mock"""
    mock = Mock(spec=ThresholdConfig)
    mock.get_all_thresholds.return_value = {
        "temperature": {"warning": 80.0, "critical": 100.0},
        "vibration": {"warning": 5.0, "critical": 10.0},
        "pressure": {"warning": 8.0, "critical": 12.0},
    }
    return mock


# ============================================================
# 연습 1 풀이: 알림 서비스 패치
# ============================================================

class TestExercise1:
    """NotificationService를 Mock으로 대체하여 테스트"""

    def test_email_sent_on_high_temperature(
        self, mock_notifier, mock_repository, mock_config
    ):
        """온도 90도에서 이메일 알림이 발송된다"""
        system = AlertSystem(
            notification_service=mock_notifier,
            alert_repository=mock_repository,
            threshold_config=mock_config,
        )

        result = system.process_reading(
            equipment_id="EQ-001",
            sensor_data={"temperature": 90.0, "vibration": 2.0},
            notify_email="admin@factory.com",
        )

        # 경고 수준 확인
        assert result["alert_level"] == "warning"

        # 이메일 발송 확인
        mock_notifier.send_email.assert_called_once()

        # 이메일 제목에 "WARNING" 포함 확인
        call_args = mock_notifier.send_email.call_args
        subject = call_args[0][1]
        assert "WARNING" in subject

    def test_sms_sent_only_on_critical(
        self, mock_notifier, mock_repository, mock_config
    ):
        """SMS는 critical 수준에서만 발송된다"""
        system = AlertSystem(
            notification_service=mock_notifier,
            alert_repository=mock_repository,
            threshold_config=mock_config,
        )

        # warning 수준: SMS 미발송
        system.process_reading(
            equipment_id="EQ-001",
            sensor_data={"temperature": 85.0, "vibration": 2.0},
            notify_email="admin@factory.com",
            notify_phone="010-1234-5678",
        )
        mock_notifier.send_sms.assert_not_called()

        # critical 수준: SMS 발송
        system.process_reading(
            equipment_id="EQ-001",
            sensor_data={"temperature": 110.0, "vibration": 2.0},
            notify_email="admin@factory.com",
            notify_phone="010-1234-5678",
        )
        mock_notifier.send_sms.assert_called_once()
        assert "긴급" in mock_notifier.send_sms.call_args[0][1]


# ============================================================
# 연습 2 풀이: 임계값 설정 패치
# ============================================================

class TestExercise2:
    """ThresholdConfig를 Mock으로 대체하여 다양한 시나리오 테스트"""

    def test_custom_low_thresholds(
        self, mock_notifier, mock_repository
    ):
        """낮은 임계값에서 정상 범위의 데이터도 경고가 된다"""
        mock_config = Mock(spec=ThresholdConfig)
        mock_config.get_all_thresholds.return_value = {
            "temperature": {"warning": 25.0, "critical": 40.0},
            "vibration": {"warning": 1.0, "critical": 3.0},
        }

        system = AlertSystem(
            notification_service=mock_notifier,
            alert_repository=mock_repository,
            threshold_config=mock_config,
        )

        # 30도: 기본 임계값에서는 정상이지만, 낮은 임계값에서는 경고
        result = system.evaluate_sensor_data(
            "EQ-001",
            {"temperature": 30.0, "vibration": 0.5}
        )

        assert result == "warning"

    def test_default_thresholds_on_config_failure(
        self, mock_notifier, mock_repository
    ):
        """설정 조회 실패 시 기본 임계값이 사용된다"""
        mock_config = Mock(spec=ThresholdConfig)
        mock_config.get_all_thresholds.side_effect = Exception("연결 실패")

        system = AlertSystem(
            notification_service=mock_notifier,
            alert_repository=mock_repository,
            threshold_config=mock_config,
        )

        # 기본 임계값(80도 warning)에 의해 warning 반환
        result = system.evaluate_sensor_data(
            "EQ-001",
            {"temperature": 85.0}
        )

        assert result == "warning"


# ============================================================
# 연습 3 풀이: 알림 이력 저장 검증
# ============================================================

class TestExercise3:
    """AlertRepository의 호출 패턴을 검증"""

    def test_alert_record_contains_correct_data(
        self, mock_notifier, mock_repository, mock_config
    ):
        """저장된 알림 이력에 올바른 데이터가 포함되어 있다"""
        system = AlertSystem(
            notification_service=mock_notifier,
            alert_repository=mock_repository,
            threshold_config=mock_config,
        )

        system.process_reading(
            equipment_id="PUMP-01",
            sensor_data={"temperature": 110.0, "vibration": 12.0},
            notify_email="admin@factory.com",
        )

        # 저장 확인
        mock_repository.save.assert_called_once()

        # 저장된 데이터 검증
        saved_record = mock_repository.save.call_args[0][0]
        assert saved_record["equipment_id"] == "PUMP-01"
        assert saved_record["alert_level"] == "critical"
        assert saved_record["sensor_data"]["temperature"] == 110.0
        assert saved_record["sensor_data"]["vibration"] == 12.0

    def test_summary_combines_repository_data(
        self, mock_notifier, mock_repository, mock_config
    ):
        """get_alert_summary가 저장소 데이터를 올바르게 조합한다"""
        mock_repository.count_by_level.side_effect = [10, 3]
        mock_repository.get_recent.return_value = [
            {"level": "critical", "message": "온도 초과"}
        ]

        system = AlertSystem(
            notification_service=mock_notifier,
            alert_repository=mock_repository,
            threshold_config=mock_config,
        )

        summary = system.get_alert_summary("EQ-001")

        assert summary["warning_count"] == 10
        assert summary["critical_count"] == 3
        assert len(summary["recent_alerts"]) == 1

        # count_by_level이 2번 호출됨
        assert mock_repository.count_by_level.call_count == 2
        mock_repository.count_by_level.assert_any_call("EQ-001", "warning")
        mock_repository.count_by_level.assert_any_call("EQ-001", "critical")
