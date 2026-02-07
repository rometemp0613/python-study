"""
pytest-mock 스타일 테스트 데모

이 파일은 unittest.mock을 사용하지만,
pytest-mock (mocker 픽스처) 사용 시의 동등한 코드를 주석으로 보여줍니다.

pytest-mock이 설치되지 않은 환경에서도 실행 가능합니다.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from src_alert_system import (
    AlertSystem,
    NotificationService,
    AlertRepository,
    ThresholdConfig,
)


# ============================================================
# 헬퍼: Mock 객체를 생성하는 픽스처
# ============================================================

@pytest.fixture
def mock_notifier():
    """알림 서비스 Mock 객체"""
    mock = Mock(spec=NotificationService)
    mock.send_email.return_value = True
    mock.send_sms.return_value = True
    mock.send_slack.return_value = True
    return mock


@pytest.fixture
def mock_repository():
    """알림 저장소 Mock 객체"""
    mock = Mock(spec=AlertRepository)
    mock.save.return_value = "ALERT-001"
    mock.get_recent.return_value = []
    mock.count_by_level.return_value = 0
    return mock


@pytest.fixture
def mock_threshold_config():
    """임계값 설정 Mock 객체"""
    mock = Mock(spec=ThresholdConfig)
    mock.get_all_thresholds.return_value = {
        "temperature": {"warning": 80.0, "critical": 100.0},
        "vibration": {"warning": 5.0, "critical": 10.0},
        "pressure": {"warning": 8.0, "critical": 12.0},
    }
    return mock


@pytest.fixture
def alert_system(mock_notifier, mock_repository, mock_threshold_config):
    """AlertSystem 인스턴스 (모든 의존성이 Mock)"""
    return AlertSystem(
        notification_service=mock_notifier,
        alert_repository=mock_repository,
        threshold_config=mock_threshold_config,
    )


# ============================================================
# 1. 기본 패치 예제 (mocker.patch 스타일)
# ============================================================

class TestBasicPatching:
    """
    unittest.mock으로 구현한 테스트

    pytest-mock에서는 mocker.patch()를 사용합니다.
    """

    def test_normal_reading_no_notification(
        self, alert_system, mock_notifier, mock_repository
    ):
        """
        정상 데이터에서는 알림이 발송되지 않는다

        # pytest-mock 동등 코드:
        # def test_normal(self, mocker):
        #     mock_notifier = mocker.MagicMock(spec=NotificationService)
        #     ...
        """
        result = alert_system.process_reading(
            equipment_id="EQ-001",
            sensor_data={"temperature": 25.0, "vibration": 2.0},
            notify_email="admin@factory.com",
        )

        assert result["alert_level"] == "normal"
        assert result["notified"] is False
        mock_notifier.send_email.assert_not_called()
        mock_repository.save.assert_not_called()

    def test_warning_sends_email(
        self, alert_system, mock_notifier, mock_repository
    ):
        """
        경고 수준에서 이메일이 발송된다

        # pytest-mock 동등 코드:
        # def test_warning(self, mocker):
        #     mock_notifier = mocker.patch.object(
        #         NotificationService, "send_email", return_value=True
        #     )
        """
        result = alert_system.process_reading(
            equipment_id="EQ-001",
            sensor_data={"temperature": 85.0, "vibration": 2.0},
            notify_email="admin@factory.com",
        )

        assert result["alert_level"] == "warning"
        assert result["notified"] is True
        mock_notifier.send_email.assert_called_once()

        # 이메일 제목에 "WARNING"이 포함되어 있는지 확인
        call_args = mock_notifier.send_email.call_args
        assert "WARNING" in call_args[0][1]

    def test_critical_sends_email_and_sms(
        self, alert_system, mock_notifier, mock_repository
    ):
        """
        위험 수준에서 이메일과 SMS가 모두 발송된다

        # pytest-mock 동등 코드:
        # spy = mocker.spy(alert_system, "_build_alert_message")
        """
        result = alert_system.process_reading(
            equipment_id="EQ-001",
            sensor_data={"temperature": 110.0, "vibration": 2.0},
            notify_email="admin@factory.com",
            notify_phone="010-1234-5678",
        )

        assert result["alert_level"] == "critical"

        # 이메일 발송 확인
        mock_notifier.send_email.assert_called_once()

        # SMS 발송 확인 (critical일 때만)
        mock_notifier.send_sms.assert_called_once_with(
            "010-1234-5678",
            "[긴급] EQ-001 위험 상태 감지"
        )


# ============================================================
# 2. patch.object 스타일 예제
# ============================================================

class TestPatchObject:
    """
    patch.object()를 사용한 테스트

    # pytest-mock 동등 코드:
    # mocker.patch.object(ThresholdConfig, "get_all_thresholds", ...)
    """

    def test_custom_thresholds(
        self, mock_notifier, mock_repository, mock_threshold_config
    ):
        """사용자 정의 임계값으로 테스트"""
        # 낮은 임계값 설정
        mock_threshold_config.get_all_thresholds.return_value = {
            "temperature": {"warning": 30.0, "critical": 50.0},
            "vibration": {"warning": 2.0, "critical": 5.0},
        }

        system = AlertSystem(
            notification_service=mock_notifier,
            alert_repository=mock_repository,
            threshold_config=mock_threshold_config,
        )

        result = system.process_reading(
            equipment_id="EQ-001",
            sensor_data={"temperature": 35.0, "vibration": 1.0},
            notify_email="admin@factory.com",
        )

        # 낮은 임계값이므로 35도에서도 경고
        assert result["alert_level"] == "warning"

    def test_fallback_to_defaults_on_config_error(
        self, mock_notifier, mock_repository, mock_threshold_config
    ):
        """설정 조회 실패 시 기본값을 사용한다"""
        # 설정 조회에서 예외 발생
        mock_threshold_config.get_all_thresholds.side_effect = Exception(
            "설정 서버 연결 실패"
        )

        system = AlertSystem(
            notification_service=mock_notifier,
            alert_repository=mock_repository,
            threshold_config=mock_threshold_config,
        )

        # 기본 임계값(80도 warning)으로 평가됨
        result = system.evaluate_sensor_data(
            "EQ-001",
            {"temperature": 85.0}
        )

        assert result == "warning"


# ============================================================
# 3. spy 스타일 예제
# ============================================================

class TestSpyStyle:
    """
    spy 스타일 테스트

    # pytest-mock에서는 mocker.spy()를 사용:
    # spy = mocker.spy(alert_system, "evaluate_sensor_data")
    # ... 호출 후 ...
    # spy.assert_called_once_with(...)

    unittest.mock에서는 wraps 매개변수를 사용하여 구현합니다.
    """

    def test_evaluate_called_during_processing(
        self, mock_notifier, mock_repository
    ):
        """process_reading 중에 evaluate_sensor_data가 호출된다"""
        system = AlertSystem(
            notification_service=mock_notifier,
            alert_repository=mock_repository,
        )

        # wraps를 사용하여 실제 메서드를 유지하면서 추적
        # pytest-mock: spy = mocker.spy(system, "evaluate_sensor_data")
        original_method = system.evaluate_sensor_data
        with patch.object(
            system, "evaluate_sensor_data",
            wraps=original_method
        ) as spy:
            result = system.process_reading(
                equipment_id="EQ-001",
                sensor_data={"temperature": 85.0, "vibration": 2.0},
                notify_email="admin@factory.com",
            )

            # 실제 동작 수행됨
            assert result["alert_level"] == "warning"

            # 호출이 추적됨
            spy.assert_called_once_with(
                "EQ-001",
                {"temperature": 85.0, "vibration": 2.0}
            )


# ============================================================
# 4. 알림 이력 저장 검증
# ============================================================

class TestAlertRepository:
    """알림 이력 저장소와의 상호작용 검증"""

    def test_alert_record_saved_on_warning(
        self, alert_system, mock_repository
    ):
        """경고 시 알림 이력이 저장된다"""
        result = alert_system.process_reading(
            equipment_id="EQ-001",
            sensor_data={"temperature": 85.0, "vibration": 6.0},
            notify_email="admin@factory.com",
        )

        # 저장소에 저장되었는지 확인
        mock_repository.save.assert_called_once()

        # 저장된 데이터 확인
        saved_record = mock_repository.save.call_args[0][0]
        assert saved_record["equipment_id"] == "EQ-001"
        assert saved_record["alert_level"] == "warning"
        assert saved_record["sensor_data"]["temperature"] == 85.0

        # 반환된 record_id 확인
        assert result["record_id"] == "ALERT-001"

    def test_no_record_saved_on_normal(
        self, alert_system, mock_repository
    ):
        """정상 상태에서는 이력이 저장되지 않는다"""
        alert_system.process_reading(
            equipment_id="EQ-001",
            sensor_data={"temperature": 25.0, "vibration": 2.0},
        )

        mock_repository.save.assert_not_called()

    def test_alert_summary_queries_repository(
        self, alert_system, mock_repository
    ):
        """알림 요약 조회 시 저장소를 올바르게 호출한다"""
        mock_repository.count_by_level.side_effect = [5, 2]
        mock_repository.get_recent.return_value = [
            {"alert_level": "warning", "message": "온도 초과"},
        ]

        summary = alert_system.get_alert_summary("EQ-001")

        assert summary["warning_count"] == 5
        assert summary["critical_count"] == 2
        assert len(summary["recent_alerts"]) == 1

        # count_by_level이 두 번 호출됨 (warning, critical)
        assert mock_repository.count_by_level.call_count == 2
        mock_repository.count_by_level.assert_any_call("EQ-001", "warning")
        mock_repository.count_by_level.assert_any_call("EQ-001", "critical")


# ============================================================
# 5. 종합 시나리오
# ============================================================

class TestIntegrationScenario:
    """실제 사용 시나리오를 시뮬레이션하는 종합 테스트"""

    def test_multiple_readings_escalation(
        self, mock_notifier, mock_repository, mock_threshold_config
    ):
        """
        여러 번의 센서 데이터 처리에서 알림 수준이 올라가는 시나리오

        # pytest-mock 동등 코드:
        # def test_escalation(self, mocker):
        #     mock_notifier = mocker.MagicMock(spec=NotificationService)
        #     ...
        """
        system = AlertSystem(
            notification_service=mock_notifier,
            alert_repository=mock_repository,
            threshold_config=mock_threshold_config,
        )

        # 1단계: 정상 데이터
        r1 = system.process_reading(
            "EQ-001",
            {"temperature": 25.0, "vibration": 1.0},
            notify_email="admin@factory.com",
        )
        assert r1["alert_level"] == "normal"

        # 2단계: 경고 수준
        r2 = system.process_reading(
            "EQ-001",
            {"temperature": 85.0, "vibration": 3.0},
            notify_email="admin@factory.com",
        )
        assert r2["alert_level"] == "warning"

        # 3단계: 위험 수준
        r3 = system.process_reading(
            "EQ-001",
            {"temperature": 105.0, "vibration": 12.0},
            notify_email="admin@factory.com",
            notify_phone="010-1234-5678",
        )
        assert r3["alert_level"] == "critical"

        # 이메일은 2번 (warning + critical), SMS는 1번 (critical)
        assert mock_notifier.send_email.call_count == 2
        assert mock_notifier.send_sms.call_count == 1

        # 저장소에 2번 저장 (normal은 저장 안 됨)
        assert mock_repository.save.call_count == 2
