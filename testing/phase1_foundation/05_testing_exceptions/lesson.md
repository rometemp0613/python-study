# 05. 예외와 에러 핸들링 테스트

## 1. 학습 목표

- `pytest.raises()`로 예외 발생을 정확하게 테스트할 수 있다
- `match` 파라미터로 예외 메시지를 검증할 수 있다
- `ExceptionInfo` 객체를 활용하여 예외의 상세 정보를 확인할 수 있다
- 커스텀 예외 클래스를 설계하고 테스트할 수 있다
- `pytest.warns()`로 경고를 테스트할 수 있다

## 2. 동기부여 (예지보전 관점)

예지보전 시스템에서 에러 핸들링은 특히 중요합니다:

- **센서 범위 초과**: 센서가 측정 가능 범위를 벗어난 값을 보내면?
- **통신 타임아웃**: 센서와의 통신이 끊기면?
- **데이터 형식 오류**: 잘못된 형식의 데이터가 들어오면?
- **설정 오류**: 잘못된 임계값이 설정되면?

이러한 상황에서 시스템이 **명확한 에러 메시지**와 함께 **예측 가능하게 실패**해야
운영자가 빠르게 문제를 파악하고 대응할 수 있습니다.

## 3. 핵심 개념 설명

### 3.1 pytest.raises() 기본 사용법

```python
import pytest

# 기본 형태: 예외 타입만 확인
def test_0으로_나누기():
    with pytest.raises(ZeroDivisionError):
        1 / 0

# 예외가 발생하지 않으면 테스트 실패!
def test_예외_미발생_시_실패():
    with pytest.raises(ZeroDivisionError):
        1 / 1  # 예외가 발생하지 않으므로 이 테스트는 실패
```

### 3.2 match 파라미터로 메시지 검증

```python
def test_예외_메시지_확인():
    with pytest.raises(ValueError, match="음수"):
        validate_temperature(-10)

    # match는 정규표현식을 지원
    with pytest.raises(ValueError, match=r"범위.*벗어남"):
        validate_temperature(500)

    # 대소문자 무시
    with pytest.raises(ValueError, match="(?i)invalid"):
        validate_temperature("abc")
```

### 3.3 ExceptionInfo 객체 활용

```python
def test_예외_상세_정보():
    with pytest.raises(SensorDataError) as exc_info:
        process_sensor_data(invalid_data)

    # 예외 인스턴스에 접근
    assert exc_info.value.sensor_id == "TEMP-001"
    assert exc_info.value.error_code == "E001"

    # 예외 타입 확인
    assert exc_info.type == SensorDataError

    # 문자열 표현 확인
    assert "TEMP-001" in str(exc_info.value)
```

### 3.4 커스텀 예외 클래스 설계

```python
class SensorError(Exception):
    """센서 관련 기본 예외 클래스"""
    pass

class SensorDataError(SensorError):
    """센서 데이터 형식 오류"""
    def __init__(self, sensor_id, message):
        self.sensor_id = sensor_id
        super().__init__(f"[{sensor_id}] {message}")

class SensorRangeError(SensorError):
    """센서 값 범위 초과"""
    def __init__(self, sensor_id, value, valid_range):
        self.sensor_id = sensor_id
        self.value = value
        self.valid_range = valid_range
        super().__init__(
            f"[{sensor_id}] 값 {value}가 유효 범위 {valid_range}를 벗어남"
        )

class SensorTimeoutError(SensorError):
    """센서 통신 타임아웃"""
    def __init__(self, sensor_id, timeout_seconds):
        self.sensor_id = sensor_id
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"[{sensor_id}] {timeout_seconds}초 타임아웃"
        )
```

### 3.5 pytest.warns() - 경고 테스트

```python
import warnings

def check_battery(level):
    if level < 20:
        warnings.warn("배터리 잔량 부족", UserWarning)
    return level

def test_배터리_경고():
    with pytest.warns(UserWarning, match="배터리"):
        check_battery(10)
```

### 3.6 예외 계층 구조 테스트

```python
# 상위 예외 타입으로도 잡을 수 있다
def test_예외_계층():
    with pytest.raises(SensorError):  # 상위 클래스
        raise SensorDataError("TEMP-001", "데이터 오류")

    with pytest.raises(SensorDataError):  # 정확한 클래스
        raise SensorDataError("TEMP-001", "데이터 오류")
```

## 4. 실습 가이드

### 실습 1: 기본 예외 테스트

```bash
pytest test_sensor_validator.py -v
```

### 실습 2: 커스텀 예외 확인

```bash
pytest test_sensor_validator.py -v -k "custom"
```

### 실습 3: 경고 테스트

```bash
pytest test_sensor_validator.py -v -k "warn"
```

## 5. 연습 문제

### 연습 1: 커스텀 예외 테스트
`exercises/exercise_05.py`에서 장비 설정 검증 함수의 예외를 테스트하세요.

### 연습 2: match 파라미터 활용
다양한 에러 메시지를 `match` 파라미터로 검증하는 테스트를 작성하세요.

### 연습 3: ExceptionInfo 활용
예외 객체의 속성(sensor_id, error_code 등)을 검증하는 테스트를 작성하세요.

## 6. 퀴즈

### Q1. pytest.raises()
`pytest.raises(ValueError)`는 어떤 경우에 테스트가 통과하나요?
- A) ValueError가 발생하지 않을 때
- B) ValueError가 발생할 때
- C) 어떤 예외든 발생할 때
- D) 코드가 정상 실행될 때

**정답: B)** `pytest.raises(ValueError)`는 해당 블록 내에서
ValueError가 발생해야 테스트가 통과합니다.

### Q2. match 파라미터
`pytest.raises(ValueError, match="범위")`의 match는 무엇을 검증하나요?
- A) 변수 이름에 "범위"가 포함되는지
- B) 예외 메시지에 "범위"가 포함되는지
- C) 함수 이름에 "범위"가 포함되는지
- D) 파일 이름에 "범위"가 포함되는지

**정답: B)** match 파라미터는 예외 메시지(str)에 대해
정규표현식 매칭을 수행합니다.

### Q3. 커스텀 예외
커스텀 예외 클래스를 만들 때 상속해야 하는 기본 클래스는?
- A) object
- B) Error
- C) Exception (또는 그 하위 클래스)
- D) BaseException

**정답: C)** 일반적으로 `Exception` 또는 그 하위 클래스를 상속합니다.
`BaseException`은 시스템 종료 등 특수한 경우에만 사용합니다.

## 7. 정리 및 다음 주제 예고

### 이번 강의 핵심 정리
- `pytest.raises(ExceptionType)`으로 예외 발생 테스트
- `match` 파라미터로 예외 메시지를 정규표현식으로 검증
- `exc_info.value`로 예외 인스턴스의 속성에 접근
- 커스텀 예외 클래스로 도메인별 에러를 명확하게 분류
- `pytest.warns()`로 경고 메시지 테스트

### 다음 주제 예고
**06. 출력 캡처** - `capsys`, `capfd`, `caplog` fixture를 사용하여
print 출력과 로그 메시지를 캡처하고 테스트하는 방법을 배웁니다.
