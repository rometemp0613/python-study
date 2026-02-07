"""
연습 문제 10: 임시 파일과 디렉토리 (tmp_path)

아래 TODO를 완성하여 파일 I/O 테스트를 작성하세요.
pytest.skip()을 제거하고 코드를 구현하세요.
"""

import pytest
import json
import sys
import os
from pathlib import Path

# 상위 디렉토리의 모듈을 import하기 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_data_file_handler import (
    SensorRecord,
    write_sensor_csv,
    read_sensor_csv,
    save_config_json,
    load_config_json,
    process_sensor_log,
)


# ============================================================
# 연습 1: CSV 센서 데이터 쓰기/읽기
# ============================================================

def test_csv_write_and_read(tmp_path):
    """
    TODO: CSV 파일 쓰기 후 읽기 테스트를 작성하세요.

    요구사항:
    1. SensorRecord 3개를 생성한다 (센서 ID, 값, 상태가 각각 다른 것)
    2. tmp_path에 "test_data.csv" 파일로 저장한다
    3. 저장된 파일을 다시 읽어온다
    4. 레코드 수, 첫 번째 레코드의 sensor_id, 마지막 레코드의 value를 검증한다
    """
    pytest.skip("TODO: CSV 쓰기/읽기 테스트를 구현하세요")


def test_csv_file_not_found(tmp_path):
    """
    TODO: 존재하지 않는 CSV 파일을 읽을 때 에러가 발생하는지 테스트하세요.

    요구사항:
    1. tmp_path에 존재하지 않는 파일 경로를 만든다
    2. read_sensor_csv를 호출한다
    3. FileNotFoundError가 발생하는지 확인한다
    """
    pytest.skip("TODO: FileNotFoundError 테스트를 구현하세요")


# ============================================================
# 연습 2: JSON 설정 파일
# ============================================================

def test_json_config_save_and_load(tmp_path):
    """
    TODO: JSON 설정 파일 저장/로드 테스트를 작성하세요.

    요구사항:
    1. 장비 설정 딕셔너리를 만든다 (장비 이름, 임계값, 센서 목록 포함)
    2. tmp_path에 "equipment_config.json"으로 저장한다
    3. 저장된 파일을 다시 로드한다
    4. 원본과 로드된 데이터가 동일한지 검증한다
    """
    pytest.skip("TODO: JSON 설정 파일 테스트를 구현하세요")


def test_json_config_with_korean(tmp_path):
    """
    TODO: 한글이 포함된 JSON 설정이 올바르게 저장/로드되는지 테스트하세요.

    요구사항:
    1. 한글 키와 값을 포함하는 설정 딕셔너리를 만든다
    2. 저장 후 로드한다
    3. 한글 값이 보존되었는지 확인한다
    """
    pytest.skip("TODO: 한글 JSON 테스트를 구현하세요")


# ============================================================
# 연습 3: 센서 로그 파일 파싱
# ============================================================

def test_sensor_log_parsing(tmp_path):
    """
    TODO: 센서 로그 파일을 생성하고 파싱하는 테스트를 작성하세요.

    요구사항:
    1. 다음 형식의 로그를 생성한다:
       [2024-01-15 10:00:00] MOTOR-001 INFO: 모터 가동 시작
       [2024-01-15 10:05:00] MOTOR-001 WARNING: 온도 상승 감지
       [2024-01-15 10:10:00] PUMP-002 INFO: 펌프 정상 가동
       [2024-01-15 10:15:00] MOTOR-001 ERROR: 과열로 긴급 정지
    2. tmp_path에 "equipment.log"로 저장한다
    3. process_sensor_log로 파싱한다
    4. total_lines, info/warning/error 개수, 센서 목록을 검증한다
    """
    pytest.skip("TODO: 로그 파일 파싱 테스트를 구현하세요")
