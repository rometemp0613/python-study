"""
연습 문제 19 풀이: 외부 API 상호작용 테스트
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

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_400_bad_request(self, mock_urlopen, client):
        """400 Bad Request 응답 처리"""
        mock_urlopen.side_effect = HTTPError(
            url="http://api.factory.test/sensors/S001/latest",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=None,
        )

        with pytest.raises(ValueError, match="잘못된 요청"):
            client.fetch_latest_readings("S001")

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_401_unauthorized(self, mock_urlopen, client):
        """401 Unauthorized 응답 처리"""
        mock_urlopen.side_effect = HTTPError(
            url="http://api.factory.test/sensors/S001/latest",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=None,
        )

        with pytest.raises(PermissionError, match="인증"):
            client.fetch_latest_readings("S001")

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_500_server_error(self, mock_urlopen, client):
        """500 Internal Server Error 응답 처리"""
        mock_urlopen.side_effect = HTTPError(
            url="http://api.factory.test/sensors/S001/latest",
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )

        with pytest.raises(RuntimeError, match="서버 오류"):
            client.fetch_latest_readings("S001")


# ============================================================
# 연습 2: 알림 전송 성공/실패 테스트
# ============================================================

class TestAlertSubmission:
    """알림 전송 동작 테스트"""

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_successful_alert_response(self, mock_urlopen, client):
        """성공적인 알림 전송 후 응답 검증"""
        response_data = {"alert_id": "A001", "status": "created"}
        mock_urlopen.return_value = make_mock_response(response_data, 201)

        alert_data = {
            "sensor_id": "S001",
            "alert_type": "temperature_high",
            "value": 95.0,
            "threshold": 80.0,
        }
        result = client.submit_alert(alert_data)

        assert result["alert_id"] == "A001"
        assert result["status"] == "created"
        mock_urlopen.assert_called_once()

    def test_alert_with_missing_fields(self, client):
        """필수 필드 누락 시 ValueError - HTTP 호출 없이 발생"""
        incomplete_data = {"sensor_id": "S001"}

        # 네트워크 모킹 없이도 ValueError가 발생해야 함
        with pytest.raises(ValueError, match="필수 필드 누락"):
            client.submit_alert(incomplete_data)

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_alert_server_error(self, mock_urlopen, client):
        """알림 전송 중 서버 오류"""
        mock_urlopen.side_effect = HTTPError(
            url="http://api.factory.test/alerts",
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )

        alert_data = {
            "sensor_id": "S001",
            "alert_type": "temperature_high",
            "value": 95.0,
            "threshold": 80.0,
        }

        with pytest.raises(RuntimeError, match="서버 오류"):
            client.submit_alert(alert_data)


# ============================================================
# 연습 3: 재시도 로직 상세 테스트
# ============================================================

class TestRetryLogic:
    """재시도 로직의 다양한 시나리오 테스트"""

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_immediate_success_no_retry(self, mock_urlopen, client):
        """첫 번째 시도에 성공하면 재시도하지 않음"""
        mock_urlopen.return_value = make_mock_response({"status": "ok"})

        result = client.fetch_with_retry(
            "http://api.test/data", max_retries=3
        )

        assert result["status"] == "ok"
        assert mock_urlopen.call_count == 1

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_fail_then_succeed(self, mock_urlopen, client):
        """실패 후 성공"""
        mock_urlopen.side_effect = [
            URLError("연결 실패"),
            URLError("타임아웃"),
            make_mock_response({"status": "recovered"}),
        ]

        result = client.fetch_with_retry(
            "http://api.test/data", max_retries=3
        )

        assert result["status"] == "recovered"
        assert mock_urlopen.call_count == 3

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_all_attempts_fail(self, mock_urlopen, client):
        """모든 시도가 실패"""
        mock_urlopen.side_effect = URLError("연결 거부")

        with pytest.raises(ConnectionError, match="재시도"):
            client.fetch_with_retry(
                "http://api.test/data", max_retries=4
            )

        assert mock_urlopen.call_count == 4
