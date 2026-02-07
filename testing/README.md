# Python 테스트 코드 작성 - 종합 커리큘럼

**학습 방식**: Claude와 함께 실습 중심 학습
**학습 시작일**: -
**목표**: 어떤 Python 코드든 자신 있게 테스트를 작성할 수 있는 수준
**최종 목표**: 공장설비 예지보전(Predictive Maintenance) 코드의 완전한 테스트 스위트 작성

---

## 커리큘럼 전체 구조

```
Phase 1: 기초 다지기 (Foundation)           - 주제 01~06
Phase 2: pytest 핵심 기능 (Core pytest)     - 주제 07~11
Phase 3: Mocking과 격리 (Mocking)           - 주제 12~16
Phase 4: 실무 코드 테스트 (Real-World)       - 주제 17~21
Phase 5: 고급 기법과 도구 (Advanced)         - 주제 22~26
Phase 6: 테스트 전략 (Strategy)             - 주제 27~31
Phase 7: 예지보전 특화 (Domain-Specific)     - 주제 32~35
```

---

## 진도 체크리스트

### Phase 1: 기초 다지기 (Foundation)

- [ ] **01. 왜 테스트가 필요한가** (`phase1_foundation/01_why_testing/`)
  - 핵심: 자동 테스트의 가치, 테스트 피라미드, 리팩토링 안전망
- [ ] **02. Python 내장 테스트: unittest & doctest** (`phase1_foundation/02_unittest_doctest/`)
  - 핵심: unittest.TestCase, doctest, 레거시 코드 이해
- [ ] **03. pytest 기본기** (`phase1_foundation/03_pytest_basics/`)
  - 핵심: 테스트 발견 규칙, assert, pytest.approx(), CLI 옵션
- [ ] **04. 테스트 구조와 프로젝트 조직** (`phase1_foundation/04_test_organization/`)
  - 핵심: 디렉토리 레이아웃, 네이밍 컨벤션, conftest.py
- [ ] **05. 예외와 에러 핸들링 테스트** (`phase1_foundation/05_testing_exceptions/`)
  - 핵심: pytest.raises(), match, ExceptionInfo, pytest.warns()
- [ ] **06. 출력 캡처** (`phase1_foundation/06_capturing_output/`)
  - 핵심: capsys, capfd, caplog, 로그 레벨 설정

### Phase 2: pytest 핵심 기능 (Core pytest)

- [ ] **07. Fixture 심화** (`phase2_core_pytest/07_fixtures/`)
  - 핵심: 스코프, yield fixture, factory fixture, 파라미터화, autouse
- [ ] **08. Parametrize** (`phase2_core_pytest/08_parametrize/`)
  - 핵심: 다중 파라미터, 테스트 ID, 데코레이터 중첩, 간접 파라미터화
- [ ] **09. Markers** (`phase2_core_pytest/09_markers/`)
  - 핵심: skip, skipif, xfail, 커스텀 마커, 마커 표현식
- [ ] **10. 임시 파일과 디렉토리** (`phase2_core_pytest/10_tmp_path/`)
  - 핵심: tmp_path, tmp_path_factory, 파일 I/O 테스트
- [ ] **11. pytest 설정** (`phase2_core_pytest/11_configuration/`)
  - 핵심: pyproject.toml, pytest.ini, testpaths, markers, addopts

### Phase 3: Mocking과 격리 (Mocking & Isolation)

- [ ] **12. 테스트 더블 이론** (`phase3_mocking/12_test_doubles_theory/`)
  - 핵심: Dummy, Stub, Spy, Mock, Fake, Classical vs Mockist
- [ ] **13. unittest.mock 심화** (`phase3_mocking/13_unittest_mock/`)
  - 핵심: Mock, MagicMock, return_value, side_effect, spec, autospec
- [ ] **14. Patching** (`phase3_mocking/14_patching/`)
  - 핵심: @patch, patch.object(), patch.dict(), 네임스페이스 이해
- [ ] **15. pytest-mock 플러그인** (`phase3_mocking/15_pytest_mock/`)
  - 핵심: mocker fixture, mocker.patch(), mocker.spy()
- [ ] **16. Monkeypatch** (`phase3_mocking/16_monkeypatch/`)
  - 핵심: setattr, setenv, setitem, monkeypatch vs mock.patch

### Phase 4: 실무 코드 테스트 패턴 (Real-World Patterns)

- [ ] **17. Pandas/NumPy 코드 테스트** (`phase4_real_world/17_testing_pandas_numpy/`)
  - 핵심: assert_frame_equal, assert_array_equal, 엣지 케이스
- [ ] **18. 파일 I/O와 데이터 파이프라인 테스트** (`phase4_real_world/18_testing_file_io/`)
  - 핵심: tmp_path, SQLite 인메모리, ETL 테스트
- [ ] **19. 외부 API 상호작용 테스트** (`phase4_real_world/19_testing_apis/`)
  - 핵심: HTTP mock, responses, vcrpy, 재시도 로직
- [ ] **20. 설정과 환경 테스트** (`phase4_real_world/20_testing_config_env/`)
  - 핵심: 환경 변수, 설정 파일, 시간 의존 코드
- [ ] **21. 머신러닝/예측 모델 테스트** (`phase4_real_world/21_testing_ml_models/`)
  - 핵심: 파이프라인, 피처 추출, 모델 직렬화, 성능 메트릭

### Phase 5: 고급 기법과 도구 (Advanced Techniques)

- [ ] **22. pytest 플러그인 생태계** (`phase5_advanced/22_plugins_ecosystem/`)
  - 핵심: pytest-cov, pytest-xdist, pytest-randomly, pytest-timeout
- [ ] **23. 테스트 커버리지** (`phase5_advanced/23_test_coverage/`)
  - 핵심: 라인 vs 브랜치 커버리지, 임계값, 리포트
- [ ] **24. Property-Based Testing** (`phase5_advanced/24_property_based_testing/`)
  - 핵심: Hypothesis, @given, strategies, shrinking
- [ ] **25. Snapshot/회귀 테스트** (`phase5_advanced/25_snapshot_testing/`)
  - 핵심: syrupy, snapshot 비교, 업데이트 워크플로우
- [ ] **26. 비동기 코드 테스트** (`phase5_advanced/26_async_testing/`)
  - 핵심: pytest-asyncio, AsyncMock, async fixture

### Phase 6: 테스트 전략과 실무 관행 (Strategy & Best Practices)

- [ ] **27. TDD (Test-Driven Development)** (`phase6_strategy/27_tdd/`)
  - 핵심: Red-Green-Refactor, TDD 워크플로우
- [ ] **28. 테스트 설계 원칙** (`phase6_strategy/28_test_design_principles/`)
  - 핵심: FIRST 원칙, AAA 패턴, 행위 테스트 vs 구현 테스트
- [ ] **29. Flaky 테스트 다루기** (`phase6_strategy/29_flaky_tests/`)
  - 핵심: 원인 진단, 해결 패턴
- [ ] **30. 테스트 안티패턴** (`phase6_strategy/30_anti_patterns/`)
  - 핵심: 구현 결합, 과도한 mocking, 테스트 오염
- [ ] **31. CI/CD 통합** (`phase6_strategy/31_cicd_integration/`)
  - 핵심: GitHub Actions, JUnit XML, tox, pre-commit

### Phase 7: 예지보전 특화 테스트 (Domain-Specific)

- [ ] **32. 센서 데이터 수집/처리 테스트** (`phase7_predictive_maintenance/32_testing_sensor_data/`)
  - 핵심: 데이터 클리닝, 신호 처리, 피처 추출
- [ ] **33. 데이터 유효성 검증 테스트** (`phase7_predictive_maintenance/33_testing_data_validation/`)
  - 핵심: 스키마 검증, 범위 검증, pandera
- [ ] **34. 예측 모델 테스트** (`phase7_predictive_maintenance/34_testing_predictive_models/`)
  - 핵심: ML 파이프라인, 모델 메트릭, 회귀 테스트
- [ ] **35. 알람/알림 시스템 테스트** (`phase7_predictive_maintenance/35_testing_alerting/`)
  - 핵심: 임계값 알람, 알림 mock, 중복 제거

---

## 필수 도구/라이브러리

| 카테고리 | 도구 |
|---------|------|
| 핵심 프레임워크 | pytest |
| 커버리지 | pytest-cov, coverage.py |
| Mocking | unittest.mock (내장), pytest-mock |
| 병렬 실행 | pytest-xdist |
| 비동기 테스트 | pytest-asyncio |
| 속성 기반 테스트 | hypothesis |
| 스냅샷 테스트 | syrupy |
| 시간 mock | freezegun, time-machine |
| HTTP mock | responses, vcrpy |
| 테스트 순서 | pytest-randomly |
| 타임아웃 | pytest-timeout |
| 출력 | pytest-sugar |
| 벤치마크 | pytest-benchmark |
| CI/CD | GitHub Actions, tox, nox |
| 리포트 | pytest-html |
| 데이터 검증 | pandera |

---

## 학습 일지

| 날짜 | Phase | 주제 | 주요 내용 | 비고 |
|------|-------|------|----------|------|

---

## 진행 현황

- **총 항목**: 35개
- **완료**: 0개
- **진행률**: 0%

---

## 디렉토리 구조

```
python-study/testing/
├── README.md                          # 진도 체크리스트 (현재 파일)
├── CLAUDE.md                          # 테스트 학습 전용 Claude 지침서
├── phase1_foundation/                 # Phase 1: 기초 다지기
│   ├── 01_why_testing/
│   ├── 02_unittest_doctest/
│   ├── 03_pytest_basics/
│   ├── 04_test_organization/
│   ├── 05_testing_exceptions/
│   └── 06_capturing_output/
├── phase2_core_pytest/                # Phase 2: pytest 핵심
├── phase3_mocking/                    # Phase 3: Mocking
├── phase4_real_world/                 # Phase 4: 실무 패턴
├── phase5_advanced/                   # Phase 5: 고급 기법
├── phase6_strategy/                   # Phase 6: 전략
├── phase7_predictive_maintenance/     # Phase 7: 예지보전 특화
├── notes/                             # 주제별 학습 노트
└── logs/                              # 학습 일지
```

---

## 검증 방법

```bash
# 각 주제별 테스트 실행
pytest phase1_foundation/01_why_testing/ -v

# Phase 전체 테스트
pytest phase1_foundation/ -v

# 전체 테스트 + 커버리지
pytest --cov -v

# 특정 마커로 실행
pytest -m "not slow" -v
```
