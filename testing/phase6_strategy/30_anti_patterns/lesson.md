# 30. 테스트 안티패턴

## 학습 목표
- 일반적인 테스트 안티패턴을 식별할 수 있다
- 구현 결합(implementation coupling)의 문제점을 이해한다
- 과도한 모킹의 위험성을 인식한다
- Ice cream cone 안티패턴과 테스트 피라미드를 비교할 수 있다
- 테스트 오염과 느린 테스트 스위트의 해결 방법을 익힌다

## 동기부여: 예지보전 관점

예지보전 시스템이 성장하면서 테스트 코드도 함께 증가합니다. 안티패턴이 쌓이면:
- **리팩토링이 두려워집니다** (테스트가 구현에 결합되어 있어서)
- **테스트 스위트가 느려집니다** (불필요한 통합 테스트가 많아서)
- **테스트 유지보수 비용이 증가합니다** (과도한 모킹으로 테스트가 복잡해서)
- **허위 보안감**이 생깁니다 (프레임워크를 테스트하고 있어서)

안티패턴을 알면 피할 수 있습니다.

## 핵심 개념

### 1. 구현 결합 (Implementation Coupling)

테스트가 내부 구현에 의존하면, 구현을 변경할 때마다 테스트도 수정해야 합니다.

```python
# 안티패턴: 내부 구현에 결합
def test_구현결합():
    service = DataService()
    service.get_sensor_data("sensor-001")
    # 내부 캐시 구조에 의존
    assert "sensor-001" in service._cache
    assert isinstance(service._cache["sensor-001"], list)

# 개선: 동작(behavior)을 테스트
def test_동작테스트():
    service = DataService()
    data = service.get_sensor_data("sensor-001")
    assert data is not None
    assert len(data) > 0
```

### 2. 과도한 모킹 (Excessive Mocking)

모든 의존성을 모킹하면 테스트가 실제 동작을 반영하지 못합니다.

```python
# 안티패턴: 모든 것을 모킹
def test_과도한_모킹(mocker):
    mock_get = mocker.patch.object(DataService, 'get_sensor_data', return_value=[1, 2, 3])
    mock_process = mocker.patch.object(DataService, 'process_data', return_value={"mean": 2})
    mock_save = mocker.patch.object(DataService, 'save_results', return_value=True)

    service = DataService()
    # 실제로는 아무것도 테스트하지 않음 - 모킹된 반환값만 확인
    result = service.get_sensor_data("sensor-001")
    assert result == [1, 2, 3]

# 개선: 필요한 것만 모킹 (외부 의존성)
def test_적절한_모킹(mocker):
    # 외부 저장소만 모킹 (내부 로직은 실제로 실행)
    mocker.patch.object(DataService, '_storage', create=True)
    service = DataService()
    data = [100.0, 200.0, 300.0]
    result = service.process_data(data)
    assert result["mean"] == 200.0  # 실제 로직 검증
```

### 3. Ice Cream Cone (아이스크림 콘)

```
올바른 테스트 피라미드:        아이스크림 콘 (안티패턴):

        /\                      ___________
       /E2E\                   |   E2E     |  ← 많음 (느림)
      /______\                 |___________|
     /통합 테스트\               |  통합     |  ← 중간
    /____________\             |___________|
   / 단위 테스트   \            |  단위     |  ← 적음
  /________________\           |___________|
   많음 (빠름)                  적음 (빠름)
```

단위 테스트가 적고 E2E 테스트가 많으면 테스트 스위트가 느려집니다.

### 4. 테스트 오염 (Test Pollution)

```python
# 안티패턴: 전역 상태 변경
_global_config = {"threshold": 100}

def test_오염_원인():
    _global_config["threshold"] = 50  # 전역 상태 변경
    assert _global_config["threshold"] == 50

def test_오염_피해자():
    # 위 테스트에 의해 threshold가 50으로 변경됨
    assert _global_config["threshold"] == 100  # 실패!

# 개선: 로컬 상태 사용
def test_독립적():
    local_config = {"threshold": 100}
    local_config["threshold"] = 50
    assert local_config["threshold"] == 50
```

### 5. 느린 테스트 스위트

```python
# 안티패턴: 불필요하게 느린 테스트
def test_느린_테스트():
    import time
    time.sleep(1)  # 네트워크 대기 시뮬레이션
    service = DataService()
    result = service.get_sensor_data("sensor-001")
    assert result is not None

# 개선: 외부 의존성을 모킹하여 빠르게
def test_빠른_테스트():
    service = DataService()
    result = service.process_data([100, 200, 300])
    assert result["mean"] == 200.0
```

### 6. 프레임워크 테스트 (Testing the Framework)

자신의 코드가 아닌 프레임워크/라이브러리를 테스트하는 것은 낭비입니다.

```python
# 안티패턴: Python 내장 기능을 테스트
def test_프레임워크_테스트():
    data = [1, 2, 3]
    assert len(data) == 3
    assert sum(data) == 6
    assert sorted(data) == [1, 2, 3]

# 개선: 자신의 비즈니스 로직을 테스트
def test_비즈니스_로직():
    service = DataService()
    result = service.process_data([100, 200, 300])
    assert result["mean"] == 200.0
    assert result["anomaly_count"] == 0
```

## 실습 가이드

### 실습 1: 안티패턴 식별

`test_anti_patterns.py`를 확인하세요. 각 안티패턴과 개선된 버전이 쌍으로 제시됩니다.

```bash
pytest test_anti_patterns.py -v
```

### 실습 2: 안티패턴 수정 연습

`exercises/exercise_30.py`에서 안티패턴을 식별하고 수정하세요.

## 연습 문제

### 연습 1: 구현 결합 제거
내부 구현에 의존하는 테스트를 동작 기반 테스트로 변경하세요.

### 연습 2: 과도한 모킹 줄이기
불필요한 모킹을 제거하고 실제 로직이 테스트되도록 수정하세요.

### 연습 3: 안티패턴 수정 (exercises/exercise_30.py)
다양한 안티패턴이 있는 테스트를 수정하세요.

## 퀴즈

### Q1. 구현 결합의 가장 큰 문제점은?
- A) 테스트 실행이 느려진다
- B) 리팩토링 시 테스트를 수정해야 한다
- C) 코드 커버리지가 낮아진다
- D) 테스트 파일이 커진다

**정답: B**
내부 구현에 결합된 테스트는 코드를 리팩토링할 때마다 함께 수정해야 하므로, 리팩토링을 어렵게 만듭니다.

### Q2. 테스트 피라미드에서 가장 많아야 하는 테스트는?
- A) E2E 테스트
- B) 통합 테스트
- C) 단위 테스트
- D) 수동 테스트

**정답: C**
테스트 피라미드의 기반은 빠르고 많은 단위 테스트입니다.

### Q3. 과도한 모킹의 위험은?
- A) 테스트가 느려진다
- B) 실제 동작을 테스트하지 못한다
- C) 모킹 라이브러리가 에러를 발생시킨다
- D) 커버리지가 100%가 된다

**정답: B**
모든 것을 모킹하면 모킹된 반환값만 확인하게 되어, 실제 로직의 버그를 놓칠 수 있습니다.

## 정리 및 다음 주제 예고

### 이번 레슨 정리
- **구현 결합**: 내부 구현이 아닌 동작을 테스트하자
- **과도한 모킹**: 외부 의존성만 모킹하고, 내부 로직은 실제로 실행
- **Ice Cream Cone**: 단위 테스트를 충분히, E2E 테스트는 핵심만
- **테스트 오염**: 테스트 간 상태를 공유하지 말자
- **프레임워크 테스트**: 자신의 코드만 테스트하자

### 다음 주제: 31. CI/CD 통합
테스트를 CI/CD 파이프라인에 통합하여 자동화하는 방법을 알아봅니다.
