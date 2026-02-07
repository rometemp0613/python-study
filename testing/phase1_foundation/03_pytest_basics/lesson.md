# 03. pytest 기본기

## 1. 학습 목표

- pytest의 테스트 발견(discovery) 규칙을 이해한다
- assert 매직(assertion introspection)의 동작 원리를 안다
- `pytest.approx()`로 부동소수점을 안전하게 비교한다
- pytest CLI 주요 옵션을 활용할 수 있다
- 테스트 실패 보고서를 읽고 원인을 파악할 수 있다

## 2. 동기부여 (예지보전 관점)

예지보전 시스템은 다양한 수학적 계산을 포함합니다:
- 센서 데이터의 이동 평균, 표준 편차 계산
- 온도 단위 변환 (섭씨 ↔ 화씨 ↔ 켈빈)
- 이상 온도 감지 알고리즘

이러한 계산 함수들을 pytest로 효과적으로 테스트하는 방법을 배웁니다.
부동소수점 오차 처리(`pytest.approx`)와 다양한 입력에 대한
체계적인 테스트(`parametrize`) 방법이 핵심입니다.

## 3. 핵심 개념 설명

### 3.1 pytest 테스트 발견 규칙

pytest는 다음 규칙에 따라 테스트를 자동으로 찾습니다:

| 대상 | 규칙 |
|------|------|
| 파일 | `test_*.py` 또는 `*_test.py` |
| 함수 | `test_`로 시작하는 함수 |
| 클래스 | `Test`로 시작하는 클래스 (\_\_init\_\_ 없음) |
| 메서드 | `test_`로 시작하는 메서드 |

```python
# test_example.py ← 파일명 규칙

def test_addition():      # ← 함수명 규칙
    assert 1 + 1 == 2

class TestMath:            # ← 클래스명 규칙 (Test로 시작)
    def test_multiply(self):  # ← 메서드명 규칙
        assert 2 * 3 == 6
```

### 3.2 Assert 매직 (Assertion Introspection)

pytest는 `assert` 문이 실패할 때 상세한 정보를 자동으로 출력합니다:

```python
def test_temperature_check():
    expected = 212.0
    actual = celsius_to_fahrenheit(100)
    assert actual == expected
    # 실패 시 출력:
    # AssertionError: assert 211.0 == 212.0
    #   where 211.0 = celsius_to_fahrenheit(100)
```

다양한 assert 패턴:

```python
# 동등성 비교
assert result == expected

# 포함 여부
assert "경고" in status_message

# 타입 확인
assert isinstance(result, dict)

# 길이 확인
assert len(data) == 5

# 범위 확인
assert 0 <= normalized_value <= 1

# 부정 확인
assert not is_overheating(25.0)

# 복합 조건
assert result > 0 and result < 100
```

### 3.3 pytest.approx() - 부동소수점 비교

부동소수점 연산은 정확하지 않을 수 있습니다:

```python
# 이 테스트는 실패할 수 있다!
assert 0.1 + 0.2 == 0.3  # False! (0.30000000000000004)

# pytest.approx()로 안전하게 비교
assert 0.1 + 0.2 == pytest.approx(0.3)

# 허용 오차 지정
assert result == pytest.approx(expected, abs=0.01)   # 절대 오차
assert result == pytest.approx(expected, rel=0.01)   # 상대 오차 (1%)

# 리스트/딕셔너리에도 사용 가능
assert [0.1 + 0.2, 0.2 + 0.3] == pytest.approx([0.3, 0.5])
```

### 3.4 pytest CLI 주요 옵션

```bash
# 기본 실행
pytest

# 상세 출력
pytest -v

# 특정 파일 실행
pytest test_calculations.py

# 특정 테스트만 실행
pytest test_calculations.py::test_add
pytest test_calculations.py::TestMath::test_multiply

# 키워드로 필터링 (-k)
pytest -k "temperature"           # "temperature"가 포함된 테스트만
pytest -k "not slow"              # "slow"가 포함되지 않은 테스트만
pytest -k "temperature and not fahrenheit"  # 조합 가능

# 첫 번째 실패 시 중지 (-x)
pytest -x

# 최대 N개 실패 시 중지
pytest --maxfail=3

# 실패한 테스트만 재실행
pytest --lf    # last failed
pytest --ff    # failed first (실패한 것 먼저, 나머지도 실행)

# 출력 캡처 비활성화 (print 출력 보기)
pytest -s

# 짧은 요약
pytest --tb=short    # 짧은 트레이스백
pytest --tb=line     # 한 줄 요약
pytest --tb=no       # 트레이스백 없음

# 테스트 목록만 보기
pytest --collect-only
```

### 3.5 실패 보고서 읽기

```
FAILED test_calculations.py::TestTemperature::test_celsius_to_fahrenheit
_______________ TestTemperature.test_celsius_to_fahrenheit _______________

self = <test_calculations.TestTemperature object at 0x...>

    def test_celsius_to_fahrenheit(self):
        """섭씨 100도 = 화씨 212도"""
>       assert celsius_to_fahrenheit(100) == 212.0
E       assert 211.0 == 212.0                 ← 실제값 vs 기대값
E        +  where 211.0 = celsius_to_fahrenheit(100)  ← 함수 호출 결과

test_calculations.py:15: AssertionError
```

읽는 순서:
1. **어떤 테스트가 실패했는지** 확인 (FAILED 줄)
2. **`>` 표시** 줄에서 실패한 assert 문 확인
3. **`E` 표시** 줄에서 실제값과 기대값 비교
4. **파일:라인번호** 에서 위치 확인

## 4. 실습 가이드

### 실습 1: 기본 pytest 실행

```bash
# 모든 테스트 실행
pytest test_calculations.py -v

# 키워드로 필터링
pytest test_calculations.py -v -k "celsius"

# 실패 보고서 확인
pytest test_calculations.py -v --tb=short
```

### 실습 2: pytest.approx() 실험

```bash
# 부동소수점 테스트 실행
pytest test_calculations.py -v -k "approx"
```

### 실습 3: parametrize 기초

```bash
# 여러 입력값으로 테스트 실행
pytest test_calculations.py -v -k "parametrize"
```

## 5. 연습 문제

### 연습 1: 이상 온도 감지 테스트
`exercises/exercise_03.py`에서 이상 온도 감지 함수의 테스트를 완성하세요.

### 연습 2: pytest.approx 활용
부동소수점 계산 결과를 `pytest.approx()`로 비교하는 테스트를 작성하세요.

### 연습 3: parametrize 기초
`@pytest.mark.parametrize`를 사용하여 여러 입력값에 대한 테스트를 작성하세요.

## 6. 퀴즈

### Q1. 테스트 발견 규칙
pytest가 자동으로 테스트로 인식하지 않는 것은?
- A) `test_sensor.py` 파일의 `test_read()` 함수
- B) `sensor_test.py` 파일의 `test_read()` 함수
- C) `TestSensor` 클래스의 `test_read()` 메서드
- D) `test_sensor.py` 파일의 `check_read()` 함수

**정답: D)** `check_`로 시작하는 함수는 pytest가 자동으로
테스트로 인식하지 않습니다. `test_`로 시작해야 합니다.

### Q2. pytest.approx
다음 중 `pytest.approx()`가 필요한 경우는?
- A) `assert 1 + 1 == 2`
- B) `assert 0.1 + 0.2 == 0.3`
- C) `assert "hello" == "hello"`
- D) `assert [1, 2] == [1, 2]`

**정답: B)** 부동소수점 연산(0.1 + 0.2)은 정확히 0.3이 아니므로
`pytest.approx()`가 필요합니다.

### Q3. CLI 옵션
첫 번째 실패에서 즉시 테스트를 중지하려면 어떤 옵션을 사용하나요?
- A) `pytest --stop`
- B) `pytest -x`
- C) `pytest --fail-fast`
- D) `pytest --break`

**정답: B)** `pytest -x` 옵션은 첫 번째 실패에서 즉시 중지합니다.

## 7. 정리 및 다음 주제 예고

### 이번 강의 핵심 정리
- pytest는 `test_`로 시작하는 파일, 함수, 메서드를 자동으로 테스트로 인식
- `assert` 문 하나로 모든 비교 가능하며, 실패 시 상세 정보 자동 제공
- `pytest.approx()`로 부동소수점을 안전하게 비교
- CLI 옵션(`-v`, `-x`, `-k`, `--tb` 등)으로 테스트 실행을 세밀하게 제어
- 실패 보고서에서 `>` (실패 줄)와 `E` (비교 결과)를 확인하면 원인 파악 가능

### 다음 주제 예고
**04. 테스트 구조와 프로젝트 조직** - 테스트 파일 배치, 네이밍 컨벤션,
`conftest.py`의 역할과 계층 구조를 배웁니다.
