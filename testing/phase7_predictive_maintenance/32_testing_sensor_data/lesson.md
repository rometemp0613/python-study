# 레슨 32: 센서 데이터 수집/처리 테스트

## 1. 학습 목표

이 레슨을 완료하면 다음을 할 수 있습니다:

- CSV/JSON 형식의 센서 데이터 로딩 코드를 테스트할 수 있다
- 결측치 처리, 보간, 이상치 제거 등 데이터 클리닝 로직을 검증할 수 있다
- 리샘플링(Resampling) 처리의 정확성을 테스트할 수 있다
- RMS, 첨도(Kurtosis), Peak-to-Peak, Crest Factor 등 특징 추출 함수를 테스트할 수 있다
- 전체 데이터 처리 파이프라인을 통합 테스트할 수 있다

## 2. 동기부여 (예지보전 관점)

공장 설비의 예지보전(Predictive Maintenance)에서 **센서 데이터는 모든 것의 출발점**입니다.

진동 센서, 온도 센서, 압력 센서 등에서 수집된 원시 데이터(raw data)는 그 자체로는
의미가 없습니다. 이 데이터를 **수집 → 클리닝 → 전처리 → 특징 추출**하는 파이프라인이
정확하게 동작해야만 이후의 모든 분석(이상 탐지, 잔여 수명 예측 등)이 신뢰할 수 있습니다.

실제 현장에서 발생하는 문제:
- 센서 통신 오류로 인한 결측치(NaN, 빈 값)
- 전기적 노이즈로 인한 이상치(spike)
- 샘플링 주파수 불일치
- 데이터 형식 변경(CSV 헤더 변경 등)

이런 문제들을 **테스트 코드로 미리 검증**하지 않으면, 잘못된 데이터가 모델에 입력되어
거짓 경보(false alarm)나 미탐지(missed detection)를 일으킵니다.

## 3. 핵심 개념 설명

### 3.1 센서 데이터 로딩 테스트

센서 데이터는 주로 CSV, JSON 형식으로 저장됩니다. 로딩 함수를 테스트할 때 주의할 점:

```python
import csv
import tempfile
import os

def test_csv_로딩_정상_데이터(tmp_path):
    """정상적인 CSV 파일을 올바르게 로딩하는지 테스트"""
    # 준비: 임시 CSV 파일 생성
    csv_file = tmp_path / "vibration.csv"
    csv_file.write_text(
        "timestamp,amplitude\n"
        "0.0,1.23\n"
        "0.001,2.34\n"
        "0.002,1.56\n"
    )

    # 실행
    processor = VibrationDataProcessor()
    data = processor.load_csv(str(csv_file))

    # 검증
    assert len(data) == 3
    assert data[0]["timestamp"] == 0.0
    assert data[0]["amplitude"] == 1.23
```

핵심 포인트:
- `tmp_path` 픽스처를 사용하여 임시 파일 생성 (테스트 후 자동 정리)
- 정상 케이스뿐만 아니라 **빈 파일, 헤더만 있는 파일, 잘못된 형식**도 테스트

### 3.2 데이터 클리닝 테스트

결측치 처리와 보간(interpolation)은 데이터 전처리의 핵심입니다:

```python
def test_결측치_선형보간():
    """None 값을 선형 보간으로 채우는지 테스트"""
    processor = VibrationDataProcessor()
    data = [1.0, 2.0, None, 4.0, 5.0]

    cleaned = processor.clean_data(data)

    # None이었던 인덱스 2는 선형 보간으로 3.0이 되어야 함
    assert cleaned[2] == 3.0
    assert None not in cleaned
```

### 3.3 이상치 제거 테스트

IQR(사분위 범위) 방법으로 이상치를 제거합니다:

```python
def test_이상치_제거_IQR():
    """IQR 방법으로 극단적인 값을 제거하는지 테스트"""
    processor = VibrationDataProcessor()
    # 정상 데이터에 극단적 이상치 추가
    data = [1.0, 1.1, 1.2, 0.9, 1.0, 100.0, 1.1, 0.8]

    cleaned = processor.remove_outliers(data, method="iqr")

    # 100.0은 제거되어야 함
    assert 100.0 not in cleaned
    assert len(cleaned) == 7
```

### 3.4 특징 추출(Feature Extraction) 테스트

진동 데이터에서 추출하는 주요 특징들:

| 특징 | 설명 | 공식 |
|------|------|------|
| RMS | 에너지 수준 | sqrt(mean(x^2)) |
| Kurtosis | 뾰족한 정도 | 4차 모멘트 기반 |
| Peak-to-Peak | 최대 진폭 범위 | max - min |
| Crest Factor | 충격 성분 비율 | peak / RMS |

```python
def test_RMS_계산():
    """RMS(Root Mean Square) 계산 정확성 테스트"""
    processor = VibrationDataProcessor()
    # RMS of [3, 4] = sqrt((9 + 16) / 2) = sqrt(12.5) ≈ 3.5355
    data = [3.0, 4.0]

    rms = processor.calculate_rms(data)

    assert abs(rms - 3.5355) < 0.001

def test_crest_factor_계산():
    """Crest Factor = peak / RMS 정확성 테스트"""
    processor = VibrationDataProcessor()
    data = [1.0, 2.0, 3.0, 4.0, 5.0]

    cf = processor.calculate_crest_factor(data)

    # peak = 5.0, RMS = sqrt((1+4+9+16+25)/5) = sqrt(11) ≈ 3.3166
    # CF = 5.0 / 3.3166 ≈ 1.5076
    expected_rms = (55 / 5) ** 0.5
    expected_cf = 5.0 / expected_rms
    assert abs(cf - expected_cf) < 0.001
```

### 3.5 신호 처리 개념 (FFT)

FFT(Fast Fourier Transform)는 시간 영역 신호를 주파수 영역으로 변환합니다.
예지보전에서 특정 주파수의 에너지 증가는 베어링 결함, 기어 마모 등의 징후입니다.

> 참고: 실제 FFT 구현은 numpy/scipy를 사용하지만, 이 레슨에서는 개념만 다루고
> 테스트 가능한 특징 추출 함수에 집중합니다.

### 3.6 리샘플링 테스트

서로 다른 샘플링 주파수의 센서 데이터를 통합할 때 리샘플링이 필요합니다:

```python
def test_다운샘플링():
    """10Hz 데이터를 5Hz로 다운샘플링"""
    processor = VibrationDataProcessor()
    # 10개 샘플 (10Hz × 1초)
    data = list(range(10))

    resampled = processor.resample(data, target_freq=5)

    # 5Hz × 1초 = 5개 샘플이 되어야 함
    assert len(resampled) == 5
```

## 4. 실습 가이드

### 단계 1: 소스 코드 읽기
`src_vibration_processor.py`를 열어서 `VibrationDataProcessor` 클래스의
각 메서드가 어떤 역할을 하는지 파악하세요.

### 단계 2: 테스트 코드 읽기
`test_vibration_processor.py`를 열어서 각 테스트가 무엇을 검증하는지 확인하세요.
특히 **경계 조건**(빈 데이터, 단일 값 등)에 주목하세요.

### 단계 3: 테스트 실행
```bash
cd phase7_predictive_maintenance/32_testing_sensor_data
pytest test_vibration_processor.py -v
```

### 단계 4: 연습 문제 풀기
`exercises/exercise_32.py`를 열어 TODO 부분을 완성하세요.

## 5. 연습 문제

### 연습 1: 온도 센서 데이터 전처리 테스트
`exercises/exercise_32.py`에서 온도 센서 데이터의 클리닝 함수를 테스트하세요.
- 물리적으로 불가능한 온도값(-50도 이하, 200도 이상) 필터링
- 결측치를 이전 유효값으로 채우기(forward fill)

### 연습 2: 특징 추출 파이프라인 테스트
주어진 진동 데이터에서 모든 특징을 한번에 추출하는 `extract_all_features()` 함수를
테스트하세요. 반환값이 올바른 키와 유효한 값을 포함하는지 검증하세요.

### 연습 3: CSV 파일 에러 처리 테스트
잘못된 CSV 파일(빈 파일, 헤더만 있는 파일, 잘못된 데이터 타입)에 대한
에러 처리를 테스트하세요.

## 6. 퀴즈

### Q1. 센서 데이터 테스트에서 `tmp_path` 픽스처를 사용하는 이유는?
- A) 테스트 속도를 높이기 위해
- B) 테스트 후 임시 파일이 자동으로 정리되어 테스트 격리가 보장되기 때문
- C) 실제 센서에서 데이터를 읽기 위해
- D) 병렬 테스트를 위해

**정답: B** - `tmp_path`는 각 테스트마다 고유한 임시 디렉토리를 제공하고,
테스트 완료 후 자동으로 정리됩니다.

### Q2. RMS(Root Mean Square)가 예지보전에서 중요한 이유는?
- A) 계산이 간단하기 때문
- B) 진동 신호의 전체 에너지 수준을 나타내어 설비 상태를 파악할 수 있기 때문
- C) 최대값만 알면 충분하기 때문
- D) 주파수 분석에 필요하기 때문

**정답: B** - RMS는 진동 신호의 전체 에너지 수준(power)을 단일 값으로 요약하며,
이 값의 증가 추세는 설비 열화의 지표입니다.

### Q3. IQR 방법으로 이상치를 제거할 때, 어떤 범위 밖의 값을 이상치로 판단합니까?
- A) 평균 ± 1 표준편차
- B) 평균 ± 2 표준편차
- C) Q1 - 1.5×IQR ~ Q3 + 1.5×IQR 범위 밖
- D) 중앙값 ± 3 표준편차

**정답: C** - IQR = Q3 - Q1이며, Q1 - 1.5×IQR 미만이거나
Q3 + 1.5×IQR 초과인 값을 이상치로 판단합니다.

## 7. 정리 및 다음 주제 예고

### 이번 레슨 정리
- 센서 데이터 로딩, 클리닝, 전처리, 특징 추출의 전체 파이프라인을 테스트하는 방법을 배웠습니다
- `tmp_path`를 사용한 파일 기반 테스트, 수치 정확도 검증, 경계 조건 테스트 등의 기법을 익혔습니다
- RMS, Kurtosis, Peak-to-Peak, Crest Factor 등 진동 분석의 핵심 특징값 테스트를 실습했습니다

### 다음 주제: 데이터 유효성 검증 테스트 (레슨 33)
다음 레슨에서는 수집된 센서 데이터가 **유효한지** 검증하는 로직을 테스트합니다.
스키마 검증, 물리적 범위 검증, 시계열 갭 탐지 등을 다룹니다.
