# 02. Python 내장 테스트: unittest & doctest

## 1. 학습 목표

- `unittest` 모듈의 TestCase 클래스를 사용하여 테스트를 작성할 수 있다
- `setUp`/`tearDown` 메서드의 역할과 사용법을 이해한다
- 주요 assertion 메서드들(`assertEqual`, `assertTrue`, `assertRaises` 등)을 활용한다
- `doctest`로 docstring에 테스트를 포함하는 방법을 배운다
- `unittest`와 `pytest`의 차이를 비교하고 `pytest`의 장점을 이해한다

## 2. 동기부여 (예지보전 관점)

예지보전 시스템에서는 다양한 센서 유틸리티 함수들이 필요합니다:
- 센서 데이터 단위 변환 (PSI → Bar, mm/s → in/s 등)
- 센서 값 정규화 및 스케일링
- 이상치 탐지를 위한 통계 계산

이러한 유틸리티 함수들은 시스템의 기반이 되므로 철저한 테스트가 필수적입니다.
Python에 내장된 `unittest`와 `doctest`는 별도 설치 없이 바로 사용할 수 있는
테스트 도구입니다. 이를 이해하면 기존 프로젝트의 테스트 코드를 읽고
수정할 수 있게 됩니다.

## 3. 핵심 개념 설명

### 3.1 unittest.TestCase 기본 구조

```python
import unittest

class TestSensorUtils(unittest.TestCase):
    """센서 유틸리티 테스트 - unittest 스타일"""

    def setUp(self):
        """각 테스트 메서드 실행 전에 호출된다.
        테스트에 필요한 데이터나 객체를 준비한다."""
        self.sample_readings = [22.5, 23.0, 22.8, 23.2, 22.9]

    def tearDown(self):
        """각 테스트 메서드 실행 후에 호출된다.
        리소스 정리에 사용한다."""
        self.sample_readings = None

    def test_psi_to_bar(self):
        """PSI를 Bar로 변환하는 테스트"""
        result = psi_to_bar(14.696)
        self.assertAlmostEqual(result, 1.01325, places=3)

    def test_invalid_input(self):
        """잘못된 입력에 대한 예외 테스트"""
        with self.assertRaises(ValueError):
            psi_to_bar(-1)
```

### 3.2 주요 Assertion 메서드

| 메서드 | 설명 | 예시 |
|--------|------|------|
| `assertEqual(a, b)` | a == b | `self.assertEqual(result, 42)` |
| `assertNotEqual(a, b)` | a != b | `self.assertNotEqual(status, "error")` |
| `assertTrue(x)` | bool(x) is True | `self.assertTrue(is_valid)` |
| `assertFalse(x)` | bool(x) is False | `self.assertFalse(is_expired)` |
| `assertAlmostEqual(a, b)` | round(a-b, 7) == 0 | `self.assertAlmostEqual(3.14, pi, places=2)` |
| `assertRaises(exc)` | 예외 발생 확인 | `self.assertRaises(ValueError)` |
| `assertIn(a, b)` | a in b | `self.assertIn("경고", message)` |
| `assertIsNone(x)` | x is None | `self.assertIsNone(result)` |
| `assertIsInstance(a, b)` | isinstance(a, b) | `self.assertIsInstance(data, list)` |

### 3.3 setUp / tearDown 실행 순서

```
setUp()     → test_method_1() → tearDown()
setUp()     → test_method_2() → tearDown()
setUp()     → test_method_3() → tearDown()
```

각 테스트 메서드는 독립적으로 실행되며, 매번 setUp/tearDown이 호출됩니다.

또한 클래스 레벨의 `setUpClass`/`tearDownClass`도 있습니다:
```python
@classmethod
def setUpClass(cls):
    """클래스의 모든 테스트 실행 전에 한 번만 호출된다.
    비용이 큰 초기화 작업에 사용한다."""
    cls.db_connection = create_connection()

@classmethod
def tearDownClass(cls):
    """클래스의 모든 테스트 실행 후에 한 번만 호출된다."""
    cls.db_connection.close()
```

### 3.4 doctest 기본 사용법

docstring에 대화형 Python 세션 형태로 테스트를 작성합니다:

```python
def psi_to_bar(psi):
    """PSI를 Bar 단위로 변환한다.

    >>> psi_to_bar(14.696)
    1.01325
    >>> psi_to_bar(0)
    0.0
    >>> psi_to_bar(-1)
    Traceback (most recent call last):
        ...
    ValueError: PSI 값은 0 이상이어야 합니다
    """
    if psi < 0:
        raise ValueError("PSI 값은 0 이상이어야 합니다")
    return round(psi * 0.0689476, 5)
```

실행 방법:
```bash
# doctest 실행
python -m doctest src_sensor_utils.py -v

# pytest로 doctest 실행
pytest --doctest-modules src_sensor_utils.py
```

### 3.5 unittest vs pytest 비교

```python
# unittest 스타일
class TestSensor(unittest.TestCase):
    def test_conversion(self):
        self.assertEqual(psi_to_bar(14.696), 1.01325)
        self.assertAlmostEqual(result, expected, places=3)
        with self.assertRaises(ValueError):
            psi_to_bar(-1)

# pytest 스타일 (더 간결!)
def test_conversion():
    assert psi_to_bar(14.696) == 1.01325
    assert result == pytest.approx(expected, abs=0.001)
    with pytest.raises(ValueError):
        psi_to_bar(-1)
```

**pytest의 장점:**
- 클래스 없이도 테스트 함수만으로 작성 가능
- `assert` 문만으로 모든 비교 가능 (별도의 assertion 메서드 불필요)
- 실패 시 상세한 diff 출력
- fixture 시스템이 더 유연함
- 풍부한 플러그인 생태계

## 4. 실습 가이드

### 실습 1: unittest 스타일 테스트 살펴보기

```bash
# unittest 테스트 실행 (python -m unittest)
python -m unittest test_sensor_utils_unittest -v

# pytest로도 unittest 테스트 실행 가능
pytest test_sensor_utils_unittest.py -v
```

### 실습 2: pytest 스타일과 비교

```bash
# pytest 스타일 테스트 실행
pytest test_sensor_utils_pytest.py -v
```

두 파일을 비교하며 같은 기능을 다른 스타일로 테스트하는 방법을 확인하세요.

### 실습 3: doctest 실행

```bash
# doctest 실행
pytest --doctest-modules src_sensor_utils.py -v
```

## 5. 연습 문제

### 연습 1: unittest 스타일로 테스트 작성하기
`exercises/exercise_02.py`에서 진동 센서 유틸리티 함수에 대한
unittest 스타일 테스트를 작성하세요.

### 연습 2: doctest 추가하기
연습 문제의 함수에 doctest를 추가해보세요.

### 연습 3: setUp 활용하기
공통 테스트 데이터를 setUp에서 준비하도록 리팩토링하세요.

## 6. 퀴즈

### Q1. setUp 메서드
`setUp` 메서드는 언제 호출되나요?
- A) 테스트 클래스가 로드될 때 한 번
- B) 각 테스트 메서드 실행 전에 매번
- C) 모든 테스트가 끝난 후
- D) 테스트가 실패할 때만

**정답: B)** setUp은 각 테스트 메서드 실행 전에 매번 호출되어
테스트 간 독립성을 보장합니다.

### Q2. assertAlmostEqual
`self.assertAlmostEqual(a, b, places=3)`은 무엇을 확인하나요?
- A) a와 b가 정확히 같은지
- B) a와 b의 차이가 소수점 3째 자리까지 같은지
- C) a가 b보다 큰지
- D) a와 b의 타입이 같은지

**정답: B)** `places=3`은 `round(a-b, 3) == 0`을 검증합니다.
부동소수점 비교에 유용합니다.

### Q3. doctest의 장점이 아닌 것은?
- A) 문서와 테스트를 동시에 작성할 수 있다
- B) docstring이 항상 최신 상태로 유지된다
- C) 복잡한 설정이 필요한 테스트에 적합하다
- D) 함수 사용 예시를 바로 보여준다

**정답: C)** doctest는 간단한 예시에 적합하며, 복잡한 설정이
필요한 테스트에는 unittest나 pytest가 더 적합합니다.

## 7. 정리 및 다음 주제 예고

### 이번 강의 핵심 정리
- `unittest`는 Python 내장 테스트 프레임워크로, TestCase 클래스를 상속하여 사용
- `setUp`/`tearDown`으로 테스트 전후 작업을 정의
- `doctest`는 docstring에 테스트를 포함하여 문서와 테스트를 동시에 관리
- `pytest`는 `unittest`보다 간결하고 강력하지만, `unittest` 코드도 실행 가능

### 다음 주제 예고
**03. pytest 기본기** - `pytest`의 핵심 기능을 본격적으로 배웁니다.
테스트 발견 규칙, assert 매직, `pytest.approx()`, CLI 옵션, 실패 보고서
읽는 방법을 실습합니다.
