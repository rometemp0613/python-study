# 레슨 35: 알람/알림 시스템 테스트

## 1. 학습 목표

이 레슨을 완료하면 다음을 할 수 있습니다:

- 임계값(threshold) 기반 알람 로직을 테스트할 수 있다
- 알람 쿨다운(cooldown) 및 중복 방지 로직을 검증할 수 있다
- 알람 억제(suppression) 기능을 테스트할 수 있다
- 알림 서비스(이메일, SMS, Slack)를 모킹(mocking)하여 테스트할 수 있다
- 심각도(severity) 기반 알림 라우팅을 테스트할 수 있다
- 전체 알람 파이프라인을 통합 테스트할 수 있다

## 2. 동기부여 (예지보전 관점)

예지보전 시스템에서 이상을 감지했다면, 다음 단계는 **적절한 사람에게 적시에 알리는 것**입니다.

알람 시스템에서 발생할 수 있는 문제:
- **알람 폭풍(Alarm Storm)**: 하나의 이상이 수백 개의 알람을 유발
- **알람 피로(Alarm Fatigue)**: 너무 많은 알람으로 인해 중요한 알람을 놓침
- **알람 누락**: 심각한 이상인데 알람이 발생하지 않음
- **알림 실패**: 알람은 발생했지만 이메일/SMS 전송이 실패

이 레슨에서는 이런 문제를 방지하기 위한 테스트 전략을 배웁니다.

## 3. 핵심 개념 설명

### 3.1 임계값 기반 알람 테스트

가장 기본적인 알람 트리거 - 센서 값이 임계값을 넘으면 알람 발생:

```python
def test_임계값_초과시_알람_발생():
    engine = AlertEngine()
    engine.add_rule(AlertRule(
        sensor_type="temperature",
        threshold=80.0,
        severity="warning",
        cooldown_seconds=60,
    ))

    alert = engine.check_reading("temperature", 85.0, datetime.now())

    assert alert is not None
    assert alert.severity == "warning"
    assert alert.value == 85.0

def test_임계값_미만시_알람_없음():
    engine = AlertEngine()
    engine.add_rule(AlertRule(
        sensor_type="temperature",
        threshold=80.0,
        severity="warning",
        cooldown_seconds=60,
    ))

    alert = engine.check_reading("temperature", 75.0, datetime.now())

    assert alert is None
```

### 3.2 쿨다운(Cooldown) 테스트

같은 센서에서 반복 알람을 방지하는 쿨다운 메커니즘:

```python
def test_쿨다운_기간_내_중복_알람_방지():
    engine = AlertEngine()
    engine.add_rule(AlertRule(
        sensor_type="vibration",
        threshold=10.0,
        severity="critical",
        cooldown_seconds=300,  # 5분 쿨다운
    ))

    now = datetime.now()

    # 첫 번째 알람 발생
    alert1 = engine.check_reading("vibration", 15.0, now)
    assert alert1 is not None

    # 1분 후 같은 센서 - 쿨다운 중이므로 알람 없음
    alert2 = engine.check_reading(
        "vibration", 15.0, now + timedelta(minutes=1)
    )
    assert alert2 is None

    # 6분 후 - 쿨다운 만료, 알람 재발생
    alert3 = engine.check_reading(
        "vibration", 15.0, now + timedelta(minutes=6)
    )
    assert alert3 is not None
```

### 3.3 알람 억제(Suppression) 테스트

유지보수 중 등의 상황에서 알람을 일시적으로 억제:

```python
def test_알람_억제_동작():
    engine = AlertEngine()
    engine.add_rule(AlertRule(
        sensor_type="temperature",
        threshold=80.0,
        severity="warning",
        cooldown_seconds=60,
    ))

    # 알람 억제 설정 (30분)
    engine.suppress_alert("temperature", duration=1800)

    # 임계값 초과해도 알람 없음 (억제 중)
    alert = engine.check_reading("temperature", 95.0, datetime.now())
    assert alert is None
```

### 3.4 알림 서비스 모킹

실제 이메일/SMS/Slack을 보내지 않고 테스트하기 위해 모킹을 사용합니다:

```python
from unittest.mock import Mock

def test_알림_디스패치_이메일():
    # 모킹된 알림 전송자
    mock_email = Mock()
    mock_sms = Mock()
    mock_slack = Mock()

    dispatcher = NotificationDispatcher(
        email_sender=mock_email,
        sms_sender=mock_sms,
        slack_sender=mock_slack,
    )

    alert = AlertEvent(
        timestamp=datetime.now(),
        sensor_type="temperature",
        value=85.0,
        severity="warning",
        message="온도 경고",
    )

    dispatcher.dispatch(alert)

    # warning은 이메일로 전송
    mock_email.send.assert_called_once()
    # warning에서는 SMS를 보내지 않음
    mock_sms.send.assert_not_called()
```

### 3.5 심각도 기반 라우팅

심각도에 따라 다른 채널로 알림을 보냅니다:

| 심각도 | 알림 채널 |
|--------|-----------|
| info | Slack만 |
| warning | Slack + Email |
| critical | Slack + Email + SMS |

```python
@pytest.mark.parametrize("severity,expected_channels", [
    ("info", ["slack"]),
    ("warning", ["slack", "email"]),
    ("critical", ["slack", "email", "sms"]),
])
def test_심각도별_알림_채널(severity, expected_channels):
    # ... 각 채널이 호출되는지 검증
```

### 3.6 전체 파이프라인 통합 테스트

센서 리딩 → 알람 엔진 → 알림 디스패처까지의 전체 흐름:

```python
def test_전체_파이프라인():
    mock_email = Mock()
    engine = AlertEngine()
    dispatcher = NotificationDispatcher(email_sender=mock_email, ...)
    pipeline = AlertPipeline(engine=engine, dispatcher=dispatcher)

    engine.add_rule(AlertRule(
        sensor_type="temperature",
        threshold=80.0,
        severity="warning",
        cooldown_seconds=60,
    ))

    # 임계값 초과 리딩 처리
    result = pipeline.process_reading("temperature", 85.0, datetime.now())

    assert result is not None
    mock_email.send.assert_called_once()
```

## 4. 실습 가이드

### 단계 1: 소스 코드 분석
`src_alert_pipeline.py`를 열어 다음을 확인하세요:
- `AlertRule` / `AlertEvent` 데이터클래스 구조
- `AlertEngine`의 알람 판정 로직 (쿨다운, 억제)
- `NotificationDispatcher`의 심각도 기반 라우팅
- `AlertPipeline`의 전체 흐름

### 단계 2: 모킹 패턴 이해
`test_alert_pipeline.py`에서 `Mock()`을 사용하는 패턴을 확인하세요:
- `assert_called_once()`: 정확히 1번 호출되었는지
- `assert_not_called()`: 호출되지 않았는지
- `call_args`: 어떤 인자로 호출되었는지

### 단계 3: 테스트 실행
```bash
cd phase7_predictive_maintenance/35_testing_alerting
pytest test_alert_pipeline.py -v
```

### 단계 4: 연습 문제 풀기
`exercises/exercise_35.py`에서 TODO를 완성하세요.

## 5. 연습 문제

### 연습 1: 쿨다운 메커니즘 테스트
알람 쿨다운이 정상 동작하는지 테스트하세요:
- 쿨다운 기간 내 중복 알람이 발생하지 않는지
- 쿨다운 만료 후 알람이 재발생하는지
- 서로 다른 센서 타입은 독립적인 쿨다운을 가지는지

### 연습 2: 심각도 기반 알림 라우팅 테스트
모킹을 사용하여 각 심각도 수준에 맞는 채널로 알림이 전송되는지 테스트하세요.

### 연습 3: 알람 파이프라인 통합 테스트
AlertEngine + NotificationDispatcher를 합친 AlertPipeline이
센서 리딩을 받아 올바르게 알람 및 알림을 처리하는지 테스트하세요.

## 6. 퀴즈

### Q1. 알람 쿨다운(cooldown)의 주된 목적은?
- A) 알람 처리 속도를 높이기 위해
- B) 동일한 이상 상태에서 반복 알람(알람 폭풍)을 방지하기 위해
- C) 서버 리소스를 절약하기 위해
- D) 알람 우선순위를 정하기 위해

**정답: B** - 센서가 지속적으로 임계값을 초과할 때 매 초마다 알람이 발생하면
알람 피로(alarm fatigue)가 생기고, 정작 중요한 알람을 놓칠 수 있습니다.

### Q2. 알림 서비스를 모킹(mocking)하여 테스트하는 이유는?
- A) 실제 이메일/SMS 전송은 비용이 들고 외부 서비스에 의존하기 때문
- B) 모킹이 실제 서비스보다 더 정확하기 때문
- C) 모킹을 사용하면 테스트가 더 느려지기 때문
- D) 실제 서비스를 사용할 수 없기 때문

**정답: A** - 테스트에서 실제 이메일/SMS를 보내면 비용이 발생하고,
외부 서비스 장애 시 테스트가 실패하며, 테스트 속도도 느려집니다.
모킹은 외부 의존성을 제거하여 빠르고 안정적인 테스트를 가능하게 합니다.

### Q3. 심각도(severity) 기반 알림 라우팅이 필요한 이유는?
- A) 모든 알림을 같은 채널로 보내면 관리가 쉬우므로
- B) 심각한 이상은 더 긴급한 채널(SMS 등)로 즉시 전달하고, 경미한 이상은 비즉시 채널(이메일, Slack)로 전달하여 대응 우선순위를 구분하기 위해
- C) 서버 부하를 줄이기 위해
- D) 비용을 절약하기 위해

**정답: B** - 모든 알림을 SMS로 보내면 알림 피로가 생기고,
모든 알림을 이메일로만 보내면 긴급 상황 대응이 늦어집니다.
심각도에 따른 라우팅으로 적절한 채널과 긴급성을 매칭합니다.

## 7. 정리 및 다음 주제 예고

### 이번 레슨 정리
- 임계값 기반 알람, 쿨다운, 억제 등의 알람 엔진 로직을 테스트하는 방법을 배웠습니다
- `Mock()`을 사용하여 외부 알림 서비스를 모킹하는 기법을 익혔습니다
- 심각도 기반 알림 라우팅 테스트, 통합 파이프라인 테스트를 실습했습니다
- 알람 폭풍 방지, 알림 피로 예방 등 실무적 관점의 테스트 전략을 이해했습니다

### Phase 7 종합 정리
Phase 7에서는 예지보전 시스템의 핵심 구성요소를 테스트했습니다:
1. **센서 데이터 처리** (레슨 32): 데이터 수집, 클리닝, 특징 추출
2. **데이터 유효성 검증** (레슨 33): 스키마, 범위, 시계열 완전성
3. **예측 모델** (레슨 34): 학습, 예측, 평가, 저장/로딩
4. **알람/알림** (레슨 35): 임계값 알람, 쿨다운, 알림 라우팅

이 네 가지 구성요소가 합쳐지면 완전한 예지보전 파이프라인이 됩니다:
**센서 데이터 → 데이터 검증 → 특징 추출 → 모델 예측 → 알람 발생 → 알림 전송**

각 단계마다 철저한 테스트가 있어야 전체 시스템을 신뢰할 수 있습니다.
