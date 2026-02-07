# 04. 테스트 구조와 프로젝트 조직

## 1. 학습 목표

- 테스트 파일과 디렉토리의 표준 배치 방법을 이해한다
- 테스트 네이밍 컨벤션을 따를 수 있다
- `conftest.py`의 역할과 계층 구조를 이해한다
- 공유 fixture를 `conftest.py`에서 정의하고 활용한다
- 잘 조직된 테스트 코드가 유지보수성에 미치는 영향을 안다

## 2. 동기부여 (예지보전 관점)

예지보전 시스템이 커지면 수십, 수백 개의 테스트가 필요합니다:
- 센서 데이터 처리 모듈 테스트
- 이상 감지 알고리즘 테스트
- 데이터베이스 연동 테스트
- API 통합 테스트

이런 테스트들을 체계적으로 관리하지 않으면:
- 어떤 테스트가 어디 있는지 찾기 어려움
- 중복 코드가 늘어남 (같은 테스트 데이터를 여러 곳에서 정의)
- 새로운 팀원이 테스트 구조를 이해하기 힘듦

**잘 조직된 테스트 코드 = 유지보수 가능한 시스템**

## 3. 핵심 개념 설명

### 3.1 프로젝트 디렉토리 구조

#### 방법 1: 소스와 테스트 분리 (권장)

```
project/
├── src/                          # 소스 코드
│   └── predictive_maintenance/
│       ├── __init__.py
│       ├── sensors.py
│       ├── data_processor.py
│       └── anomaly_detector.py
├── tests/                        # 테스트 코드
│   ├── conftest.py               # 공유 fixture (최상위)
│   ├── test_sensors.py
│   ├── test_data_processor.py
│   └── test_anomaly_detector.py
├── pyproject.toml
└── README.md
```

#### 방법 2: 소스 옆에 테스트 (소규모 프로젝트)

```
project/
├── predictive_maintenance/
│   ├── __init__.py
│   ├── sensors.py
│   ├── test_sensors.py           # 소스 옆에 테스트
│   ├── data_processor.py
│   └── test_data_processor.py
└── conftest.py
```

### 3.2 네이밍 컨벤션

| 대상 | 규칙 | 예시 |
|------|------|------|
| 테스트 파일 | `test_모듈명.py` | `test_sensors.py` |
| 테스트 클래스 | `Test기능명` | `TestTemperatureSensor` |
| 테스트 메서드 | `test_행동_조건` | `test_detect_overheating_when_above_threshold` |
| fixture | `명사형` | `sample_readings`, `db_connection` |
| conftest | `conftest.py` (고정) | 디렉토리별 하나 |

```python
# 좋은 네이밍 예시
class TestDataProcessor:
    def test_정상_데이터_처리(self): ...
    def test_빈_데이터_예외_발생(self): ...
    def test_이상치_필터링(self): ...

# 나쁜 네이밍 예시
class Tests:                            # 너무 일반적
    def test1(self): ...                # 의미 없음
    def test_it_works(self): ...        # 무엇이 동작하는지 불명확
```

### 3.3 conftest.py의 역할

`conftest.py`는 pytest의 특수 파일로, **같은 디렉토리와 하위 디렉토리**의
모든 테스트에서 사용할 수 있는 fixture, hook, plugin을 정의합니다.

```
tests/
├── conftest.py              # 모든 테스트에서 사용 가능
├── unit/
│   ├── conftest.py          # unit 테스트에서만 사용 가능
│   ├── test_sensors.py
│   └── test_processor.py
└── integration/
    ├── conftest.py          # integration 테스트에서만 사용 가능
    └── test_api.py
```

### 3.4 conftest.py 예제

```python
# tests/conftest.py - 최상위 공유 fixture

import pytest

@pytest.fixture
def sample_sensor_data():
    """테스트용 센서 데이터를 제공한다."""
    return {
        "sensor_id": "TEMP-001",
        "readings": [25.0, 25.5, 26.0, 25.8, 25.2],
        "unit": "celsius",
        "location": "모터 A",
    }

@pytest.fixture
def sample_config():
    """테스트용 시스템 설정을 제공한다."""
    return {
        "temperature_threshold": 80.0,
        "vibration_threshold": 7.1,
        "sampling_interval": 60,
        "alert_email": "operator@factory.com",
    }
```

### 3.5 fixture의 범위(scope)

```python
@pytest.fixture(scope="function")   # 기본값: 각 테스트 함수마다
def temp_data():
    return [25.0, 26.0, 27.0]

@pytest.fixture(scope="class")      # 테스트 클래스마다
def db_connection():
    conn = create_connection()
    yield conn
    conn.close()

@pytest.fixture(scope="module")     # 모듈(파일)마다
def expensive_resource():
    return load_large_dataset()

@pytest.fixture(scope="session")    # 전체 테스트 세션에서 한 번
def global_config():
    return load_config()
```

### 3.6 테스트 클래스로 그룹화

```python
class TestDataProcessor:
    """데이터 처리 모듈의 모든 테스트를 그룹화"""

    class TestNormalization:
        """정규화 관련 테스트"""
        def test_0_1_정규화(self): ...
        def test_음수값_정규화(self): ...

    class TestFiltering:
        """필터링 관련 테스트"""
        def test_이상치_제거(self): ...
        def test_빈_데이터_처리(self): ...

    class TestAggregation:
        """집계 관련 테스트"""
        def test_평균_계산(self): ...
        def test_최대값_추출(self): ...
```

## 4. 실습 가이드

### 실습 1: conftest.py 확인

```bash
# conftest.py의 fixture가 테스트에서 사용되는지 확인
pytest test_data_processor.py -v

# fixture 목록 확인
pytest --fixtures
```

### 실습 2: 테스트 구조 분석

파일들을 열어보고 다음을 확인하세요:
- `conftest.py`에 정의된 fixture들
- `test_data_processor.py`에서 fixture를 사용하는 방법
- 클래스와 메서드의 네이밍 패턴

## 5. 연습 문제

### 연습 1: conftest.py fixture 작성
`exercises/exercise_04.py`에서 fixture를 정의하고 테스트에서 활용하세요.

### 연습 2: 테스트 구조 설계
예지보전 시스템의 "알람 모듈"에 대한 테스트 구조를 설계해보세요.
(클래스, 메서드 네이밍 등)

### 연습 3: 테스트 네이밍 개선
`test1`, `test_it_works` 같은 나쁜 이름을 의미 있는 이름으로 바꿔보세요.

## 6. 퀴즈

### Q1. conftest.py
`conftest.py`에 정의된 fixture는 어디에서 사용할 수 있나요?
- A) 같은 파일 내에서만
- B) 같은 디렉토리와 하위 디렉토리의 모든 테스트
- C) 프로젝트 전체
- D) import해야 사용 가능

**정답: B)** conftest.py의 fixture는 같은 디렉토리와 모든 하위
디렉토리에서 import 없이 자동으로 사용할 수 있습니다.

### Q2. 테스트 네이밍
다음 중 가장 좋은 테스트 메서드 이름은?
- A) `test1()`
- B) `test_it()`
- C) `test_overheating_detection_returns_true_when_above_80()`
- D) `testOverheatingDetection()`

**정답: C)** 테스트 이름은 무엇을 테스트하는지, 어떤 조건에서,
어떤 결과를 기대하는지 명확히 표현해야 합니다.

### Q3. fixture scope
비용이 큰 데이터베이스 연결을 전체 테스트 세션에서 한 번만 만들려면?
- A) `@pytest.fixture(scope="function")`
- B) `@pytest.fixture(scope="class")`
- C) `@pytest.fixture(scope="module")`
- D) `@pytest.fixture(scope="session")`

**정답: D)** `scope="session"`은 전체 테스트 세션에서 fixture를
한 번만 생성하고 공유합니다.

## 7. 정리 및 다음 주제 예고

### 이번 강의 핵심 정리
- 테스트 파일은 소스와 분리하여 `tests/` 디렉토리에 배치하는 것이 권장됨
- `test_`로 시작하는 파일/함수, `Test`로 시작하는 클래스가 pytest 규칙
- `conftest.py`는 같은 디렉토리와 하위 디렉토리에서 공유되는 fixture를 정의
- fixture의 scope(function, class, module, session)으로 생명주기를 제어
- 의미 있는 네이밍이 테스트 가독성과 유지보수성의 핵심

### 다음 주제 예고
**05. 예외와 에러 핸들링 테스트** - `pytest.raises()`를 깊이 있게 다루고,
커스텀 예외 클래스를 정의하고 테스트하는 방법을 배웁니다.
