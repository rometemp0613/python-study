# 27. TDD (Test-Driven Development)

## 학습 목표
- TDD의 Red-Green-Refactor 사이클을 이해하고 적용할 수 있다
- 테스트를 먼저 작성하는 습관을 기를 수 있다
- 작은 단계(Small Steps)로 개발하는 방법을 익힌다
- TDD가 적합한 상황과 그렇지 않은 상황을 구분할 수 있다

## 동기부여: 예지보전 관점

공장 장비의 이상 감지 시스템을 개발한다고 생각해보세요. 센서 데이터에서 이상치를 탐지하는 알고리즘은 정확해야 합니다. 잘못된 이상 감지는 불필요한 장비 정지를 유발하고, 감지 실패는 장비 고장으로 이어질 수 있습니다.

TDD를 사용하면:
- **요구사항을 명확히** 할 수 있습니다 (테스트가 곧 명세)
- **엣지 케이스를 미리** 고려할 수 있습니다
- **리팩토링에 대한 자신감**을 가질 수 있습니다
- **회귀 버그를 방지**할 수 있습니다

## 핵심 개념

### 1. Red-Green-Refactor 사이클

TDD의 핵심은 세 단계의 반복입니다:

```
┌─────────┐     ┌─────────┐     ┌──────────┐
│  RED    │ ──→ │  GREEN  │ ──→ │ REFACTOR │
│ 실패하는 │     │ 통과하는 │     │ 코드를   │
│ 테스트   │     │ 최소코드 │     │ 개선     │
│ 작성    │     │ 작성    │     │          │
└─────────┘     └─────────┘     └──────────┘
      ↑                               │
      └───────────────────────────────┘
```

**Red (빨간색)**: 실패하는 테스트를 먼저 작성합니다.
**Green (초록색)**: 테스트를 통과하는 최소한의 코드를 작성합니다.
**Refactor (리팩토링)**: 코드를 깨끗하게 정리합니다 (테스트는 계속 통과).

### 2. TDD 단계별 예시: 센서 이상 감지기

#### Step 1: RED - 빈 클래스에 대한 테스트 작성

```python
# test_tdd_demo.py
import pytest
from src_anomaly_detector_tdd import SensorAnomalyDetector

def test_새로운_감지기는_비어있다():
    """새로 생성된 감지기에는 데이터가 없어야 한다."""
    detector = SensorAnomalyDetector()
    assert detector.get_reading_count() == 0
```

이 시점에서 `SensorAnomalyDetector` 클래스가 없으므로 테스트는 실패합니다.

#### Step 2: GREEN - 최소한의 구현

```python
# src_anomaly_detector_tdd.py
class SensorAnomalyDetector:
    def __init__(self):
        self._readings = []

    def get_reading_count(self):
        return len(self._readings)
```

#### Step 3: RED - 다음 기능에 대한 테스트

```python
def test_데이터_추가():
    detector = SensorAnomalyDetector()
    detector.add_reading(25.0)
    assert detector.get_reading_count() == 1
```

#### Step 4: GREEN - add_reading 구현

```python
def add_reading(self, value):
    self._readings.append(value)
```

이 과정을 반복하면서 점진적으로 기능을 완성합니다.

### 3. TDD의 세 가지 규칙 (Uncle Bob)

1. **실패하는 단위 테스트 없이는 프로덕션 코드를 작성하지 않는다**
2. **실패를 보여주기에 충분한 만큼만 단위 테스트를 작성한다** (컴파일 실패도 실패)
3. **현재 실패하는 테스트를 통과시키기에 충분한 만큼만 프로덕션 코드를 작성한다**

### 4. 한 사이클에 하나의 Assert

각 TDD 사이클에서는 하나의 동작만 검증합니다:

```python
# 좋은 예: 한 가지 동작만 테스트
def test_평균_계산():
    detector = SensorAnomalyDetector()
    detector.add_reading(10.0)
    detector.add_reading(20.0)
    detector.add_reading(30.0)
    assert detector.get_mean() == 20.0

# 나쁜 예: 여러 동작을 한 번에 테스트
def test_모든_것을_한꺼번에():
    detector = SensorAnomalyDetector()
    detector.add_reading(10.0)
    assert detector.get_reading_count() == 1  # 한 테스트에
    assert detector.get_mean() == 10.0        # 여러 개념을
    assert detector.is_anomaly(100.0) == False # 섞지 마세요
```

### 5. TDD가 효과적인 경우 vs 그렇지 않은 경우

#### 효과적인 경우
- **비즈니스 로직**: 이상 감지 알고리즘, RUL 계산
- **데이터 변환**: 센서 데이터 정규화, 특성 추출
- **규칙 기반 시스템**: 경보 규칙, 유지보수 스케줄링
- **유틸리티 함수**: 단위 변환, 데이터 검증

#### 효과적이지 않은 경우
- **UI/프론트엔드**: 시각적 요소는 TDD가 어려움
- **탐색적 코드**: 프로토타이핑, 데이터 분석 탐색
- **외부 시스템 연동**: API 통합, 하드웨어 인터페이스
- **머신러닝 모델 학습**: 하이퍼파라미터 튜닝

### 6. 데이터 처리에서의 TDD

센서 데이터 처리 파이프라인을 TDD로 개발하는 예시:

```python
# Step 1: 원시 데이터 검증 테스트
def test_유효하지_않은_센서값_거부():
    detector = SensorAnomalyDetector()
    with pytest.raises(ValueError):
        detector.add_reading(float('nan'))

# Step 2: 통계 계산 테스트
def test_표준편차_계산():
    detector = SensorAnomalyDetector()
    for v in [10, 20, 30]:
        detector.add_reading(v)
    expected_std = 8.16496580927726  # 모표준편차
    assert abs(detector.get_std() - expected_std) < 0.0001

# Step 3: 이상치 판별 테스트
def test_3시그마_이상치_감지():
    detector = SensorAnomalyDetector()
    for v in [100, 100, 100, 100, 100]:
        detector.add_reading(v)
    assert detector.is_anomaly(200) == True  # 평균에서 멀리 벗어남
```

## 실습 가이드

### 실습 1: TDD 사이클 체험

`test_tdd_demo.py`를 확인하세요. 각 테스트에는 Red-Green-Refactor 주석이 달려 있습니다.

```bash
# 모든 테스트 실행
pytest test_tdd_demo.py -v

# 특정 테스트만 실행
pytest test_tdd_demo.py -v -k "평균"
```

### 실습 2: RUL 추정기 TDD 연습

`exercises/exercise_27.py`에서 RUL(잔여 수명) 추정기를 TDD로 만들어보세요.

1. 테스트를 먼저 작성
2. 테스트가 실패하는 것을 확인
3. 최소한의 코드를 작성하여 통과
4. 리팩토링

## 연습 문제

### 연습 1: TDD로 센서 데이터 필터 만들기
TDD 사이클을 따라 고주파 노이즈를 제거하는 이동평균 필터를 만들어보세요.

### 연습 2: TDD로 경보 시스템 만들기
센서값이 임계치를 초과하면 경보를 발생시키는 시스템을 TDD로 개발하세요.

### 연습 3: RUL 추정기 (exercises/exercise_27.py)
잔여 수명 추정기를 TDD 방식으로 구현하세요.

## 퀴즈

### Q1. TDD의 세 단계를 올바른 순서로 나열한 것은?
- A) Green → Red → Refactor
- B) Red → Green → Refactor
- C) Refactor → Red → Green
- D) Red → Refactor → Green

**정답: B**
테스트 실패(Red) → 최소 구현으로 통과(Green) → 코드 개선(Refactor)

### Q2. TDD에서 Green 단계의 목표는?
- A) 완벽한 코드를 작성하는 것
- B) 모든 엣지 케이스를 처리하는 것
- C) 테스트를 통과하는 최소한의 코드를 작성하는 것
- D) 코드를 리팩토링하는 것

**정답: C**
Green 단계에서는 테스트를 통과시키기 위한 최소한의 코드만 작성합니다. 코드 개선은 Refactor 단계에서 합니다.

### Q3. 다음 중 TDD가 가장 효과적인 상황은?
- A) UI 레이아웃 설계
- B) 센서 데이터 이상치 감지 알고리즘 개발
- C) 머신러닝 모델 하이퍼파라미터 탐색
- D) 외부 API 연동 프로토타이핑

**정답: B**
명확한 입출력이 있는 비즈니스 로직(이상치 감지 등)은 TDD에 적합합니다.

## 정리 및 다음 주제 예고

### 이번 레슨 정리
- TDD는 **테스트 먼저, 구현 나중**의 개발 방법론
- **Red-Green-Refactor** 사이클을 반복
- 한 사이클에 **하나의 동작**만 검증
- 데이터 처리, 비즈니스 로직에 특히 효과적
- 탐색적 코드나 UI에는 덜 적합

### 다음 주제: 28. 테스트 설계 원칙
좋은 테스트를 작성하는 원칙(FIRST, AAA 패턴)에 대해 알아봅니다. TDD로 테스트를 작성했다면, 이제 그 테스트의 품질을 높이는 방법을 배워봅시다.
