"""
연습 문제 18: 파일 I/O와 데이터 파이프라인 테스트

tmp_path를 활용하여 파일 I/O와 ETL 파이프라인을 테스트하세요.
각 TODO 주석을 실제 테스트 코드로 교체하세요.
"""
import pytest
import os

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

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
        pytest.skip(
            "TODO: 빈 파일을 생성하고 read_sensor_csv가 적절히 처리하는지 "
            "(예외 발생 또는 빈 DataFrame 반환) 테스트하세요"
        )

    def test_header_only_csv(self, tmp_path):
        """헤더만 있는 CSV 파일 처리"""
        pytest.skip(
            "TODO: 헤더만 있는 CSV를 생성하고 빈 DataFrame이 반환되는지 확인하세요"
        )

    def test_different_delimiter(self, tmp_path):
        """탭으로 구분된 파일 처리"""
        pytest.skip(
            "TODO: 탭 구분자로 된 파일을 만들고 read_sensor_csv의 동작을 테스트하세요. "
            "올바르게 읽히지 않을 수 있음을 확인하세요"
        )


# ============================================================
# 연습 2: 대용량 데이터 파이프라인 테스트
# ============================================================

class TestLargeDataPipeline:
    """대용량 데이터 처리 테스트"""

    def test_pipeline_with_1000_rows(self, tmp_path):
        """1000행 데이터의 파이프라인 처리"""
        pytest.skip(
            "TODO: 1000행의 CSV 데이터를 프로그래밍적으로 생성하고, "
            "파이프라인을 통해 정상적으로 처리되는지 확인하세요. "
            "힌트: for 루프로 CSV 문자열 생성"
        )

    def test_pipeline_output_row_count(self, tmp_path):
        """대용량 처리 후 행 수 보존 확인"""
        pytest.skip(
            "TODO: 500행 데이터 (NaN 없음)를 파이프라인에 통과시키고 "
            "출력 행 수가 동일한지 확인하세요"
        )


# ============================================================
# 연습 3: 에러 복구 테스트
# ============================================================

class TestErrorRecovery:
    """파이프라인 에러 처리 테스트"""

    def test_missing_input_file(self, tmp_path):
        """입력 파일이 없을 때의 에러 처리"""
        pytest.skip(
            "TODO: 존재하지 않는 입력 경로로 run_pipeline을 호출하고 "
            "result['success']가 False인지, errors에 메시지가 있는지 확인하세요"
        )

    def test_pipeline_result_contains_error_info(self, tmp_path):
        """에러 발생 시 결과에 에러 정보가 포함되는지 확인"""
        pytest.skip(
            "TODO: 파이프라인 실패 시 result 딕셔너리에 "
            "'success', 'errors' 키가 모두 있는지 확인하세요"
        )

    def test_save_and_reload_consistency(self, tmp_path):
        """저장 후 다시 읽었을 때 데이터 일관성 확인"""
        pytest.skip(
            "TODO: DataFrame을 저장한 후 다시 읽어서 "
            "원래 데이터와 값이 동일한지 (열 이름, 값) 확인하세요"
        )
