# 06. 모듈, 패키지 & 타입 힌트

## 핵심 개념

### 모듈 (Module) = Python 파일 하나

```python
# sensor.py ← 이 파일 자체가 "sensor" 모듈
def read_temperature(sensor_id):
    return 72.5

MAX_TEMP = 100.0
```

### 패키지 (Package) = `__init__.py`가 있는 폴더

```
equipment/              ← 패키지
├── __init__.py         ← "이 폴더는 패키지입니다" (간판)
├── sensor.py           ← 모듈
├── alarm.py            ← 모듈
└── analysis/           ← 서브 패키지
    ├── __init__.py
    └── vibration.py
```

- `__init__.py`가 없으면 Python이 폴더를 패키지로 인식 못함
- 비어 있어도 됨 (간판 역할만)
- 편의 import를 등록하면 더 짧게 사용 가능

---

## import 방식 4가지

```python
# 방법 1: 모듈 전체 (가장 안전, 출처 명확)
import sensor
sensor.read_temperature("M-001")

# 방법 2: 특정 함수만
from sensor import read_temperature
read_temperature("M-001")

# 방법 3: 여러 개
from sensor import read_temperature, read_vibration, MAX_TEMP

# 방법 4: 별명 (긴 이름일 때)
import sensor as sn
sn.read_temperature("M-001")

# ⚠️ 금지: 전부 가져오기 (이름 충돌 위험!)
from sensor import *
```

### `from X import *`가 위험한 이유

```python
from equipment import *         # read_temperature 가져옴
from weather_station import *   # 여기도 read_temperature가 있으면?!
read_temperature("M-001")       # 어떤 건지 모름! 나중 거가 덮어씀
```

| 방식 | 출처 | 안전성 |
|------|------|--------|
| `import equipment` | `equipment.함수명` → 출처 명확 | 안전 |
| `from equipment import 함수명` | import문에서 확인 가능 | 괜찮음 |
| `from equipment import *` | 어디서 왔는지 모름 | 위험 |

---

## `__init__.py` 활용

### 빈 파일 (기본)

```python
# __init__.py (빈 파일)
# → from equipment.sensor import read_temperature  (모듈명까지 적어야 함)
```

### 편의 등록

```python
# __init__.py
from .sensor import read_temperature, read_vibration
from .alarm import check_temperature, check_pressure

# → from equipment import read_temperature  (더 짧게!)
```

- `.sensor`의 `.`(점) = "같은 패키지 안에 있는" (상대 임포트)
- **새 함수를 모듈에 추가하면 `__init__.py`에도 등록해야** 패키지 레벨에서 사용 가능

---

## `if __name__ == "__main__":` 패턴

```python
# sensor.py
def read_temperature(sensor_id):
    return 72.5

if __name__ == "__main__":
    # 테스트용 코드
    print(read_temperature("TEST-001"))
```

| 상황 | `__name__` 값 | 테스트 코드 실행? |
|------|-------------|-----------------|
| `python sensor.py` (직접 실행) | `"__main__"` | 실행됨 |
| `import sensor` (다른 파일에서) | `"sensor"` | 실행 안 됨 |

→ 모듈 안에 테스트 코드를 넣되, import 시에는 실행 안 되게 하는 패턴

---

## 타입 힌트 (Type Hints)

### 기본 사용법

```python
# 타입 힌트 없이
def check_alarm(temp, threshold):
    return temp > threshold

# 타입 힌트 있이
def check_alarm(temp: float, threshold: float) -> bool:
    return temp > threshold
# 읽는 법: "float 2개 받고, bool 반환"
```

### 변수에도 사용 가능

```python
name: str = "Motor-001"
temp: float = 72.5
count: int = 10
is_running: bool = True
```

### 복잡한 타입 (typing 모듈)

```python
from typing import Optional, Union

# Optional: 값이 있거나 None
def find_sensor(sensor_id: str) -> Optional[dict]:
    return sensors.get(sensor_id)   # dict 또는 None

# Union: 여러 타입 중 하나
def process(value: Union[int, float]) -> float:
    return float(value)

# Python 3.10+ 간편 문법
def process(value: int | float) -> float:   # | 로 대체
    return float(value)
```

### 핵심 포인트

```
┌──────────────────────────────────────────┐
│  타입 힌트는 "힌트"일 뿐, 강제가 아님!     │
│  - 실행 시: Python이 체크 안 함            │
│  - 개발 시: VS Code 자동완성 & 경고        │
│  - 검사 도구: mypy로 실행 전 타입 오류 탐지  │
└──────────────────────────────────────────┘
```

---

## 코드/함수 정리표

| 문법 | 설명 | 예시 |
|------|------|------|
| `import X` | 모듈 전체 가져오기 | `import sensor` |
| `from X import Y` | 특정 항목만 | `from sensor import read_temperature` |
| `import X as 별명` | 별명 붙이기 | `import numpy as np` |
| `from .X import Y` | 상대 임포트 (패키지 내부) | `from .sensor import read_temperature` |
| `__init__.py` | 폴더를 패키지로 만드는 파일 | 비어 있어도 OK |
| `__name__` | 모듈 이름 (직접 실행 시 `"__main__"`) | `if __name__ == "__main__":` |
| `x: int` | 타입 힌트 (변수) | `count: int = 10` |
| `-> bool` | 타입 힌트 (반환값) | `def f() -> bool:` |
| `Optional[X]` | X 또는 None | `Optional[dict]` |
| `Union[X, Y]` / `X \| Y` | 여러 타입 중 하나 | `Union[int, float]` |

---

## 주의사항 & 흔한 실수

1. **`__init__.py` 깜빡함**: 모듈에 함수 추가 후 `__init__.py` 업데이트 안 하면 `ImportError` 발생
2. **`from X import *` 사용**: 이름 충돌 + 출처 불명 → 실무에서 금지
3. **타입 힌트 = 강제가 아님**: 잘못된 타입 넣어도 에러 안 남. `mypy`로 별도 검사 필요
4. **상대 임포트 위치**: `.`으로 시작하는 import는 패키지 안(`__init__.py`가 있는 곳)에서만 사용 가능
