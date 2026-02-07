"""
연습 문제 18 풀이: 파일 I/O와 데이터 파이프라인 테스트
"""
import pytest
import os

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

from pandas.testing import assert_frame_equal

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src_data_pipeline import (
    read_sensor_csv,
    validate_data,
    transform_data,
    save_processed_data,
    run_pipeline,
)


# ============================================================
# 연습 1: 손상된 CSV 파일 처리 테스트
# ============================================================

class TestCorruptedCSV:
    """손상되거나 비정상적인 CSV 파일 처리 테스트"""

    def test_completely_empty_file(self, tmp_path):
        """완전히 빈 파일 (0바이트) 처리"""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")

        # 빈 파일은 파싱 오류를 발생시켜야 함
        with pytest.raises((ValueError, Exception)):
            read_sensor_csv(str(empty_file))

    def test_header_only_csv(self, tmp_path):
        """헤더만 있는 CSV 파일 처리"""
        header_file = tmp_path / "header_only.csv"
        header_file.write_text("timestamp,sensor_id,temperature,vibration\n")

        result = read_sensor_csv(str(header_file))
        assert len(result) == 0
        assert "temperature" in result.columns

    def test_different_delimiter(self, tmp_path):
        """탭으로 구분된 파일 처리"""
        tab_file = tmp_path / "tab_separated.csv"
        tab_file.write_text(
            "timestamp\tsensor_id\ttemperature\tvibration\n"
            "2024-01-01\tS001\t25.0\t0.5\n"
        )

        # CSV 리더는 쉼표를 기대하므로 올바르게 파싱되지 않음
        result = read_sensor_csv(str(tab_file))
        # 탭 구분 파일은 하나의 열로 읽힐 수 있음
        assert "temperature" not in result.columns or len(result.columns) == 1


# ============================================================
# 연습 2: 대용량 데이터 파이프라인 테스트
# ============================================================

class TestLargeDataPipeline:
    """대용량 데이터 처리 테스트"""

    def test_pipeline_with_1000_rows(self, tmp_path):
        """1000행 데이터의 파이프라인 처리"""
        # 1000행의 CSV 데이터 생성
        lines = ["timestamp,sensor_id,temperature,vibration"]
        for i in range(1000):
            hour = i % 24
            day = (i // 24) + 1
            temp = 25.0 + (i % 10) * 0.5
            vib = 0.5 + (i % 5) * 0.1
            lines.append(
                f"2024-01-{day:02d} {hour:02d}:00:00,S001,{temp},{vib}"
            )

        input_file = tmp_path / "large_input.csv"
        input_file.write_text("\n".join(lines) + "\n")
        output_file = tmp_path / "large_output.csv"

        result = run_pipeline(str(input_file), str(output_file))

        assert result["success"] is True
        assert result["rows_input"] == 1000
        assert output_file.exists()

    def test_pipeline_output_row_count(self, tmp_path):
        """대용량 처리 후 행 수 보존 확인"""
        lines = ["timestamp,sensor_id,temperature,vibration"]
        for i in range(500):
            lines.append(
                f"2024-01-01 {i % 24:02d}:{i % 60:02d}:00,S001,{25.0 + i * 0.01},{0.5 + i * 0.001}"
            )

        input_file = tmp_path / "input_500.csv"
        input_file.write_text("\n".join(lines) + "\n")
        output_file = tmp_path / "output_500.csv"

        result = run_pipeline(str(input_file), str(output_file))

        assert result["success"] is True
        assert result["rows_output"] == 500


# ============================================================
# 연습 3: 에러 복구 테스트
# ============================================================

class TestErrorRecovery:
    """파이프라인 에러 처리 테스트"""

    def test_missing_input_file(self, tmp_path):
        """입력 파일이 없을 때의 에러 처리"""
        output_file = tmp_path / "output.csv"
        result = run_pipeline("/no/such/file.csv", str(output_file))

        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_pipeline_result_contains_error_info(self, tmp_path):
        """에러 발생 시 결과에 에러 정보가 포함되는지 확인"""
        result = run_pipeline("/nonexistent.csv", str(tmp_path / "out.csv"))

        # 필수 키가 모두 존재하는지 확인
        assert "success" in result
        assert "errors" in result
        assert "input_path" in result
        assert "output_path" in result

    def test_save_and_reload_consistency(self, tmp_path):
        """저장 후 다시 읽었을 때 데이터 일관성 확인"""
        original_df = pd.DataFrame({
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "sensor_id": ["S001", "S001", "S001"],
            "temperature": [25.0, 26.0, 27.0],
            "vibration": [0.5, 0.6, 0.7],
        })

        output_file = tmp_path / "consistency_test.csv"
        save_processed_data(original_df, str(output_file))

        # 다시 읽기
        loaded_df = pd.read_csv(str(output_file))

        # 열 이름 동일
        assert list(loaded_df.columns) == list(original_df.columns)

        # 수치 값 동일
        for col in ["temperature", "vibration"]:
            assert loaded_df[col].tolist() == original_df[col].tolist()

        # sensor_id 동일
        assert loaded_df["sensor_id"].tolist() == original_df["sensor_id"].tolist()
