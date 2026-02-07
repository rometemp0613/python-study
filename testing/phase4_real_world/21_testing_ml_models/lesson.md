# 21. 머신러닝/예측 모델 테스트

## 학습 목표

이 레슨을 마치면 다음을 할 수 있습니다:

1. 통계 기반 이상 탐지 모델의 학습/예측 파이프라인 테스트
2. 특징 추출 함수의 수학적 정확성 검증
3. 모델 직렬화(저장)/역직렬화(로드) 일관성 테스트
4. 성능 지표의 회귀(regression) 테스트 작성

## 동기부여: 예지보전 관점

예지보전의 핵심은 **이상 탐지 모델**입니다. 정상 가동 데이터를 학습하고,
실시간 센서 데이터에서 이상 패턴을 감지하여 장비 고장을 사전에 예측합니다.

**모델 테스트가 중요한 이유:**
- 모델 업데이트 후 성능이 오히려 저하될 수 있음 (회귀)
- 특징 추출 버그로 잘못된 이상 점수가 계산될 수 있음
- 모델 저장/로드 과정에서 파라미터가 손실될 수 있음
- 새로운 센서 유형 추가 시 기존 로직이 깨질 수 있음

**이 레슨에서 다루는 모델:**
- Z-score 기반 이상 탐지 (외부 라이브러리 불필요)
- 학습 데이터의 평균과 표준편차로 이상 점수 계산
- RMS, 피크 대 피크, 표준편차 등 진동 특징 추출

## 핵심 개념 설명

### 1. 모델 학습(fit) 테스트

```python
def test_fit_calculates_mean_and_std():
    """학습 시 평균과 표준편차가 올바르게 계산되는지 확인"""
    model = SimpleAnomalyDetector()
    training_data = [10.0, 20.0, 30.0, 40.0, 50.0]

    model.fit(training_data)

    assert model.mean == pytest.approx(30.0)
    assert model.std == pytest.approx(14.1421, rel=1e-3)


def test_fit_with_constant_data():
    """모든 값이 동일한 데이터로 학습 (std=0 처리)"""
    model = SimpleAnomalyDetector()
    training_data = [25.0, 25.0, 25.0, 25.0]

    model.fit(training_data)

    assert model.mean == 25.0
    assert model.std == 0.0
```

### 2. 예측(predict) 테스트

```python
def test_predict_returns_z_scores():
    """예측 결과가 올바른 Z-score인지 확인"""
    model = SimpleAnomalyDetector()
    model.fit([100.0, 100.0, 100.0])  # mean=100, std=0 -> 특별 처리

    # std=0일 때는 동일값이면 0, 다른 값이면 큰 점수
    scores = model.predict([100.0, 200.0])
    assert scores[0] == 0.0  # 정확히 평균과 같으면 0


def test_predict_known_z_scores():
    """알려진 Z-score 값 검증"""
    model = SimpleAnomalyDetector()
    # mean=50, std=10으로 직접 설정
    model.mean = 50.0
    model.std = 10.0

    scores = model.predict([50.0, 60.0, 70.0])
    # z = (x - mean) / std
    assert scores[0] == pytest.approx(0.0)   # (50-50)/10 = 0
    assert scores[1] == pytest.approx(1.0)   # (60-50)/10 = 1
    assert scores[2] == pytest.approx(2.0)   # (70-50)/10 = 2
```

### 3. 분류(classify) 테스트

```python
def test_classify_with_threshold():
    """임계값 기반 이진 분류"""
    model = SimpleAnomalyDetector()
    model.mean = 50.0
    model.std = 10.0

    labels = model.classify([50.0, 65.0, 80.0], threshold=2.0)
    # z-scores: [0.0, 1.5, 3.0]
    # threshold=2.0: 0.0<2(정상), 1.5<2(정상), 3.0>=2(이상)
    assert labels == [0, 0, 1]
```

### 4. 모델 직렬화 테스트

```python
def test_save_and_load_model(tmp_path):
    """모델 저장 후 로드하여 동일한 결과를 내는지 확인"""
    # 원본 모델 학습
    model = SimpleAnomalyDetector()
    model.fit([10.0, 20.0, 30.0, 40.0, 50.0])

    # 저장
    model_path = str(tmp_path / "model.json")
    model.save_model(model_path)

    # 새 모델로 로드
    loaded_model = SimpleAnomalyDetector()
    loaded_model.load_model(model_path)

    # 동일한 입력에 대해 동일한 결과
    test_data = [15.0, 25.0, 35.0, 45.0, 55.0]
    original_scores = model.predict(test_data)
    loaded_scores = loaded_model.predict(test_data)

    assert original_scores == loaded_scores
```

### 5. 특징 추출 테스트

```python
def test_rms_feature():
    """RMS(Root Mean Square) 계산 정확성"""
    model = SimpleAnomalyDetector()
    raw_data = [3.0, 4.0]
    features = model.extract_features(raw_data)

    # RMS = sqrt((9 + 16) / 2) = sqrt(12.5)
    import math
    expected_rms = math.sqrt(12.5)
    assert features["rms"] == pytest.approx(expected_rms)


def test_peak_to_peak_feature():
    """피크 대 피크 계산"""
    model = SimpleAnomalyDetector()
    raw_data = [5.0, -3.0, 8.0, -1.0]
    features = model.extract_features(raw_data)

    # peak_to_peak = max - min = 8.0 - (-3.0) = 11.0
    assert features["peak_to_peak"] == pytest.approx(11.0)
```

### 6. 성능 회귀 테스트

```python
def test_detection_accuracy():
    """이상 탐지 정확도가 기준 이상인지 확인"""
    model = SimpleAnomalyDetector()

    # 정상 데이터로 학습
    normal_data = [50.0 + i * 0.1 for i in range(100)]
    model.fit(normal_data)

    # 정상 데이터는 정상으로 분류해야 함
    test_normal = [50.0, 51.0, 49.5, 50.5]
    normal_labels = model.classify(test_normal, threshold=3.0)
    assert all(label == 0 for label in normal_labels), "정상 데이터 오탐"

    # 이상 데이터는 이상으로 분류해야 함
    test_anomaly = [200.0, -50.0]
    anomaly_labels = model.classify(test_anomaly, threshold=3.0)
    assert all(label == 1 for label in anomaly_labels), "이상 데이터 미탐"
```

## 실습 가이드

1. `src_anomaly_model.py`의 이상 탐지 모델 클래스를 살펴보세요
2. `test_anomaly_model.py`의 테스트 패턴을 확인하세요
3. 테스트 실행:
   ```bash
   pytest -v test_anomaly_model.py
   ```
4. 연습 문제에서 직접 모델 테스트를 작성해보세요

## 연습 문제

### 연습 1: 특징 추출 정확성 테스트
`extract_features` 함수가 RMS, 피크 대 피크, 표준편차를
올바르게 계산하는지 다양한 입력으로 테스트하세요.

### 연습 2: 모델 직렬화 왕복 테스트
모델을 저장하고 로드한 후 원래 모델과 동일한 결과를
생성하는지 검증하세요.

### 연습 3: 엣지 케이스 및 에러 처리
빈 데이터, 단일 값, 학습 전 예측 시도 등
엣지 케이스에 대한 처리를 테스트하세요.

## 퀴즈

### Q1. 모델 테스트에서 '결정적(deterministic)' 테스트가 중요한 이유는?

**A)** 모델 테스트는 동일한 입력에 대해 항상 동일한 결과를 반환해야 합니다.
랜덤 시드를 고정하지 않거나, 비결정적 알고리즘을 사용하면
테스트가 때때로 실패하는 불안정한(flaky) 테스트가 됩니다.
통계 기반 모델(Z-score)은 결정적이므로 정확한 값 비교가 가능합니다.

### Q2. 모델 직렬화 테스트에서 '왕복(round-trip)' 테스트란?

**A)** 모델을 저장(직렬화)한 후 다시 로드(역직렬화)하여
원래 모델과 동일한 파라미터와 예측 결과를 내는지 확인하는 테스트입니다.
이는 모델 배포 시 학습 환경과 운영 환경에서 동일한 동작을 보장합니다.

### Q3. 성능 회귀 테스트에서 허용 오차를 어떻게 설정해야 하나요?

**A)** 성능 지표(정확도, F1-score 등)에 대해 최소 기준선을 설정합니다.
예: "이상 탐지 재현율(recall)은 95% 이상이어야 한다".
너무 엄격하면 사소한 변경에도 실패하고, 너무 느슨하면 성능 저하를 놓칩니다.
비즈니스 요구사항에 맞는 합리적인 기준선을 팀과 합의해야 합니다.

## 정리 및 다음 주제 예고

이번 레슨에서 배운 내용:
- 통계 기반 이상 탐지 모델의 학습/예측 파이프라인 테스트
- 특징 추출(RMS, 피크 대 피크, 표준편차) 정확성 검증
- 모델 직렬화/역직렬화 왕복 테스트
- 성능 지표 회귀 테스트

이것으로 **Phase 4: 실전 테스트**를 마칩니다!

**다음 Phase 5 (고급 테스트)** 에서는:
- pytest 플러그인 생태계
- 테스트 커버리지 측정
- 속성 기반 테스트 (property-based testing)
- 스냅샷 테스트
- 비동기 코드 테스트
