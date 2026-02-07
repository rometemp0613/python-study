# 22. pytest 플러그인 생태계

## 학습 목표

이 주제를 마치면 다음을 할 수 있게 된다:
- pytest의 플러그인 아키텍처를 이해한다
- 주요 플러그인(pytest-cov, pytest-xdist, pytest-randomly, pytest-timeout, pytest-sugar, pytest-benchmark, pytest-html)의 역할과 사용법을 안다
- 프로젝트에 적합한 플러그인을 선택하고 설정할 수 있다
- 성능 벤치마크 테스트를 작성할 수 있다

## 동기부여 (예지보전 관점)

공장설비 예지보전 시스템에서는:
- **수천 개의 센서 테스트**를 빠르게 실행해야 한다 → `pytest-xdist` (병렬 실행)
- **신호 처리 함수의 성능**이 중요하다 → `pytest-benchmark` (벤치마크)
- **테스트 순서에 의존하는 버그**를 찾아야 한다 → `pytest-randomly` (랜덤 실행)
- **무한 루프에 빠진 모니터링 코드**를 감지해야 한다 → `pytest-timeout` (타임아웃)
- **커버리지 리포트**로 미검증 코드를 파악해야 한다 → `pytest-cov` (커버리지)
- **CI/CD 파이프라인에 리포트**를 통합해야 한다 → `pytest-html` (HTML 리포트)

## 핵심 개념

### pytest 플러그인 아키텍처

pytest는 "훅(hook)" 기반 플러그인 시스템을 사용한다. 플러그인은 pytest의 실행 과정에
훅 함수를 등록하여 동작을 변경하거나 확장한다.

```
pytest 실행 흐름:
  수집(collect) → 설정(configure) → 실행(run) → 리포트(report)
       ↑              ↑              ↑            ↑
    플러그인        플러그인        플러그인      플러그인
    (훅 등록)      (훅 등록)      (훅 등록)    (훅 등록)
```

### 설치된 플러그인 확인

```bash
# 현재 설치된 플러그인 목록 확인
pytest --co -q  # 수집만 하기
pytest -p no:cacheprovider  # 특정 플러그인 비활성화
```

---

### 1. pytest-cov (커버리지)

테스트가 소스 코드의 몇 %를 실행하는지 측정한다.

```bash
pip install pytest-cov
```

```bash
# 기본 사용법
pytest --cov=src_module tests/

# 터미널에 라인별 리포트 출력
pytest --cov=src_module --cov-report=term-missing

# HTML 리포트 생성
pytest --cov=src_module --cov-report=html

# 최소 커버리지 설정 (미달 시 실패)
pytest --cov=src_module --cov-fail-under=80
```

```python
# pyproject.toml 설정 예시
# [tool.pytest.ini_options]
# addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"
```

---

### 2. pytest-xdist (병렬 실행)

테스트를 여러 프로세스/머신에서 병렬로 실행한다.

```bash
pip install pytest-xdist
```

```bash
# CPU 코어 수만큼 병렬 실행
pytest -n auto

# 4개 프로세스로 실행
pytest -n 4

# 테스트 분배 방식 지정
pytest -n 4 --dist=loadscope  # 같은 모듈/클래스는 같은 워커에
```

**주의**: 병렬 실행 시 공유 리소스(파일, DB)에 대한 경쟁 조건을 조심해야 한다.

```python
# 병렬 안전한 테스트 작성 예시
def test_sensor_processing(tmp_path):
    """tmp_path는 각 테스트마다 고유한 디렉토리를 제공하므로 병렬 안전"""
    output_file = tmp_path / "result.csv"
    # ... 테스트 코드
```

---

### 3. pytest-randomly (랜덤 실행 순서)

테스트 실행 순서를 무작위로 섞어서, 순서 의존적 버그를 발견한다.

```bash
pip install pytest-randomly
```

```bash
# 설치만 하면 자동으로 랜덤 실행
pytest -v  # 시드 번호가 출력됨

# 특정 시드로 재현
pytest -v -p randomly --randomly-seed=12345

# 마지막 실패 시드로 재현
pytest -v -p randomly --randomly-seed=last

# 랜덤 비활성화
pytest -p no:randomly
```

---

### 4. pytest-timeout (타임아웃)

테스트가 지정된 시간 내에 완료되지 않으면 실패 처리한다.

```bash
pip install pytest-timeout
```

```python
import pytest

# 데코레이터로 개별 테스트에 타임아웃 설정
@pytest.mark.timeout(5)  # 5초
def test_sensor_monitoring():
    """센서 모니터링 함수가 5초 이내에 완료되어야 한다"""
    pass

# 전역 설정 (pyproject.toml)
# [tool.pytest.ini_options]
# timeout = 30  # 모든 테스트에 30초 타임아웃
```

---

### 5. pytest-sugar (예쁜 출력)

테스트 실행 결과를 프로그레스 바와 색상으로 보기 좋게 출력한다.

```bash
pip install pytest-sugar
```

설치만 하면 자동으로 적용된다. 기존의 점(`.`)과 `F` 대신 진행 바가 표시된다.

```bash
# 비활성화
pytest -p no:sugar
```

---

### 6. pytest-benchmark (성능 벤치마크)

함수의 실행 시간을 정밀하게 측정하고 비교한다.

```bash
pip install pytest-benchmark
```

```python
def test_rms_performance(benchmark):
    """RMS 계산 성능 벤치마크"""
    values = list(range(10000))

    # benchmark 픽스처가 자동으로 여러 번 실행하고 통계 산출
    result = benchmark(calculate_rms, values)

    assert result > 0

def test_peak_detection_performance(benchmark):
    """피크 감지 성능 벤치마크"""
    values = [1, 5, 2, 8, 3, 9, 1, 7]

    # 인자가 있는 함수
    result = benchmark(detect_peaks, values, threshold=6)
```

```bash
# 벤치마크 실행
pytest --benchmark-only

# 벤치마크 비교 (이전 결과 저장)
pytest --benchmark-save=baseline
pytest --benchmark-compare=baseline

# 벤치마크 비활성화 (일반 테스트만)
pytest --benchmark-disable
```

---

### 7. pytest-html (HTML 리포트)

테스트 결과를 HTML 파일로 내보낸다. CI/CD 파이프라인에서 유용하다.

```bash
pip install pytest-html
```

```bash
# HTML 리포트 생성
pytest --html=report.html

# CSS를 리포트에 포함 (독립 파일)
pytest --html=report.html --self-contained-html
```

---

### 플러그인 조합 예시

실무에서는 여러 플러그인을 함께 사용한다:

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = """
    --cov=src
    --cov-report=term-missing
    --cov-fail-under=80
    --timeout=60
    -n auto
    --html=reports/test_report.html
    --self-contained-html
"""
```

```bash
# 개발 중: 빠르게 실행
pytest -x -q --no-header

# CI/CD: 전체 실행 + 리포트
pytest -n auto --cov=src --cov-report=html --html=report.html

# 성능 테스트만
pytest --benchmark-only -k "benchmark"
```

## 실습 가이드

### 실습 파일 구조

```
22_plugins_ecosystem/
├── lesson.md                    # 이 파일
├── src_performance_critical.py  # 벤치마크 대상 함수들
├── test_plugins_demo.py         # 플러그인 활용 테스트
└── exercises/
    ├── exercise_22.py           # 연습문제
    └── solution_22.py           # 정답
```

### 실행 방법

```bash
# 기본 테스트 실행
pytest test_plugins_demo.py -v

# 커버리지와 함께 (pytest-cov 설치 시)
pytest test_plugins_demo.py --cov=src_performance_critical --cov-report=term-missing

# 벤치마크와 함께 (pytest-benchmark 설치 시)
pytest test_plugins_demo.py --benchmark-enable -v
```

## 연습 문제

### 연습 1: 타임아웃 테스트
`batch_process_sensors()` 함수에 대해 큰 데이터셋을 처리할 때
적절한 타임아웃을 설정한 테스트를 작성하라.

### 연습 2: 벤치마크 비교
`moving_average()` 함수를 두 가지 방법(단순 반복 vs 슬라이딩 윈도우)으로
구현하고, 벤치마크로 성능을 비교하는 테스트를 작성하라.

### 연습 3: 플러그인 설정
`pyproject.toml`에 적절한 pytest 플러그인 설정을 작성하라.
(커버리지 80% 이상, 타임아웃 30초, 병렬 실행)

## 퀴즈

### Q1. pytest-xdist로 병렬 실행 시 주의해야 할 점은?
<details>
<summary>정답 보기</summary>

공유 리소스(파일, 데이터베이스, 네트워크 포트 등)에 대한 경쟁 조건(race condition)이
발생할 수 있다. `tmp_path`처럼 테스트별 고유 리소스를 사용하거나,
`--dist=loadscope`으로 같은 모듈의 테스트를 같은 워커에 배치해야 한다.
</details>

### Q2. pytest-randomly는 왜 사용하는가?
<details>
<summary>정답 보기</summary>

테스트 간의 순서 의존성(order dependency)을 발견하기 위해서다.
테스트 A가 먼저 실행되어야 테스트 B가 통과하는 경우, 이는 테스트 격리가
제대로 되지 않았다는 신호이다. 랜덤 실행으로 이런 문제를 조기에 발견할 수 있다.
</details>

### Q3. pytest-benchmark에서 `benchmark` 픽스처는 무엇을 하는가?
<details>
<summary>정답 보기</summary>

함수를 여러 번(보통 수백~수천 회) 반복 실행하여 정밀한 실행 시간 통계
(평균, 중앙값, 표준편차, 최솟값, 최댓값 등)를 산출한다.
단일 실행의 변동성을 제거하고 안정적인 성능 측정을 가능하게 한다.
</details>

## 정리 및 다음 주제 예고

### 오늘 배운 핵심
- pytest는 **훅 기반 플러그인 아키텍처**로 확장 가능하다
- **pytest-cov**: 커버리지 측정 → 미검증 코드 파악
- **pytest-xdist**: 병렬 실행 → 테스트 실행 시간 단축
- **pytest-randomly**: 랜덤 순서 → 순서 의존 버그 발견
- **pytest-timeout**: 타임아웃 → 무한 루프/행 방지
- **pytest-sugar**: 예쁜 출력 → 개발 경험 향상
- **pytest-benchmark**: 성능 벤치마크 → 성능 회귀 감지
- **pytest-html**: HTML 리포트 → CI/CD 통합

### 다음 주제: 23. 테스트 커버리지
pytest-cov를 더 깊이 파고들어, 라인 커버리지 vs 브랜치 커버리지의 차이,
커버리지 설정 파일(.coveragerc) 작성법, 그리고 "커버리지는 가이드이지
목표가 아니다"라는 중요한 관점을 배운다.
