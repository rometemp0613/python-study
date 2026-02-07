# 20. 설정과 환경 테스트

## 학습 목표

이 레슨을 마치면 다음을 할 수 있습니다:

1. `monkeypatch.setenv()`를 사용하여 환경 변수에 의존하는 코드 테스트
2. `tmp_path`로 설정 파일을 생성하여 파일 기반 설정 테스트
3. `datetime` 모킹으로 시간 의존 코드 테스트
4. 설정 검증 로직과 기본값 처리 테스트

## 동기부여: 예지보전 관점

예지보전 시스템의 동작은 다양한 설정과 환경에 의해 결정됩니다:

1. **임계값 설정**: 센서별 경고/위험 온도, 진동 한계값
2. **환경 변수**: API 키, 데이터베이스 연결 문자열, 알림 채널 설정
3. **시간 기반 로직**: 야간에는 알림 억제, 정기 점검 시간 자동 알림
4. **설정 파일**: JSON/YAML로 관리되는 센서별 설정

**설정 관련 실제 사고 사례:**
- 환경 변수 오타로 기본 임계값이 적용되어 경고 누락
- 설정 파일 형식 오류로 시스템 시작 실패
- 시간대(timezone) 설정 오류로 야간 알림이 주간에 억제됨
- 설정 우선순위(환경 변수 > 파일 > 기본값) 구현 오류

## 핵심 개념 설명

### 1. monkeypatch.setenv() 기본 사용법

```python
def test_load_threshold_from_env(monkeypatch):
    """환경 변수에서 임계값을 읽는 테스트"""
    # 테스트용 환경 변수 설정 (테스트 후 자동 복원)
    monkeypatch.setenv("SENSOR_TEMP_WARNING", "80.0")
    monkeypatch.setenv("SENSOR_TEMP_CRITICAL", "95.0")

    config = ThresholdConfig()
    config.load_from_env()

    assert config.get_threshold("temperature")["warning"] == 80.0
    assert config.get_threshold("temperature")["critical"] == 95.0


def test_default_threshold_when_env_missing(monkeypatch):
    """환경 변수가 없을 때 기본값 사용"""
    # 기존 환경 변수가 있다면 제거
    monkeypatch.delenv("SENSOR_TEMP_WARNING", raising=False)
    monkeypatch.delenv("SENSOR_TEMP_CRITICAL", raising=False)

    config = ThresholdConfig()
    config.load_from_env()

    # 기본값이 적용되어야 함
    threshold = config.get_threshold("temperature")
    assert threshold["warning"] is not None
    assert threshold["critical"] is not None
```

### 2. 설정 파일 테스트 (tmp_path 활용)

```python
import json


def test_load_config_from_file(tmp_path):
    """JSON 설정 파일에서 임계값 읽기"""
    config_data = {
        "thresholds": {
            "temperature": {"warning": 75.0, "critical": 90.0},
            "vibration": {"warning": 5.0, "critical": 10.0},
        },
        "alert_hours": {"start": 8, "end": 22},
    }

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data, indent=2))

    config = ThresholdConfig()
    config.load_from_file(str(config_file))

    assert config.get_threshold("temperature")["warning"] == 75.0
    assert config.get_threshold("vibration")["critical"] == 10.0
```

### 3. datetime 모킹으로 시간 테스트

```python
from unittest.mock import patch
from datetime import datetime


def test_alert_during_business_hours():
    """업무 시간(8~22시) 중에는 알림 활성화"""
    config = ThresholdConfig()
    config.alert_start_hour = 8
    config.alert_end_hour = 22

    # 오후 2시로 시간 고정
    mock_now = datetime(2024, 1, 15, 14, 0, 0)
    with patch("src_threshold_config.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *a, **kw: datetime(*a, **kw)

        assert config.is_alert_time() is True


def test_alert_suppressed_at_night():
    """야간(22~8시)에는 알림 억제"""
    config = ThresholdConfig()
    config.alert_start_hour = 8
    config.alert_end_hour = 22

    # 새벽 3시로 시간 고정
    mock_now = datetime(2024, 1, 15, 3, 0, 0)
    with patch("src_threshold_config.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *a, **kw: datetime(*a, **kw)

        assert config.is_alert_time() is False
```

### 4. 설정 우선순위 테스트

```python
def test_env_overrides_file(monkeypatch, tmp_path):
    """환경 변수가 설정 파일보다 우선"""
    # 파일에는 80.0
    config_data = {
        "thresholds": {
            "temperature": {"warning": 80.0, "critical": 95.0},
        }
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))

    # 환경 변수에는 70.0
    monkeypatch.setenv("SENSOR_TEMP_WARNING", "70.0")

    config = ThresholdConfig()
    config.load_from_file(str(config_file))
    config.load_from_env()  # 환경 변수가 나중에 로드되어 덮어씀

    assert config.get_threshold("temperature")["warning"] == 70.0
```

### 5. 잘못된 설정 처리

```python
def test_invalid_threshold_value(monkeypatch):
    """잘못된 임계값 설정 시 ValueError"""
    monkeypatch.setenv("SENSOR_TEMP_WARNING", "not_a_number")

    config = ThresholdConfig()
    with pytest.raises(ValueError):
        config.load_from_env()


def test_missing_config_file():
    """설정 파일이 없을 때 FileNotFoundError"""
    config = ThresholdConfig()
    with pytest.raises(FileNotFoundError):
        config.load_from_file("/nonexistent/config.json")
```

## 실습 가이드

1. `src_threshold_config.py`의 설정 클래스를 살펴보세요
2. `test_config.py`의 다양한 테스트 패턴을 확인하세요
3. 테스트 실행:
   ```bash
   pytest -v test_config.py
   ```
4. 연습 문제에서 직접 설정 테스트를 작성해보세요

## 연습 문제

### 연습 1: 환경 변수 기반 설정 테스트
`monkeypatch`를 사용하여 다양한 환경 변수 시나리오(설정됨, 미설정, 잘못된 값)를
테스트하세요.

### 연습 2: 설정 파일 테스트
`tmp_path`를 사용하여 정상/비정상 JSON 설정 파일에 대한 동작을 테스트하세요.

### 연습 3: 시간 의존 로직 테스트
`datetime` 모킹을 사용하여 다양한 시간대에서의 알림 활성화/비활성화를
테스트하세요.

## 퀴즈

### Q1. `monkeypatch.setenv()`와 `os.environ`을 직접 수정하는 것의 차이점은?

**A)** `monkeypatch.setenv()`는 테스트가 끝나면 자동으로 원래 값으로 복원됩니다.
`os.environ`을 직접 수정하면 다른 테스트에 영향을 줄 수 있고,
수동으로 정리(cleanup)해야 합니다. monkeypatch는 테스트 격리를 보장합니다.

### Q2. 시간 의존 코드를 테스트할 때 `datetime.now()`를 모킹하는 이유는?

**A)** 테스트는 어느 시간에 실행하든 동일한 결과를 반환해야 합니다(결정적 테스트).
`datetime.now()`를 그대로 사용하면 테스트 실행 시간에 따라 결과가 달라져
불안정한(flaky) 테스트가 됩니다. 모킹으로 시간을 고정하면 일관된 결과를 보장합니다.

### Q3. 설정 검증 테스트에서 '행복한 경로(happy path)'만 테스트하면 안 되는 이유는?

**A)** 실제 운영 환경에서는 잘못된 설정이 자주 발생합니다:
- 환경 변수 오타, 타입 불일치
- 설정 파일 JSON 구문 오류
- 필수 설정 누락
이런 경우에 시스템이 명확한 에러 메시지와 함께 빠르게 실패하는 것이
조용히 잘못된 기본값을 사용하는 것보다 훨씬 안전합니다.

## 정리 및 다음 주제 예고

이번 레슨에서 배운 내용:
- `monkeypatch.setenv()`로 환경 변수 테스트
- `tmp_path`로 설정 파일 테스트
- `datetime` 모킹으로 시간 의존 코드 테스트
- 설정 우선순위와 유효성 검증 테스트

**다음 레슨 (21. 머신러닝/예측 모델 테스트)** 에서는:
- 이상 탐지 모델의 학습/예측 파이프라인 테스트
- 특징 추출 정확성 검증
- 모델 직렬화/역직렬화 테스트
- 성능 지표 회귀 테스트
