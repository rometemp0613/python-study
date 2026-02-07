# 24. Property-Based Testing (속성 기반 테스트)

## 학습 목표

이 주제를 마치면 다음을 할 수 있게 된다:
- 예제 기반 테스트와 속성 기반 테스트의 차이를 이해한다
- 함수의 **불변 속성(invariant)**을 식별하고 테스트로 표현할 수 있다
- Hypothesis 라이브러리의 `@given`, `strategies`를 사용할 수 있다
- Shrinking(축소) 개념을 이해한다
- 센서 데이터 처리 함수에 속성 기반 테스트를 적용할 수 있다

## 동기부여 (예지보전 관점)

예지보전 시스템에서 속성 기반 테스트가 유용한 이유:

- 센서 데이터는 **예측할 수 없는 다양한 값**을 가진다. 몇 가지 예제만으로는 모든 경우를 커버할 수 없다.
- `normalize()` 함수는 **어떤 입력이든 0~1 사이 값을 반환해야 한다** → 이것이 "속성"이다.
- `encode → decode`는 **원본과 동일해야 한다** → 왕복(roundtrip) 속성이다.
- 수천 개의 랜덤 입력으로 **엣지 케이스**를 자동으로 발견할 수 있다.

## 핵심 개념

### 예제 기반 vs 속성 기반

```
예제 기반 테스트 (Example-Based):
  "normalize([1, 2, 3])의 결과는 [0.0, 0.5, 1.0]이다"
  → 특정 입력 → 특정 출력 검증

속성 기반 테스트 (Property-Based):
  "normalize(아무 리스트)의 결과는 항상 0과 1 사이이다"
  → 모든 가능한 입력 → 속성(property) 검증
```

### 불변 속성(Invariant)이란?

함수가 **어떤 입력에서도 항상 만족해야 하는 조건**이다.

```python
# normalize() 함수의 불변 속성들:
# 1. 결과의 모든 값은 0 이상 1 이하이다
# 2. 최솟값은 0.0이다
# 3. 최댓값은 1.0이다
# 4. 결과 리스트의 길이는 입력과 동일하다
# 5. 입력의 순서 관계가 유지된다 (a < b → normalize(a) < normalize(b))
```

### Hypothesis 라이브러리

```bash
pip install hypothesis
```

```python
from hypothesis import given
from hypothesis import strategies as st

@given(st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2))
def test_normalize_range(values):
    """정규화 결과는 항상 0~1 범위"""
    result = normalize(values)
    assert all(0 <= v <= 1 for v in result)
```

### 주요 전략(Strategy)

```python
from hypothesis import strategies as st

# 기본 타입
st.integers()                           # 정수
st.floats(min_value=0, max_value=100)   # 실수 (범위 제한)
st.text()                               # 문자열
st.booleans()                           # 불리언

# 컬렉션
st.lists(st.integers(), min_size=1)     # 정수 리스트 (최소 1개)
st.tuples(st.integers(), st.text())     # (정수, 문자열) 튜플
st.dictionaries(st.text(), st.integers()) # {문자열: 정수} 딕셔너리

# 선택
st.sampled_from(["temp", "vibration", "pressure"])  # 목록에서 선택
st.one_of(st.integers(), st.text())     # 정수 또는 문자열

# 복합
st.fixed_dictionaries({                 # 고정 키 딕셔너리
    "sensor_id": st.text(min_size=1),
    "value": st.floats(min_value=-100, max_value=500),
})
```

### Shrinking (축소)

Hypothesis는 실패하는 입력을 발견하면, **가능한 가장 작은 실패 사례**를 찾아준다.

```
발견: [234, -567, 891, 0, 1234, -999] → 실패!
축소 과정:
  [234, -567, 891, 0, 1234, -999] → 실패
  [234, -567, 891] → 실패
  [-567, 891] → 실패
  [-567] → 통과
  [891] → 통과
  [-567, 891] → 실패!  ← 최소 실패 사례

보고: "[-567, 891]에서 실패" (더 이해하기 쉬움!)
```

### 속성 기반 테스트 패턴

```python
# 1. 왕복(Roundtrip) 속성
# encode 후 decode하면 원본과 동일
@given(st.sampled_from(["temperature", "vibration", "pressure"]))
def test_encode_decode_roundtrip(sensor_type):
    code = encode_sensor_type(sensor_type)
    decoded = decode_sensor_type(code)
    assert decoded == sensor_type

# 2. 불변(Invariant) 속성
# 결과가 항상 특정 조건을 만족
@given(st.lists(st.floats(min_value=0, max_value=100), min_size=1))
def test_aggregate_count_matches(readings):
    result = aggregate_readings(readings)
    assert result["count"] == len(readings)

# 3. 멱등성(Idempotent) 속성
# 두 번 적용해도 결과가 동일
@given(st.lists(st.floats(min_value=0, max_value=100), min_size=2))
def test_normalize_idempotent(values):
    once = normalize(values)
    twice = normalize(once)
    # 이미 0~1 범위이므로 두 번 정규화해도 동일
    assert once == twice

# 4. 동치(Equivalence) 속성
# 다른 구현이지만 같은 결과
@given(st.lists(st.floats(min_value=0, max_value=100), min_size=1))
def test_aggregate_mean_equals_sum_div_count(readings):
    result = aggregate_readings(readings)
    assert result["mean"] == pytest.approx(result["sum"] / result["count"])
```

## 실습 가이드

### 실습 파일 구조

```
24_property_based_testing/
├── lesson.md                  # 이 파일
├── src_data_transforms.py     # 순수 변환 함수들
├── test_property_demo.py      # 속성 기반 테스트 데모
└── exercises/
    ├── exercise_24.py         # 연습문제
    └── solution_24.py         # 정답
```

### 실행 방법

```bash
# 기본 실행 (hypothesis 없으면 일부 skip)
pytest test_property_demo.py -v

# hypothesis 설치 후 실행
pip install hypothesis
pytest test_property_demo.py -v

# hypothesis 상세 출력
pytest test_property_demo.py -v --hypothesis-show-statistics
```

## 연습 문제

### 연습 1: 불변 속성 식별
`validate_reading()` 함수의 불변 속성을 3개 이상 찾아 테스트로 작성하라.

### 연습 2: 왕복 속성
`encode_sensor_type()`과 `decode_sensor_type()`의 왕복 속성을 테스트하라.

### 연습 3: 동치 속성
`aggregate_readings()`의 `mean`이 `sum / count`와 동일한지 테스트하라.

## 퀴즈

### Q1. 예제 기반 테스트 대비 속성 기반 테스트의 장단점은?
<details>
<summary>정답 보기</summary>

**장점**:
- 자동으로 다양한 엣지 케이스를 발견
- 개발자가 미처 생각하지 못한 입력 조합 테스트
- Shrinking으로 최소 실패 사례 제공

**단점**:
- 속성을 정의하기 어려울 수 있음
- 특정 비즈니스 로직 검증에는 부적합
- 실행 시간이 예제 기반보다 길 수 있음
- 비결정적(nondeterministic) 실행

**최선**: 두 가지를 함께 사용 - 핵심 로직은 예제 기반, 불변 속성은 속성 기반으로.
</details>

### Q2. Shrinking이란 무엇이고 왜 유용한가?
<details>
<summary>정답 보기</summary>

Shrinking은 Hypothesis가 실패하는 입력을 발견했을 때,
**같은 실패를 유발하는 가장 작은(단순한) 입력**을 자동으로 찾아주는 과정이다.

예: `[334, -29, 882, 0, -413]`에서 실패 → `[-29, 882]`로 축소

유용한 이유: 실패 원인을 파악하기가 훨씬 쉬워진다.
긴 리스트보다 짧은 리스트에서 디버깅이 간단하다.
</details>

### Q3. 어떤 함수에 속성 기반 테스트가 적합한가?
<details>
<summary>정답 보기</summary>

- **순수 함수** (같은 입력 → 같은 출력, 부작용 없음)
- **수학적 성질이 있는 함수** (정규화, 인코딩/디코딩, 정렬)
- **역함수가 있는 함수** (encrypt/decrypt, serialize/deserialize)
- **범위 제약이 있는 함수** (결과가 항상 0~100 사이)
- **멱등성이 있는 함수** (두 번 적용해도 같은 결과)

적합하지 않은 경우:
- 특정 비즈니스 규칙 검증 (예: "VIP 고객은 할인 10%")
- 부작용이 있는 함수 (DB 저장, 파일 쓰기)
</details>

## 정리 및 다음 주제 예고

### 오늘 배운 핵심
- **속성 기반 테스트**: "어떤 입력에서도 이 속성이 만족된다"를 검증
- **Hypothesis**: `@given`, `strategies`로 자동 입력 생성
- **Shrinking**: 실패하는 최소 입력을 자동으로 찾아줌
- **속성 패턴**: 왕복, 불변, 멱등성, 동치
- 예제 기반과 속성 기반을 **함께 사용**하는 것이 가장 효과적

### 다음 주제: 25. Snapshot/회귀 테스트
함수의 출력이 **이전과 동일한지** 자동으로 비교하는 스냅샷 테스트를 배운다.
리포트 생성, 데이터 변환 등 구조화된 출력의 회귀를 감지하는 방법을 알아본다.
