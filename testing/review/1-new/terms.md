# 새로 배운 용어/개념

## 01. 왜 테스트가 필요한가

(01 용어 전부 2-practicing으로 승급 — 2026-02-28)

## 02. Python 내장 테스트: unittest & doctest

- **unittest.TestCase**: Python 표준 라이브러리 내장 테스트 프레임워크의 기본 클래스. 이 클래스를 상속받아 test_ 메서드를 작성하는 xUnit 스타일
- **assertEqual / assertAlmostEqual / assertRaises**: unittest의 핵심 assert 메서드. assertEqual은 동등 비교, assertAlmostEqual은 부동소수점 근사 비교(places 지정), assertRaises는 예외 발생 검증
- **setUp / tearDown**: 각 테스트 메서드 실행 전후에 호출되는 초기화/정리 메서드. pytest의 fixture와 유사하지만 fixture가 더 유연함
- **doctest**: docstring 안에 `>>>` 입력과 기대 출력을 작성하여 문서와 테스트를 겸하는 방식. 간단한 함수 문서화에 적합하지만 에러 테스트나 복잡한 셋업에는 부적합
- **pytest.approx()**: 부동소수점 비교를 위한 pytest 유틸리티. assertAlmostEqual보다 직관적 (예: `assert 0.1+0.2 == pytest.approx(0.3)`)
- **pytest.raises()**: 예외 발생을 검증하는 pytest context manager. assertRaises보다 깔끔한 문법 (예: `with pytest.raises(ValueError):`)

## 03. pytest 기본기

- **테스트 발견 규칙 (Test Discovery)**: pytest가 테스트를 자동으로 찾는 3가지 규칙. 파일명: `test_*.py` 또는 `*_test.py`, 함수명: `test_`로 시작, 클래스명: `Test`로 시작 (`__init__` 없어야 함)
- **assert 매직**: pytest는 `assert`문 하나로 모든 비교를 처리. 실패 시 자동으로 상세한 차이점을 보여줌 (unittest의 assertEqual 등 20개+ 메서드 대신)
- **pytest.approx()**: 부동소수점 숫자 비교 전용. 딕셔너리 리스트에는 안 맞고 `==`로 비교. `abs=`(절대오차), `rel=`(상대오차) 지정 가능
- **-k 옵션**: 테스트 이름 패턴으로 필터링. `pytest -k "alarm and not warning"`은 이름에 alarm 포함, warning 제외한 테스트만 실행
- **@pytest.mark.parametrize**: 여러 입력값을 리스트로 넣고, 함수에서는 한 번만 assert. 테스트 케이스를 데이터로 관리하는 방식
- **주요 CLI 옵션**: `-v`(상세), `-x`(첫 실패에서 멈춤), `-s`(print 출력 보기), `--lf`(마지막 실패만 재실행), `-k`(이름 필터)
