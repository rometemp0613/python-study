# 07. Fixture 심화

## 1. 학습 목표

- pytest fixture의 다양한 스코프(function, class, module, session)를 이해하고 적용한다
- yield fixture를 사용하여 설정(setup)과 정리(teardown)를 관리한다
- factory fixture 패턴으로 동적 테스트 데이터를 생성한다
- parametrize된 fixture로 여러 시나리오를 자동 테스트한다
- autouse fixture와 fixture 의존성 체인을 활용한다
- conftest.py를 통해 fixture를 프로젝트 전체에서 공유한다

## 2. 동기부여: 예지보전 관점

공장 설비 예지보전 시스템에서는 센서 데이터베이스, 장비 설정, 네트워크 연결 등
다양한 리소스를 테스트해야 합니다. 매 테스트마다 데이터베이스를 새로 만들고 삭제하는 것은
비효율적입니다.

Fixture를 활용하면:
- **센서 DB 연결**을 테스트 세션 동안 한 번만 생성
- **테스트 데이터**를 각 테스트 함수마다 깨끗한 상태로 제공
- **장비 설정**을 여러 시나리오로 자동 반복 테스트
- **리소스 정리**를 자동화하여 메모리 누수 방지

## 3. 핵심 개념 설명

### 3.1 Fixture 기본 복습

```python
import pytest

@pytest.fixture
def sensor_reading():
    """단일 센서 읽기값을 제공하는 fixture"""
    return {"sensor_id": "TEMP-001", "value": 72.5, "unit": "°C"}

def test_sensor_has_id(sensor_reading):
    assert "sensor_id" in sensor_reading
```

### 3.2 Fixture 스코프 (Scope)

스코프는 fixture가 생성되고 소멸되는 범위를 결정합니다.

| 스코프 | 설명 | 사용 예 |
|--------|------|---------|
| `function` | 각 테스트 함수마다 (기본값) | 개별 센서 읽기값 |
| `class` | 테스트 클래스마다 | 클래스 내 공유 설정 |
| `module` | 모듈(파일)마다 | 모듈 내 공유 DB |
| `session` | 전체 테스트 세션마다 | DB 연결, 서버 설정 |

```python
@pytest.fixture(scope="module")
def sensor_database():
    """모듈 단위로 공유되는 센서 데이터베이스"""
    db = SensorDatabase()
    db.initialize()
    return db

@pytest.fixture(scope="session")
def db_connection():
    """전체 테스트 세션에서 한 번만 생성되는 DB 연결"""
    conn = create_connection()
    return conn
```

### 3.3 Yield Fixture (설정과 정리)

`yield`를 사용하면 fixture의 설정(setup)과 정리(teardown)를 한 곳에 작성할 수 있습니다.

```python
@pytest.fixture
def sensor_db():
    """설정과 정리가 포함된 센서 DB fixture"""
    # === 설정 (Setup) ===
    db = SensorDatabase()
    db.initialize()

    yield db  # 테스트에 db 제공

    # === 정리 (Teardown) ===
    db.clear()
    db.close()
```

### 3.4 Factory Fixture

동적으로 다양한 테스트 데이터를 생성해야 할 때 factory 패턴을 사용합니다.

```python
@pytest.fixture
def make_sensor_reading():
    """센서 읽기값을 동적으로 생성하는 팩토리 fixture"""
    def _make(sensor_id="TEMP-001", value=25.0, status="normal"):
        return SensorReading(
            sensor_id=sensor_id,
            value=value,
            timestamp=datetime.now(),
            status=status
        )
    return _make

def test_multiple_readings(make_sensor_reading):
    normal = make_sensor_reading(value=25.0, status="normal")
    warning = make_sensor_reading(value=85.0, status="warning")
    assert normal.status != warning.status
```

### 3.5 Parametrized Fixture

fixture 자체를 매개변수화하여 여러 시나리오를 자동 테스트합니다.

```python
@pytest.fixture(params=["TEMP-001", "VIBR-002", "PRESS-003"])
def sensor_id(request):
    """여러 센서 ID로 자동 반복 테스트"""
    return request.param

def test_sensor_id_format(sensor_id):
    # 3번 실행됨 (각 센서 ID마다)
    parts = sensor_id.split("-")
    assert len(parts) == 2
```

### 3.6 Autouse Fixture

`autouse=True`로 설정하면 명시적으로 요청하지 않아도 자동 적용됩니다.

```python
@pytest.fixture(autouse=True)
def reset_warning_counter():
    """매 테스트 전에 경고 카운터를 자동 초기화"""
    WarningSystem.reset()
    yield
    # 정리 코드도 가능
```

### 3.7 Fixture 의존성 체인

fixture는 다른 fixture를 의존성으로 사용할 수 있습니다.

```python
@pytest.fixture
def sensor_db():
    return SensorDatabase()

@pytest.fixture
def populated_db(sensor_db):
    """sensor_db에 데이터를 추가한 fixture"""
    sensor_db.add_reading("TEMP-001", 25.0)
    sensor_db.add_reading("TEMP-001", 26.0)
    return sensor_db

def test_average(populated_db):
    avg = populated_db.get_average("TEMP-001")
    assert avg == 25.5
```

### 3.8 conftest.py

`conftest.py`에 fixture를 정의하면 해당 디렉토리와 하위 디렉토리의 모든 테스트에서 사용할 수 있습니다.

```
project/
├── conftest.py          # 프로젝트 전체 공유 fixture
├── tests/
│   ├── conftest.py      # tests/ 하위 공유 fixture
│   ├── unit/
│   │   ├── conftest.py  # unit 테스트 전용 fixture
│   │   └── test_*.py
│   └── integration/
│       ├── conftest.py
│       └── test_*.py
```

## 4. 실습 가이드

### 실습 1: 스코프 확인

`test_fixtures_demo.py`를 실행하여 각 스코프에서 fixture가 몇 번 호출되는지 확인하세요.

```bash
pytest test_fixtures_demo.py -v -s
```

`-s` 옵션으로 print 출력을 확인할 수 있습니다.

### 실습 2: Yield Fixture

센서 데이터베이스의 설정과 정리가 올바르게 이루어지는지 확인하세요.

```bash
pytest test_fixtures_demo.py::test_yield_fixture_cleanup -v -s
```

### 실습 3: Factory Fixture

팩토리 fixture로 다양한 센서 데이터를 생성하는 테스트를 실행하세요.

```bash
pytest test_fixtures_demo.py -k "factory" -v
```

## 5. 연습 문제

### 연습 1: 장비 상태 fixture
장비 상태(정상, 경고, 위험)에 따라 parametrize된 fixture를 만들고,
각 상태에 맞는 동작을 테스트하세요.

### 연습 2: 데이터 생성 factory
센서 읽기값을 생성하는 factory fixture를 만들고, 정상/비정상 데이터를
모두 생성하여 이상 탐지 로직을 테스트하세요.

### 연습 3: fixture 의존성 체인
DB 연결 → 테이블 생성 → 데이터 삽입의 의존성 체인을 fixture로 구성하세요.

## 6. 퀴즈

### Q1. fixture 스코프
다음 중 fixture가 테스트 세션 전체에서 한 번만 생성되게 하는 스코프는?

A) `scope="function"`
B) `scope="module"`
C) `scope="session"`
D) `scope="global"`

**정답: C** - `scope="session"`은 전체 테스트 세션에서 한 번만 생성됩니다.

### Q2. yield fixture
yield fixture에서 `yield` 이후의 코드는 언제 실행되나요?

A) fixture가 생성될 때
B) 테스트가 시작될 때
C) 테스트가 끝난 후 (정리 단계)
D) 모든 테스트가 끝난 후

**정답: C** - yield 이후의 코드는 해당 스코프의 정리(teardown) 단계에서 실행됩니다.

### Q3. conftest.py
conftest.py에 대한 설명으로 틀린 것은?

A) import 없이 자동으로 fixture를 사용할 수 있다
B) 여러 계층에 conftest.py를 둘 수 있다
C) conftest.py는 반드시 프로젝트 루트에만 위치해야 한다
D) conftest.py에 hook 함수도 정의할 수 있다

**정답: C** - conftest.py는 어느 디렉토리에든 위치할 수 있으며, 해당 디렉토리와 하위에서 적용됩니다.

## 7. 정리 및 다음 주제 예고

### 이번 단원 정리
- fixture **스코프**로 생성/소멸 범위를 제어한다
- **yield fixture**로 설정과 정리를 깔끔하게 관리한다
- **factory fixture**로 동적 테스트 데이터를 생성한다
- **parametrized fixture**로 여러 시나리오를 자동 테스트한다
- **autouse**로 전체 테스트에 자동 적용되는 fixture를 만든다
- **conftest.py**로 fixture를 프로젝트 전체에서 공유한다

### 다음 주제: 08. Parametrize
다음 단원에서는 `@pytest.mark.parametrize`를 사용하여 하나의 테스트 함수를
다양한 입력값과 기대 결과로 반복 실행하는 방법을 배웁니다.
센서 이상 탐지의 다양한 경계값을 효율적으로 테스트할 수 있습니다.
