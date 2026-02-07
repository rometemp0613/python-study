"""
연습 문제 14: Patching

@patch, patch.object(), patch.dict()를 활용하여
정비 리포트 시스템을 테스트하세요.
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
# 연습 1: datetime 패칭
# ============================================================

class TestExercise1:
    """get_current_time을 패치하여 리포트 날짜를 고정"""

    def test_report_date_fixed_to_specific_date(self):
        """리포트 날짜를 2024년 7월 1일 오전 9시로 고정하세요"""
        pytest.skip("TODO: get_current_time을 패치하여 날짜를 고정하세요")
        # TODO:
        # 1. @patch 또는 with patch로 get_current_time 패치
        #    패치 대상: "src_maintenance_reporter.get_current_time"
        # 2. return_value를 datetime(2024, 7, 1, 9, 0, 0)으로 설정
        # 3. generate_report 호출
        # 4. report["report_date"]가 "2024-07-01 09:00:00"인지 확인
        # 5. report["report_year"]가 2024인지 확인

    def test_next_check_after_12_hours(self):
        """점검 주기를 12시간으로 변경하고 다음 점검 일시를 확인하세요"""
        pytest.skip("TODO: patch.dict와 get_current_time 패치를 함께 사용하세요")
        # TODO:
        # 1. patch.dict로 check_interval_hours를 12로 변경
        # 2. get_current_time을 datetime(2024, 1, 1, 0, 0, 0)으로 고정
        # 3. generate_report 호출
        # 4. next_check가 "2024-01-01 12:00:00"인지 확인


# ============================================================
# 연습 2: 설정 딕셔너리 패칭
# ============================================================

class TestExercise2:
    """patch.dict()를 사용한 설정 변경 테스트"""

    def test_custom_thresholds(self):
        """온도 임계값을 60으로 낮추고 경고가 발생하는지 확인하세요"""
        pytest.skip("TODO: patch.dict로 temperature_threshold를 변경하세요")
        # TODO:
        # 1. patch.dict(MAINTENANCE_CONFIG, {"temperature_threshold": 60.0})
        # 2. 온도 65도 데이터로 generate_report 호출
        # 3. 경고가 발생하는지 확인 (warnings 리스트에 항목 존재)
        # 4. status가 "경고"인지 확인

    def test_config_restored_after_test(self):
        """patch.dict 후 원래 설정이 복원되는지 확인하세요"""
        pytest.skip("TODO: patch.dict 전후의 설정 값을 비교하세요")
        # TODO:
        # 1. 원래 temperature_threshold 값을 기록
        # 2. with patch.dict로 값을 변경
        # 3. with 블록 안에서 변경된 값 확인
        # 4. with 블록 밖에서 원래 값으로 복원 확인


# ============================================================
# 연습 3: 외부 서비스 패칭
# ============================================================

class TestExercise3:
    """외부 알림 서비스를 패치하여 동작을 검증"""

    def test_alert_sent_with_correct_message(self):
        """경고 시 올바른 메시지가 전송되는지 검증하세요"""
        pytest.skip("TODO: patch.object로 send_alert를 패치하세요")
        # TODO:
        # 1. patch.object(NotificationClient, "send_alert")로 패치
        # 2. get_current_time도 함께 패치
        # 3. 온도 90도 데이터로 generate_and_send_report 호출
        # 4. send_alert이 호출되었는지 확인
        # 5. 전송된 메시지에 설비 ID가 포함되어 있는지 확인

    def test_no_alert_on_normal_status(self):
        """정상 상태에서는 알림이 전송되지 않는지 검증하세요"""
        pytest.skip("TODO: 정상 데이터에서 send_alert이 미호출임을 확인하세요")
        # TODO:
        # 1. patch.object(NotificationClient, "send_alert")로 패치
        # 2. get_current_time도 함께 패치
        # 3. 정상 범위 데이터로 generate_and_send_report 호출
        # 4. send_alert.assert_not_called() 확인
