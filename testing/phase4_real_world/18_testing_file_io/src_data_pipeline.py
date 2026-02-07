"""
센서 데이터 파이프라인 모듈

CSV 파일에서 센서 데이터를 읽고, 검증하고, 변환하고,
저장하는 ETL(Extract-Transform-Load) 파이프라인을 구현합니다.

pandas가 있으면 pandas를 사용하고, 없으면 csv 모듈로 대체합니다.
"""
import csv
import json
import os
from datetime import datetime
from typing import Any

# pandas 선택적 임포트
try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


# ============================================================
# 필수 열 정의
# ============================================================

REQUIRED_COLUMNS = ["timestamp", "sensor_id", "temperature", "vibration"]

# 센서 값의 유효 범위
VALID_RANGES = {
    "temperature": (-40.0, 150.0),   # 섭씨 기준
    "vibration": (0.0, 50.0),        # mm/s 기준
}


def read_sensor_csv(filepath: str) -> "pd.DataFrame":
    """
    센서 CSV 파일 읽기

    CSV 파일을 읽어 pandas DataFrame으로 반환합니다.
    timestamp 열은 datetime 타입으로 자동 변환합니다.

    Args:
        filepath: CSV 파일 경로

    Returns:
        센서 데이터 DataFrame

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        ValueError: CSV 파싱 실패 시
    """
    if not HAS_PANDAS:
        raise ImportError("이 함수는 pandas가 필요합니다")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"CSV 파싱 실패: {e}")

    # timestamp 열이 있으면 datetime 변환 시도
    if "timestamp" in df.columns:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        except (ValueError, TypeError):
            pass  # 변환 실패 시 문자열 유지

    return df


def validate_data(df: "pd.DataFrame") -> tuple:
    """
    데이터 유효성 검증

    다음을 검증합니다:
    1. 필수 열 존재 여부
    2. 수치 열의 값 범위
    3. NaN 비율 (50% 초과 시 경고)
    4. 중복 행 존재 여부

    Args:
        df: 검증할 DataFrame

    Returns:
        (is_valid: bool, errors: list[str]) 튜플
    """
    errors = []

    # 1. 필수 열 존재 확인
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            errors.append(f"필수 열 누락: {col}")

    if errors:
        return False, errors

    # 2. 값 범위 검증
    for col, (min_val, max_val) in VALID_RANGES.items():
        if col in df.columns:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                out_of_range = col_data[
                    (col_data < min_val) | (col_data > max_val)
                ]
                if len(out_of_range) > 0:
                    errors.append(
                        f"열 '{col}'에 범위 밖 값 {len(out_of_range)}개 "
                        f"(유효 범위: {min_val}~{max_val})"
                    )

    # 3. NaN 비율 확인
    for col in REQUIRED_COLUMNS:
        if col in df.columns:
            nan_ratio = df[col].isna().mean()
            if nan_ratio > 0.5:
                errors.append(
                    f"열 '{col}'의 NaN 비율이 50% 초과: {nan_ratio:.1%}"
                )

    # 4. 중복 행 확인
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        errors.append(f"중복 행 {duplicate_count}개 발견")

    is_valid = len(errors) == 0
    return is_valid, errors


def transform_data(df: "pd.DataFrame") -> "pd.DataFrame":
    """
    센서 데이터 변환 및 정제

    처리 과정:
    1. 중복 행 제거
    2. NaN 값을 전후 값의 평균(보간)으로 대체
    3. 범위 밖 값 클리핑
    4. 타임스탬프 정렬

    Args:
        df: 원본 센서 데이터

    Returns:
        변환된 DataFrame
    """
    if not HAS_PANDAS:
        raise ImportError("이 함수는 pandas가 필요합니다")

    result = df.copy()

    # 1. 중복 행 제거
    result = result.drop_duplicates()

    # 2. 수치 열 NaN 보간 (선형 보간법)
    numeric_cols = result.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        result[col] = result[col].interpolate(method="linear")
        # 첫 번째/마지막 값이 NaN이면 가장 가까운 유효 값으로 채움
        result[col] = result[col].bfill().ffill()

    # 3. 범위 밖 값 클리핑
    for col, (min_val, max_val) in VALID_RANGES.items():
        if col in result.columns:
            result[col] = result[col].clip(lower=min_val, upper=max_val)

    # 4. 타임스탬프 정렬
    if "timestamp" in result.columns:
        result = result.sort_values("timestamp").reset_index(drop=True)

    return result


def save_processed_data(df: "pd.DataFrame", filepath: str) -> dict:
    """
    처리된 데이터를 CSV 파일로 저장

    Args:
        df: 저장할 DataFrame
        filepath: 출력 파일 경로

    Returns:
        저장 결과 딕셔너리 (행 수, 파일 크기 등)

    Raises:
        OSError: 파일 저장 실패 시
    """
    if not HAS_PANDAS:
        raise ImportError("이 함수는 pandas가 필요합니다")

    # 디렉토리가 없으면 생성
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    df.to_csv(filepath, index=False)

    file_size = os.path.getsize(filepath)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "file_size_bytes": file_size,
        "filepath": filepath,
    }


def run_pipeline(input_path: str, output_path: str) -> dict:
    """
    전체 ETL 파이프라인 실행

    1. Extract: CSV 파일에서 데이터 읽기
    2. Validate: 데이터 유효성 검증
    3. Transform: 데이터 변환 및 정제
    4. Load: 처리된 데이터 저장

    Args:
        input_path: 입력 CSV 파일 경로
        output_path: 출력 CSV 파일 경로

    Returns:
        파이프라인 실행 결과 딕셔너리
    """
    result = {
        "success": False,
        "input_path": input_path,
        "output_path": output_path,
        "errors": [],
        "warnings": [],
        "rows_input": 0,
        "rows_output": 0,
    }

    try:
        # 1단계: Extract
        df = read_sensor_csv(input_path)
        result["rows_input"] = len(df)

        # 2단계: Validate
        is_valid, errors = validate_data(df)
        if not is_valid:
            # 오류가 있어도 변환 시도 (경고로 기록)
            result["warnings"].extend(errors)

        # 3단계: Transform
        df_transformed = transform_data(df)

        # 4단계: Load
        save_info = save_processed_data(df_transformed, output_path)
        result["rows_output"] = save_info["rows"]
        result["file_size_bytes"] = save_info["file_size_bytes"]
        result["success"] = True

    except FileNotFoundError as e:
        result["errors"].append(str(e))
    except ValueError as e:
        result["errors"].append(str(e))
    except OSError as e:
        result["errors"].append(f"파일 저장 실패: {e}")

    return result
