"""
센서 API 클라이언트 모듈

공장 센서 데이터를 조회하고 이상 감지 알림을 전송하는
API 클라이언트를 구현합니다.

HTTP 통신에 urllib.request를 사용합니다 (외부 의존성 없음).
"""
import json
import socket
import time
import urllib.request
import urllib.error
from typing import Any, Optional


class SensorAPIClient:
    """
    센서 데이터 API 클라이언트

    공장 설비 모니터링 시스템의 REST API와 통신합니다.
    재시도 로직, 타임아웃 처리, 에러 핸들링을 포함합니다.
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        default_retries: int = 3,
    ):
        """
        Args:
            base_url: API 기본 URL (예: "http://api.factory.com")
            timeout: HTTP 요청 타임아웃 (초)
            default_retries: 기본 재시도 횟수
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_retries = default_retries

    def fetch_latest_readings(self, sensor_id: str) -> dict:
        """
        특정 센서의 최신 읽기값 조회

        GET /sensors/{sensor_id}/latest

        Args:
            sensor_id: 센서 식별자 (예: "S001")

        Returns:
            센서 읽기값 딕셔너리
            예: {"sensor_id": "S001", "temperature": 25.5, "timestamp": "..."}

        Raises:
            ValueError: 센서를 찾을 수 없을 때 (404)
            ConnectionError: 네트워크 오류 시
            TimeoutError: 요청 타임아웃 시
            RuntimeError: 서버 오류 시 (5xx)
        """
        url = f"{self.base_url}/sensors/{sensor_id}/latest"

        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(
                    f"센서 '{sensor_id}'를 찾을 수 없습니다"
                ) from e
            elif e.code == 401:
                raise PermissionError("API 인증에 실패했습니다") from e
            elif e.code == 400:
                raise ValueError("잘못된 요청입니다") from e
            elif e.code >= 500:
                raise RuntimeError(
                    f"서버 오류가 발생했습니다 (HTTP {e.code})"
                ) from e
            else:
                raise RuntimeError(
                    f"예상치 못한 HTTP 오류: {e.code}"
                ) from e

        except socket.timeout as e:
            raise TimeoutError(
                f"센서 '{sensor_id}' 데이터 조회 타임아웃"
            ) from e

        except urllib.error.URLError as e:
            raise ConnectionError(
                f"네트워크 연결 실패: {e.reason}"
            ) from e

    def submit_alert(self, alert_data: dict) -> dict:
        """
        이상 감지 알림 전송

        POST /alerts

        Args:
            alert_data: 알림 데이터 딕셔너리
                필수 키: sensor_id, alert_type, value, threshold

        Returns:
            생성된 알림 정보
            예: {"alert_id": "A001", "status": "created"}

        Raises:
            ValueError: 잘못된 알림 데이터 (400)
            ConnectionError: 네트워크 오류 시
            TimeoutError: 요청 타임아웃 시
            RuntimeError: 서버 오류 시 (5xx)
        """
        # 필수 필드 검증
        required_fields = ["sensor_id", "alert_type", "value", "threshold"]
        missing = [f for f in required_fields if f not in alert_data]
        if missing:
            raise ValueError(f"필수 필드 누락: {', '.join(missing)}")

        url = f"{self.base_url}/alerts"
        payload = json.dumps(alert_data).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data

        except urllib.error.HTTPError as e:
            if e.code == 400:
                raise ValueError("잘못된 알림 데이터입니다") from e
            elif e.code == 401:
                raise PermissionError("API 인증에 실패했습니다") from e
            elif e.code >= 500:
                raise RuntimeError(
                    f"서버 오류가 발생했습니다 (HTTP {e.code})"
                ) from e
            else:
                raise RuntimeError(
                    f"예상치 못한 HTTP 오류: {e.code}"
                ) from e

        except socket.timeout as e:
            raise TimeoutError("알림 전송 타임아웃") from e

        except urllib.error.URLError as e:
            raise ConnectionError(
                f"네트워크 연결 실패: {e.reason}"
            ) from e

    def fetch_with_retry(
        self,
        url: str,
        max_retries: Optional[int] = None,
        retry_delay: float = 0.0,
    ) -> dict:
        """
        재시도 로직이 포함된 HTTP GET 요청

        네트워크 오류(URLError) 발생 시 지정된 횟수만큼 재시도합니다.
        HTTP 에러(4xx, 5xx)는 즉시 실패합니다.

        Args:
            url: 요청 URL
            max_retries: 최대 재시도 횟수 (기본: self.default_retries)
            retry_delay: 재시도 간 대기 시간 (초, 테스트 시 0으로 설정)

        Returns:
            응답 데이터 딕셔너리

        Raises:
            ConnectionError: 모든 재시도가 실패했을 때
        """
        if max_retries is None:
            max_retries = self.default_retries

        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                with urllib.request.urlopen(url, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    return data

            except urllib.error.HTTPError:
                # HTTP 에러(4xx, 5xx)는 재시도하지 않고 즉시 전파
                raise

            except urllib.error.URLError as e:
                # 네트워크 오류는 재시도
                last_error = e
                if attempt < max_retries and retry_delay > 0:
                    time.sleep(retry_delay)
                continue

        raise ConnectionError(
            f"{max_retries}회 재시도 후에도 연결 실패: {last_error}"
        )

    def fetch_sensor_history(
        self,
        sensor_id: str,
        start_time: str,
        end_time: str,
    ) -> list:
        """
        센서 이력 데이터 조회

        GET /sensors/{sensor_id}/history?start={start}&end={end}

        Args:
            sensor_id: 센서 식별자
            start_time: 시작 시간 (ISO 형식)
            end_time: 종료 시간 (ISO 형식)

        Returns:
            센서 읽기값 리스트
        """
        url = (
            f"{self.base_url}/sensors/{sensor_id}/history"
            f"?start={start_time}&end={end_time}"
        )

        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(
                    f"센서 '{sensor_id}'를 찾을 수 없습니다"
                ) from e
            raise RuntimeError(f"HTTP 오류: {e.code}") from e

        except socket.timeout as e:
            raise TimeoutError("이력 데이터 조회 타임아웃") from e

        except urllib.error.URLError as e:
            raise ConnectionError(
                f"네트워크 연결 실패: {e.reason}"
            ) from e
