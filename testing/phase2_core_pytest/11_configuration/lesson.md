# 11. pytest 설정 (Configuration)

## 1. 학습 목표

- `pyproject.toml`, `pytest.ini`, `setup.cfg`에서 pytest 설정을 구성한다
- 주요 설정 항목(testpaths, markers, addopts, filterwarnings)을 이해한다
- `conftest.py`에서 프로그래밍 방식으로 설정한다
- 프로젝트에 맞는 최적의 설정 전략을 수립한다

## 2. 동기부여: 예지보전 관점

예지보전 시스템 프로젝트가 커지면 테스트 관리가 복잡해집니다:
- 수백 개의 테스트 파일이 여러 디렉토리에 분산
- 느린 통합 테스트와 빠른 단위 테스트 구분 필요
- CI/CD 파이프라인에서 특정 옵션으로 실행
- 경고 메시지 필터링 및 로깅 설정

pytest 설정을 올바르게 구성하면:
- **테스트 실행 경로**를 명확히 지정
- **기본 옵션**으로 매번 긴 명령어를 입력하지 않아도 됨
- **마커 등록**으로 경고 없이 커스텀 마커 사용
- **경고 필터**로 불필요한 경고 메시지 제거

## 3. 핵심 개념 설명

### 3.1 설정 파일 우선순위

pytest는 다음 순서로 설정 파일을 찾습니다:

1. `pyproject.toml` (권장)
2. `pytest.ini`
3. `setup.cfg`
4. `tox.ini`

**`pyproject.toml`이 현대 Python 프로젝트의 표준**입니다.

### 3.2 pyproject.toml 주요 설정

```toml
[tool.pytest.ini_options]
# 테스트 파일을 찾을 디렉토리
testpaths = ["tests"]

# 테스트 파일 패턴
python_files = ["test_*.py", "*_test.py"]

# 테스트 함수 패턴
python_functions = ["test_*"]

# 테스트 클래스 패턴
python_classes = ["Test*"]

# 기본 명령줄 옵션
addopts = "-v --strict-markers --tb=short"

# 커스텀 마커 등록
markers = [
    "slow: 실행 시간이 오래 걸리는 테스트",
    "integration: 외부 시스템 연동 테스트",
    "sensor: 센서 관련 테스트",
]

# 경고 필터
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]

# 최소 pytest 버전
minversion = "7.0"
```

### 3.3 pytest.ini

```ini
[pytest]
testpaths = tests
addopts = -v --strict-markers
markers =
    slow: 느린 테스트
    integration: 통합 테스트
```

### 3.4 주요 설정 항목 상세

#### testpaths
테스트를 검색할 디렉토리를 지정합니다.

```toml
# 단일 디렉토리
testpaths = ["tests"]

# 여러 디렉토리
testpaths = ["tests/unit", "tests/integration"]
```

#### addopts
매번 기본으로 적용할 명령줄 옵션을 설정합니다.

```toml
addopts = [
    "-v",              # 상세 출력
    "--strict-markers", # 미등록 마커 사용 시 에러
    "--tb=short",       # 짧은 트레이스백
    "-ra",             # 실패/건너뜀 테스트 요약 표시
]
```

#### markers
커스텀 마커를 등록합니다. `--strict-markers`와 함께 사용하면 미등록 마커를 방지합니다.

```toml
markers = [
    "slow: 실행 시간이 오래 걸리는 테스트",
    "integration: 외부 시스템 연동 테스트",
    "sensor: 센서 관련 테스트",
    "motor: 모터 장비 테스트",
]
```

#### filterwarnings
테스트 중 발생하는 경고를 필터링합니다.

```toml
filterwarnings = [
    "error",                          # 모든 경고를 에러로 처리
    "ignore::DeprecationWarning",     # DeprecationWarning 무시
    "ignore::PendingDeprecationWarning",
]
```

### 3.5 conftest.py에서 프로그래밍 설정

```python
# conftest.py

def pytest_configure(config):
    """pytest 설정을 프로그래밍 방식으로 구성"""
    config.addinivalue_line(
        "markers", "smoke: 핵심 기능 확인 테스트"
    )

def pytest_collection_modifyitems(config, items):
    """수집된 테스트를 수정 (예: 자동 마커 부여)"""
    for item in items:
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)
```

### 3.6 환경별 설정 전략

```
project/
├── pyproject.toml           # 기본 설정
├── conftest.py              # 프로젝트 루트 fixture
├── tests/
│   ├── conftest.py          # 테스트 공통 fixture
│   ├── unit/                # 단위 테스트
│   │   └── conftest.py
│   └── integration/         # 통합 테스트
│       └── conftest.py
```

## 4. 실습 가이드

### 실습 1: pyproject.toml 설정

`pyproject.toml`의 설정을 확인하고 테스트를 실행합니다.

```bash
# 상세 출력으로 실행
pytest test_config_demo.py -v

# 등록된 마커 확인
pytest --markers

# strict-markers 테스트
pytest --strict-markers -v
```

### 실습 2: 설정 효과 확인

```bash
# 기본 설정 확인
pytest --co  # 수집만 하고 실행하지 않음

# 설정 파일 위치 확인
pytest --version
```

### 실습 3: conftest.py 효과

```bash
# conftest.py의 hook이 동작하는지 확인
pytest test_config_demo.py -v -s
```

## 5. 연습 문제

### 연습 1: pyproject.toml 설정
예지보전 프로젝트에 맞는 pyproject.toml 설정을 작성하세요.
testpaths, markers, addopts를 포함해야 합니다.

### 연습 2: conftest.py hook
conftest.py에서 pytest_configure를 사용하여 커스텀 마커를
프로그래밍 방식으로 등록하세요.

### 연습 3: 설정 검증 테스트
설정이 올바르게 적용되는지 확인하는 테스트를 작성하세요.

## 6. 퀴즈

### Q1. 설정 파일 우선순위
다음 중 pytest가 가장 먼저 찾는 설정 파일은?

A) `setup.cfg`
B) `pytest.ini`
C) `pyproject.toml`
D) `tox.ini`

**정답: C** - `pyproject.toml`이 가장 높은 우선순위를 가집니다.

### Q2. strict-markers
`--strict-markers` 옵션의 효과는?

A) 마커가 있는 테스트만 실행
B) 등록되지 않은 마커를 사용하면 에러 발생
C) 마커 순서를 강제
D) 마커를 자동으로 등록

**정답: B** - 등록되지 않은 마커를 사용하면 에러를 발생시켜, 마커 오타를 방지합니다.

### Q3. addopts
`addopts = "-v --tb=short"`의 효과는?

A) 특정 테스트만 실행
B) 매번 `-v --tb=short` 옵션이 자동으로 적용
C) 이 옵션들을 사용할 수 없게 함
D) 테스트 속도를 빠르게 함

**정답: B** - `addopts`에 설정한 옵션은 매 테스트 실행 시 자동으로 적용됩니다.

## 7. 정리 및 다음 주제 예고

### 이번 단원 정리
- **pyproject.toml**: 현대 Python 프로젝트의 표준 설정 파일
- **testpaths**: 테스트 검색 디렉토리 지정
- **addopts**: 기본 명령줄 옵션 설정
- **markers**: 커스텀 마커 등록 및 문서화
- **filterwarnings**: 경고 메시지 필터링
- **conftest.py**: 프로그래밍 방식의 동적 설정
- **strict-markers**: 마커 오타 방지

### 다음 주제: Phase 3 - 모킹(Mocking)
다음 단계에서는 테스트 더블(Test Double)의 개념과 `unittest.mock`,
`pytest-mock` 라이브러리를 활용한 모킹 기법을 배웁니다.
외부 API, 데이터베이스, 하드웨어 연결 등을 모킹하여
단위 테스트를 효과적으로 작성할 수 있습니다.
