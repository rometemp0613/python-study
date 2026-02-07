# 레슨 16: Monkeypatch

## 1. 학습 목표

이 레슨을 마치면 다음을 할 수 있습니다:

- `monkeypatch.setattr()`로 객체의 속성/메서드를 임시로 변경할 수 있다
- `monkeypatch.setenv()`/`delenv()`로 환경 변수를 조작할 수 있다
- `monkeypatch.setitem()`/`delitem()`으로 딕셔너리를 변경할 수 있다
- `monkeypatch.syspath_prepend()`와 `chdir()`를 활용할 수 있다
- `monkeypatch`와 `mock.patch`의 차이를 이해하고 적절히 선택할 수 있다

## 2. 동기부여: 예지보전 관점

예지보전 시스템의 설정은 다양한 소스에서 가져옵니다:

```
환경 변수:  SENSOR_API_URL, DB_HOST, ALERT_EMAIL
설정 파일:  config.yaml, thresholds.json
딕셔너리:  app_config["sensor"]["interval"]
클래스 속성: SensorConfig.DEFAULT_INTERVAL = 60
```

이런 설정들을 테스트에서 변경하려면:
- 실제 환경 변수를 바꾸면 다른 테스트에 영향
- 설정 파일을 수정하면 원래대로 복원 필요
- 클래스 속성을 바꾸면 전역 상태 오염

`monkeypatch`는 pytest의 내장 픽스처로, 테스트 중에 안전하게
값을 변경하고 테스트 후 자동으로 복원합니다.

## 3. 핵심 개념 설명

### 3.1 monkeypatch.setattr() - 속성 변경

```python
import os

class SensorConfig:
    DEFAULT_INTERVAL = 60
    API_TIMEOUT = 30

    @classmethod
    def get_interval(cls):
        return cls.DEFAULT_INTERVAL

def test_change_class_attribute(monkeypatch):
    """클래스 속성을 임시로 변경"""
    monkeypatch.setattr(SensorConfig, "DEFAULT_INTERVAL", 10)

    assert SensorConfig.DEFAULT_INTERVAL == 10
    assert SensorConfig.get_interval() == 10
    # 테스트 후 자동으로 60으로 복원됨

def test_change_function(monkeypatch):
    """함수를 임시로 대체"""
    monkeypatch.setattr(os.path, "exists", lambda path: True)

    # 어떤 경로든 존재한다고 반환
    assert os.path.exists("/nonexistent/path") is True
```

### 3.2 monkeypatch.setenv() / delenv() - 환경 변수

```python
def test_set_env_variable(monkeypatch):
    """환경 변수를 설정"""
    monkeypatch.setenv("SENSOR_API_URL", "http://test-api:8080")
    monkeypatch.setenv("DB_HOST", "localhost")

    import os
    assert os.environ["SENSOR_API_URL"] == "http://test-api:8080"
    assert os.environ["DB_HOST"] == "localhost"
    # 테스트 후 자동으로 원래 상태로 복원

def test_delete_env_variable(monkeypatch):
    """환경 변수를 삭제"""
    monkeypatch.setenv("TEMP_VAR", "value")  # 먼저 설정
    monkeypatch.delenv("TEMP_VAR")  # 삭제

    import os
    assert "TEMP_VAR" not in os.environ

def test_delete_env_with_raising(monkeypatch):
    """존재하지 않는 환경 변수 삭제 시 에러 무시"""
    # raising=False로 존재하지 않아도 에러 안 남
    monkeypatch.delenv("NONEXISTENT_VAR", raising=False)
```

### 3.3 monkeypatch.setitem() / delitem() - 딕셔너리

```python
config = {
    "temperature_threshold": 80.0,
    "vibration_threshold": 5.0,
    "check_interval": 60,
}

def test_change_dict_item(monkeypatch):
    """딕셔너리 항목을 임시로 변경"""
    monkeypatch.setitem(config, "temperature_threshold", 100.0)

    assert config["temperature_threshold"] == 100.0
    # 테스트 후 80.0으로 복원됨

def test_delete_dict_item(monkeypatch):
    """딕셔너리 항목을 임시로 삭제"""
    monkeypatch.delitem(config, "check_interval")

    assert "check_interval" not in config
    # 테스트 후 원래대로 복원됨
```

### 3.4 monkeypatch.syspath_prepend() / chdir()

```python
def test_add_to_sys_path(monkeypatch):
    """sys.path에 경로를 임시로 추가"""
    monkeypatch.syspath_prepend("/custom/module/path")

    import sys
    assert "/custom/module/path" in sys.path
    # 테스트 후 제거됨

def test_change_directory(monkeypatch, tmp_path):
    """작업 디렉토리를 임시로 변경"""
    monkeypatch.chdir(tmp_path)

    import os
    assert os.getcwd() == str(tmp_path)
    # 테스트 후 원래 디렉토리로 복원
```

### 3.5 monkeypatch vs mock.patch 비교

| 기능 | monkeypatch | mock.patch |
|------|------------|------------|
| 환경 변수 | `setenv()` / `delenv()` | `patch.dict(os.environ, ...)` |
| 딕셔너리 | `setitem()` / `delitem()` | `patch.dict(config, ...)` |
| 속성/메서드 | `setattr()` | `patch.object()` |
| 호출 추적 | X (불가) | O (Mock 객체 사용) |
| 반환값 제어 | 함수 대체만 | `return_value`, `side_effect` |
| 자동 복원 | O (픽스처) | O (데코레이터/컨텍스트) |
| 적합한 용도 | 설정, 환경 변수 | 행위 검증, 복잡한 목킹 |

**가이드라인:**
- 값을 바꾸기만 하면 되는 경우 → `monkeypatch`
- 호출 여부/인자를 검증해야 하는 경우 → `mock.patch`
- 환경 변수 조작 → `monkeypatch` (더 직관적)

## 4. 실습 가이드

### 프로젝트 구조
```
16_monkeypatch/
├── lesson.md
├── src_sensor_config.py       # 소스 코드
├── test_monkeypatch_demo.py   # Monkeypatch 데모
└── exercises/
    ├── exercise_16.py         # 연습 문제
    └── solution_16.py         # 풀이
```

### 실행 방법
```bash
pytest test_monkeypatch_demo.py -v
pytest exercises/exercise_16.py -v
pytest exercises/solution_16.py -v
```

## 5. 연습 문제

### 연습 1: 환경 변수로 API 설정 변경
`SensorConfig`가 환경 변수에서 API URL과 타임아웃을 읽도록 하고,
`monkeypatch.setenv()`로 테스트 환경의 설정을 변경하세요.

### 연습 2: 클래스 속성 패치
`SensorConfig.DEFAULT_INTERVAL`을 `monkeypatch.setattr()`로 변경하고,
변경된 값이 올바르게 사용되는지 테스트하세요.

### 연습 3: 설정 딕셔너리 조작
`SENSOR_THRESHOLDS` 딕셔너리의 항목을 `monkeypatch.setitem()`으로 변경하고,
변경된 임계값에서 올바른 상태가 반환되는지 테스트하세요.

## 6. 퀴즈

### 퀴즈 1
`monkeypatch`로 변경된 값은 언제 원래대로 복원되는가?
- A) 수동으로 복원해야 한다
- B) 테스트 함수가 끝나면 자동으로 복원된다
- C) 전체 테스트 세션이 끝난 후 복원된다
- D) Python 프로세스 종료 시 복원된다

<details>
<summary>정답</summary>
B) monkeypatch는 pytest 픽스처이므로, 테스트 함수가 끝나면
자동으로 변경된 값을 원래 상태로 복원합니다.
</details>

### 퀴즈 2
메서드가 올바른 인자로 호출되었는지 검증하고 싶을 때 적합한 도구는?
- A) monkeypatch만 사용
- B) mock.patch (또는 mocker.patch)
- C) 둘 다 동일하게 가능
- D) 어느 쪽도 불가능

<details>
<summary>정답</summary>
B) monkeypatch는 값을 바꾸는 데 특화되어 있고, 호출 추적 기능이 없습니다.
호출 여부와 인자를 검증하려면 Mock 객체를 사용하는 mock.patch가 적합합니다.
</details>

### 퀴즈 3
환경 변수를 테스트에서 조작할 때 `monkeypatch.setenv()`와
`patch.dict(os.environ, ...)` 중 어떤 것이 더 권장되는가?
- A) monkeypatch.setenv() - 더 직관적이고 pytest 스타일
- B) patch.dict(os.environ) - 더 강력함
- C) 차이 없음
- D) 환경 변수는 테스트에서 조작하면 안 됨

<details>
<summary>정답</summary>
A) pytest를 사용한다면 monkeypatch.setenv()가 더 직관적이고 간결합니다.
기능적으로는 둘 다 동일하게 동작하며 자동 복원도 됩니다.
</details>

## 7. 정리 및 다음 주제 예고

### 이 레슨에서 배운 것
- **setattr()**: 객체의 속성/메서드를 임시로 변경
- **setenv()/delenv()**: 환경 변수 조작
- **setitem()/delitem()**: 딕셔너리 항목 변경/삭제
- **syspath_prepend()/chdir()**: 시스템 경로 조작
- **monkeypatch vs mock.patch**: 용도에 따른 선택 기준

### 다음 레슨 예고
**Phase 4: 실전 테스트**로 넘어가서 pandas/numpy 데이터, 파일 I/O,
API 통신, 환경 설정, ML 모델 등 실제 시스템 컴포넌트의
테스트 방법을 학습합니다.
