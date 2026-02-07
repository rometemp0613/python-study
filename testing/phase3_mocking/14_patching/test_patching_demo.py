"""
Patching 데모

@patch 데코레이터, patch() 컨텍스트 매니저, patch.object(),
patch.dict(), 올바른 네임스페이스 패칭을 보여주는 예제입니다.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock, call
from datetime import datetime, timedelta

from src_maintenance_reporter import (
    MaintenanceReporter,
    NotificationClient,
    MAINTENANCE_CONFIG,
    get_current_time,
    calculate_next_check,
)


# ============================================================
# 1. @patch 데코레이터 기본 사용법
# ============================================================

class TestPatchDecorator:
    """@patch 데코레이터 사용 예제"""

    @patch("src_maintenance_reporter.get_current_time")
    def test_report_date_is_fixed(self, mock_time):
        """get_current_time을 패치하여 리포트 날짜를 고정한다"""
        # 고정된 시각 설정
        fixed_time = datetime(2024, 6, 15, 10, 30, 0)
        mock_time.return_value = fixed_time

        reporter = MaintenanceReporter()
        report = reporter.generate_report("EQ-001", {
            "temperature": 25.0,
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 리포트 날짜가 고정된 시각인지 확인
        assert report["report_date"] == "2024-06-15 10:30:00"
        assert report["report_year"] == 2024
        assert report["report_month"] == 6

    @patch("src_maintenance_reporter.get_current_time")
    def test_next_check_calculated_correctly(self, mock_time):
        """다음 점검 일시가 올바르게 계산되는지 확인한다"""
        fixed_time = datetime(2024, 1, 1, 0, 0, 0)
        mock_time.return_value = fixed_time

        reporter = MaintenanceReporter()
        report = reporter.generate_report("EQ-001", {
            "temperature": 25.0,
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 기본 점검 주기: 24시간 후
        assert report["next_check"] == "2024-01-02 00:00:00"


# ============================================================
# 2. patch() 컨텍스트 매니저
# ============================================================

class TestPatchContextManager:
    """patch() 컨텍스트 매니저 사용 예제"""

    def test_with_context_manager(self):
        """with 블록 안에서만 패치가 적용된다"""
        fixed_time = datetime(2024, 3, 15, 14, 0, 0)

        with patch("src_maintenance_reporter.get_current_time") as mock_time:
            mock_time.return_value = fixed_time

            reporter = MaintenanceReporter()
            report = reporter.generate_report("EQ-001", {
                "temperature": 25.0,
                "vibration": 2.0,
                "pressure": 5.0,
            })

            assert report["report_date"] == "2024-03-15 14:00:00"

        # with 블록 밖에서는 원래 함수가 복원됨
        actual_time = get_current_time()
        assert actual_time.year >= 2024  # 실제 시각이 반환됨

    def test_multiple_patches_context_manager(self):
        """여러 패치를 컨텍스트 매니저로 동시 적용"""
        fixed_time = datetime(2024, 6, 1, 9, 0, 0)

        with patch("src_maintenance_reporter.get_current_time") as mock_time, \
             patch.object(NotificationClient, "send_alert",
                          return_value=True) as mock_alert:

            mock_time.return_value = fixed_time

            reporter = MaintenanceReporter()
            report = reporter.generate_and_send_report("EQ-001", {
                "temperature": 90.0,  # 임계값 초과
                "vibration": 2.0,
                "pressure": 5.0,
            })

            # 경고 상태에서 알림이 발송되었는지 확인
            assert report["status"] == "경고"
            mock_alert.assert_called_once()


# ============================================================
# 3. patch.object() - 객체 메서드 패치
# ============================================================

class TestPatchObject:
    """patch.object() 사용 예제"""

    @patch.object(NotificationClient, "send_alert", return_value=True)
    @patch("src_maintenance_reporter.get_current_time")
    def test_alert_sent_on_warning(self, mock_time, mock_alert):
        """경고 상태에서 알림이 발송된다"""
        mock_time.return_value = datetime(2024, 6, 15, 10, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_and_send_report("EQ-001", {
            "temperature": 90.0,
            "vibration": 6.0,
            "pressure": 5.0,
        })

        # 알림이 올바른 수신자에게 발송되었는지 확인
        mock_alert.assert_called_once()
        call_args = mock_alert.call_args
        assert call_args[0][0] == "admin@factory.com"  # 수신자
        assert "EQ-001" in call_args[0][1]  # 메시지에 설비 ID 포함

    @patch.object(NotificationClient, "send_alert", return_value=True)
    @patch("src_maintenance_reporter.get_current_time")
    def test_no_alert_on_normal(self, mock_time, mock_alert):
        """정상 상태에서는 알림이 발송되지 않는다"""
        mock_time.return_value = datetime(2024, 6, 15, 10, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_and_send_report("EQ-001", {
            "temperature": 25.0,
            "vibration": 2.0,
            "pressure": 5.0,
        })

        assert report["status"] == "정상"
        assert report["warnings"] == []
        mock_alert.assert_not_called()

    @patch.object(NotificationClient, "send_report", return_value=True)
    @patch("src_maintenance_reporter.get_current_time")
    def test_periodic_report_sent(self, mock_time, mock_send_report):
        """정기 리포트가 발송된다"""
        mock_time.return_value = datetime(2024, 6, 15, 10, 0, 0)

        reporter = MaintenanceReporter()
        reporter.send_periodic_report("EQ-001", {
            "temperature": 25.0,
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 리포트가 발송되었는지 확인
        mock_send_report.assert_called_once()
        report_text = mock_send_report.call_args[0][1]
        assert "정비 리포트" in report_text
        assert "EQ-001" in report_text


# ============================================================
# 4. patch.dict() - 딕셔너리 패치
# ============================================================

class TestPatchDict:
    """patch.dict() 사용 예제"""

    @patch.dict(MAINTENANCE_CONFIG, {"temperature_threshold": 100.0})
    @patch("src_maintenance_reporter.get_current_time")
    def test_higher_threshold_no_warning(self, mock_time):
        """임계값을 높이면 같은 데이터에서 경고가 발생하지 않는다"""
        mock_time.return_value = datetime(2024, 6, 15, 10, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_report("EQ-001", {
            "temperature": 90.0,  # 기본 임계값(80)에서는 경고
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 임계값이 100으로 높아져서 경고 없음
        assert report["status"] == "정상"
        assert len(report["warnings"]) == 0

    @patch.dict(MAINTENANCE_CONFIG, {"temperature_threshold": 50.0})
    @patch("src_maintenance_reporter.get_current_time")
    def test_lower_threshold_triggers_warning(self, mock_time):
        """임계값을 낮추면 정상 데이터에서도 경고가 발생한다"""
        mock_time.return_value = datetime(2024, 6, 15, 10, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_report("EQ-001", {
            "temperature": 60.0,  # 기본 임계값(80)에서는 정상
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 임계값이 50으로 낮아져서 경고 발생
        assert report["status"] == "경고"
        assert len(report["warnings"]) > 0
        assert "온도 초과" in report["warnings"][0]

    @patch.dict(MAINTENANCE_CONFIG, {
        "check_interval_hours": 8,
        "company_name": "테스트공장"
    })
    @patch("src_maintenance_reporter.get_current_time")
    def test_custom_interval_and_company(self, mock_time):
        """점검 주기와 회사명을 변경하여 테스트한다"""
        mock_time.return_value = datetime(2024, 1, 1, 0, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_report("EQ-001", {
            "temperature": 25.0,
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 8시간 후 점검
        assert report["next_check"] == "2024-01-01 08:00:00"
        assert report["company"] == "테스트공장"

    @patch.dict(MAINTENANCE_CONFIG, {
        "report_recipients": ["manager@factory.com", "engineer@factory.com"]
    })
    @patch.object(NotificationClient, "send_alert", return_value=True)
    @patch("src_maintenance_reporter.get_current_time")
    def test_multiple_recipients(self, mock_time, mock_alert):
        """여러 수신자에게 알림이 발송된다"""
        mock_time.return_value = datetime(2024, 6, 15, 10, 0, 0)

        reporter = MaintenanceReporter()
        reporter.generate_and_send_report("EQ-001", {
            "temperature": 90.0,
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 2명에게 알림 발송
        assert mock_alert.call_count == 2
        recipients = [c[0][0] for c in mock_alert.call_args_list]
        assert "manager@factory.com" in recipients
        assert "engineer@factory.com" in recipients

    def test_patch_dict_restores_original(self):
        """patch.dict 후 원래 값이 복원되는지 확인한다"""
        original_threshold = MAINTENANCE_CONFIG["temperature_threshold"]

        with patch.dict(MAINTENANCE_CONFIG,
                        {"temperature_threshold": 999.0}):
            assert MAINTENANCE_CONFIG["temperature_threshold"] == 999.0

        # with 블록 밖에서 원래 값으로 복원됨
        assert MAINTENANCE_CONFIG["temperature_threshold"] == original_threshold


# ============================================================
# 5. WHERE to patch 올바른 예제
# ============================================================

class TestWhereToPath:
    """올바른 네임스페이스 패치를 보여주는 예제"""

    @patch("src_maintenance_reporter.get_current_time")
    def test_patch_where_used(self, mock_time):
        """
        get_current_time은 src_maintenance_reporter 모듈에서 정의되고 사용됨.
        따라서 'src_maintenance_reporter.get_current_time'을 패치해야 함.
        """
        mock_time.return_value = datetime(2024, 12, 25, 0, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_report("EQ-001", {
            "temperature": 25.0,
            "vibration": 2.0,
            "pressure": 5.0,
        })

        assert "2024-12-25" in report["report_date"]

    @patch("src_maintenance_reporter.MAINTENANCE_CONFIG",
           {"temperature_threshold": 50.0,
            "vibration_threshold": 3.0,
            "pressure_threshold": 6.0,
            "check_interval_hours": 12,
            "report_recipients": ["test@test.com"],
            "company_name": "테스트"})
    @patch("src_maintenance_reporter.get_current_time")
    def test_patch_module_level_config(self, mock_time):
        """모듈 수준 설정을 통째로 교체할 수 있다"""
        mock_time.return_value = datetime(2024, 1, 1, 0, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_report("EQ-001", {
            "temperature": 55.0,
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 변경된 임계값(50도)에 의해 경고 발생
        assert report["status"] == "경고"
        assert report["company"] == "테스트"


# ============================================================
# 6. 데코레이터 순서 주의
# ============================================================

class TestDecoratorOrder:
    """여러 @patch 데코레이터의 순서와 인자 매핑"""

    @patch.object(NotificationClient, "send_report", return_value=True)
    @patch.object(NotificationClient, "send_alert", return_value=True)
    @patch("src_maintenance_reporter.get_current_time")
    def test_decorator_order(self, mock_time, mock_alert, mock_report):
        """
        데코레이터 순서: 아래에서 위로 인자가 전달됨

        @patch send_report → mock_report (세 번째)
        @patch send_alert  → mock_alert (두 번째)
        @patch get_current_time → mock_time (첫 번째)
        """
        mock_time.return_value = datetime(2024, 6, 15, 10, 0, 0)

        reporter = MaintenanceReporter()

        # 경고 상태 리포트 생성 및 발송
        reporter.generate_and_send_report("EQ-001", {
            "temperature": 90.0,
            "vibration": 6.0,
            "pressure": 5.0,
        })

        # alert은 호출됨 (경고 상태)
        mock_alert.assert_called()

        # send_report는 호출되지 않음 (generate_and_send_report는 alert만 발송)
        mock_report.assert_not_called()
