"""
연습 문제 19: 외부 API 상호작용 테스트

unittest.mock을 사용하여 HTTP 호출을 모킹하고
API 클라이언트의 다양한 동작을 테스트하세요.
"""
import json
import socket
import pytest
from unittest.mock import patch, MagicMock
from urllib.error import URLError, HTTPError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src_sensor_api_client import SensorAPIClient


def make_mock_response(data: dict, status: int = 200) -> MagicMock:
    """테스트용 가짜 HTTP 응답 객체 생성 헬퍼"""
    mock_resp = MagicMock()
    mock_resp.status = status
    mock_resp.read.return_value = json.dumps(data).encode("utf-8")
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


@pytest.fixture
def client():
    """API 클라이언트 인스턴스"""
    return SensorAPIClient(
        base_url="http://api.factory.test",
        timeout=10,
    )


# ============================================================
# 연습 1: 다양한 HTTP 에러 응답 테스트
# ============================================================

class TestHTTPErrors:
    """다양한 HTTP 상태 코드에 대한 에러 처리 테스트"""

    def test_400_bad_request(self, client):
        """400 Bad Request 응답 처리"""
        pytest.skip(
            "TODO: urlopen이 HTTPError(code=400)를 발생시키도록 모킹하고 "
            "fetch_latest_readings가 ValueError를 발생시키는지 확인하세요"
        )

    def test_401_unauthorized(self, client):
        """401 Unauthorized 응답 처리"""
        pytest.skip(
            "TODO: urlopen이 HTTPError(code=401)를 발생시키도록 모킹하고 "
            "fetch_latest_readings가 PermissionError를 발생시키는지 확인하세요"
        )

    def test_500_server_error(self, client):
        """500 Internal Server Error 응답 처리"""
        pytest.skip(
            "TODO: urlopen이 HTTPError(code=500)를 발생시키도록 모킹하고 "
            "fetch_latest_readings가 RuntimeError를 발생시키는지 확인하세요"
        )


# ============================================================
# 연습 2: 알림 전송 성공/실패 테스트
# ============================================================

class TestAlertSubmission:
    """알림 전송 동작 테스트"""

    def test_successful_alert_response(self, client):
        """성공적인 알림 전송 후 응답 검증"""
        pytest.skip(
            "TODO: urlopen이 {alert_id: 'A001', status: 'created'}를 반환하도록 "
            "모킹하고 submit_alert의 반환값을 검증하세요"
        )

    def test_alert_with_missing_fields(self, client):
        """필수 필드 누락 시 ValidationError"""
        pytest.skip(
            "TODO: sensor_id만 포함된 불완전한 데이터로 submit_alert를 호출하고 "
            "ValueError가 발생하는지 확인하세요. 힌트: HTTP 호출 없이 발생해야 함"
        )

    def test_alert_server_error(self, client):
        """알림 전송 중 서버 오류"""
        pytest.skip(
            "TODO: urlopen이 HTTPError(code=500)를 발생시키도록 모킹하고 "
            "submit_alert가 RuntimeError를 발생시키는지 확인하세요"
        )


# ============================================================
# 연습 3: 재시도 로직 상세 테스트
# ============================================================

class TestRetryLogic:
    """재시도 로직의 다양한 시나리오 테스트"""

    def test_immediate_success_no_retry(self, client):
        """첫 번째 시도에 성공하면 재시도하지 않음"""
        pytest.skip(
            "TODO: urlopen이 즉시 성공 응답을 반환하도록 모킹하고 "
            "call_count가 1인지 확인하세요"
        )

    def test_fail_then_succeed(self, client):
        """실패 후 성공"""
        pytest.skip(
            "TODO: side_effect로 [URLError, URLError, 성공응답]을 설정하고 "
            "최종적으로 성공 결과를 반환하며 call_count가 3인지 확인하세요"
        )

    def test_all_attempts_fail(self, client):
        """모든 시도가 실패"""
        pytest.skip(
            "TODO: urlopen이 항상 URLError를 발생시키도록 설정하고 "
            "max_retries=4일 때 ConnectionError가 발생하며 "
            "call_count가 4인지 확인하세요"
        )
