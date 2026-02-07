# 08. Parametrize - 매개변수화 테스트

## 1. 학습 목표

- `@pytest.mark.parametrize`로 하나의 테스트를 여러 입력값으로 반복 실행한다
- 단일/다중 매개변수를 사용하는 방법을 익힌다
- 테스트 ID를 지정하여 결과를 읽기 쉽게 만든다
- 중첩 데코레이터로 데카르트 곱(cartesian product) 테스트를 작성한다
- `indirect` parametrize로 fixture와 연계한다
- `pytest.param`으로 개별 테스트 케이스에 마커를 부여한다

## 2. 동기부여: 예지보전 관점

설비 이상 탐지 시스템에서는 다양한 경계값과 임계값을 테스트해야 합니다:
- 온도 센서: -40°C ~ 200°C 범위의 다양한 값
- 진동 센서: 정상, 경고, 위험 각 수준별 테스트
- 압력 센서: 여러 임계값 조합으로 심각도 분류 테스트

매번 같은 테스트 로직을 복사-붙여넣기하면 코드가 폭발적으로 늘어납니다.
`parametrize`를 사용하면 **하나의 테스트 함수로 수십 가지 시나리오**를 검증할 수 있습니다.

## 3. 핵심 개념 설명

### 3.1 단일 매개변수

```python
@pytest.mark.parametrize("temperature", [20.0, 50.0, 80.0, 100.0])
def test_temperature_reading(temperature):
    """4가지 온도값으로 테스트가 각각 실행됨"""
    assert isinstance(temperature, float)
    assert temperature > 0
```

### 3.2 다중 매개변수

```python
@pytest.mark.parametrize("value, expected_status", [
    (25.0, "normal"),     # 정상 범위
    (75.0, "warning"),    # 경고 범위
    (95.0, "critical"),   # 위험 범위
])
def test_classify_status(value, expected_status):
    """값에 따라 올바른 상태가 분류되는지 확인"""
    result = classify(value)
    assert result == expected_status
```

### 3.3 테스트 ID 지정

기본적으로 pytest는 매개변수 값을 테스트 ID로 사용합니다.
`ids` 매개변수로 읽기 쉬운 이름을 지정할 수 있습니다.

```python
@pytest.mark.parametrize("value, expected", [
    (25.0, "normal"),
    (75.0, "warning"),
    (95.0, "critical"),
], ids=["정상범위", "경고범위", "위험범위"])
def test_with_ids(value, expected):
    assert classify(value) == expected
```

실행 결과:
```
test_example.py::test_with_ids[정상범위] PASSED
test_example.py::test_with_ids[경고범위] PASSED
test_example.py::test_with_ids[위험범위] PASSED
```

### 3.4 중첩 데코레이터 (데카르트 곱)

두 개의 `@pytest.mark.parametrize`를 중첩하면 모든 조합이 테스트됩니다.

```python
@pytest.mark.parametrize("sensor_type", ["temperature", "vibration", "pressure"])
@pytest.mark.parametrize("threshold", [50.0, 80.0])
def test_all_combinations(sensor_type, threshold):
    """3 x 2 = 6가지 조합으로 테스트 실행"""
    assert threshold > 0
```

### 3.5 pytest.param과 마커

`pytest.param`으로 개별 테스트 케이스에 마커를 부여할 수 있습니다.

```python
@pytest.mark.parametrize("value, expected", [
    pytest.param(25.0, "normal", id="정상"),
    pytest.param(75.0, "warning", id="경고"),
    pytest.param(
        -10.0, "error",
        id="음수값",
        marks=pytest.mark.xfail(reason="음수값 처리 미구현")
    ),
])
def test_with_param(value, expected):
    assert classify(value) == expected
```

### 3.6 Indirect Parametrize

`indirect=True`를 사용하면 매개변수가 fixture를 통해 전달됩니다.

```python
@pytest.fixture
def sensor_reading(request):
    """매개변수를 받아 센서 읽기값 생성"""
    return create_reading(request.param)

@pytest.mark.parametrize("sensor_reading", [
    {"id": "TEMP-001", "value": 25.0},
    {"id": "VIBR-002", "value": 3.5},
], indirect=True)
def test_indirect(sensor_reading):
    assert sensor_reading is not None
```

## 4. 실습 가이드

### 실습 1: 기본 parametrize

```bash
pytest test_parametrize_demo.py -v -k "test_single_param"
```

### 실습 2: 데카르트 곱

```bash
pytest test_parametrize_demo.py -v -k "test_cartesian"
```

### 실습 3: 특정 ID만 실행

```bash
pytest test_parametrize_demo.py -v -k "정상"
```

## 5. 연습 문제

### 연습 1: 경계값 테스트
`detect` 메서드를 다양한 경계값(threshold - 1, threshold, threshold + 1)으로
parametrize하여 테스트하세요.

### 연습 2: 심각도 분류 테스트
`classify_severity`를 여러 입력값과 기대 결과로 parametrize하세요.
pytest.param을 사용하여 테스트 ID를 지정하세요.

### 연습 3: 패턴 탐지 조합 테스트
여러 window_size와 데이터 패턴을 중첩 parametrize로 테스트하세요.

## 6. 퀴즈

### Q1. parametrize 실행 횟수
다음 테스트는 몇 번 실행될까요?

```python
@pytest.mark.parametrize("a", [1, 2, 3])
@pytest.mark.parametrize("b", [10, 20])
def test_multiply(a, b):
    assert a * b > 0
```

A) 2번
B) 3번
C) 5번
D) 6번

**정답: D** - 3 x 2 = 6가지 조합으로 실행됩니다.

### Q2. pytest.param
`pytest.param`의 `marks` 매개변수로 할 수 있는 것은?

A) 특정 테스트 케이스를 건너뛰기(skip)
B) 특정 테스트 케이스를 예상 실패(xfail)로 표시
C) 특정 테스트 케이스에 커스텀 마커 부여
D) 위의 모든 것

**정답: D** - marks로 skip, xfail, 커스텀 마커 등을 부여할 수 있습니다.

### Q3. indirect parametrize
`indirect=True`의 동작은?

A) 매개변수 값이 fixture의 `request.param`으로 전달된다
B) 매개변수 값이 무시된다
C) 테스트가 간접적으로(lazy하게) 실행된다
D) fixture가 자동으로 생성된다

**정답: A** - indirect=True이면 값이 해당 이름의 fixture의 request.param으로 전달됩니다.

## 7. 정리 및 다음 주제 예고

### 이번 단원 정리
- **단일/다중 매개변수**로 여러 입력값을 효율적으로 테스트
- **테스트 ID**로 결과를 읽기 쉽게 만듦
- **중첩 데코레이터**로 모든 조합의 데카르트 곱 테스트
- **pytest.param**으로 개별 케이스에 마커 부여
- **indirect**로 fixture와 연계하여 복잡한 설정 가능

### 다음 주제: 09. Markers
다음 단원에서는 테스트에 마커를 부여하여 조건부 실행, 선택적 실행, 분류를
하는 방법을 배웁니다. 느린 테스트, 통합 테스트 등을 구분하여 효율적으로
테스트를 관리할 수 있습니다.
