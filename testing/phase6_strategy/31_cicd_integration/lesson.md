# 31. CI/CD 통합

## 학습 목표
- CI/CD 파이프라인에서 테스트 자동화의 중요성을 이해한다
- GitHub Actions 워크플로우를 작성할 수 있다
- JUnit XML 형식으로 테스트 결과를 출력할 수 있다
- tox/nox를 사용하여 여러 환경에서 테스트를 실행할 수 있다
- pre-commit 훅으로 코드 품질을 관리할 수 있다

## 동기부여: 예지보전 관점

예지보전 시스템은 **안정성이 생명**입니다. 장비 고장 예측 모델이나 경보 시스템에 버그가 있으면 장비 손상이나 생산 중단으로 이어질 수 있습니다.

CI/CD를 통해:
- **모든 변경사항이 자동으로 테스트**됩니다
- **코드 리뷰 전에 문제를 발견**할 수 있습니다
- **배포 전 품질이 보장**됩니다
- **테스트 커버리지를 지속적으로 관리**할 수 있습니다

## 핵심 개념

### 1. CI/CD 파이프라인 개요

```
코드 푸시 → 린팅 → 단위 테스트 → 통합 테스트 → 커버리지 → 배포
   │          │          │            │            │         │
   │    코드 스타일    빠른 검증    API/DB 검증   품질 게이트  자동 배포
   │    검사          (pytest)     (느린 테스트)  (80%+)
   └──────────────────────────────────────────────────────────┘
                    자동화된 파이프라인
```

### 2. GitHub Actions 워크플로우

```yaml
# .github/workflows/test.yml
name: Python 테스트

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
    - name: 코드 체크아웃
      uses: actions/checkout@v4

    - name: Python 설정
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: 의존성 설치
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8

    - name: 린팅 (flake8)
      run: |
        flake8 src/ --max-line-length=120 --count --statistics

    - name: 테스트 실행 (pytest)
      run: |
        pytest tests/ -v --tb=short --junitxml=test-results.xml

    - name: 커버리지 확인
      run: |
        pytest tests/ --cov=src --cov-report=xml --cov-fail-under=80

    - name: 테스트 결과 업로드
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: test-results-${{ matrix.python-version }}
        path: test-results.xml
```

### 3. JUnit XML 출력

CI 도구들은 JUnit XML 형식을 표준으로 사용합니다:

```bash
# JUnit XML 형식으로 테스트 결과 출력
pytest tests/ --junitxml=test-results.xml -v

# 커버리지와 함께
pytest tests/ --cov=src --cov-report=xml --junitxml=test-results.xml
```

생성되는 XML 예시:
```xml
<?xml version="1.0" encoding="utf-8"?>
<testsuites>
  <testsuite name="pytest" tests="10" errors="0" failures="0" skipped="1">
    <testcase classname="tests.test_sensor" name="test_reading" time="0.001"/>
    <testcase classname="tests.test_sensor" name="test_anomaly" time="0.002"/>
  </testsuite>
</testsuites>
```

### 4. 브랜치 보호 규칙

GitHub에서 브랜치 보호를 설정하여 테스트를 강제합니다:

- **필수 상태 검사**: CI 테스트가 통과해야만 머지 가능
- **필수 리뷰어**: 최소 1명의 코드 리뷰 필요
- **브랜치 최신화**: PR 브랜치가 최신이어야 함

### 5. tox를 사용한 다중 환경 테스트

```ini
# tox.ini
[tox]
envlist = py39, py310, py311, py312, lint

[testenv]
deps =
    pytest
    pytest-cov
commands =
    pytest tests/ -v --cov=src --cov-report=term-missing

[testenv:lint]
deps =
    flake8
    mypy
commands =
    flake8 src/ --max-line-length=120
    mypy src/ --ignore-missing-imports
```

```bash
# 모든 환경에서 테스트 실행
tox

# 특정 환경만 실행
tox -e py311

# 린팅만 실행
tox -e lint
```

### 6. nox를 사용한 유연한 자동화

```python
# noxfile.py
import nox

@nox.session(python=["3.9", "3.10", "3.11", "3.12"])
def tests(session):
    session.install("pytest", "pytest-cov")
    session.install("-r", "requirements.txt")
    session.run("pytest", "tests/", "-v", "--cov=src")

@nox.session
def lint(session):
    session.install("flake8", "mypy")
    session.run("flake8", "src/", "--max-line-length=120")
    session.run("mypy", "src/", "--ignore-missing-imports")
```

### 7. pre-commit 훅

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml

  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=120]

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/ -x -q
        language: system
        pass_filenames: false
        always_run: true
```

```bash
# pre-commit 설치
pip install pre-commit
pre-commit install

# 수동 실행
pre-commit run --all-files
```

### 8. 실제 프로젝트 구조

```
predictive-maintenance/
├── .github/
│   └── workflows/
│       ├── test.yml          # 테스트 워크플로우
│       └── deploy.yml        # 배포 워크플로우
├── src/
│   ├── __init__.py
│   ├── sensor_monitor.py
│   ├── anomaly_detector.py
│   └── maintenance_scheduler.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_sensor.py
│   │   └── test_detector.py
│   └── integration/
│       └── test_pipeline.py
├── .pre-commit-config.yaml
├── tox.ini
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

## 실습 가이드

### 실습 1: 워크플로우 파일 확인

`github_actions_example.yml`을 확인하고 각 단계를 이해하세요.

### 실습 2: CI용 테스트 실행

```bash
# JUnit XML 출력으로 테스트 실행
pytest test_cicd_example.py -v --tb=short --junitxml=test-results.xml

# 커버리지와 함께
pytest test_cicd_example.py --cov=src_cicd_example --cov-report=term-missing
```

### 실습 3: tox 설정 확인

`tox_example.ini`를 확인하고 tox의 구조를 이해하세요.

## 연습 문제

### 연습 1: GitHub Actions 워크플로우 작성
예지보전 프로젝트를 위한 GitHub Actions 워크플로우를 작성하세요.

### 연습 2: tox 설정 작성
다중 Python 버전에서 테스트를 실행하는 tox 설정을 작성하세요.

### 연습 3: CI 파이프라인 연습 (exercises/exercise_31.py)
CI 환경에서 실행되는 테스트를 작성하세요.

## 퀴즈

### Q1. CI/CD에서 테스트 결과를 표준 형식으로 출력하는 방법은?
- A) `pytest --output=json`
- B) `pytest --junitxml=results.xml`
- C) `pytest --report=html`
- D) `pytest --format=ci`

**정답: B**
`--junitxml` 옵션으로 JUnit XML 형식의 테스트 결과를 출력합니다.

### Q2. tox의 주요 용도는?
- A) 코드 포매팅
- B) 여러 Python 환경에서 테스트 실행
- C) 도커 컨테이너 관리
- D) 코드 배포

**정답: B**
tox는 여러 Python 버전에서 테스트를 자동으로 실행하는 도구입니다.

### Q3. pre-commit 훅의 역할은?
- A) 커밋 후 테스트 실행
- B) 푸시 후 배포
- C) 커밋 전 코드 품질 검사
- D) PR 생성 후 리뷰 요청

**정답: C**
pre-commit은 git commit 전에 코드 품질 검사(린팅, 포매팅, 테스트 등)를 자동으로 수행합니다.

## 정리 및 다음 주제 예고

### 이번 레슨 정리
- **GitHub Actions**: 코드 푸시/PR 시 자동으로 테스트 실행
- **워크플로우 단계**: Checkout → Install → Lint → Test → Coverage
- **JUnit XML**: CI 도구 표준 테스트 결과 형식
- **브랜치 보호**: 테스트 통과를 머지 조건으로 설정
- **tox/nox**: 다중 환경 테스트 자동화
- **pre-commit**: 커밋 전 품질 검사

### 다음 주제: Phase 7 - 예지보전 프로젝트
지금까지 배운 모든 테스트 기법을 종합하여 실제 예지보전 프로젝트에 적용합니다.
