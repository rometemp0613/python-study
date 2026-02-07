"""
데이터 파이프라인 테스트

tmp_path 픽스처를 활용하여 CSV 파일 I/O와
ETL 파이프라인을 테스트합니다.
"""
import pytest
import os

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

from pandas.testing import assert_frame_equal

from src_data_pipeline import (
    read_sensor_csv,
    validate_data,
    transform_data,
    save_processed_data,
    run_pipeline,
    REQUIRED_COLUMNS,
)


# ============================================================
# 테스트 데이터 픽스처
# ============================================================

@pytest.fixture
def valid_csv_content():
    """유효한 센서 CSV 데이터"""
    return (
        "timestamp,sensor_id,temperature,vibration\n"
        "2024-01-01 00:00:00,S001,25.0,0.5\n"
        "2024-01-01 01:00:00,S001,26.1,0.6\n"
        "2024-01-01 02:00:00,S002,27.3,0.7\n"
    )


@pytest.fixture
def csv_with_nan():
    """NaN이 포함된 CSV 데이터"""
    return (
        "timestamp,sensor_id,temperature,vibration\n"
        "2024-01-01 00:00:00,S001,25.0,0.5\n"
        "2024-01-01 01:00:00,S001,,0.6\n"
        "2024-01-01 02:00:00,S001,27.0,0.7\n"
    )


@pytest.fixture
def csv_with_outliers():
    """이상치가 포함된 CSV 데이터"""
    return (
        "timestamp,sensor_id,temperature,vibration\n"
        "2024-01-01 00:00:00,S001,25.0,0.5\n"
        "2024-01-01 01:00:00,S001,999.0,0.6\n"
        "2024-01-01 02:00:00,S001,27.0,100.0\n"
    )


@pytest.fixture
def valid_csv_file(tmp_path, valid_csv_content):
    """유효한 CSV 파일 생성"""
    csv_file = tmp_path / "valid_sensor.csv"
    csv_file.write_text(valid_csv_content)
    return csv_file


@pytest.fixture
def valid_df():
    """유효한 센서 DataFrame"""
    return pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2024-01-01 00:00:00",
            "2024-01-01 01:00:00",
            "2024-01-01 02:00:00",
        ]),
        "sensor_id": ["S001", "S001", "S002"],
        "temperature": [25.0, 26.1, 27.3],
        "vibration": [0.5, 0.6, 0.7],
    })


# ============================================================
# read_sensor_csv 테스트
# ============================================================

class TestReadSensorCSV:
    """CSV 파일 읽기 테스트"""

    def test_read_valid_csv(self, valid_csv_file):
        """유효한 CSV 파일 읽기"""
        result = read_sensor_csv(str(valid_csv_file))
        assert len(result) == 3
        assert list(result.columns) == REQUIRED_COLUMNS

    def test_timestamp_parsed_as_datetime(self, valid_csv_file):
        """timestamp 열이 datetime으로 변환되는지 확인"""
        result = read_sensor_csv(str(valid_csv_file))
        assert pd.api.types.is_datetime64_any_dtype(result["timestamp"])

    def test_file_not_found(self):
        """존재하지 않는 파일"""
        with pytest.raises(FileNotFoundError):
            read_sensor_csv("/nonexistent/path/data.csv")

    def test_empty_csv(self, tmp_path):
        """빈 CSV 파일 (헤더만)"""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("timestamp,sensor_id,temperature,vibration\n")
        result = read_sensor_csv(str(csv_file))
        assert len(result) == 0
        assert list(result.columns) == REQUIRED_COLUMNS

    def test_csv_with_extra_columns(self, tmp_path):
        """추가 열이 있는 CSV 파일"""
        csv_file = tmp_path / "extra.csv"
        csv_file.write_text(
            "timestamp,sensor_id,temperature,vibration,pressure\n"
            "2024-01-01,S001,25.0,0.5,1013.0\n"
        )
        result = read_sensor_csv(str(csv_file))
        assert "pressure" in result.columns


# ============================================================
# validate_data 테스트
# ============================================================

class TestValidateData:
    """데이터 유효성 검증 테스트"""

    def test_valid_data(self, valid_df):
        """유효한 데이터 검증 통과"""
        is_valid, errors = validate_data(valid_df)
        assert is_valid
        assert len(errors) == 0

    def test_missing_required_column(self):
        """필수 열 누락 감지"""
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-01"]),
            "temperature": [25.0],
        })
        is_valid, errors = validate_data(df)
        assert not is_valid
        assert any("sensor_id" in err for err in errors)

    def test_out_of_range_temperature(self):
        """온도 범위 초과 감지"""
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-01"]),
            "sensor_id": ["S001"],
            "temperature": [999.0],  # 범위 밖
            "vibration": [0.5],
        })
        is_valid, errors = validate_data(df)
        assert not is_valid
        assert any("temperature" in err for err in errors)

    def test_negative_temperature_valid(self):
        """음수 온도는 유효 범위 내"""
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-01"]),
            "sensor_id": ["S001"],
            "temperature": [-10.0],  # 유효 범위: -40 ~ 150
            "vibration": [0.5],
        })
        is_valid, errors = validate_data(df)
        assert is_valid

    def test_high_nan_ratio_warning(self):
        """NaN 비율 50% 초과 경고"""
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "sensor_id": ["S001", "S001", "S001"],
            "temperature": [25.0, np.nan, np.nan],  # 66% NaN
            "vibration": [0.5, 0.6, 0.7],
        })
        is_valid, errors = validate_data(df)
        assert not is_valid
        assert any("NaN" in err for err in errors)

    def test_duplicate_rows_detected(self):
        """중복 행 감지"""
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-01", "2024-01-01"]),
            "sensor_id": ["S001", "S001"],
            "temperature": [25.0, 25.0],
            "vibration": [0.5, 0.5],
        })
        is_valid, errors = validate_data(df)
        assert not is_valid
        assert any("중복" in err for err in errors)


# ============================================================
# transform_data 테스트
# ============================================================

class TestTransformData:
    """데이터 변환 테스트"""

    def test_removes_duplicates(self):
        """중복 행 제거"""
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-01", "2024-01-01"]),
            "sensor_id": ["S001", "S001"],
            "temperature": [25.0, 25.0],
            "vibration": [0.5, 0.5],
        })
        result = transform_data(df)
        assert len(result) == 1

    def test_interpolates_nan(self):
        """NaN 값 보간"""
        df = pd.DataFrame({
            "timestamp": pd.to_datetime([
                "2024-01-01", "2024-01-02", "2024-01-03"
            ]),
            "sensor_id": ["S001", "S001", "S001"],
            "temperature": [20.0, np.nan, 30.0],
            "vibration": [0.5, 0.6, 0.7],
        })
        result = transform_data(df)
        assert result["temperature"].isna().sum() == 0
        # 선형 보간: 20.0과 30.0 사이 = 25.0
        assert result["temperature"].iloc[1] == pytest.approx(25.0)

    def test_clips_out_of_range_values(self):
        """범위 밖 값 클리핑"""
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-01"]),
            "sensor_id": ["S001"],
            "temperature": [999.0],  # 최대 150.0으로 클리핑
            "vibration": [0.5],
        })
        result = transform_data(df)
        assert result["temperature"].iloc[0] == 150.0

    def test_sorts_by_timestamp(self):
        """타임스탬프 기준 정렬"""
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-03", "2024-01-01", "2024-01-02"]),
            "sensor_id": ["S001", "S001", "S001"],
            "temperature": [27.0, 25.0, 26.0],
            "vibration": [0.7, 0.5, 0.6],
        })
        result = transform_data(df)
        assert result["timestamp"].is_monotonic_increasing
        assert result["temperature"].iloc[0] == 25.0  # 가장 이른 시간의 값

    def test_preserves_valid_data(self, valid_df):
        """유효한 데이터가 보존되는지 확인"""
        result = transform_data(valid_df)
        assert len(result) == len(valid_df)

    def test_returns_copy(self, valid_df):
        """원본 데이터가 변경되지 않는지 확인"""
        original = valid_df.copy()
        _ = transform_data(valid_df)
        assert_frame_equal(valid_df, original)


# ============================================================
# save_processed_data 테스트
# ============================================================

class TestSaveProcessedData:
    """데이터 저장 테스트"""

    def test_save_creates_file(self, tmp_path, valid_df):
        """파일이 정상적으로 생성되는지 확인"""
        output_file = tmp_path / "output.csv"
        result = save_processed_data(valid_df, str(output_file))
        assert output_file.exists()
        assert result["rows"] == 3

    def test_save_file_readable(self, tmp_path, valid_df):
        """저장된 파일이 다시 읽히는지 확인"""
        output_file = tmp_path / "output.csv"
        save_processed_data(valid_df, str(output_file))

        # 저장된 파일 다시 읽기
        loaded = pd.read_csv(str(output_file))
        assert len(loaded) == len(valid_df)
        assert list(loaded.columns) == list(valid_df.columns)

    def test_save_creates_directory(self, tmp_path, valid_df):
        """출력 디렉토리가 없으면 자동 생성"""
        output_file = tmp_path / "subdir" / "nested" / "output.csv"
        save_processed_data(valid_df, str(output_file))
        assert output_file.exists()

    def test_save_returns_metadata(self, tmp_path, valid_df):
        """저장 결과 메타데이터 확인"""
        output_file = tmp_path / "output.csv"
        result = save_processed_data(valid_df, str(output_file))
        assert "rows" in result
        assert "columns" in result
        assert "file_size_bytes" in result
        assert result["file_size_bytes"] > 0


# ============================================================
# run_pipeline 엔드-투-엔드 테스트
# ============================================================

class TestRunPipeline:
    """전체 ETL 파이프라인 테스트"""

    def test_successful_pipeline(self, tmp_path, valid_csv_content):
        """정상적인 파이프라인 실행"""
        input_file = tmp_path / "input.csv"
        input_file.write_text(valid_csv_content)
        output_file = tmp_path / "output.csv"

        result = run_pipeline(str(input_file), str(output_file))

        assert result["success"] is True
        assert result["rows_input"] == 3
        assert result["rows_output"] == 3
        assert output_file.exists()

    def test_pipeline_handles_nan(self, tmp_path, csv_with_nan):
        """NaN이 포함된 데이터 파이프라인"""
        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_with_nan)
        output_file = tmp_path / "output.csv"

        result = run_pipeline(str(input_file), str(output_file))

        assert result["success"] is True
        # 출력 파일에 NaN이 없어야 함
        output_df = pd.read_csv(str(output_file))
        assert output_df["temperature"].isna().sum() == 0

    def test_pipeline_clips_outliers(self, tmp_path, csv_with_outliers):
        """이상치가 포함된 데이터 파이프라인"""
        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_with_outliers)
        output_file = tmp_path / "output.csv"

        result = run_pipeline(str(input_file), str(output_file))

        assert result["success"] is True
        output_df = pd.read_csv(str(output_file))
        assert output_df["temperature"].max() <= 150.0
        assert output_df["vibration"].max() <= 50.0

    def test_pipeline_file_not_found(self, tmp_path):
        """입력 파일이 없을 때"""
        output_file = tmp_path / "output.csv"
        result = run_pipeline("/nonexistent/input.csv", str(output_file))

        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_pipeline_preserves_all_rows(self, tmp_path):
        """파이프라인이 행을 잃지 않는지 확인"""
        csv_content = "timestamp,sensor_id,temperature,vibration\n"
        for i in range(100):
            csv_content += f"2024-01-01 {i % 24:02d}:00:00,S001,{25.0 + i * 0.1},{0.5 + i * 0.01}\n"

        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_content)
        output_file = tmp_path / "output.csv"

        result = run_pipeline(str(input_file), str(output_file))

        assert result["success"] is True
        assert result["rows_output"] == 100
