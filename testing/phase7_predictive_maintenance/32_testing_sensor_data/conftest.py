"""
센서 데이터 테스트를 위한 공유 픽스처 모듈

진동 센서 데이터 샘플과 임시 CSV 파일을 제공합니다.
"""

import pytest
import math
import os


@pytest.fixture
def sample_vibration_data():
    """정상 상태의 진동 센서 데이터 (float 리스트)"""
    # 간단한 사인파 형태의 진동 데이터 (100 샘플)
    return [math.sin(2 * math.pi * i / 50) for i in range(100)]


@pytest.fixture
def noisy_vibration_data():
    """노이즈와 이상치가 포함된 진동 데이터"""
    # 기본 사인파 + 일부 이상치
    data = [math.sin(2 * math.pi * i / 50) for i in range(100)]
    # 이상치 삽입
    data[10] = 100.0   # 극단적인 양의 이상치
    data[50] = -100.0   # 극단적인 음의 이상치
    return data


@pytest.fixture
def data_with_missing_values():
    """결측치(None)가 포함된 데이터"""
    data = [1.0, 2.0, None, None, 5.0, 6.0, None, 8.0, 9.0, 10.0]
    return data


@pytest.fixture
def sample_csv_content():
    """정상 CSV 파일 내용"""
    return (
        "timestamp,amplitude\n"
        "0.000,0.5\n"
        "0.001,1.2\n"
        "0.002,-0.3\n"
        "0.003,0.8\n"
        "0.004,-1.1\n"
    )


@pytest.fixture
def sample_csv_file(tmp_path, sample_csv_content):
    """정상 CSV 파일을 임시 디렉토리에 생성"""
    csv_file = tmp_path / "vibration_data.csv"
    csv_file.write_text(sample_csv_content, encoding="utf-8")
    return str(csv_file)


@pytest.fixture
def empty_csv_file(tmp_path):
    """빈 CSV 파일"""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")
    return str(csv_file)


@pytest.fixture
def header_only_csv_file(tmp_path):
    """헤더만 있는 CSV 파일"""
    csv_file = tmp_path / "header_only.csv"
    csv_file.write_text("timestamp,amplitude\n", encoding="utf-8")
    return str(csv_file)


@pytest.fixture
def malformed_csv_file(tmp_path):
    """데이터 타입이 잘못된 CSV 파일"""
    csv_file = tmp_path / "malformed.csv"
    csv_file.write_text(
        "timestamp,amplitude\n"
        "0.001,1.2\n"
        "invalid,abc\n",
        encoding="utf-8",
    )
    return str(csv_file)


@pytest.fixture
def missing_column_csv_file(tmp_path):
    """필수 컬럼이 누락된 CSV 파일"""
    csv_file = tmp_path / "missing_col.csv"
    csv_file.write_text(
        "timestamp,pressure\n"
        "0.001,1.2\n",
        encoding="utf-8",
    )
    return str(csv_file)


@pytest.fixture
def large_vibration_data():
    """대량 진동 데이터 (1000 샘플)"""
    # 여러 주파수 성분이 혼합된 신호
    data = []
    for i in range(1000):
        t = i / 1000.0
        # 기본 주파수 + 2차 고조파 + 약간의 변동
        value = (
            math.sin(2 * math.pi * 50 * t)
            + 0.5 * math.sin(2 * math.pi * 100 * t)
            + 0.1 * math.sin(2 * math.pi * 200 * t)
        )
        data.append(value)
    return data


@pytest.fixture
def constant_data():
    """일정한 값의 데이터 (변동 없음)"""
    return [5.0] * 50


@pytest.fixture
def single_value_data():
    """단일 값 데이터"""
    return [3.14]
