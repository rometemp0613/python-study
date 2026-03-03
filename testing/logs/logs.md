# Python 테스트 학습 일지

테스트 코드 작성 커리큘럼 학습 기록

---

## 2026-03-02 - Phase 1: 03. pytest 기본기

### 오늘 한 것
- pytest vs unittest 차이점 비교
- 테스트 발견 규칙 (Test Discovery) 3가지
- assert 매직 (하나로 모든 비교 처리)
- pytest.approx() 부동소수점 비교
- pytest.raises() 예외 검증
- @pytest.mark.parametrize 데이터 기반 테스트
- CLI 옵션 (-v, -x, -s, -k, --lf)
- 실습: test_calculations.py 38개 테스트 전부 통과
- 연습문제: exercise_03.py 12개 테스트 작성 및 전부 통과

### 배운 것
- `pytest.approx()`는 숫자/리스트 전용, 딕셔너리에는 `==` 사용
- `pytest.raises()` 안에서 assert 불필요, 함수 호출만
- `pytest.skip()` 남겨두면 테스트가 skip 처리됨 → 반드시 제거
- parametrize는 리스트에 데이터, 함수에서는 한 번만 assert
- `-k` 옵션으로 이름 패턴 필터링 가능 (and, not 조합)
- 에러 메시지를 잘 읽으면 어디가 틀렸는지 바로 보임 (prominence 사례)

### 다음 할 것
- 04. 테스트 구조와 프로젝트 조직 (conftest.py, 디렉토리 레이아웃)

---

## 2026-03-03 - Phase 1: 04. 테스트 구조와 프로젝트 조직

### 오늘 한 것
- 프로젝트 레이아웃 2가지 (tests/ 분리형 vs 같은 폴더형)
- 네이밍 컨벤션 (파일, 함수, 클래스, fixture)
- conftest.py 역할과 계층 구조
- fixture scope (function, class, module, session)
- pyproject.toml의 addopts 설정
- 기존 실습 24개 테스트 전부 통과
- 연습문제: exercise_04.py 7개 테스트 작성 및 전부 통과

### 배운 것
- fixture는 **함수 인자**로 넣어야 pytest가 주입해줌 — 빠뜨리면 에러
- 클래스 안에서 정의한 변수는 `self.변수명`으로 접근해야 함
- `Test` 클래스에 `__init__`이 있으면 pytest가 발견 못 함
- `alarm_tests.py` (복수형) → 발견 안 됨, `test_alarm.py` 또는 `alarm_test.py`만 가능
- conftest.py는 같은 디렉토리 + 하위 디렉토리에서 import 없이 자동 발견
- addopts로 `-v --tb=short` 같은 옵션을 기본값으로 설정 가능

### 다음 할 것
- 05. 예외와 에러 핸들링 테스트 (pytest.raises(), match, ExceptionInfo)

---

