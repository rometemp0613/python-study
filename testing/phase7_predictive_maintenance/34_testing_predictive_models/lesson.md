# 레슨 34: 예측 모델 테스트

## 1. 학습 목표

이 레슨을 완료하면 다음을 할 수 있습니다:

- ML 파이프라인의 각 단계(학습 → 예측 → 평가)를 독립적으로 테스트할 수 있다
- 고정 시드(fixed seed)로 결정론적(deterministic) 테스트를 작성할 수 있다
- 성능 지표(accuracy, precision, recall, F1)의 임계값을 테스트할 수 있다
- 잔여 수명(RUL) 예측 로직의 합리성을 검증할 수 있다
- 모델 저장/로딩 후 동일한 결과가 나오는지 검증할 수 있다
- 모델 열화(degradation)를 탐지하는 회귀 테스트를 작성할 수 있다

## 2. 동기부여 (예지보전 관점)

예지보전 시스템의 핵심은 **예측 모델**입니다. 베어링 고장 예측, 잔여 수명(RUL) 추정,
이상 탐지 등의 모델이 올바르게 작동하지 않으면 설비가 멈추거나, 불필요한 정비가 발생합니다.

ML 모델 테스트의 어려움:
- **비결정성**: 같은 데이터로 학습해도 결과가 달라질 수 있음
- **성능 기준**: "정확도 90% 이상" 같은 기준을 어떻게 테스트할 것인가
- **데이터 의존성**: 모델은 학습 데이터의 품질에 크게 좌우됨
- **시간 경과**: 모델 성능은 시간이 지나면서 열화될 수 있음

이 레슨에서는 외부 라이브러리 없이 **통계 기반의 간단한 모델**을 구현하고,
ML 파이프라인 테스트의 패턴을 배웁니다.

## 3. 핵심 개념 설명

### 3.1 모델 학습(fit) 테스트

모델 학습 후 내부 상태가 올바르게 설정되었는지 테스트합니다:

```python
def test_학습후_파라미터_유효():
    model = BearingFailurePredictor()
    training_data = [
        {"rms": 0.5, "kurtosis": 0.1, "crest_factor": 1.2, "label": "normal"},
        {"rms": 2.5, "kurtosis": 5.0, "crest_factor": 3.5, "label": "fault"},
    ]

    model.fit(training_data)

    # 학습 후 정상 패턴의 통계가 저장되어야 함
    assert model.is_fitted is True
    assert "rms" in model.normal_params
    assert model.normal_params["rms"]["mean"] > 0
```

### 3.2 결정론적 테스트 (Fixed Seed)

랜덤 요소가 있는 모델은 시드를 고정하여 재현 가능한 테스트를 만듭니다:

```python
import random

def test_고정_시드로_결정론적_결과():
    random.seed(42)
    model = BearingFailurePredictor()
    model.fit(training_data)
    result1 = model.predict_health_score(features)

    random.seed(42)
    model2 = BearingFailurePredictor()
    model2.fit(training_data)
    result2 = model2.predict_health_score(features)

    assert result1 == result2  # 동일한 시드 → 동일한 결과
```

### 3.3 성능 지표 테스트

모델의 성능이 최소 기준을 만족하는지 테스트합니다:

```python
def test_정확도_임계값():
    model = BearingFailurePredictor()
    model.fit(training_data)

    metrics = model.evaluate(test_data, true_labels)

    assert metrics.accuracy >= 0.8, f"정확도 {metrics.accuracy} < 0.8"
    assert metrics.recall >= 0.9, "고장 미탐지율이 너무 높습니다"
```

> **주의**: 성능 임계값 테스트는 CI/CD에서 모델 열화를 감지하는 "회귀 테스트" 역할을 합니다.

### 3.4 RUL(Remaining Useful Life) 예측 테스트

잔여 수명 예측의 합리성을 검증합니다:

```python
def test_RUL_예측_합리성():
    model = BearingFailurePredictor()
    model.fit(training_data)

    # 건강도가 점차 감소하는 이력
    health_history = [95, 88, 76, 65, 50]

    rul = model.predict_rul(health_history)

    # RUL은 양수여야 함
    assert rul > 0
    # 건강도 하락 속도로 볼 때 합리적인 범위
    assert rul < 100  # 너무 먼 미래 예측은 비현실적
```

### 3.5 모델 저장/로딩 테스트

모델을 저장하고 다시 로딩했을 때 동일한 결과가 나오는지 검증합니다:

```python
def test_저장_로딩_일관성(tmp_path):
    model = BearingFailurePredictor()
    model.fit(training_data)

    # 저장 전 예측
    score_before = model.predict_health_score(features)

    # 저장 → 로딩
    filepath = str(tmp_path / "model.json")
    model.save_model(filepath)
    loaded_model = BearingFailurePredictor()
    loaded_model.load_model(filepath)

    # 로딩 후 예측
    score_after = loaded_model.predict_health_score(features)

    assert score_before == pytest.approx(score_after)
```

### 3.6 모델 열화 감지 (회귀 테스트)

모델의 성능이 이전 버전보다 떨어지지 않는지 확인합니다:

```python
# 이전 버전의 성능을 "기준선(baseline)"으로 저장
BASELINE_ACCURACY = 0.85
BASELINE_F1 = 0.82

def test_모델_성능_회귀_없음():
    model = BearingFailurePredictor()
    model.fit(training_data)
    metrics = model.evaluate(test_data, true_labels)

    assert metrics.accuracy >= BASELINE_ACCURACY, \
        f"정확도가 기준선({BASELINE_ACCURACY}) 미만: {metrics.accuracy}"
    assert metrics.f1 >= BASELINE_F1, \
        f"F1이 기준선({BASELINE_F1}) 미만: {metrics.f1}"
```

## 4. 실습 가이드

### 단계 1: 모델 코드 분석
`src_bearing_model.py`를 열어 다음을 확인하세요:
- `fit()`: 정상 데이터의 평균/표준편차를 학습
- `predict_health_score()`: 마할라노비스 거리 기반 건강도 점수
- `predict_rul()`: 건강도 이력의 선형 외삽으로 RUL 추정
- `evaluate()`: 이진 분류 성능 지표 계산

### 단계 2: 테스트 코드 분석
`test_bearing_model.py`에서 다음 테스트 패턴을 확인하세요:
- 학습 상태 검증
- 예측 결과의 범위/형태 검증
- 저장/로딩 일관성 검증
- 성능 임계값 검증

### 단계 3: 테스트 실행
```bash
cd phase7_predictive_maintenance/34_testing_predictive_models
pytest test_bearing_model.py -v
```

### 단계 4: 연습 문제 풀기
`exercises/exercise_34.py`에서 TODO를 완성하세요.

## 5. 연습 문제

### 연습 1: 모델 학습 상태 검증
`fit()` 호출 전후의 모델 상태 변화를 테스트하세요.
학습 전에는 `is_fitted=False`, 학습 후에는 `is_fitted=True`이고
정상 패턴 파라미터가 저장되는지 확인하세요.

### 연습 2: 건강도 점수 범위 검증
다양한 입력에 대해 `predict_health_score()`가 0~100 범위의 값을 반환하는지 테스트하세요.
정상 데이터는 높은 점수, 비정상 데이터는 낮은 점수를 반환하는지 확인하세요.

### 연습 3: 모델 저장/로딩 테스트
모델을 JSON으로 저장하고 다시 로딩한 후,
동일한 입력에 대해 동일한 예측을 하는지 테스트하세요.

## 6. 퀴즈

### Q1. ML 모델 테스트에서 고정 시드(fixed seed)를 사용하는 이유는?
- A) 테스트 속도를 높이기 위해
- B) 랜덤 요소를 제거하여 결과를 재현 가능하게 만들기 위해
- C) 모델 정확도를 높이기 위해
- D) 메모리 사용량을 줄이기 위해

**정답: B** - 고정 시드를 사용하면 랜덤 초기화, 데이터 셔플링 등의 결과가
항상 동일해지므로, 테스트가 항상 같은 조건에서 실행됩니다.

### Q2. 성능 지표 중 recall(재현율)이 예지보전에서 특히 중요한 이유는?
- A) 계산이 간단하기 때문
- B) 정밀도보다 항상 높기 때문
- C) 실제 고장을 놓치지 않는 것(미탐지 방지)이 중요하기 때문
- D) 거짓 경보가 없어야 하기 때문

**정답: C** - 예지보전에서는 실제 고장을 놓치면(미탐지) 설비가 예고 없이 멈춰
큰 손해가 발생합니다. recall은 실제 고장 중 얼마나 많이 탐지했는지를 나타냅니다.

### Q3. 모델 저장/로딩 테스트가 필요한 이유는?
- A) 파일 크기를 줄이기 위해
- B) 직렬화/역직렬화 과정에서 정보 손실이 없는지 확인하기 위해
- C) 모델 학습 속도를 높이기 위해
- D) 다른 프로그래밍 언어와 호환되는지 확인하기 위해

**정답: B** - 모델을 파일로 저장(직렬화)하고 다시 로딩(역직렬화)하는 과정에서
부동소수점 정밀도 손실, 누락된 속성 등의 문제가 발생할 수 있습니다.

## 7. 정리 및 다음 주제 예고

### 이번 레슨 정리
- ML 파이프라인의 각 단계(fit → predict → evaluate → save/load)를 테스트하는 방법을 배웠습니다
- 고정 시드로 결정론적 테스트를 작성하는 기법을 익혔습니다
- 성능 임계값 테스트와 회귀 테스트의 패턴을 이해했습니다
- RUL 예측의 합리성 검증 방법을 학습했습니다

### 다음 주제: 알람/알림 시스템 테스트 (레슨 35)
다음 레슨에서는 예측 결과를 기반으로 알람을 발생시키고 알림을 보내는 시스템을 테스트합니다.
임계값 기반 알람, 알람 중복 방지, 알림 서비스 모킹 등을 다룹니다.
