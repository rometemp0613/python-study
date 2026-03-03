# 04. 테스트 구조와 프로젝트 조직

## 프로젝트 레이아웃

### tests/ 분리형 (권장)

```
project/
├── src/                    # 프로덕션 코드
│   └── predictive/
│       ├── __init__.py
│       ├── sensor.py
│       └── alarm.py
├── tests/                  # 테스트 코드
│   ├── conftest.py         # 공통 fixture
│   ├── unit/
│   │   ├── conftest.py     # unit 전용 fixture
│   │   └── test_sensor.py
│   └── integration/
│       └── test_pipeline.py
└── pyproject.toml
```

- 프로덕션/테스트 분리 → 관리 쉬움, 배포 시 테스트 제외 가능
- `pytest tests/unit/ -v`로 단위 테스트만 실행 가능

---

## 네이밍 컨벤션

| 대상 | 규칙 | 예시 |
|------|------|------|
| 파일 | `test_*.py` 또는 `*_test.py` | `test_sensor.py` |
| 함수 | `test_`로 시작 | `test_alarm_when_hot()` |
| 클래스 | `Test`로 시작, **`__init__` 없어야 함** | `TestSensor` |
| fixture | 명사형 | `sample_readings` |

### 좋은 테스트 이름 패턴

```python
# test_[대상]_[상황]_[기대결과]
def test_alarm_when_temp_over_80_returns_danger(): ...
def test_sensor_with_negative_value_raises_error(): ...
```

### 발견 안 되는 것들

```python
alarm_tests.py          # ❌ tests 복수형
check_alarm.py          # ❌ test_ 없음
class SensorTest:       # ❌ Test로 시작 안 함
class TestSensor:       # ❌ __init__ 있으면 발견 안 됨
    def __init__(self): pass
```

---

## conftest.py

**같은 디렉토리 + 하위 디렉토리**에서 import 없이 자동 사용 가능.

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_vibration():
    return [0.5, 1.2, 0.8, 3.5, 0.6]

@pytest.fixture
def sensor_config():
    return {"threshold": 2.0, "unit": "mm/s"}
```

```python
# tests/test_sensor.py — import 없이 fixture 사용!
def test_vibration_alert(sample_vibration, sensor_config):
    threshold = sensor_config["threshold"]
    alerts = [v for v in sample_vibration if v > threshold]
    assert len(alerts) == 1
```

### 핵심 규칙

| 규칙 | 설명 |
|------|------|
| import 불필요 | 자동 발견 |
| 계층 구조 | 하위 conftest가 상위를 오버라이드 |
| 여러 개 가능 | 폴더마다 하나씩 |

---

## fixture scope

```python
@pytest.fixture(scope="function")   # 기본: 각 테스트마다
@pytest.fixture(scope="class")      # 클래스마다
@pytest.fixture(scope="module")     # 파일마다
@pytest.fixture(scope="session")    # 전체 테스트에서 한 번
```

비용 큰 리소스(DB 연결 등)는 scope을 넓게!

---

## pyproject.toml 설정

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"    # 매번 자동 적용
```

---

## 주의사항 & 흔한 실수

- **fixture를 인자로 안 넣음**: `def test_xxx(self, my_fixture)` ← 인자로 넣어야 pytest가 주입
- **클래스 변수 접근 시 `self.` 빠뜨림**: 클래스 안에서 정의한 변수는 `self.변수명`으로 접근
- **Test 클래스에 `__init__` 넣으면** pytest가 테스트로 인식 안 함
- **`alarm_tests.py`** (복수형 s) → 발견 안 됨!
