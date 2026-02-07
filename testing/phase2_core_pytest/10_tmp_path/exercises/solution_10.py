"""
연습 문제 10 풀이: 임시 파일과 디렉토리 (tmp_path)

각 연습의 풀이를 확인하세요.
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
# 연습 1 풀이: CSV 센서 데이터 쓰기/읽기
# ============================================================

def test_csv_write_and_read(tmp_path):
    """CSV 파일 쓰기 후 읽기 테스트"""
    # 1. 센서 레코드 3개 생성
    records = [
        SensorRecord("TEMP-001", "2024-01-15T10:00:00", 72.5, "°C", "normal"),
        SensorRecord("VIBR-002", "2024-01-15T10:05:00", 5.3, "mm/s", "warning"),
        SensorRecord("PRESS-003", "2024-01-15T10:10:00", 145.0, "bar", "critical"),
    ]

    # 2. CSV 파일로 저장
    csv_file = tmp_path / "test_data.csv"
    write_sensor_csv(csv_file, records)

    # 3. 저장된 파일 읽기
    loaded = read_sensor_csv(csv_file)

    # 4. 검증
    assert len(loaded) == 3
    assert loaded[0].sensor_id == "TEMP-001"
    assert loaded[2].value == 145.0


def test_csv_file_not_found(tmp_path):
    """존재하지 않는 CSV 파일 읽기 시 에러"""
    nonexistent = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError):
        read_sensor_csv(nonexistent)


# ============================================================
# 연습 2 풀이: JSON 설정 파일
# ============================================================

def test_json_config_save_and_load(tmp_path):
    """JSON 설정 파일 저장/로드 테스트"""
    # 1. 장비 설정 딕셔너리
    config = {
        "equipment_name": "CNC Machine A",
        "thresholds": {
            "temperature": {"warning": 80, "critical": 100},
            "vibration": {"warning": 7, "critical": 10},
        },
        "sensors": ["TEMP-001", "VIBR-002", "PRESS-003"],
    }

    # 2. 저장
    config_file = tmp_path / "equipment_config.json"
    save_config_json(config_file, config)

    # 3. 로드
    loaded = load_config_json(config_file)

    # 4. 검증
    assert loaded == config
    assert loaded["equipment_name"] == "CNC Machine A"
    assert loaded["thresholds"]["temperature"]["warning"] == 80
    assert len(loaded["sensors"]) == 3


def test_json_config_with_korean(tmp_path):
    """한글이 포함된 JSON 설정 보존 테스트"""
    # 1. 한글 포함 설정
    config = {
        "장비명": "1번 모터",
        "위치": "A동 3층",
        "담당자": "김영수",
        "설명": "메인 구동 모터",
    }

    # 2. 저장 후 로드
    config_file = tmp_path / "korean_config.json"
    save_config_json(config_file, config)
    loaded = load_config_json(config_file)

    # 3. 한글 값 보존 확인
    assert loaded["장비명"] == "1번 모터"
    assert loaded["위치"] == "A동 3층"
    assert loaded["담당자"] == "김영수"


# ============================================================
# 연습 3 풀이: 센서 로그 파일 파싱
# ============================================================

def test_sensor_log_parsing(tmp_path):
    """센서 로그 파일 파싱 테스트"""
    # 1. 로그 내용 생성
    log_content = (
        "[2024-01-15 10:00:00] MOTOR-001 INFO: 모터 가동 시작\n"
        "[2024-01-15 10:05:00] MOTOR-001 WARNING: 온도 상승 감지\n"
        "[2024-01-15 10:10:00] PUMP-002 INFO: 펌프 정상 가동\n"
        "[2024-01-15 10:15:00] MOTOR-001 ERROR: 과열로 긴급 정지\n"
    )

    # 2. 로그 파일 저장
    log_file = tmp_path / "equipment.log"
    log_file.write_text(log_content, encoding="utf-8")

    # 3. 파싱
    result = process_sensor_log(log_file)

    # 4. 검증
    assert result["total_lines"] == 4
    assert result["info_count"] == 2
    assert result["warning_count"] == 1
    assert result["error_count"] == 1
    assert "MOTOR-001" in result["sensors"]
    assert "PUMP-002" in result["sensors"]
    assert len(result["sensors"]) == 2
