# 레슨 14: Patching (패칭)

## 1. 학습 목표

이 레슨을 마치면 다음을 할 수 있습니다:

- `@patch` 데코레이터와 `patch()` 컨텍스트 매니저의 사용법을 익힌다
- `patch.object()`로 특정 객체의 메서드를 패치할 수 있다
- `patch.dict()`로 딕셔너리를 임시로 변경할 수 있다
- **WHERE to patch**: 어디를 패치해야 하는지 정확히 이해한다
- `datetime.now()` 패칭 등 흔한 실수를 피할 수 있다

## 2. 동기부여: 예지보전 관점

예지보전 리포트를 생성하는 시스템을 생각해 봅시다:

```python
# 리포트 생성 시 현재 시각이 필요함
report_date = datetime.now()

# 설정 값을 딕셔너리에서 읽음
threshold = config["temperature_threshold"]

# 외부 서비스를 호출함
result = external_api.get_predictions()
```

이런 코드를 테스트할 때의 문제:
- `datetime.now()`는 호출할 때마다 다른 값을 반환 → 결과가 불안정
- 설정 딕셔너리를 테스트용으로 바꾸고 싶지만 원본을 수정하면 안 됨
- 외부 API는 테스트 환경에서 사용할 수 없음

**Patching**은 이런 의존성을 테스트 실행 중에만 일시적으로 교체합니다.
테스트가 끝나면 자동으로 원래대로 복원됩니다.

## 3. 핵심 개념 설명

### 3.1 @patch 데코레이터

```python
from unittest.mock import patch

# 데코레이터로 패치: 테스트 함수에 Mock 객체가 인자로 전달됨
@patch('module_name.ClassName.method_name')
def test_something(mock_method):
    mock_method.return_value = 42
    # ... 테스트 코드 ...
```

### 3.2 patch() 컨텍스트 매니저

```python
from unittest.mock import patch

def test_something():
    # with 블록 안에서만 패치가 적용됨
    with patch('module_name.function_name') as mock_func:
        mock_func.return_value = 42
        result = module_name.function_name()
        assert result == 42
    # with 블록을 벗어나면 원래대로 복원됨
```

### 3.3 patch.object() - 객체 메서드 패치

```python
from unittest.mock import patch

class SensorReader:
    def read(self):
        return actual_sensor_value()

# 특정 클래스의 메서드를 패치
@patch.object(SensorReader, 'read', return_value=75.5)
def test_with_patched_read(mock_read):
    reader = SensorReader()
    assert reader.read() == 75.5
```

### 3.4 patch.dict() - 딕셔너리 패치

```python
from unittest.mock import patch

config = {"threshold": 80, "interval": 60}

# 딕셔너리의 값을 임시로 변경
@patch.dict(config, {"threshold": 100})
def test_with_different_threshold():
    assert config["threshold"] == 100  # 변경됨

# 테스트 후 원래 값으로 복원됨
assert config["threshold"] == 80
```

### 3.5 WHERE to patch (핵심!)

```python
# ===== src_reporter.py =====
from datetime import datetime

def create_report():
    now = datetime.now()  # datetime을 이 모듈에서 임포트
    return f"리포트 생성: {now}"

# ===== test_reporter.py =====
# 올바른 패치: datetime을 사용하는 모듈의 네임스페이스를 패치
@patch('src_reporter.datetime')  # ✅ 올바름!
def test_report(mock_datetime):
    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0)
    # ...

# 잘못된 패치: datetime 모듈 자체를 패치
@patch('datetime.datetime')  # ❌ 잘못됨! src_reporter에는 영향 없음
def test_report_wrong(mock_datetime):
    # src_reporter는 이미 datetime을 임포트했으므로
    # datetime 모듈을 패치해도 영향 없음
    pass
```

**핵심 규칙:**
> "패치 대상이 **정의된** 곳이 아니라, **사용되는(look up)** 곳을 패치하라"

### 3.6 datetime 패칭 패턴

```python
from unittest.mock import patch
from datetime import datetime

# 방법 1: 모듈 네임스페이스의 datetime 패치
@patch('src_reporter.datetime')
def test_report_date(mock_datetime):
    mock_datetime.now.return_value = datetime(2024, 6, 15, 10, 30)
    mock_datetime.side_effect = lambda *a, **kw: datetime(*a, **kw)
    # ...

# 방법 2: 별도 함수로 감싸서 패치
# src_reporter.py에 get_current_time() 함수를 만들고 그것을 패치
@patch('src_reporter.get_current_time')
def test_report_date_v2(mock_time):
    mock_time.return_value = datetime(2024, 6, 15, 10, 30)
    # ...
```

### 3.7 여러 패치를 동시에 적용

```python
# 데코레이터 순서 주의: 아래에서 위로 인자가 전달됨
@patch('module.ClassC')   # → mock_c (세 번째 인자)
@patch('module.ClassB')   # → mock_b (두 번째 인자)
@patch('module.ClassA')   # → mock_a (첫 번째 인자)
def test_multiple(mock_a, mock_b, mock_c):
    pass  # 순서 주의!

# 컨텍스트 매니저로 여러 패치
def test_multiple_context():
    with patch('module.A') as mock_a, \
         patch('module.B') as mock_b:
        # 둘 다 패치됨
        pass
```

## 4. 실습 가이드

### 프로젝트 구조
```
14_patching/
├── lesson.md
├── src_maintenance_reporter.py  # 소스 코드
├── test_patching_demo.py        # 패칭 데모
└── exercises/
    ├── exercise_14.py           # 연습 문제
    └── solution_14.py           # 풀이
```

### 실행 방법
```bash
pytest test_patching_demo.py -v
pytest exercises/exercise_14.py -v
pytest exercises/solution_14.py -v
```

## 5. 연습 문제

### 연습 1: datetime 패칭
`MaintenanceReporter.generate_report()`가 특정 날짜로 리포트를 생성하도록
`datetime.now()`를 패치하세요.

### 연습 2: 설정 딕셔너리 패칭
`patch.dict()`를 사용하여 임계값 설정을 변경하고,
변경된 설정에서 올바른 경고가 발생하는지 테스트하세요.

### 연습 3: 외부 서비스 패칭
외부 알림 서비스를 패치하여 알림 발송 동작을 검증하세요.
올바른 네임스페이스를 패치하는 것에 주의하세요.

## 6. 퀴즈

### 퀴즈 1
`@patch`로 패치할 때, 패치 대상을 어디로 지정해야 하는가?
- A) 패치 대상이 정의된 모듈
- B) 패치 대상이 사용되는(임포트된) 모듈
- C) 테스트 파일의 네임스페이스
- D) Python 내장 모듈

<details>
<summary>정답</summary>
B) 패치 대상이 사용되는(임포트된) 모듈의 네임스페이스를 지정해야 합니다.
예: `from datetime import datetime`으로 임포트한 모듈에서는
`'해당모듈.datetime'`으로 패치합니다.
</details>

### 퀴즈 2
여러 `@patch` 데코레이터를 사용할 때, Mock 인자의 순서는?
```python
@patch('module.C')
@patch('module.B')
@patch('module.A')
def test_func(mock_a, mock_b, mock_c):
    pass
```
위 코드에서 `mock_a`는 어떤 패치에 해당하는가?
- A) module.C
- B) module.B
- C) module.A
- D) 순서가 없음

<details>
<summary>정답</summary>
C) module.A. 데코레이터는 아래에서 위로 적용되므로,
가장 가까운 `@patch('module.A')`가 첫 번째 인자 `mock_a`에 매핑됩니다.
</details>

### 퀴즈 3
`patch.dict()`의 특징으로 올바른 것은?
- A) 딕셔너리를 영구적으로 변경한다
- B) 테스트 실행 중에만 딕셔너리를 변경하고, 끝나면 원래대로 복원한다
- C) 딕셔너리의 키만 변경할 수 있다
- D) 중첩 딕셔너리는 지원하지 않는다

<details>
<summary>정답</summary>
B) patch.dict()는 테스트 실행 중에만 딕셔너리를 변경하고,
테스트가 끝나면 자동으로 원래 값으로 복원합니다.
</details>

## 7. 정리 및 다음 주제 예고

### 이 레슨에서 배운 것
- **@patch 데코레이터**: 함수/클래스를 테스트 중에만 Mock으로 교체
- **patch() 컨텍스트 매니저**: with 블록 내에서만 패치 적용
- **patch.object()**: 특정 객체의 메서드/속성 패치
- **patch.dict()**: 딕셔너리를 임시로 변경
- **WHERE to patch**: 사용되는 곳의 네임스페이스를 패치
- **datetime 패칭**: 시간 의존 코드의 올바른 테스트 방법

### 다음 레슨 예고
**레슨 15: pytest-mock 플러그인**에서는 pytest의 `mocker` 픽스처를 통해
더 간결하고 Pythonic한 방식으로 목킹하는 방법을 학습합니다.
