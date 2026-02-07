# 레슨 12: 테스트 더블 이론 (Test Doubles Theory)

## 1. 학습 목표

이 레슨을 마치면 다음을 할 수 있습니다:

- 5가지 테스트 더블(Dummy, Stub, Spy, Mock, Fake)의 개념과 차이점을 설명할 수 있다
- 각 테스트 더블을 언제 사용해야 하는지 판단할 수 있다
- Classical(고전파) vs Mockist(런던파) 테스트 스타일의 차이를 이해한다
- 예지보전 시스템의 의존성을 테스트 더블로 대체할 수 있다

## 2. 동기부여: 예지보전 관점

공장 설비 예지보전 시스템을 개발한다고 상상해 봅시다:

```
센서 → 데이터 수집기 → 분석 엔진 → 알림 서비스 → 이메일/SMS 발송
```

이 시스템을 테스트할 때 실제 문제들:
- **센서**: 실제 센서에서 데이터를 읽으면 테스트가 하드웨어에 의존
- **이메일 발송**: 테스트할 때마다 실제 이메일이 전송됨
- **데이터베이스**: 테스트 데이터가 실제 DB를 오염시킴
- **외부 API**: 네트워크 상태에 따라 테스트 결과가 달라짐

**테스트 더블**은 이런 외부 의존성을 "대역(替身)"으로 교체하여,
빠르고 안정적이며 반복 가능한 테스트를 만들 수 있게 해줍니다.

## 3. 핵심 개념 설명

### 3.1 테스트 더블이란?

"테스트 더블(Test Double)"은 영화의 "스턴트 더블"에서 유래한 용어입니다.
실제 객체 대신 테스트 목적으로 사용되는 대체 객체를 총칭합니다.

Gerard Meszaros가 정의한 5가지 유형:

| 유형 | 목적 | 비유 |
|------|------|------|
| **Dummy** | 매개변수 채우기용 | 빈 소화기 (자리만 차지) |
| **Stub** | 미리 준비된 응답 반환 | 녹음된 안내 메시지 |
| **Spy** | 호출 기록 + 실제 동작 | CCTV 카메라 |
| **Mock** | 기대 행위 검증 | 시험 감독관 |
| **Fake** | 간소화된 실제 구현 | 훈련용 시뮬레이터 |

### 3.2 Dummy (더미)

```python
# 더미: 실제로 사용되지 않지만 매개변수를 채우기 위해 필요한 객체
class DummyLogger:
    """아무 동작도 하지 않는 더미 로거"""
    def log(self, message):
        pass  # 아무것도 안 함

def test_sensor_creation():
    # 센서 생성 시 로거가 필수 매개변수이지만
    # 이 테스트에서는 로깅 기능을 검증하지 않음
    dummy_logger = DummyLogger()
    sensor = TemperatureSensor(logger=dummy_logger)
    assert sensor.name == "온도센서"
```

**언제 사용?**: 인터페이스를 만족시키기 위해 넘겨야 하지만, 테스트에서 실제로 사용되지 않을 때

### 3.3 Stub (스텁)

```python
# 스텁: 미리 준비된 데이터를 반환하는 객체
class StubSensorReader:
    """항상 고정된 센서 데이터를 반환하는 스텁"""
    def read_temperature(self):
        return 75.5  # 항상 같은 값 반환

    def read_vibration(self):
        return 2.3   # 항상 같은 값 반환

def test_analyze_normal_condition():
    stub_reader = StubSensorReader()
    analyzer = ConditionAnalyzer(sensor_reader=stub_reader)

    result = analyzer.analyze()

    # 상태 검증 (State Verification)
    assert result.status == "정상"
    assert result.temperature == 75.5
```

**언제 사용?**: 특정 입력에 대한 출력을 검증하고 싶을 때 (상태 검증)

### 3.4 Spy (스파이)

```python
# 스파이: 호출된 내용을 기록하면서 실제 동작도 수행
class SpyNotificationService:
    """호출 기록을 저장하는 스파이 알림 서비스"""
    def __init__(self):
        self.sent_notifications = []  # 호출 기록

    def send(self, recipient, message):
        # 호출 기록 저장
        self.sent_notifications.append({
            "recipient": recipient,
            "message": message
        })
        return True  # 성공 반환

def test_alert_sends_notification():
    spy_notifier = SpyNotificationService()
    alert_system = AlertSystem(notifier=spy_notifier)

    alert_system.check_and_alert(temperature=120.0)

    # 행위 검증 (Behavior Verification)
    assert len(spy_notifier.sent_notifications) == 1
    assert "과열" in spy_notifier.sent_notifications[0]["message"]
```

**언제 사용?**: 메서드가 올바른 인자로 호출되었는지 확인하고 싶을 때

### 3.5 Mock (목)

```python
from unittest.mock import Mock

# 목: 기대하는 호출 패턴을 미리 설정하고 검증
def test_maintenance_scheduled_on_anomaly():
    mock_scheduler = Mock()

    monitor = EquipmentMonitor(scheduler=mock_scheduler)
    monitor.process_reading(vibration=15.0)  # 비정상 진동

    # 기대한 대로 호출되었는지 검증
    mock_scheduler.schedule_maintenance.assert_called_once_with(
        equipment_id="EQ-001",
        priority="긴급"
    )
```

**언제 사용?**: 특정 메서드가 정확한 인자로 호출되었는지 검증하고 싶을 때

### 3.6 Fake (페이크)

```python
# 페이크: 실제 동작하지만 간소화된 구현
class FakeDatabase:
    """인메모리 딕셔너리로 구현한 가짜 데이터베이스"""
    def __init__(self):
        self._data = {}

    def save(self, key, value):
        self._data[key] = value

    def load(self, key):
        return self._data.get(key)

    def delete(self, key):
        self._data.pop(key, None)

def test_sensor_data_persistence():
    fake_db = FakeDatabase()
    repo = SensorDataRepository(database=fake_db)

    repo.save_reading("sensor-01", {"temp": 75.5})
    result = repo.get_reading("sensor-01")

    assert result["temp"] == 75.5
```

**언제 사용?**: 실제 구현이 너무 무겁거나 느릴 때 (DB, 파일시스템 등)

### 3.7 Classical vs Mockist 스타일

#### Classical (고전파 / Detroit School)

```python
# 고전파: 가능하면 실제 객체 사용, 외부 의존성만 대체
def test_classical_style():
    """실제 객체를 사용하고 상태를 검증"""
    # 실제 분석기 사용 (외부 의존성 없음)
    analyzer = VibrationAnalyzer()
    readings = [2.1, 2.3, 2.2, 2.4, 2.1]

    result = analyzer.analyze(readings)

    # 상태 검증: 결과 값 확인
    assert result.mean == pytest.approx(2.22, abs=0.01)
    assert result.status == "정상"
```

#### Mockist (런던파 / London School)

```python
# 런던파: 테스트 대상 외의 모든 협력자를 목으로 대체
def test_mockist_style():
    """모든 의존성을 목으로 대체하고 행위를 검증"""
    mock_reader = Mock()
    mock_reader.read.return_value = [2.1, 2.3, 2.2]

    mock_calculator = Mock()
    mock_calculator.compute_mean.return_value = 2.2

    analyzer = VibrationAnalyzer(
        reader=mock_reader,
        calculator=mock_calculator
    )
    analyzer.analyze()

    # 행위 검증: 올바른 메서드가 호출되었는지 확인
    mock_reader.read.assert_called_once()
    mock_calculator.compute_mean.assert_called_once_with([2.1, 2.3, 2.2])
```

#### 비교 정리

| 관점 | Classical (고전파) | Mockist (런던파) |
|------|-------------------|-----------------|
| 검증 방식 | 상태 검증 (State) | 행위 검증 (Behavior) |
| 테스트 대상 외 | 실제 객체 사용 | 목으로 대체 |
| 장점 | 리팩터링에 강함 | 실패 원인 찾기 쉬움 |
| 단점 | 실패 원인 찾기 어려움 | 구현에 결합됨 |
| 적합한 경우 | 도메인 로직 | 외부 시스템 연동 |

### 3.8 실무 가이드: 어떤 테스트 더블을 쓸까?

```
의존성이 외부 시스템인가? (DB, API, 이메일 등)
├── Yes → Mock 또는 Stub 사용
│   ├── 응답 데이터가 중요 → Stub
│   └── 호출 여부가 중요 → Mock
└── No → 가능하면 실제 객체 사용 (Classical)
    ├── 매개변수만 채우면 됨 → Dummy
    ├── 간소화된 구현 필요 → Fake
    └── 호출 추적 필요 → Spy
```

## 4. 실습 가이드

### 프로젝트 구조
```
12_test_doubles_theory/
├── lesson.md
├── src_notification_service.py   # 소스 코드
├── test_doubles_demo.py          # 테스트 더블 데모
└── exercises/
    ├── exercise_12.py            # 연습 문제
    └── solution_12.py            # 풀이
```

### 실행 방법
```bash
# 데모 테스트 실행
pytest test_doubles_demo.py -v

# 연습 문제 실행 (TODO를 풀기 전에는 skip됨)
pytest exercises/exercise_12.py -v

# 풀이 확인
pytest exercises/solution_12.py -v
```

## 5. 연습 문제

### 연습 1: 스텁으로 센서 데이터 대체하기
`StubSensorReader`를 만들어 특정 온도/진동 값을 반환하도록 하고,
`EquipmentAnalyzer`가 올바른 상태를 판별하는지 테스트하세요.

### 연습 2: 스파이로 알림 호출 검증하기
`SpyNotifier`를 만들어 알림 발송 내역을 기록하고,
경고 조건에서 올바른 메시지가 전송되었는지 검증하세요.

### 연습 3: 페이크 DB로 저장/조회 테스트하기
`FakeMaintenanceRepository`를 만들어 인메모리로 동작하게 하고,
정비 일정의 CRUD 동작을 테스트하세요.

## 6. 퀴즈

### 퀴즈 1
다음 중 "미리 준비된 응답을 반환"하는 테스트 더블은?
- A) Dummy
- B) Stub
- C) Mock
- D) Spy

<details>
<summary>정답</summary>
B) Stub - 스텁은 테스트에서 필요한 미리 준비된 응답을 반환합니다.
</details>

### 퀴즈 2
Classical(고전파) 테스트 스타일의 특징으로 올바른 것은?
- A) 모든 의존성을 목으로 대체한다
- B) 행위 검증을 주로 사용한다
- C) 가능하면 실제 객체를 사용하고 상태를 검증한다
- D) 테스트 실패 원인을 쉽게 찾을 수 있다

<details>
<summary>정답</summary>
C) 고전파는 가능하면 실제 객체를 사용하고, 최종 상태를 검증합니다.
</details>

### 퀴즈 3
외부 API 호출이 정확한 매개변수로 이루어졌는지 확인하고 싶을 때 가장 적합한 테스트 더블은?
- A) Dummy
- B) Stub
- C) Fake
- D) Mock

<details>
<summary>정답</summary>
D) Mock - 목은 기대하는 호출 패턴(메서드명, 인자)을 검증하는 데 특화되어 있습니다.
</details>

## 7. 정리 및 다음 주제 예고

### 이 레슨에서 배운 것
- **Dummy**: 매개변수 자리 채우기용
- **Stub**: 미리 준비된 응답 반환 (상태 검증)
- **Spy**: 호출 기록 + 결과 반환 (호출 추적)
- **Mock**: 기대 행위 설정 및 검증 (행위 검증)
- **Fake**: 간소화된 실제 구현 (인메모리 DB 등)
- **Classical vs Mockist**: 상태 검증 vs 행위 검증

### 다음 레슨 예고
**레슨 13: unittest.mock 심화**에서는 Python 표준 라이브러리의 `unittest.mock` 모듈을 깊이 있게 학습합니다.
`Mock`, `MagicMock`, `return_value`, `side_effect`, `spec` 등 실전에서 자주 쓰이는 기능을 다룹니다.
