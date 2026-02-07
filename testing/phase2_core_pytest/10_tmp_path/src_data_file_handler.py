"""
데이터 파일 처리 모듈

센서 데이터 CSV, 설정 JSON, 로그 파일을 읽고 쓰는 기능을 제공한다.
예지보전 시스템에서 다양한 파일 포맷의 입출력을 담당한다.
"""

import csv
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class SensorRecord:
    """센서 측정 레코드"""
    sensor_id: str
    timestamp: str       # ISO 형식 문자열
    value: float
    unit: str
    status: str


def write_sensor_csv(filepath: Path, records: list[SensorRecord]) -> int:
    """
    센서 데이터를 CSV 파일로 저장한다.

    Args:
        filepath: 저장할 파일 경로
        records: 센서 레코드 리스트

    Returns:
        저장된 레코드 수

    Raises:
        ValueError: records가 빈 리스트일 때
    """
    if not records:
        raise ValueError("저장할 레코드가 없습니다")

    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # 헤더 행 쓰기
        writer.writerow(["sensor_id", "timestamp", "value", "unit", "status"])
        # 데이터 행 쓰기
        for record in records:
            writer.writerow([
                record.sensor_id,
                record.timestamp,
                record.value,
                record.unit,
                record.status,
            ])

    return len(records)


def read_sensor_csv(filepath: Path) -> list[SensorRecord]:
    """
    CSV 파일에서 센서 데이터를 읽어온다.

    Args:
        filepath: 읽을 파일 경로

    Returns:
        SensorRecord 리스트

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        ValueError: CSV 형식이 잘못되었을 때
    """
    if not filepath.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")

    records = []
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # 필수 컬럼 확인
        required_columns = {"sensor_id", "timestamp", "value", "unit", "status"}
        if reader.fieldnames is None:
            raise ValueError("CSV 파일에 헤더가 없습니다")

        missing = required_columns - set(reader.fieldnames)
        if missing:
            raise ValueError(f"필수 컬럼이 없습니다: {missing}")

        for row in reader:
            try:
                records.append(SensorRecord(
                    sensor_id=row["sensor_id"],
                    timestamp=row["timestamp"],
                    value=float(row["value"]),
                    unit=row["unit"],
                    status=row["status"],
                ))
            except (ValueError, KeyError) as e:
                raise ValueError(f"CSV 데이터 파싱 오류: {e}")

    return records


def save_config_json(filepath: Path, config: dict) -> None:
    """
    설정을 JSON 파일로 저장한다.

    Args:
        filepath: 저장할 파일 경로
        config: 설정 딕셔너리
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_config_json(filepath: Path) -> dict:
    """
    JSON 파일에서 설정을 읽어온다.

    Args:
        filepath: 읽을 파일 경로

    Returns:
        설정 딕셔너리

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        json.JSONDecodeError: JSON 형식이 잘못되었을 때
    """
    if not filepath.exists():
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {filepath}")

    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def process_sensor_log(filepath: Path) -> dict:
    """
    센서 로그 파일을 파싱하여 요약 정보를 반환한다.

    로그 파일 형식 (각 줄):
    [YYYY-MM-DD HH:MM:SS] SENSOR_ID LEVEL: message

    예:
    [2024-01-15 10:00:00] TEMP-001 INFO: 온도 측정 72.5°C
    [2024-01-15 10:05:00] TEMP-001 WARNING: 온도 상승 85.0°C
    [2024-01-15 10:10:00] VIBR-002 ERROR: 진동 이상 감지 12.5mm/s

    Args:
        filepath: 로그 파일 경로

    Returns:
        dict: {
            "total_lines": int,
            "info_count": int,
            "warning_count": int,
            "error_count": int,
            "sensors": list[str],  # 고유 센서 ID 목록
        }

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
    """
    if not filepath.exists():
        raise FileNotFoundError(f"로그 파일을 찾을 수 없습니다: {filepath}")

    info_count = 0
    warning_count = 0
    error_count = 0
    sensors = set()
    total_lines = 0

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            total_lines += 1

            # 로그 파싱: [timestamp] sensor_id LEVEL: message
            try:
                # 대괄호 안의 타임스탬프 건너뛰기
                after_bracket = line.split("] ", 1)[1]
                parts = after_bracket.split(" ", 1)
                sensor_id = parts[0]
                sensors.add(sensor_id)

                level_part = parts[1].split(":", 1)[0].strip()

                if level_part == "INFO":
                    info_count += 1
                elif level_part == "WARNING":
                    warning_count += 1
                elif level_part == "ERROR":
                    error_count += 1
            except (IndexError, ValueError):
                # 형식에 맞지 않는 줄은 무시
                continue

    return {
        "total_lines": total_lines,
        "info_count": info_count,
        "warning_count": warning_count,
        "error_count": error_count,
        "sensors": sorted(sensors),
    }


def merge_sensor_files(input_dir: Path, output_file: Path) -> int:
    """
    디렉토리 내의 모든 센서 CSV 파일을 하나로 합친다.

    Args:
        input_dir: CSV 파일이 있는 디렉토리
        output_file: 합쳐진 결과를 저장할 파일

    Returns:
        총 합쳐진 레코드 수

    Raises:
        FileNotFoundError: 디렉토리가 존재하지 않을 때
        ValueError: CSV 파일이 없을 때
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"디렉토리를 찾을 수 없습니다: {input_dir}")

    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise ValueError(f"CSV 파일이 없습니다: {input_dir}")

    all_records = []
    for csv_file in csv_files:
        records = read_sensor_csv(csv_file)
        all_records.extend(records)

    write_sensor_csv(output_file, all_records)
    return len(all_records)
