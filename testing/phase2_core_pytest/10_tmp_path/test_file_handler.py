"""
임시 파일/디렉토리 데모 테스트

tmp_path와 tmp_path_factory를 활용한 파일 I/O 테스트:
1. CSV 센서 데이터 읽기/쓰기
2. JSON 설정 파일 저장/로드
3. 로그 파일 파싱
4. 파일 병합
5. 디렉토리 구조 테스트
"""

import pytest
import json
from pathlib import Path
from src_data_file_handler import (
    SensorRecord,
    write_sensor_csv,
    read_sensor_csv,
    save_config_json,
    load_config_json,
    process_sensor_log,
    merge_sensor_files,
)


# ============================================================
# 공통 Fixture
# ============================================================

@pytest.fixture
def sample_records():
    """테스트용 센서 레코드 리스트"""
    return [
        SensorRecord("TEMP-001", "2024-01-15T10:00:00", 72.5, "°C", "normal"),
        SensorRecord("TEMP-001", "2024-01-15T10:05:00", 85.0, "°C", "warning"),
        SensorRecord("VIBR-002", "2024-01-15T10:10:00", 3.2, "mm/s", "normal"),
        SensorRecord("PRESS-003", "2024-01-15T10:15:00", 150.0, "bar", "critical"),
    ]


@pytest.fixture
def sample_config():
    """테스트용 설정 딕셔너리"""
    return {
        "system_name": "예지보전 모니터링 시스템",
        "version": "1.0.0",
        "thresholds": {
            "temperature": {"warning": 80.0, "critical": 100.0},
            "vibration": {"warning": 7.0, "critical": 10.0},
            "pressure": {"warning": 120.0, "critical": 150.0},
        },
        "sensors": [
            {"id": "TEMP-001", "type": "temperature", "location": "모터 1"},
            {"id": "VIBR-002", "type": "vibration", "location": "베어링 A"},
        ],
    }


@pytest.fixture
def sample_log_content():
    """테스트용 로그 파일 내용"""
    return (
        "[2024-01-15 10:00:00] TEMP-001 INFO: 온도 측정 72.5°C\n"
        "[2024-01-15 10:05:00] TEMP-001 WARNING: 온도 상승 85.0°C\n"
        "[2024-01-15 10:10:00] VIBR-002 INFO: 진동 측정 3.2mm/s\n"
        "[2024-01-15 10:15:00] PRESS-003 ERROR: 압력 이상 감지 150.0bar\n"
        "[2024-01-15 10:20:00] TEMP-001 INFO: 온도 안정 75.0°C\n"
    )


# ============================================================
# 1. CSV 파일 테스트
# ============================================================

class TestCSVOperations:
    """CSV 파일 읽기/쓰기 테스트 (tmp_path 활용)"""

    def test_write_csv_creates_file(self, tmp_path, sample_records):
        """CSV 파일이 올바르게 생성되는지 확인"""
        csv_file = tmp_path / "sensor_data.csv"
        count = write_sensor_csv(csv_file, sample_records)

        assert csv_file.exists()
        assert count == 4

    def test_write_and_read_csv(self, tmp_path, sample_records):
        """CSV 쓰기 후 읽기가 올바르게 동작하는지 확인"""
        csv_file = tmp_path / "sensor_data.csv"
        write_sensor_csv(csv_file, sample_records)

        # 읽기
        loaded_records = read_sensor_csv(csv_file)

        assert len(loaded_records) == 4
        assert loaded_records[0].sensor_id == "TEMP-001"
        assert loaded_records[0].value == 72.5
        assert loaded_records[3].status == "critical"

    def test_write_csv_with_subdirectory(self, tmp_path, sample_records):
        """하위 디렉토리에 CSV 파일 생성"""
        csv_file = tmp_path / "data" / "2024" / "sensor_data.csv"
        write_sensor_csv(csv_file, sample_records)

        assert csv_file.exists()
        assert (tmp_path / "data" / "2024").is_dir()

    def test_read_csv_file_not_found(self, tmp_path):
        """존재하지 않는 CSV 파일 읽기 시 에러"""
        csv_file = tmp_path / "nonexistent.csv"
        with pytest.raises(FileNotFoundError, match="파일을 찾을 수 없습니다"):
            read_sensor_csv(csv_file)

    def test_write_csv_empty_records(self, tmp_path):
        """빈 레코드 리스트로 쓰기 시 에러"""
        csv_file = tmp_path / "empty.csv"
        with pytest.raises(ValueError, match="저장할 레코드가 없습니다"):
            write_sensor_csv(csv_file, [])

    def test_read_csv_invalid_format(self, tmp_path):
        """잘못된 형식의 CSV 파일 읽기 시 에러"""
        csv_file = tmp_path / "invalid.csv"
        csv_file.write_text("col_a,col_b\n1,2\n")

        with pytest.raises(ValueError, match="필수 컬럼이 없습니다"):
            read_sensor_csv(csv_file)


# ============================================================
# 2. JSON 설정 파일 테스트
# ============================================================

class TestJSONConfig:
    """JSON 설정 파일 저장/로드 테스트"""

    def test_save_config_creates_file(self, tmp_path, sample_config):
        """JSON 설정 파일이 올바르게 생성되는지 확인"""
        config_file = tmp_path / "config.json"
        save_config_json(config_file, sample_config)

        assert config_file.exists()

    def test_save_and_load_config(self, tmp_path, sample_config):
        """JSON 저장 후 로드가 올바르게 동작하는지 확인"""
        config_file = tmp_path / "config.json"
        save_config_json(config_file, sample_config)

        loaded = load_config_json(config_file)

        assert loaded["system_name"] == "예지보전 모니터링 시스템"
        assert loaded["thresholds"]["temperature"]["warning"] == 80.0
        assert len(loaded["sensors"]) == 2

    def test_config_korean_text_preserved(self, tmp_path, sample_config):
        """한글 텍스트가 올바르게 보존되는지 확인"""
        config_file = tmp_path / "config.json"
        save_config_json(config_file, sample_config)

        # 파일 내용을 직접 읽어서 한글 확인
        content = config_file.read_text(encoding="utf-8")
        assert "예지보전" in content
        assert "모터 1" in content

    def test_load_config_file_not_found(self, tmp_path):
        """존재하지 않는 설정 파일 로드 시 에러"""
        config_file = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError, match="설정 파일을 찾을 수 없습니다"):
            load_config_json(config_file)

    def test_load_config_invalid_json(self, tmp_path):
        """잘못된 JSON 파일 로드 시 에러"""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("이것은 JSON이 아닙니다 {{{")

        with pytest.raises(json.JSONDecodeError):
            load_config_json(config_file)

    def test_config_in_subdirectory(self, tmp_path, sample_config):
        """하위 디렉토리에 설정 파일 저장"""
        config_file = tmp_path / "settings" / "production" / "config.json"
        save_config_json(config_file, sample_config)

        loaded = load_config_json(config_file)
        assert loaded["version"] == "1.0.0"


# ============================================================
# 3. 로그 파일 파싱 테스트
# ============================================================

class TestLogProcessing:
    """센서 로그 파일 파싱 테스트"""

    def test_process_sensor_log(self, tmp_path, sample_log_content):
        """로그 파일을 파싱하여 요약 정보 확인"""
        log_file = tmp_path / "sensor.log"
        log_file.write_text(sample_log_content, encoding="utf-8")

        result = process_sensor_log(log_file)

        assert result["total_lines"] == 5
        assert result["info_count"] == 3
        assert result["warning_count"] == 1
        assert result["error_count"] == 1
        assert "TEMP-001" in result["sensors"]
        assert "VIBR-002" in result["sensors"]
        assert "PRESS-003" in result["sensors"]

    def test_process_empty_log(self, tmp_path):
        """빈 로그 파일 처리"""
        log_file = tmp_path / "empty.log"
        log_file.write_text("", encoding="utf-8")

        result = process_sensor_log(log_file)

        assert result["total_lines"] == 0
        assert result["info_count"] == 0
        assert result["warning_count"] == 0
        assert result["error_count"] == 0

    def test_process_log_file_not_found(self, tmp_path):
        """존재하지 않는 로그 파일 처리 시 에러"""
        log_file = tmp_path / "nonexistent.log"
        with pytest.raises(FileNotFoundError, match="로그 파일을 찾을 수 없습니다"):
            process_sensor_log(log_file)

    def test_process_log_with_only_errors(self, tmp_path):
        """에러만 있는 로그 파일 처리"""
        log_content = (
            "[2024-01-15 10:00:00] MOTOR-001 ERROR: 과열 감지\n"
            "[2024-01-15 10:01:00] MOTOR-001 ERROR: 긴급 정지\n"
        )
        log_file = tmp_path / "errors.log"
        log_file.write_text(log_content, encoding="utf-8")

        result = process_sensor_log(log_file)

        assert result["error_count"] == 2
        assert result["info_count"] == 0
        assert result["sensors"] == ["MOTOR-001"]


# ============================================================
# 4. 파일 병합 테스트
# ============================================================

class TestFileMerging:
    """여러 CSV 파일 병합 테스트"""

    def test_merge_sensor_files(self, tmp_path):
        """여러 센서 파일을 하나로 합치기"""
        # 입력 디렉토리와 파일 생성
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # 센서별 CSV 파일 생성
        records_a = [
            SensorRecord("TEMP-001", "2024-01-15T10:00:00", 72.5, "°C", "normal"),
        ]
        records_b = [
            SensorRecord("VIBR-002", "2024-01-15T10:00:00", 3.2, "mm/s", "normal"),
            SensorRecord("VIBR-002", "2024-01-15T10:05:00", 4.1, "mm/s", "normal"),
        ]

        write_sensor_csv(input_dir / "temp.csv", records_a)
        write_sensor_csv(input_dir / "vibr.csv", records_b)

        # 병합
        output_file = tmp_path / "merged.csv"
        total = merge_sensor_files(input_dir, output_file)

        assert total == 3
        assert output_file.exists()

        # 병합 결과 확인
        merged_records = read_sensor_csv(output_file)
        assert len(merged_records) == 3

    def test_merge_no_csv_files(self, tmp_path):
        """CSV 파일이 없는 디렉토리에서 병합 시 에러"""
        input_dir = tmp_path / "empty_dir"
        input_dir.mkdir()

        output_file = tmp_path / "merged.csv"
        with pytest.raises(ValueError, match="CSV 파일이 없습니다"):
            merge_sensor_files(input_dir, output_file)


# ============================================================
# 5. tmp_path_factory 테스트
# ============================================================

@pytest.fixture(scope="module")
def module_data_dir(tmp_path_factory):
    """모듈 수준에서 공유하는 데이터 디렉토리"""
    data_dir = tmp_path_factory.mktemp("module_data")
    # 공유 데이터 파일 생성
    config = {"module_level": True, "shared": True}
    config_file = data_dir / "shared_config.json"
    save_config_json(config_file, config)
    return data_dir


class TestTmpPathFactory:
    """tmp_path_factory 사용 예제"""

    def test_module_dir_exists(self, module_data_dir):
        """모듈 수준 디렉토리가 존재하는지 확인"""
        assert module_data_dir.exists()
        assert module_data_dir.is_dir()

    def test_shared_config_accessible(self, module_data_dir):
        """모듈 수준에서 생성한 설정 파일에 접근 가능"""
        config = load_config_json(module_data_dir / "shared_config.json")
        assert config["module_level"] is True
        assert config["shared"] is True

    def test_can_add_files_to_module_dir(self, module_data_dir):
        """모듈 디렉토리에 파일 추가 가능"""
        new_file = module_data_dir / "additional.txt"
        new_file.write_text("추가 데이터")
        assert new_file.exists()


# ============================================================
# 6. 디렉토리 구조 테스트
# ============================================================

class TestDirectoryStructure:
    """복잡한 디렉토리 구조 테스트"""

    def test_create_sensor_directory_tree(self, tmp_path, sample_records):
        """센서별 디렉토리 구조 생성 및 파일 분배"""
        # 센서별 디렉토리 생성
        for record in sample_records:
            sensor_dir = tmp_path / "sensors" / record.sensor_id
            sensor_dir.mkdir(parents=True, exist_ok=True)

            # 각 센서 디렉토리에 개별 파일 저장
            data_file = sensor_dir / "latest.csv"
            write_sensor_csv(data_file, [record])

        # 디렉토리 구조 확인
        sensor_dirs = list((tmp_path / "sensors").iterdir())
        assert len(sensor_dirs) == 3  # TEMP-001, VIBR-002, PRESS-003

        # 각 디렉토리에 파일이 있는지 확인
        for sensor_dir in sensor_dirs:
            assert (sensor_dir / "latest.csv").exists()

    def test_glob_pattern_matching(self, tmp_path):
        """glob 패턴으로 파일 찾기"""
        # 여러 파일 생성
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        for name in ["temp_001.csv", "temp_002.csv", "vibr_001.csv", "config.json"]:
            (data_dir / name).write_text("test content")

        # glob으로 CSV 파일만 찾기
        csv_files = list(data_dir.glob("*.csv"))
        assert len(csv_files) == 3

        # glob으로 temp_ 파일만 찾기
        temp_files = list(data_dir.glob("temp_*.csv"))
        assert len(temp_files) == 2
