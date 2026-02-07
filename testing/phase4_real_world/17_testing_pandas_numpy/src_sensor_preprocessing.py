"""
센서 데이터 전처리 모듈

공장 설비의 진동, 온도, 전류 센서 데이터를 정제하고
통계 특징을 추출하는 함수들을 제공합니다.

의존성: pandas, numpy
"""
import numpy as np
import pandas as pd


def clean_sensor_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    센서 데이터 정제

    처리 과정:
    1. NaN 값이 포함된 행 제거
    2. 수치 열의 이상치 제거 (IQR 방법)
    3. 데이터 타입 보정

    Args:
        df: 센서 데이터 DataFrame (timestamp, temperature, vibration 등)

    Returns:
        정제된 DataFrame
    """
    if df.empty:
        return df.copy()

    # 원본 보존을 위해 복사
    result = df.copy()

    # 수치형 열 식별
    numeric_cols = result.select_dtypes(include=[np.number]).columns.tolist()

    # 1단계: NaN 값이 포함된 행 제거
    result = result.dropna(subset=numeric_cols)

    if result.empty:
        return result

    # 2단계: IQR 방법으로 이상치 제거
    for col in numeric_cols:
        q1 = result[col].quantile(0.25)
        q3 = result[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 3.0 * iqr
        upper_bound = q3 + 3.0 * iqr
        result = result[(result[col] >= lower_bound) & (result[col] <= upper_bound)]

    # 3단계: 인덱스 리셋
    result = result.reset_index(drop=True)

    return result


def calculate_rolling_stats(
    df: pd.DataFrame, window: int = 5
) -> pd.DataFrame:
    """
    롤링 통계 계산

    각 수치 열에 대해 롤링 평균, 표준편차, 최소, 최대를 계산합니다.

    Args:
        df: 센서 데이터 DataFrame
        window: 롤링 윈도우 크기 (기본값: 5)

    Returns:
        롤링 통계 열이 추가된 DataFrame
    """
    if df.empty:
        return df.copy()

    result = df.copy()
    numeric_cols = result.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols:
        # 롤링 평균
        result[f"{col}_rolling_mean"] = result[col].rolling(
            window=window, min_periods=window
        ).mean()
        # 롤링 표준편차
        result[f"{col}_rolling_std"] = result[col].rolling(
            window=window, min_periods=window
        ).std()
        # 롤링 최소값
        result[f"{col}_rolling_min"] = result[col].rolling(
            window=window, min_periods=window
        ).min()
        # 롤링 최대값
        result[f"{col}_rolling_max"] = result[col].rolling(
            window=window, min_periods=window
        ).max()

    return result


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    센서 데이터에서 통계 특징 추출

    각 수치 열에 대해 다음 특징을 계산합니다:
    - 평균 (mean)
    - 표준편차 (std)
    - 최소값 (min)
    - 최대값 (max)
    - 중앙값 (median)
    - RMS (Root Mean Square)
    - 피크 대 피크 (peak to peak)

    Args:
        df: 센서 데이터 DataFrame

    Returns:
        특징이 포함된 단일 행 DataFrame
    """
    if df.empty:
        return pd.DataFrame()

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    features = {}

    for col in numeric_cols:
        col_data = df[col].dropna()

        if col_data.empty:
            continue

        features[f"{col}_mean"] = col_data.mean()
        features[f"{col}_std"] = col_data.std()
        features[f"{col}_min"] = col_data.min()
        features[f"{col}_max"] = col_data.max()
        features[f"{col}_median"] = col_data.median()
        # RMS (Root Mean Square) - 진동 분석에 핵심적인 특징
        features[f"{col}_rms"] = np.sqrt(np.mean(col_data.values ** 2))
        # 피크 대 피크 - 진폭 범위
        features[f"{col}_peak_to_peak"] = col_data.max() - col_data.min()

    return pd.DataFrame([features])


def merge_sensor_data(
    df1: pd.DataFrame, df2: pd.DataFrame, on: str = "timestamp"
) -> pd.DataFrame:
    """
    여러 센서 소스의 데이터 병합

    두 센서 데이터를 지정된 키 열 기준으로 내부 조인(inner join)합니다.
    타임스탬프가 일치하는 데이터만 유지됩니다.

    Args:
        df1: 첫 번째 센서 데이터
        df2: 두 번째 센서 데이터
        on: 병합 기준 열 이름 (기본값: "timestamp")

    Returns:
        병합된 DataFrame
    """
    if df1.empty or df2.empty:
        # 빈 DataFrame이 있으면 공통 열 구조만 반환
        all_cols = list(set(df1.columns.tolist() + df2.columns.tolist()))
        return pd.DataFrame(columns=sorted(all_cols))

    # 내부 조인으로 병합
    result = pd.merge(df1, df2, on=on, how="inner")

    # 타임스탬프 기준 정렬
    if on in result.columns:
        result = result.sort_values(by=on).reset_index(drop=True)

    return result
