"""
센서 API 클라이언트 테스트

unittest.mock을 사용하여 HTTP 호출을 모킹하고
API 클라이언트의 동작을 검증합니다.
실제 네트워크 호출은 발생하지 않습니다.
"""
import json
import socket
import pytest
from unittest.mock import patch, MagicMock, call
from urllib.error import URLError, HTTPError

from src_sensor_api_client import SensorAPIClient


# ============================================================
# 헬퍼: 가짜 HTTP 응답 생성
# ============================================================

def make_mock_response(data: dict, status: int = 200) -> MagicMock:
    """테스트용 가짜 HTTP 응답 객체 생성"""
    mock_resp = MagicMock()
    mock_resp.status = status
    mock_resp.read.return_value = json.dumps(data).encode("utf-8")
    # context manager 지원
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ============================================================
# 픽스처
# ============================================================

@pytest.fixture
def client():
    """API 클라이언트 인스턴스"""
    return SensorAPIClient(
        base_url="http://api.factory.test",
        timeout=10,
        default_retries=3,
    )


@pytest.fixture
def sample_alert_data():
    """샘플 알림 데이터"""
    return {
        "sensor_id": "S001",
        "alert_type": "temperature_high",
        "value": 95.0,
        "threshold": 80.0,
    }


# ============================================================
# fetch_latest_readings 테스트
# ============================================================

class TestFetchLatestReadings:
    """센서 읽기값 조회 테스트"""

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_successful_fetch(self, mock_urlopen, client):
        """정상적인 센서 데이터 조회"""
        response_data = {
            "sensor_id": "S001",
            "temperature": 25.5,
            "vibration": 0.6,
            "timestamp": "2024-01-01T00:00:00",
        }
        mock_urlopen.return_value = make_mock_response(response_data)

        result = client.fetch_latest_readings("S001")

        assert result["sensor_id"] == "S001"
        assert result["temperature"] == 25.5
        assert result["vibration"] == 0.6
        mock_urlopen.assert_called_once()

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_correct_url_called(self, mock_urlopen, client):
        """올바른 URL로 호출되는지 확인"""
        mock_urlopen.return_value = make_mock_response({"sensor_id": "S001"})

        client.fetch_latest_readings("S001")

        # 첫 번째 인자(URL) 확인
        called_url = mock_urlopen.call_args[0][0]
        assert called_url == "http://api.factory.test/sensors/S001/latest"

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_404_raises_value_error(self, mock_urlopen, client):
        """존재하지 않는 센서 조회 시 ValueError"""
        mock_urlopen.side_effect = HTTPError(
            url="http://api.factory.test/sensors/XXXX/latest",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None,
        )

        with pytest.raises(ValueError, match="찾을 수 없습니다"):
            client.fetch_latest_readings("XXXX")

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_401_raises_permission_error(self, mock_urlopen, client):
        """인증 실패 시 PermissionError"""
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
    def test_500_raises_runtime_error(self, mock_urlopen, client):
        """서버 오류 시 RuntimeError"""
        mock_urlopen.side_effect = HTTPError(
            url="http://api.factory.test/sensors/S001/latest",
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )

        with pytest.raises(RuntimeError, match="서버 오류"):
            client.fetch_latest_readings("S001")

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_timeout_raises_timeout_error(self, mock_urlopen, client):
        """타임아웃 시 TimeoutError"""
        mock_urlopen.side_effect = socket.timeout("요청 타임아웃")

        with pytest.raises(TimeoutError, match="타임아웃"):
            client.fetch_latest_readings("S001")

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_network_error_raises_connection_error(self, mock_urlopen, client):
        """네트워크 오류 시 ConnectionError"""
        mock_urlopen.side_effect = URLError("연결 거부")

        with pytest.raises(ConnectionError, match="네트워크"):
            client.fetch_latest_readings("S001")


# ============================================================
# submit_alert 테스트
# ============================================================

class TestSubmitAlert:
    """알림 전송 테스트"""

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_successful_alert(self, mock_urlopen, client, sample_alert_data):
        """정상적인 알림 전송"""
        response_data = {"alert_id": "A001", "status": "created"}
        mock_urlopen.return_value = make_mock_response(response_data, 201)

        result = client.submit_alert(sample_alert_data)

        assert result["alert_id"] == "A001"
        assert result["status"] == "created"

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_alert_sends_post_request(self, mock_urlopen, client, sample_alert_data):
        """POST 요청으로 전송되는지 확인"""
        mock_urlopen.return_value = make_mock_response(
            {"alert_id": "A001", "status": "created"}, 201
        )

        client.submit_alert(sample_alert_data)

        # Request 객체가 전달되었는지 확인
        call_args = mock_urlopen.call_args[0][0]
        assert call_args.method == "POST"
        assert call_args.get_header("Content-type") == "application/json"

    def test_missing_required_fields(self, client):
        """필수 필드 누락 시 ValueError"""
        incomplete_data = {
            "sensor_id": "S001",
            # alert_type, value, threshold 누락
        }

        with pytest.raises(ValueError, match="필수 필드 누락"):
            client.submit_alert(incomplete_data)

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_alert_400_bad_request(self, mock_urlopen, client, sample_alert_data):
        """잘못된 알림 데이터 (400 응답)"""
        mock_urlopen.side_effect = HTTPError(
            url="http://api.factory.test/alerts",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=None,
        )

        with pytest.raises(ValueError, match="잘못된"):
            client.submit_alert(sample_alert_data)

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_alert_timeout(self, mock_urlopen, client, sample_alert_data):
        """알림 전송 타임아웃"""
        mock_urlopen.side_effect = socket.timeout("타임아웃")

        with pytest.raises(TimeoutError, match="타임아웃"):
            client.submit_alert(sample_alert_data)


# ============================================================
# fetch_with_retry 테스트
# ============================================================

class TestFetchWithRetry:
    """재시도 로직 테스트"""

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_success_on_first_try(self, mock_urlopen, client):
        """첫 번째 시도에서 성공"""
        mock_urlopen.return_value = make_mock_response({"status": "ok"})

        result = client.fetch_with_retry("http://api.test/data", max_retries=3)

        assert result["status"] == "ok"
        assert mock_urlopen.call_count == 1

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_success_after_retries(self, mock_urlopen, client):
        """재시도 후 성공"""
        mock_urlopen.side_effect = [
            URLError("연결 거부"),          # 1차 시도 실패
            URLError("타임아웃"),             # 2차 시도 실패
            make_mock_response({"status": "ok"}),  # 3차 시도 성공
        ]

        result = client.fetch_with_retry("http://api.test/data", max_retries=3)

        assert result["status"] == "ok"
        assert mock_urlopen.call_count == 3

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_all_retries_fail(self, mock_urlopen, client):
        """모든 재시도 실패 시 ConnectionError"""
        mock_urlopen.side_effect = URLError("연결 거부")

        with pytest.raises(ConnectionError, match="재시도"):
            client.fetch_with_retry("http://api.test/data", max_retries=3)

        assert mock_urlopen.call_count == 3

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_single_retry(self, mock_urlopen, client):
        """재시도 1회로 제한"""
        mock_urlopen.side_effect = URLError("연결 거부")

        with pytest.raises(ConnectionError):
            client.fetch_with_retry("http://api.test/data", max_retries=1)

        assert mock_urlopen.call_count == 1

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_retry_count_matches_max_retries(self, mock_urlopen, client):
        """재시도 횟수가 max_retries와 정확히 일치"""
        mock_urlopen.side_effect = URLError("연결 거부")

        with pytest.raises(ConnectionError):
            client.fetch_with_retry("http://api.test/data", max_retries=5)

        assert mock_urlopen.call_count == 5

    @patch("src_sensor_api_client.urllib.request.urlopen")
    def test_success_on_last_retry(self, mock_urlopen, client):
        """마지막 재시도에서 성공"""
        mock_urlopen.side_effect = [
            URLError("실패 1"),
            URLError("실패 2"),
            URLError("실패 3"),
            URLError("실패 4"),
            make_mock_response({"status": "recovered"}),
        ]

        result = client.fetch_with_retry("http://api.test/data", max_retries=5)

        assert result["status"] == "recovered"
        assert mock_urlopen.call_count == 5


# ============================================================
# 클라이언트 초기화 테스트
# ============================================================

class TestClientInit:
    """클라이언트 초기화 테스트"""

    def test_base_url_trailing_slash_removed(self):
        """base_url 끝의 슬래시가 제거되는지 확인"""
        client = SensorAPIClient(base_url="http://api.test/")
        assert client.base_url == "http://api.test"

    def test_default_timeout(self):
        """기본 타임아웃 설정"""
        client = SensorAPIClient(base_url="http://api.test")
        assert client.timeout == 30

    def test_custom_timeout(self):
        """사용자 정의 타임아웃"""
        client = SensorAPIClient(base_url="http://api.test", timeout=60)
        assert client.timeout == 60

    def test_default_retries(self):
        """기본 재시도 횟수"""
        client = SensorAPIClient(base_url="http://api.test")
        assert client.default_retries == 3
