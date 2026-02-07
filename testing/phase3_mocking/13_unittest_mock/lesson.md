# 레슨 13: unittest.mock 심화

## 1. 학습 목표

이 레슨을 마치면 다음을 할 수 있습니다:

- `Mock`과 `MagicMock`의 차이를 이해하고 적절히 사용할 수 있다
- `return_value`와 `side_effect`를 활용하여 다양한 시나리오를 시뮬레이션할 수 있다
- `assert_called_*` 메서드로 호출 패턴을 검증할 수 있다
- `spec`/`autospec`으로 안전한 목 객체를 만들 수 있다
- `PropertyMock`과 `sentinel`을 실전에서 활용할 수 있다

## 2. 동기부여: 예지보전 관점

예지보전 시스템에서는 다양한 외부 시스템과 통신합니다:

```
센서 API → 데이터 수집기 → 분석 엔진 → 결과 저장소
                                    ↓
                              알림 시스템
```

`unittest.mock`은 Python 표준 라이브러리에 포함된 강력한 목킹 도구입니다.
외부 API, 데이터베이스, 센서 등을 Mock으로 대체하면:

- 센서 API가 다운되어도 테스트 가능
- 다양한 센서 응답 시나리오 시뮬레이션 가능
- API 호출 횟수/인자를 정확히 검증 가능
- 네트워크 오류, 타임아웃 등 예외 상황 테스트 가능

## 3. 핵심 개념 설명

### 3.1 Mock vs MagicMock

```python
from unittest.mock import Mock, MagicMock

# Mock: 기본 목 객체
mock = Mock()
mock.some_method()           # 에러 없이 호출 가능
mock.any_attribute            # 에러 없이 접근 가능

# MagicMock: Mock + 매직 메서드 지원
magic = MagicMock()
len(magic)                    # __len__ 자동 지원 → 0
str(magic)                    # __str__ 자동 지원
magic[0]                      # __getitem__ 자동 지원
bool(magic)                   # __bool__ 자동 지원 → True
```

**차이점 요약:**
| 기능 | Mock | MagicMock |
|------|------|-----------|
| 메서드/속성 자동 생성 | O | O |
| 매직 메서드 (__len__ 등) | X | O |
| 대부분의 경우 사용 | - | 권장 |

### 3.2 return_value

```python
from unittest.mock import Mock

# 반환값 설정
mock_sensor = Mock()
mock_sensor.read_temperature.return_value = 75.5

result = mock_sensor.read_temperature()
assert result == 75.5

# 체인된 호출의 반환값
mock_api = Mock()
mock_api.get_client.return_value.fetch_data.return_value = {"temp": 80}

data = mock_api.get_client().fetch_data()
assert data == {"temp": 80}
```

### 3.3 side_effect

#### 여러 값을 순차적으로 반환

```python
# 여러 값을 순서대로 반환 (센서 데이터 시뮬레이션)
mock_sensor = Mock()
mock_sensor.read.side_effect = [72.0, 73.5, 75.0, 78.2, 82.1]

readings = [mock_sensor.read() for _ in range(5)]
assert readings == [72.0, 73.5, 75.0, 78.2, 82.1]
```

#### 예외 발생

```python
# 예외를 발생시켜 오류 상황 테스트
mock_api = Mock()
mock_api.connect.side_effect = ConnectionError("센서 연결 실패")

with pytest.raises(ConnectionError, match="센서 연결 실패"):
    mock_api.connect()
```

#### 대체 함수

```python
# 호출 시 다른 함수를 실행
def validate_and_return(sensor_id):
    if not sensor_id.startswith("SENSOR-"):
        raise ValueError("잘못된 센서 ID 형식")
    return {"id": sensor_id, "status": "active"}

mock_api = Mock()
mock_api.get_sensor.side_effect = validate_and_return

result = mock_api.get_sensor("SENSOR-01")
assert result["status"] == "active"

with pytest.raises(ValueError):
    mock_api.get_sensor("INVALID")
```

### 3.4 Assertion 메서드

```python
mock = Mock()

# 호출 여부 확인
mock.method()
mock.method.assert_called()           # 최소 1번 호출됨
mock.method.assert_called_once()      # 정확히 1번 호출됨

# 인자 확인
mock.process("sensor-01", threshold=80)
mock.process.assert_called_with("sensor-01", threshold=80)
mock.process.assert_called_once_with("sensor-01", threshold=80)

# 호출되지 않음 확인
mock.unused.assert_not_called()

# 여러 번 호출된 경우 모든 호출 확인
mock.log("first")
mock.log("second")
mock.log.assert_any_call("first")     # 어떤 호출이든 매칭
assert mock.log.call_count == 2       # 호출 횟수

# call_args_list로 전체 호출 이력 확인
from unittest.mock import call
mock.log.assert_has_calls([
    call("first"),
    call("second")
])
```

### 3.5 spec과 autospec

```python
from unittest.mock import Mock, create_autospec

class SensorAPI:
    def read_temperature(self, sensor_id: str) -> float:
        pass

    def read_vibration(self, sensor_id: str) -> float:
        pass

# spec 없이 사용하면 오타를 감지 못함 (위험!)
mock_bad = Mock()
mock_bad.read_temparature()  # 오타인데도 에러 안 남!

# spec 사용: 존재하지 않는 메서드 호출 시 에러
mock_safe = Mock(spec=SensorAPI)
# mock_safe.read_temparature()  # AttributeError 발생!
mock_safe.read_temperature("SENSOR-01")  # 정상

# create_autospec: 시그니처까지 검증
mock_strict = create_autospec(SensorAPI)
# mock_strict.read_temperature()  # TypeError: 인자 부족!
mock_strict.read_temperature("SENSOR-01")  # 정상
```

### 3.6 PropertyMock

```python
from unittest.mock import PropertyMock, patch

class Equipment:
    @property
    def status(self):
        """실제로는 DB에서 상태를 조회"""
        return self._fetch_status()

# PropertyMock으로 프로퍼티를 목킹
with patch.object(Equipment, 'status',
                  new_callable=PropertyMock,
                  return_value="가동중"):
    eq = Equipment()
    assert eq.status == "가동중"
```

### 3.7 sentinel

```python
from unittest.mock import sentinel

# sentinel: 고유한 테스트용 객체 생성
# 어떤 값과도 같지 않은 고유 객체가 필요할 때 사용
def test_data_passes_through():
    mock_processor = Mock()
    mock_processor.process.return_value = sentinel.processed_data

    result = mock_processor.process(sentinel.raw_data)

    # sentinel 객체로 정확한 전달 검증
    mock_processor.process.assert_called_with(sentinel.raw_data)
    assert result is sentinel.processed_data
```

## 4. 실습 가이드

### 프로젝트 구조
```
13_unittest_mock/
├── lesson.md
├── src_sensor_collector.py    # 소스 코드
├── test_mock_demo.py          # 테스트 예제
└── exercises/
    ├── exercise_13.py         # 연습 문제
    └── solution_13.py         # 풀이
```

### 실행 방법
```bash
# 데모 테스트 실행
pytest test_mock_demo.py -v

# 연습 문제
pytest exercises/exercise_13.py -v
pytest exercises/solution_13.py -v
```

## 5. 연습 문제

### 연습 1: side_effect로 센서 데이터 시뮬레이션
센서 API의 `fetch_reading()`을 Mock으로 대체하고,
`side_effect`를 사용하여 점점 상승하는 온도 데이터를 시뮬레이션하세요.

### 연습 2: spec으로 안전한 목 객체 만들기
`SensorAPI` 클래스의 `spec`을 사용한 Mock을 만들고,
존재하지 않는 메서드 호출이 에러를 발생시키는 것을 확인하세요.

### 연습 3: 호출 패턴 검증
`SensorCollector`가 여러 센서의 데이터를 수집할 때,
API가 올바른 순서와 인자로 호출되었는지 `assert_has_calls`로 검증하세요.

## 6. 퀴즈

### 퀴즈 1
`side_effect`에 리스트를 설정하면 어떤 동작을 하는가?
- A) 모든 호출에서 리스트 전체를 반환한다
- B) 호출할 때마다 리스트의 다음 값을 순서대로 반환한다
- C) 랜덤하게 리스트의 값을 반환한다
- D) 첫 번째 호출에서만 리스트를 반환한다

<details>
<summary>정답</summary>
B) 호출할 때마다 리스트의 다음 값을 순서대로 반환합니다.
리스트가 소진되면 StopIteration이 발생합니다.
</details>

### 퀴즈 2
`Mock(spec=SomeClass)`를 사용하는 주된 이유는?
- A) 테스트 속도를 높이기 위해
- B) 존재하지 않는 속성/메서드 접근 시 에러를 발생시켜 오타를 방지하기 위해
- C) 메모리 사용량을 줄이기 위해
- D) 매직 메서드를 자동 지원하기 위해

<details>
<summary>정답</summary>
B) spec을 설정하면 원본 클래스에 존재하지 않는 속성이나 메서드에 접근할 때
AttributeError가 발생하여, 오타로 인한 잘못된 테스트를 방지합니다.
</details>

### 퀴즈 3
다음 코드의 결과는?
```python
mock = Mock()
mock.a.b.c.return_value = 42
result = mock.a.b.c()
```
- A) AttributeError 발생
- B) result == 42
- C) result == None
- D) result는 Mock 객체

<details>
<summary>정답</summary>
B) result == 42. Mock은 체인된 속성 접근을 자동으로 지원하며,
끝에 return_value를 설정하면 해당 값이 반환됩니다.
</details>

## 7. 정리 및 다음 주제 예고

### 이 레슨에서 배운 것
- **Mock vs MagicMock**: MagicMock은 매직 메서드까지 지원
- **return_value**: 고정 반환값 설정
- **side_effect**: 순차 반환, 예외 발생, 대체 함수
- **assert_called_***: 호출 여부, 횟수, 인자 검증
- **spec/autospec**: 오타 방지를 위한 안전한 목
- **PropertyMock**: 프로퍼티 목킹
- **sentinel**: 고유한 테스트용 객체

### 다음 레슨 예고
**레슨 14: Patching**에서는 `@patch` 데코레이터와 컨텍스트 매니저를 사용하여
모듈 수준에서 객체를 목으로 교체하는 방법을 학습합니다.
"어디를 패치해야 하는가?"라는 핵심 질문에 대한 답을 배웁니다.
