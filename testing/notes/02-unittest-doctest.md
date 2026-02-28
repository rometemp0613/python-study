# 02. Python 내장 테스트: unittest & doctest

## 핵심 개념

### unittest.TestCase
- Python 표준 라이브러리에 내장된 테스트 프레임워크
- `unittest.TestCase`를 상속받아 테스트 클래스를 작성
- 메서드 이름이 `test_`로 시작해야 테스트로 인식됨
- Java의 JUnit에서 영향을 받은 xUnit 스타일

### assert 메서드
- **assertEqual(a, b)**: a == b 확인
- **assertAlmostEqual(a, b, places=7)**: 부동소수점 비교. places 자릿수까지 근사 비교
- **assertRaises(Exception)**: 특정 예외가 발생하는지 확인 (context manager로 사용 가능)
- **assertTrue/assertFalse**: 불리언 확인
- **assertIn**: 멤버십 확인
- pytest의 단순 `assert`와 달리 메서드별로 분리되어 있어 코드가 장황해질 수 있음

### setUp / tearDown
- **setUp()**: 각 테스트 메서드 실행 전에 호출. 테스트에 필요한 객체/데이터 초기화
- **tearDown()**: 각 테스트 메서드 실행 후에 호출. 리소스 정리 (파일 닫기, DB 연결 해제 등)
- pytest의 fixture와 유사한 역할이지만, fixture가 더 유연하고 재사용성이 높음

### doctest
- 문법: docstring 안에 `>>>` 뒤에 입력, 다음 줄에 기대 출력을 작성
- `python -m doctest 파일.py` 또는 `pytest --doctest-modules`로 실행
- **장점**: 문서와 테스트가 하나 — 문서가 항상 최신 상태 유지
- **한계**: 에러/예외 테스트가 어려움, 복잡한 셋업이 필요한 테스트에 부적합, 출력 형식에 민감

### pytest와의 비교
- pytest는 단순 `assert`문 사용 → 더 읽기 쉽고 간결
- pytest는 **unittest 테스트를 그대로 실행 가능** (마이그레이션 부담 없음)
- `pytest.approx()` = `assertAlmostEqual()`의 더 직관적인 대안
- `pytest.raises()` = `assertRaises()`의 더 깔끔한 대안
- 레거시 unittest 코드를 이해하는 건 중요하지만, 신규 코드는 pytest 권장

## 실무 관점
- 레거시 Python 프로젝트에서 unittest 코드를 자주 만남
- unittest 코드를 읽고 이해할 수 있어야 유지보수 가능
- doctest는 간단한 유틸리티 함수의 사용 예시 문서화에 적합
- 예지보전 코드에서: 센서 데이터 처리 함수의 docstring에 doctest로 사용 예시 제공 가능
