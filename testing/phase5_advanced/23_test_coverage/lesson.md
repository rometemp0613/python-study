# 23. 테스트 커버리지

## 학습 목표

이 주제를 마치면 다음을 할 수 있게 된다:
- 라인 커버리지와 브랜치 커버리지의 차이를 이해한다
- pytest-cov를 설정하고 커버리지 리포트를 생성할 수 있다
- `.coveragerc` 파일로 커버리지 측정을 세밀하게 설정할 수 있다
- `pragma: no cover`를 적절하게 사용할 수 있다
- "커버리지는 가이드이지 목표가 아니다"라는 관점을 이해한다

## 동기부여 (예지보전 관점)

예지보전 시스템에서 커버리지가 중요한 이유:
- **설비 상태 분류 로직**에는 수많은 분기(if/elif/else)가 있다. 모든 분기를 테스트했는지 확인해야 한다.
- **비상 정지(shutdown) 로직**은 절대 실패해서는 안 된다. 브랜치 커버리지로 모든 경로를 검증해야 한다.
- **유지보수 우선순위** 결정 로직에 빈틈이 있으면, 중요한 설비를 놓칠 수 있다.
- 커버리지 리포트는 "어디를 테스트하지 않았는가"를 알려주는 **지도** 역할을 한다.

## 핵심 개념

### 라인 커버리지 (Line Coverage)

테스트 중 실행된 코드 라인의 비율이다.

```python
def classify_status(temp):  # 라인 1: 항상 실행
    if temp > 100:           # 라인 2: 항상 실행
        return "danger"      # 라인 3: temp > 100일 때만
    elif temp > 80:          # 라인 4: temp <= 100일 때만
        return "warning"     # 라인 5: 80 < temp <= 100일 때만
    else:                    # 라인 6: temp <= 80일 때만
        return "normal"      # 라인 7: temp <= 80일 때만
```

`test_classify_status(50)` → 라인 1, 2, 4, 6, 7 실행 → 5/7 = 71% 라인 커버리지

### 브랜치 커버리지 (Branch Coverage)

모든 조건문의 **참/거짓 양쪽 경로**가 실행되었는지 측정한다.

```
라인 커버리지 vs 브랜치 커버리지 차이:

def process(value):
    result = "default"        # 라인 A
    if value > 0:             # 분기점: True/False 두 경로
        result = "positive"   # 라인 B
    return result             # 라인 C

# test_process(5) 실행 시:
# 라인 커버리지: A, B, C 모두 실행 → 100%
# 브랜치 커버리지: True 경로만 실행 → 50% (False 경로 미실행!)
```

**브랜치 커버리지가 더 엄격하고 유용하다.**

### pytest-cov 사용법

```bash
# 설치
pip install pytest-cov

# 기본 실행 (라인 커버리지)
pytest --cov=src_equipment_classifier

# 미싱 라인 표시
pytest --cov=src_equipment_classifier --cov-report=term-missing

# 브랜치 커버리지
pytest --cov=src_equipment_classifier --cov-branch --cov-report=term-missing

# HTML 리포트 생성
pytest --cov=src_equipment_classifier --cov-report=html

# 최소 커버리지 (미달 시 실패)
pytest --cov=src_equipment_classifier --cov-fail-under=90
```

### .coveragerc 설정 파일

```ini
# .coveragerc 또는 pyproject.toml의 [tool.coverage.*] 섹션

[run]
# 측정 대상
source = src/
# 브랜치 커버리지 활성화
branch = True
# 제외할 파일 패턴
omit =
    */tests/*
    */migrations/*
    */__init__.py

[report]
# 커버리지 리포트에서 제외할 라인 패턴
exclude_lines =
    pragma: no cover
    def __repr__
    if __name__ == .__main__
    raise NotImplementedError
    pass

# 최소 커버리지 퍼센트
fail_under = 80

# 부분 브랜치 표시
show_missing = True

[html]
# HTML 리포트 출력 디렉토리
directory = htmlcov
```

### pragma: no cover

테스트하기 어렵거나 불필요한 코드를 커버리지 측정에서 제외한다.

```python
def main():  # pragma: no cover
    """CLI 진입점 - 통합 테스트로 검증"""
    app = create_app()
    app.run()

class DebugHelper:  # pragma: no cover
    """디버깅 전용 클래스 - 프로덕션에서 사용하지 않음"""
    pass

def process_data(data):
    if not data:
        raise ValueError("데이터가 비어있습니다")  # 이건 테스트해야 함!

    if os.getenv("DEBUG"):  # pragma: no cover
        print(f"처리 중: {data}")  # 디버그 출력은 제외 가능
```

**주의**: `pragma: no cover`를 남용하면 커버리지 숫자만 높이고 실제로 검증하지 않게 된다.

### 커버리지는 가이드이지 목표가 아니다

```
좋은 사용법:
  ✓ "이 분기를 테스트하지 않았구나" → 테스트 추가
  ✓ "핵심 로직의 커버리지가 95%인데, 나머지 5%는 뭐지?" → 확인
  ✓ "PR에서 새로 추가된 코드의 커버리지는?" → 코드 리뷰 가이드

나쁜 사용법:
  ✗ "100% 커버리지를 달성했으니 버그가 없다" → 착각!
  ✗ "커버리지를 올리기 위해 assert 없는 테스트 추가" → 무의미
  ✗ "pragma: no cover를 남발해서 100% 달성" → 기만
```

**100% 커버리지 ≠ 100% 테스트됨**

```python
# 커버리지 100%이지만 실제로는 아무것도 검증하지 않는 나쁜 예
def test_bad_coverage():
    result = classify_status(50, 10, 100)
    # assert가 없다! 함수가 실행만 되고 결과는 검증하지 않음
```

## 실습 가이드

### 실습 파일 구조

```
23_test_coverage/
├── lesson.md                    # 이 파일
├── src_equipment_classifier.py  # 분기가 많은 분류 로직
├── test_coverage_demo.py        # 의도적으로 일부 분기 미커버
├── test_coverage_complete.py    # 모든 분기를 커버하는 테스트
├── .coveragerc                  # 커버리지 설정 파일
└── exercises/
    ├── exercise_23.py           # 연습문제
    └── solution_23.py           # 정답
```

### 실행 방법

```bash
# 불완전한 테스트의 커버리지 확인
pytest test_coverage_demo.py --cov=src_equipment_classifier --cov-report=term-missing

# 완전한 테스트의 커버리지 확인
pytest test_coverage_complete.py --cov=src_equipment_classifier --cov-report=term-missing

# 브랜치 커버리지 포함
pytest test_coverage_complete.py --cov=src_equipment_classifier --cov-branch --cov-report=term-missing

# 둘 다 실행하여 커버리지 합산
pytest test_coverage_demo.py test_coverage_complete.py --cov=src_equipment_classifier --cov-report=term-missing
```

## 연습 문제

### 연습 1: 커버리지 갭 분석
`test_coverage_demo.py`를 실행하고 커버리지 리포트를 분석하여,
어떤 분기가 테스트되지 않았는지 파악하라.

### 연습 2: 브랜치 커버리지 달성
`should_shutdown()` 함수의 모든 분기 경로를 커버하는 테스트를 작성하라.

### 연습 3: .coveragerc 작성
프로젝트에 맞는 `.coveragerc` 설정을 작성하라.
(브랜치 커버리지, 80% 이상, 테스트 파일 제외)

## 퀴즈

### Q1. 라인 커버리지 100%인데 브랜치 커버리지는 50%인 경우가 가능한가?
<details>
<summary>정답 보기</summary>

가능하다. 예를 들어:
```python
def check(x):
    result = "default"
    if x > 0:
        result = "positive"
    return result
```
`check(5)`만 테스트하면 모든 라인이 실행되어 라인 커버리지 100%이지만,
`if x > 0`의 False 분기는 실행되지 않아 브랜치 커버리지는 50%이다.
</details>

### Q2. `pragma: no cover`를 사용해야 하는 적절한 경우는?
<details>
<summary>정답 보기</summary>

- `if __name__ == "__main__":` 블록
- 디버깅 전용 코드 (`if DEBUG:`)
- 추상 메서드의 `raise NotImplementedError`
- 방어적 코드 중 정상적으로 도달할 수 없는 분기
- `__repr__`, `__str__` 등 표현 메서드 (선택적)

**절대 사용하면 안 되는 경우**: 비즈니스 로직, 에러 처리 코드, 분기 조건
</details>

### Q3. 커버리지를 높이기 위한 잘못된 방법은?
<details>
<summary>정답 보기</summary>

- `assert` 없이 함수만 호출하는 테스트 추가
- `pragma: no cover`를 남발하여 미테스트 코드 제외
- 테스트 의미 없이 모든 경로만 통과시키는 테스트 작성
- 커버리지 측정 대상에서 복잡한 코드를 제외

올바른 방법: 각 분기가 올바른 동작을 하는지 **assert로 검증**하는 테스트 추가
</details>

## 정리 및 다음 주제 예고

### 오늘 배운 핵심
- **라인 커버리지**: 실행된 라인 비율 (기본)
- **브랜치 커버리지**: 조건문의 참/거짓 양쪽 실행 여부 (더 엄격)
- **pytest-cov**: `--cov`, `--cov-branch`, `--cov-report`, `--cov-fail-under`
- **.coveragerc**: 커버리지 설정 파일 (대상, 제외, 임계값)
- **pragma: no cover**: 테스트 불필요한 코드 제외 (남용 금지)
- 커버리지는 **가이드**이지 **목표**가 아니다

### 다음 주제: 24. Property-Based Testing
예제 기반 테스트의 한계를 넘어, "이 함수가 어떤 입력에서도
이 속성을 만족해야 한다"는 방식의 **속성 기반 테스트**를 배운다.
Hypothesis 라이브러리를 사용하여 자동으로 엣지 케이스를 발견하는 방법을 알아본다.
