"""
연습 문제 14 풀이: Patching

@patch, patch.object(), patch.dict()를 활용한 풀이입니다.
"""

import pytest
import sys
import os
from unittest.mock import patch, Mock, call
from datetime import datetime

# 상위 디렉토리의 모듈을 임포트하기 위한 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src_maintenance_reporter import (
    MaintenanceReporter,
    NotificationClient,
    MAINTENANCE_CONFIG,
    get_current_time,
)


# ============================================================
# 연습 1 풀이: datetime 패칭
# ============================================================

class TestExercise1:
    """get_current_time을 패치하여 리포트 날짜를 고정"""

    @patch("src_maintenance_reporter.get_current_time")
    def test_report_date_fixed_to_specific_date(self, mock_time):
        """리포트 날짜를 2024년 7월 1일 오전 9시로 고정"""
        # 고정 시각 설정
        mock_time.return_value = datetime(2024, 7, 1, 9, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_report("EQ-001", {
            "temperature": 25.0,
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 날짜 확인
        assert report["report_date"] == "2024-07-01 09:00:00"
        assert report["report_year"] == 2024
        assert report["report_month"] == 7

    @patch.dict(MAINTENANCE_CONFIG, {"check_interval_hours": 12})
    @patch("src_maintenance_reporter.get_current_time")
    def test_next_check_after_12_hours(self, mock_time):
        """점검 주기를 12시간으로 변경하고 다음 점검 일시를 확인"""
        mock_time.return_value = datetime(2024, 1, 1, 0, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_report("EQ-001", {
            "temperature": 25.0,
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 12시간 후 점검
        assert report["next_check"] == "2024-01-01 12:00:00"


# ============================================================
# 연습 2 풀이: 설정 딕셔너리 패칭
# ============================================================

class TestExercise2:
    """patch.dict()를 사용한 설정 변경 테스트"""

    @patch.dict(MAINTENANCE_CONFIG, {"temperature_threshold": 60.0})
    @patch("src_maintenance_reporter.get_current_time")
    def test_custom_thresholds(self, mock_time):
        """온도 임계값을 60으로 낮추면 65도에서 경고가 발생한다"""
        mock_time.return_value = datetime(2024, 6, 15, 10, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_report("EQ-001", {
            "temperature": 65.0,  # 기본 임계값(80)에서는 정상이지만
            "vibration": 2.0,     # 낮춘 임계값(60)에서는 경고
            "pressure": 5.0,
        })

        assert report["status"] == "경고"
        assert len(report["warnings"]) > 0
        assert "온도 초과" in report["warnings"][0]

    def test_config_restored_after_test(self):
        """patch.dict 후 원래 설정이 복원된다"""
        original_threshold = MAINTENANCE_CONFIG["temperature_threshold"]

        with patch.dict(MAINTENANCE_CONFIG,
                        {"temperature_threshold": 999.0}):
            # 변경된 값 확인
            assert MAINTENANCE_CONFIG["temperature_threshold"] == 999.0

        # 원래 값으로 복원 확인
        assert MAINTENANCE_CONFIG["temperature_threshold"] == original_threshold


# ============================================================
# 연습 3 풀이: 외부 서비스 패칭
# ============================================================

class TestExercise3:
    """외부 알림 서비스를 패치하여 동작을 검증"""

    @patch.object(NotificationClient, "send_alert", return_value=True)
    @patch("src_maintenance_reporter.get_current_time")
    def test_alert_sent_with_correct_message(self, mock_time, mock_alert):
        """경고 시 올바른 메시지가 전송된다"""
        mock_time.return_value = datetime(2024, 6, 15, 10, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_and_send_report("EQ-001", {
            "temperature": 90.0,  # 임계값 초과
            "vibration": 2.0,
            "pressure": 5.0,
        })

        # 알림이 호출되었는지 확인
        mock_alert.assert_called_once()

        # 전송된 메시지에 설비 ID가 포함되어 있는지 확인
        call_args = mock_alert.call_args
        recipient = call_args[0][0]
        message = call_args[0][1]

        assert recipient == "admin@factory.com"
        assert "EQ-001" in message
        assert "경고" in message

    @patch.object(NotificationClient, "send_alert", return_value=True)
    @patch("src_maintenance_reporter.get_current_time")
    def test_no_alert_on_normal_status(self, mock_time, mock_alert):
        """정상 상태에서는 알림이 전송되지 않는다"""
        mock_time.return_value = datetime(2024, 6, 15, 10, 0, 0)

        reporter = MaintenanceReporter()
        report = reporter.generate_and_send_report("EQ-001", {
            "temperature": 25.0,  # 정상 범위
            "vibration": 2.0,
            "pressure": 5.0,
        })

        assert report["status"] == "정상"
        mock_alert.assert_not_called()
