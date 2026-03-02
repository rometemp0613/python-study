# 복습 중인 용어/개념

## 01. 왜 테스트가 필요한가 (2026-02-28 승급)

- **경계값 테스트 (Boundary Testing)**: 조건 분기의 경계에서 값을 테스트하는 기법. 예: 4.49 vs 4.5로 정상/주의 분류 검증

## 03. pytest 기본기 (2026-03-02 승급)

- **pytest.approx()**: 부동소수점 비교를 위한 pytest 유틸리티. assertAlmostEqual보다 직관적 (예: `assert 0.1+0.2 == pytest.approx(0.3)`). 딕셔너리에는 사용 불가
