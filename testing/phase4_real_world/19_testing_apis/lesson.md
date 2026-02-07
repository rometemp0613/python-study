# 19. 외부 API 상호작용 테스트

## 학습 목표

이 레슨을 마치면 다음을 할 수 있습니다:

1. `unittest.mock`을 사용하여 HTTP 호출을 모킹하는 테스트 작성
2. API 클라이언트의 재시도(retry) 로직 테스트
3. 타임아웃과 네트워크 오류 처리 테스트
4. 다양한 HTTP 응답 상태 코드에 대한 에러 처리 테스트

## 동기부여: 예지보전 관점

예지보전 시스템은 다양한 외부 API와 상호작용합니다:

1. **센서 데이터 API**: IoT 플랫폼에서 실시간 센서 읽기값 조회
2. **알림 API**: 이상 감지 시 유지보수팀에 경고 전송
3. **장비 관리 API**: 장비 상태 업데이트, 정비 이력 조회

**실제로 발생하는 문제들:**
- 네트워크 불안정으로 API 호출 실패 -> 센서 데이터 누락
- 알림 API 타임아웃 -> 긴급 경고가 전달되지 않음
- 재시도 로직 버그 -> 동일 알림이 수십 번 중복 전송
- API 응답 형식 변경 -> 파싱 오류로 시스템 전체 중단

**테스트에서 실제 API를 호출하면 안 되는 이유:**
- 네트워크 의존성으로 테스트가 불안정해짐
- 실제 알림이 발송될 수 있음
- API 호출 비용 발생
- 테스트 실행 속도 저하

## 핵심 개념 설명

### 1. unittest.mock 기본: HTTP 호출 모킹

```python
from unittest.mock import patch, MagicMock
import json


def test_fetch_sensor_reading():
    """센서 읽기값 조회 API 테스트"""
    # 가짜 HTTP 응답 생성
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = json.dumps({
        "sensor_id": "S001",
        "temperature": 25.5,
        "timestamp": "2024-01-01T00:00:00"
    }).encode("utf-8")
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = SensorAPIClient(base_url="http://api.example.com")
        result = client.fetch_latest_readings("S001")

    assert result["sensor_id"] == "S001"
    assert result["temperature"] == 25.5
```

### 2. POST 요청 모킹

```python
def test_submit_alert():
    """이상 감지 알림 전송 테스트"""
    mock_response = MagicMock()
    mock_response.status = 201
    mock_response.read.return_value = json.dumps({
        "alert_id": "A001",
        "status": "created"
    }).encode("utf-8")
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        client = SensorAPIClient(base_url="http://api.example.com")
        alert_data = {
            "sensor_id": "S001",
            "alert_type": "temperature_high",
            "value": 95.0,
            "threshold": 80.0,
        }
        result = client.submit_alert(alert_data)

    assert result["alert_id"] == "A001"
    # urlopen이 호출되었는지 확인
    mock_urlopen.assert_called_once()
```

### 3. 재시도 로직 테스트

```python
from urllib.error import URLError


def test_retry_on_failure():
    """네트워크 오류 시 재시도 동작 확인"""
    mock_success = MagicMock()
    mock_success.status = 200
    mock_success.read.return_value = b'{"status": "ok"}'
    mock_success.__enter__ = lambda s: s
    mock_success.__exit__ = MagicMock(return_value=False)

    # 처음 2번은 실패, 3번째에 성공
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = [
            URLError("연결 거부"),      # 1차 시도 실패
            URLError("타임아웃"),         # 2차 시도 실패
            mock_success,               # 3차 시도 성공
        ]

        client = SensorAPIClient(base_url="http://api.example.com")
        result = client.fetch_with_retry(
            "http://api.example.com/data",
            max_retries=3
        )

    assert result["status"] == "ok"
    assert mock_urlopen.call_count == 3


def test_retry_exhausted():
    """최대 재시도 횟수 초과 시 예외 발생"""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = URLError("연결 거부")

        client = SensorAPIClient(base_url="http://api.example.com")
        with pytest.raises(ConnectionError):
            client.fetch_with_retry(
                "http://api.example.com/data",
                max_retries=3
            )

    assert mock_urlopen.call_count == 3
```

### 4. 타임아웃 테스트

```python
import socket


def test_timeout_handling():
    """타임아웃 발생 시 적절한 에러 처리"""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = socket.timeout("요청 타임아웃")

        client = SensorAPIClient(base_url="http://api.example.com")
        with pytest.raises(TimeoutError):
            client.fetch_latest_readings("S001")
```

### 5. HTTP 상태 코드별 에러 처리

```python
from urllib.error import HTTPError


def test_404_not_found():
    """존재하지 않는 센서 ID 조회"""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = HTTPError(
            url="http://api.example.com/sensors/XXXX",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None,
        )

        client = SensorAPIClient(base_url="http://api.example.com")
        with pytest.raises(ValueError, match="센서.*찾을 수 없습니다"):
            client.fetch_latest_readings("XXXX")
```

## 실습 가이드

1. `src_sensor_api_client.py`의 API 클라이언트 클래스를 살펴보세요
2. `test_api_client.py`의 모킹 패턴을 확인하세요
3. 테스트 실행:
   ```bash
   pytest -v test_api_client.py
   ```
4. 연습 문제에서 직접 모킹 테스트를 작성해보세요

## 연습 문제

### 연습 1: 다양한 HTTP 에러 응답 테스트
400(Bad Request), 401(Unauthorized), 500(Internal Server Error) 응답에 대한
에러 처리를 테스트하세요.

### 연습 2: 알림 전송 성공/실패 테스트
`submit_alert` 메서드가 성공 시 올바른 응답을 반환하고,
실패 시 적절한 예외를 발생시키는지 테스트하세요.

### 연습 3: 재시도 로직 상세 테스트
다양한 실패 패턴(모두 실패, 마지막에 성공, 즉시 성공)에 대한
재시도 동작을 테스트하세요.

## 퀴즈

### Q1. 테스트에서 실제 HTTP 호출 대신 mock을 사용하는 주요 이유 3가지는?

**A)** 1) 테스트 격리: 네트워크 상태에 무관하게 일관된 테스트 결과
2) 속도: 네트워크 호출 없이 밀리초 단위로 테스트 실행
3) 안전: 실제 알림 전송, API 호출 비용 등 부작용 방지

### Q2. `side_effect`와 `return_value`의 차이점은?

**A)** `return_value`는 mock이 호출될 때마다 같은 값을 반환합니다.
`side_effect`는 리스트를 전달하면 호출될 때마다 순서대로 다른 값을 반환하고,
예외 클래스를 전달하면 호출 시 예외를 발생시킵니다.
재시도 로직 테스트 시 `side_effect=[에러, 에러, 성공값]` 패턴이 자주 사용됩니다.

### Q3. `assert_called_once()`와 `assert_called_once_with()`의 차이점은?

**A)** `assert_called_once()`는 mock이 정확히 한 번 호출되었는지만 확인합니다.
`assert_called_once_with(args)`는 한 번 호출되었는지와 함께
전달된 인자가 정확히 일치하는지도 확인합니다.
API 테스트에서는 올바른 URL과 파라미터로 호출되었는지 검증할 때 유용합니다.

## 정리 및 다음 주제 예고

이번 레슨에서 배운 내용:
- `unittest.mock.patch`로 HTTP 호출 모킹
- 재시도(retry) 로직의 다양한 시나리오 테스트
- 타임아웃, 네트워크 오류 처리 테스트
- HTTP 상태 코드별 에러 처리 테스트

**다음 레슨 (20. 설정과 환경 테스트)** 에서는:
- `monkeypatch.setenv()`로 환경 변수 테스트
- 설정 파일 읽기 테스트
- 시간 의존 코드 테스트 (datetime 모킹)
- 설정 검증 로직 테스트
