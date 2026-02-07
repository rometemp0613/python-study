# 29. Flaky 테스트 다루기

## 학습 목표
- Flaky 테스트의 정의와 위험성을 이해한다
- 일반적인 Flaky 테스트 원인을 파악할 수 있다
- Flaky 테스트를 진단하는 도구를 사용할 수 있다
- 각 원인별 해결 방법을 적용할 수 있다

## 동기부여: 예지보전 관점

예지보전 시스템의 CI/CD 파이프라인에서 테스트가 불안정하면:
- **배포가 지연**됩니다 (테스트 실패 → 재실행 → 시간 낭비)
- **신뢰도가 하락**합니다 (팀원들이 테스트 실패를 무시하기 시작)
- **실제 버그를 놓칩니다** ("또 flaky 테스트겠지"라고 생각)
- **개발 생산성이 저하**됩니다

센서 데이터를 다루는 시스템에서는 시간, 부동소수점, 랜덤 값 등이
flaky 테스트의 주요 원인이 됩니다.

## 핵심 개념

### 1. Flaky 테스트란?

같은 코드에 대해 **때때로 통과하고, 때때로 실패**하는 테스트입니다.
코드 변경 없이 테스트 결과가 달라집니다.

### 2. 주요 원인과 해결 방법

#### 원인 1: 현재 시간(datetime) 의존

```python
# 문제: 현재 시간에 따라 결과가 달라짐
def test_flaky_시간의존():
    monitor = SensorMonitor()
    # 현재 시간이 포함되어 결과가 매번 달라질 수 있음
    result = monitor.format_timestamp(datetime.now())
    assert "2024" in result  # 2025년이 되면 실패!

# 해결: 고정된 시간을 주입
def test_fixed_시간고정():
    monitor = SensorMonitor()
    fixed_time = datetime(2024, 6, 15, 10, 30, 0)
    result = monitor.format_timestamp(fixed_time)
    assert result == "2024-06-15 10:30:00"
```

#### 원인 2: 부동소수점 비교

```python
# 문제: 부동소수점 정밀도 차이로 실패
def test_flaky_부동소수점():
    readings = [0.1, 0.2, 0.3]
    total = sum(readings)
    assert total == 0.6  # 실제로는 0.6000000000000001

# 해결: pytest.approx 사용
def test_fixed_부동소수점():
    readings = [0.1, 0.2, 0.3]
    total = sum(readings)
    assert total == pytest.approx(0.6)  # 허용 오차 내에서 비교
```

#### 원인 3: 테스트 오염 (Test Pollution)

```python
# 문제: 이전 테스트가 전역 상태를 변경
shared_data = []

def test_flaky_오염1():
    shared_data.append("data")
    assert len(shared_data) == 1  # 실행 순서에 따라 달라짐

def test_flaky_오염2():
    assert len(shared_data) == 0  # 위 테스트가 먼저 실행되면 실패

# 해결: 각 테스트에서 상태를 초기화
def test_fixed_독립1():
    local_data = []
    local_data.append("data")
    assert len(local_data) == 1

def test_fixed_독립2():
    local_data = []
    assert len(local_data) == 0
```

#### 원인 4: 외부 서비스 의존

```python
# 문제: 네트워크 상태에 따라 실패
def test_flaky_외부서비스():
    response = requests.get("https://api.example.com/sensor/data")
    assert response.status_code == 200

# 해결: Mock 사용
def test_fixed_모킹(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mocker.patch("requests.get", return_value=mock_response)

    response = requests.get("https://api.example.com/sensor/data")
    assert response.status_code == 200
```

#### 원인 5: 타이밍/순서 의존

```python
# 문제: 딕셔너리 순서에 의존 (Python 3.7+ 에서는 삽입 순서 보장이지만
# 세트나 다른 자료구조에서는 여전히 문제)
def test_flaky_순서의존():
    data = {1, 2, 3}  # 세트는 순서가 보장되지 않음
    result = list(data)
    assert result == [1, 2, 3]  # 순서 불일정

# 해결: 정렬 후 비교
def test_fixed_정렬비교():
    data = {1, 2, 3}
    result = sorted(data)
    assert result == [1, 2, 3]
```

### 3. Flaky 테스트 진단 도구

#### pytest-randomly: 테스트 순서를 무작위화
```bash
pip install pytest-randomly
pytest --randomly-seed=12345  # 특정 시드로 재현
```

#### pytest-repeat: 테스트를 반복 실행
```bash
pip install pytest-repeat
pytest --count=10  # 10번 반복 실행
pytest --count=10 -x  # 실패 시 중단
```

#### pytest-flakefinder: flaky 테스트 탐지
```bash
pip install pytest-flakefinder
pytest --flake-finder --flake-runs=50
```

### 4. 센서 데이터에서의 Flaky 테스트

센서 데이터를 다루는 시스템에서 특히 주의할 점:

```python
# 센서 드리프트 계산에서의 부동소수점 문제
def test_센서_드리프트():
    monitor = SensorMonitor()
    readings = [100.0, 100.1, 100.2, 100.3, 100.4]
    drift = monitor.calculate_drift(readings)
    # pytest.approx로 비교
    assert drift == pytest.approx(0.1, abs=0.01)
```

## 실습 가이드

### 실습 1: Flaky 테스트 확인과 수정

`test_flaky_examples.py`를 확인하세요. 원래 flaky했던 테스트가 어떻게 수정되었는지 볼 수 있습니다.

```bash
pytest test_flaky_examples.py -v
```

### 실습 2: Flaky 테스트 수정 연습

`exercises/exercise_29.py`에서 flaky 테스트를 수정하세요.

## 연습 문제

### 연습 1: 시간 의존 테스트 수정
현재 시간에 의존하는 테스트를 고정 시간으로 수정하세요.

### 연습 2: 부동소수점 비교 수정
정확한 동등 비교를 pytest.approx로 수정하세요.

### 연습 3: Flaky 테스트 수정 (exercises/exercise_29.py)
다양한 원인의 flaky 테스트를 수정하세요.

## 퀴즈

### Q1. 다음 중 flaky 테스트의 가장 큰 위험은?
- A) 테스트 실행 속도가 느려진다
- B) 팀이 테스트 실패를 무시하게 되어 실제 버그를 놓친다
- C) 코드 커버리지가 낮아진다
- D) 테스트 파일 크기가 커진다

**정답: B**
Flaky 테스트가 많으면 "또 그거겠지"라며 실패를 무시하게 되고, 실제 버그도 놓치게 됩니다.

### Q2. 부동소수점 비교 문제를 해결하는 pytest 기능은?
- A) pytest.mark.float
- B) pytest.approx
- C) pytest.compare
- D) pytest.float_equal

**정답: B**
`pytest.approx(expected, abs=tolerance)`로 허용 오차 내에서 비교합니다.

### Q3. 테스트 순서 의존성을 찾는 데 유용한 도구는?
- A) pytest-cov
- B) pytest-randomly
- C) pytest-benchmark
- D) pytest-html

**정답: B**
pytest-randomly는 테스트 실행 순서를 무작위화하여 순서 의존성을 발견할 수 있게 합니다.

## 정리 및 다음 주제 예고

### 이번 레슨 정리
- **Flaky 테스트**: 같은 코드에 대해 결과가 달라지는 불안정한 테스트
- **주요 원인**: 시간 의존, 부동소수점, 테스트 오염, 외부 서비스, 순서 의존
- **진단 도구**: pytest-randomly, pytest-repeat
- **핵심 해결법**: 시간 주입, pytest.approx, 테스트 독립성 확보, Mock 사용

### 다음 주제: 30. 테스트 안티패턴
테스트 코드에서 피해야 할 안티패턴들을 체계적으로 알아봅니다.
