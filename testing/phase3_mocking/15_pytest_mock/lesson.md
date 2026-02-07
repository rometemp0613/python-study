# 레슨 15: pytest-mock 플러그인

## 1. 학습 목표

이 레슨을 마치면 다음을 할 수 있습니다:

- `pytest-mock` 플러그인의 `mocker` 픽스처를 이해한다
- `mocker.patch()`, `mocker.patch.object()`, `mocker.MagicMock()`을 활용할 수 있다
- `mocker.spy()`로 실제 동작을 유지하면서 호출을 추적할 수 있다
- `pytest-mock`과 `unittest.mock`의 차이점과 장점을 설명할 수 있다

## 2. 동기부여: 예지보전 관점

예지보전 시스템의 알림 체계를 테스트한다고 생각해 봅시다:

```
이상 감지 → AlertSystem → NotificationService → 이메일/SMS
                        → AlertRepository → DB 저장
                        → ThresholdConfig → 설정 조회
```

`unittest.mock`의 `@patch` 데코레이터는 강력하지만:
- 데코레이터가 쌓이면 코드가 복잡해짐
- 테스트 함수의 매개변수 순서를 관리해야 함
- 패치 범위가 함수 전체에 적용됨

`pytest-mock`의 `mocker` 픽스처는 이런 불편함을 해소합니다:
- 픽스처 기반으로 자동 정리 (cleanup)
- 함수 본문 안에서 직관적으로 패치
- pytest와 자연스럽게 통합

## 3. 핵심 개념 설명

### 3.1 mocker 픽스처 기본 사용법

```python
# pytest-mock 설치 필요: pip install pytest-mock

def test_with_mocker(mocker):
    """mocker 픽스처를 매개변수로 받으면 자동 주입됨"""

    # mocker.patch: unittest.mock.patch와 동일
    mock_func = mocker.patch("module_name.function_name")
    mock_func.return_value = 42

    # mocker.patch.object: 특정 객체의 메서드 패치
    mocker.patch.object(SomeClass, "method", return_value="mocked")

    # mocker.MagicMock: MagicMock 생성
    mock_obj = mocker.MagicMock(spec=SomeClass)
```

### 3.2 mocker.patch() vs @patch

```python
# === unittest.mock 방식 ===
from unittest.mock import patch

@patch("module.ClassC.method")
@patch("module.ClassB.method")
@patch("module.ClassA.method")
def test_complex(mock_a, mock_b, mock_c):
    # 데코레이터가 쌓이고, 인자 순서 헷갈림
    mock_a.return_value = "a"
    mock_b.return_value = "b"
    mock_c.return_value = "c"
    # ...

# === pytest-mock 방식 ===
def test_complex_with_mocker(mocker):
    # 함수 본문에서 직관적으로 패치
    mock_a = mocker.patch("module.ClassA.method", return_value="a")
    mock_b = mocker.patch("module.ClassB.method", return_value="b")
    mock_c = mocker.patch("module.ClassC.method", return_value="c")
    # 이름과 값이 바로 옆에 있어서 읽기 쉬움
```

### 3.3 mocker.spy()

```python
def test_spy_real_behavior(mocker):
    """실제 동작을 유지하면서 호출을 추적"""
    calculator = Calculator()

    # spy: 실제 메서드를 호출하면서 호출 기록도 남김
    spy = mocker.spy(calculator, "add")

    result = calculator.add(2, 3)

    assert result == 5  # 실제 결과
    spy.assert_called_once_with(2, 3)  # 호출 기록도 확인
```

### 3.4 mocker의 주요 장점

| 특성 | unittest.mock | pytest-mock |
|------|---------------|-------------|
| 패치 정리 | 수동 또는 데코레이터 | 자동 (픽스처 스코프) |
| 코드 위치 | 데코레이터 (함수 위) | 함수 본문 (사용 위치) |
| 매개변수 순서 | 역순 (헷갈림) | 변수명으로 관리 |
| pytest 통합 | 별도 | 자연스러운 통합 |
| 에러 메시지 | 기본 | 향상된 메시지 |

### 3.5 unittest.mock으로 동일한 패턴 구현

pytest-mock이 설치되지 않은 환경에서는 unittest.mock으로도
비슷한 패턴을 구현할 수 있습니다:

```python
from unittest.mock import patch, Mock

def test_without_pytest_mock():
    """unittest.mock만으로도 충분히 테스트 가능"""
    with patch("module.service") as mock_service:
        mock_service.process.return_value = "result"

        # 테스트 실행
        result = do_something()

        # 검증
        mock_service.process.assert_called_once()
        assert result == "result"
```

## 4. 실습 가이드

### 프로젝트 구조
```
15_pytest_mock/
├── lesson.md
├── src_alert_system.py      # 소스 코드
├── test_pytest_mock_demo.py  # 테스트 예제 (unittest.mock 사용)
└── exercises/
    ├── exercise_15.py        # 연습 문제
    └── solution_15.py        # 풀이
```

### 실행 방법
```bash
pytest test_pytest_mock_demo.py -v
pytest exercises/exercise_15.py -v
pytest exercises/solution_15.py -v
```

### 참고: pytest-mock이 설치된 환경에서는
```bash
pip install pytest-mock
```
설치 후 mocker 픽스처를 직접 사용할 수 있습니다.

## 5. 연습 문제

### 연습 1: 알림 서비스 패치
`AlertSystem`의 `NotificationService`를 패치하여
경고 알림이 올바르게 발송되는지 테스트하세요.

### 연습 2: 임계값 설정 패치
`ThresholdConfig`를 패치하여 다양한 임계값 시나리오에서
올바른 알림 수준이 결정되는지 테스트하세요.

### 연습 3: 알림 이력 저장 검증
`AlertRepository`의 `save` 메서드가 올바른 인자로 호출되는지 검증하세요.

## 6. 퀴즈

### 퀴즈 1
`pytest-mock`의 `mocker` 픽스처 사용 시 패치가 정리(cleanup)되는 시점은?
- A) 테스트 함수 실행 직후 자동으로
- B) 전체 테스트 스위트가 끝난 후
- C) 수동으로 mocker.stopall()을 호출해야
- D) Python 프로세스 종료 시

<details>
<summary>정답</summary>
A) mocker 픽스처는 테스트 함수가 끝나면 자동으로 모든 패치를 정리합니다.
pytest 픽스처의 기본 스코프(function)에 의해 관리됩니다.
</details>

### 퀴즈 2
`mocker.spy()`의 특징은?
- A) 실제 메서드를 Mock으로 완전히 대체한다
- B) 실제 메서드를 실행하면서 호출 기록도 남긴다
- C) 메서드의 반환값만 변경한다
- D) 예외만 발생시킨다

<details>
<summary>정답</summary>
B) spy는 실제 메서드를 실행하면서도 호출 여부, 인자 등을 기록합니다.
실제 동작을 유지하면서 호출 패턴을 검증하고 싶을 때 유용합니다.
</details>

### 퀴즈 3
unittest.mock과 비교했을 때 pytest-mock의 주된 장점이 아닌 것은?
- A) 자동 패치 정리
- B) 함수 본문에서 직관적으로 패치 가능
- C) 더 빠른 실행 속도
- D) pytest와 자연스러운 통합

<details>
<summary>정답</summary>
C) pytest-mock은 실행 속도 향상이 목적이 아닙니다.
내부적으로 unittest.mock을 사용하므로 성능은 동일합니다.
주된 장점은 코드 가독성과 편의성입니다.
</details>

## 7. 정리 및 다음 주제 예고

### 이 레슨에서 배운 것
- **mocker 픽스처**: pytest-mock의 핵심, 자동 정리 지원
- **mocker.patch()**: @patch 대신 함수 본문에서 패치
- **mocker.patch.object()**: 객체 메서드 패치
- **mocker.spy()**: 실제 동작 유지 + 호출 추적
- **unittest.mock 호환**: pytest-mock 없이도 동일한 테스트 가능

### 다음 레슨 예고
**레슨 16: Monkeypatch**에서는 pytest의 내장 `monkeypatch` 픽스처를 학습합니다.
환경 변수, 딕셔너리, 클래스 속성 등을 테스트 중에 안전하게 변경하는 방법을 다룹니다.
