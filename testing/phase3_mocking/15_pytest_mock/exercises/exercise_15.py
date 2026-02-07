"""
연습 문제 15: pytest-mock 플러그인 (unittest.mock으로 구현)

AlertSystem의 다양한 동작을 테스트하세요.
pytest-mock의 패턴을 unittest.mock으로 구현합니다.
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
# 연습 1: 알림 서비스 패치
# ============================================================

class TestExercise1:
    """NotificationService를 Mock으로 대체하여 테스트"""

    def test_email_sent_on_high_temperature(self):
        """온도 90도에서 이메일 알림이 발송되는지 테스트하세요"""
        pytest.skip("TODO: NotificationService를 Mock으로 만들고 이메일 발송을 검증하세요")
        # TODO:
        # 1. Mock(spec=NotificationService)로 mock_notifier 생성
        #    - send_email.return_value = True
        # 2. Mock(spec=AlertRepository)로 mock_repo 생성
        #    - save.return_value = "ALERT-001"
        # 3. AlertSystem 생성 (위 Mock들 전달)
        # 4. process_reading 호출:
        #    - equipment_id="EQ-001"
        #    - sensor_data={"temperature": 90.0, "vibration": 2.0}
        #    - notify_email="admin@factory.com"
        # 5. result["alert_level"]이 "warning"인지 확인
        # 6. mock_notifier.send_email.assert_called_once() 확인
        # 7. 이메일 제목에 "WARNING"이 포함되어 있는지 확인

    def test_sms_sent_only_on_critical(self):
        """SMS는 critical 수준에서만 발송되는지 테스트하세요"""
        pytest.skip("TODO: warning에서는 SMS 미발송, critical에서는 발송을 검증하세요")
        # TODO:
        # 1. warning 수준 데이터로 process_reading 호출
        #    → send_sms.assert_not_called() 확인
        # 2. critical 수준 데이터로 process_reading 호출
        #    → send_sms.assert_called_once() 확인


# ============================================================
# 연습 2: 임계값 설정 패치
# ============================================================

class TestExercise2:
    """ThresholdConfig를 Mock으로 대체하여 다양한 시나리오 테스트"""

    def test_custom_low_thresholds(self):
        """낮은 임계값에서 정상 범위의 데이터도 경고가 되는지 테스트하세요"""
        pytest.skip("TODO: 낮은 임계값을 설정하고 경고 수준을 확인하세요")
        # TODO:
        # 1. Mock(spec=ThresholdConfig)로 mock_config 생성
        # 2. get_all_thresholds의 반환값을 낮은 임계값으로 설정:
        #    {"temperature": {"warning": 25.0, "critical": 40.0}, ...}
        # 3. 온도 30도 데이터로 evaluate_sensor_data 호출
        # 4. 결과가 "warning"인지 확인

    def test_default_thresholds_on_config_failure(self):
        """설정 조회 실패 시 기본 임계값이 사용되는지 테스트하세요"""
        pytest.skip("TODO: ThresholdConfig에서 예외를 발생시키고 기본값 사용을 확인하세요")
        # TODO:
        # 1. mock_config.get_all_thresholds.side_effect = Exception("연결 실패")
        # 2. 온도 85도 데이터로 evaluate_sensor_data 호출
        # 3. 기본 임계값(80도 warning)에 의해 "warning"이 반환되는지 확인


# ============================================================
# 연습 3: 알림 이력 저장 검증
# ============================================================

class TestExercise3:
    """AlertRepository의 호출 패턴을 검증"""

    def test_alert_record_contains_correct_data(self):
        """저장된 알림 이력에 올바른 데이터가 포함되어 있는지 검증하세요"""
        pytest.skip("TODO: save 호출 인자를 검증하세요")
        # TODO:
        # 1. AlertSystem 생성 (Mock 의존성)
        # 2. 온도 110도 데이터로 process_reading 호출
        # 3. mock_repository.save.assert_called_once()
        # 4. save에 전달된 딕셔너리에서 확인:
        #    - equipment_id가 올바른지
        #    - alert_level이 "critical"인지
        #    - sensor_data에 temperature가 포함되어 있는지

    def test_summary_combines_repository_data(self):
        """get_alert_summary가 저장소 데이터를 올바르게 조합하는지 테스트하세요"""
        pytest.skip("TODO: count_by_level과 get_recent의 반환값을 설정하고 요약을 확인하세요")
        # TODO:
        # 1. mock_repository.count_by_level.side_effect = [10, 3]
        # 2. mock_repository.get_recent.return_value = [{"level": "critical"}]
        # 3. get_alert_summary("EQ-001") 호출
        # 4. warning_count가 10, critical_count가 3인지 확인
        # 5. recent_alerts에 1개 항목이 있는지 확인
