# 17. Pandas/NumPy 코드 테스트

## 학습 목표

이 레슨을 마치면 다음을 할 수 있습니다:

1. `pandas.testing.assert_frame_equal`과 `assert_series_equal`로 DataFrame을 비교하는 테스트 작성
2. `numpy.testing.assert_array_equal`과 `assert_allclose`로 수치 배열 테스트
3. 센서 데이터 전처리 파이프라인의 엣지 케이스 처리 및 테스트
4. 부동소수점 비교 시 정밀도 문제 해결

## 동기부여: 예지보전 관점

공장의 진동 센서, 온도 센서, 전류 센서에서 수집되는 데이터는 pandas DataFrame으로
관리됩니다. 이 데이터의 전처리(결측값 제거, 이상치 처리, 통계 특징 추출)가
잘못되면 예지보전 모델의 예측 정확도가 크게 떨어집니다.

**실제 사고 사례:**
- 센서 데이터의 NaN 값을 잘못 처리하여 모델이 정상 장비를 고장으로 오판
- 롤링 통계 계산에서 윈도우 크기 오류로 인한 잘못된 트렌드 분석
- 여러 센서 데이터 병합 시 타임스탬프 불일치로 데이터 누락

이런 문제를 방지하려면 데이터 전처리 코드에 대한 철저한 테스트가 필수입니다.

## 핵심 개념 설명

### 1. pandas.testing을 활용한 DataFrame 비교

```python
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal, assert_series_equal

# === DataFrame 동등성 비교 ===
def test_basic_dataframe_comparison():
    """기본 DataFrame 비교 테스트"""
    df_expected = pd.DataFrame({
        "sensor_id": ["S001", "S002"],
        "temperature": [25.0, 30.0]
    })
    df_actual = pd.DataFrame({
        "sensor_id": ["S001", "S002"],
        "temperature": [25.0, 30.0]
    })
    # 정확한 일치 확인
    assert_frame_equal(df_actual, df_expected)


def test_dataframe_with_tolerance():
    """부동소수점 오차 허용 비교"""
    df_expected = pd.DataFrame({"value": [1.0, 2.0, 3.0]})
    df_actual = pd.DataFrame({"value": [1.0000001, 2.0000002, 3.0000003]})
    # atol: 절대 허용 오차, rtol: 상대 허용 오차
    assert_frame_equal(df_actual, df_expected, atol=1e-5)
```

### 2. numpy.testing을 활용한 배열 비교

```python
import numpy as np
from numpy.testing import assert_array_equal, assert_allclose

def test_numpy_exact_comparison():
    """정확한 배열 비교"""
    expected = np.array([1, 2, 3, 4, 5])
    actual = np.array([1, 2, 3, 4, 5])
    assert_array_equal(actual, expected)


def test_numpy_floating_point():
    """부동소수점 근사 비교 - 센서 데이터에 필수!"""
    # 진동 센서의 RMS 계산 결과
    vibration_data = np.array([0.1, -0.2, 0.15, -0.05, 0.3])
    rms = np.sqrt(np.mean(vibration_data ** 2))
    expected_rms = 0.18574  # 수동 계산 값

    # assert_allclose: rtol(상대 오차)과 atol(절대 오차) 지정 가능
    assert_allclose(rms, expected_rms, rtol=1e-3)
```

### 3. 센서 데이터 전처리 테스트 전략

```python
import pytest

# pandas가 없으면 테스트를 우아하게 건너뛰기
pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")


@pytest.fixture
def sample_sensor_df():
    """테스트용 센서 데이터 생성"""
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=10, freq="h"),
        "temperature": [25.0, 26.1, np.nan, 27.3, 200.0, 25.5, 26.0, np.nan, 25.8, 26.2],
        "vibration": [0.5, 0.6, 0.55, 0.7, 0.65, 0.58, 0.62, 0.59, 0.61, 0.63],
    })


def test_clean_sensor_data_removes_nan(sample_sensor_df):
    """NaN 값이 올바르게 제거되는지 확인"""
    result = clean_sensor_data(sample_sensor_df)
    assert result["temperature"].isna().sum() == 0


def test_clean_sensor_data_handles_outliers(sample_sensor_df):
    """이상치(200도)가 올바르게 처리되는지 확인"""
    result = clean_sensor_data(sample_sensor_df)
    assert result["temperature"].max() < 100  # 200도는 명백한 이상치
```

### 4. 엣지 케이스 테스트

```python
def test_empty_dataframe():
    """빈 DataFrame 처리"""
    empty_df = pd.DataFrame(columns=["timestamp", "temperature", "vibration"])
    result = clean_sensor_data(empty_df)
    assert len(result) == 0
    assert list(result.columns) == ["timestamp", "temperature", "vibration"]


def test_single_row_dataframe():
    """단일 행 DataFrame - 롤링 통계에서 주의 필요"""
    single_df = pd.DataFrame({
        "timestamp": [pd.Timestamp("2024-01-01")],
        "temperature": [25.0],
        "vibration": [0.5],
    })
    result = calculate_rolling_stats(single_df, window=3)
    # 윈도우보다 데이터가 적으면 NaN이 될 수 있음
    assert len(result) == 1


def test_all_nan_column():
    """모든 값이 NaN인 열 처리"""
    nan_df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
        "temperature": [np.nan] * 5,
        "vibration": [0.5, 0.6, 0.55, 0.7, 0.65],
    })
    result = clean_sensor_data(nan_df)
    assert len(result) == 0  # 온도가 모두 NaN이면 해당 행 제거
```

### 5. 롤링 통계 테스트

```python
def test_rolling_stats_values():
    """롤링 통계 계산값 정확성 검증"""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
        "temperature": [20.0, 22.0, 21.0, 23.0, 22.0],
    })
    result = calculate_rolling_stats(df, window=3)

    # 윈도우=3일 때, 인덱스 2부터 유효한 롤링 평균
    expected_rolling_mean = pd.Series(
        [np.nan, np.nan, 21.0, 22.0, 22.0],
        name="temperature_rolling_mean"
    )
    assert_series_equal(
        result["temperature_rolling_mean"],
        expected_rolling_mean,
        check_names=False,
        atol=1e-10,
    )
```

### 6. 데이터 병합 테스트

```python
def test_merge_sensor_data():
    """두 센서 소스 병합 테스트"""
    df_temp = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
        "temperature": [25.0, 26.0, 27.0],
    })
    df_vibration = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
        "vibration": [0.5, 0.6, 0.7],
    })
    result = merge_sensor_data(df_temp, df_vibration, on="timestamp")

    assert "temperature" in result.columns
    assert "vibration" in result.columns
    assert len(result) == 3
```

## 실습 가이드

1. `src_sensor_preprocessing.py`의 함수들을 살펴보세요
2. `conftest.py`의 픽스처를 확인하세요
3. `test_preprocessing.py`를 실행하여 모든 테스트가 통과하는지 확인하세요:
   ```bash
   pytest -v test_preprocessing.py
   ```
4. 연습 문제 파일에서 TODO를 완성하세요

## 연습 문제

### 연습 1: 특징 추출 함수 테스트
`extract_features()` 함수가 올바른 통계 특징(평균, 표준편차, 최소, 최대, 중앙값)을
추출하는지 테스트하세요.

### 연습 2: 엣지 케이스 처리
빈 DataFrame, 단일 행 DataFrame, 모든 값이 동일한 DataFrame에 대해
각 함수가 올바르게 동작하는지 테스트하세요.

### 연습 3: 데이터 타입 검증
전처리 후 각 열의 데이터 타입이 올바른지 검증하는 테스트를 작성하세요.

## 퀴즈

### Q1. `assert_frame_equal`과 `==` 연산자의 차이점은?

**A)** `==`는 element-wise 비교로 Boolean DataFrame을 반환하고, NaN 비교가 어렵습니다.
`assert_frame_equal`은 전체 구조(컬럼명, 인덱스, 데이터타입, 값)를 한번에 비교하고,
실패 시 어떤 부분이 다른지 상세한 에러 메시지를 제공합니다.

### Q2. 부동소수점 비교 시 `assert_allclose(a, b, rtol=1e-5)`에서 rtol의 의미는?

**A)** rtol은 상대적 허용 오차(relative tolerance)입니다.
`|a - b| <= atol + rtol * |b|` 조건을 만족하면 통과합니다.
센서 데이터처럼 값의 크기가 다양한 경우 rtol이 유용합니다.

### Q3. `pytest.importorskip("pandas")`는 어떤 역할을 하나요?

**A)** pandas가 설치되어 있지 않으면 해당 테스트 모듈 전체를 건너뜁니다(skip).
이를 통해 선택적 의존성(pandas, numpy 등)이 없는 환경에서도
테스트 스위트가 실패하지 않고 정상적으로 실행됩니다.

## 정리 및 다음 주제 예고

이번 레슨에서 배운 내용:
- `pandas.testing`과 `numpy.testing`을 활용한 데이터 비교 테스트
- 부동소수점 비교에서의 허용 오차 설정
- 센서 데이터 전처리의 엣지 케이스 테스트
- `pytest.importorskip()`을 통한 선택적 의존성 처리

**다음 레슨 (18. 파일 I/O와 데이터 파이프라인 테스트)** 에서는:
- `tmp_path`를 활용한 파일 I/O 테스트
- CSV, JSON 파일 읽기/쓰기 테스트
- ETL 파이프라인 엔드-투-엔드 테스트
- 테스트 데이터 관리 전략
