"""
Lesson 17 테스트 픽스처 모음

센서 데이터 전처리 테스트에 사용되는 샘플 DataFrame을 제공합니다.
pandas/numpy가 설치되어 있지 않으면 이 모듈의 테스트는 건너뜁니다.
"""
import pytest

# pandas/numpy가 없으면 모든 테스트를 건너뜀
pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")


@pytest.fixture
def sample_sensor_df():
    """기본 센서 데이터 - NaN과 이상치 포함"""
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=10, freq="h"),
        "temperature": [
            25.0, 26.1, np.nan, 27.3, 200.0,
            25.5, 26.0, np.nan, 25.8, 26.2,
        ],
        "vibration": [
            0.50, 0.60, 0.55, 0.70, 0.65,
            0.58, 0.62, 0.59, 0.61, 0.63,
        ],
    })


@pytest.fixture
def clean_sensor_df():
    """정제된 센서 데이터 - NaN 및 이상치 없음"""
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=8, freq="h"),
        "temperature": [25.0, 26.1, 27.3, 25.5, 26.0, 25.8, 26.2, 25.9],
        "vibration": [0.50, 0.60, 0.70, 0.58, 0.62, 0.59, 0.61, 0.63],
    })


@pytest.fixture
def empty_sensor_df():
    """빈 센서 DataFrame - 열 구조만 존재"""
    return pd.DataFrame(
        columns=["timestamp", "temperature", "vibration"]
    )


@pytest.fixture
def single_row_df():
    """단일 행 DataFrame - 엣지 케이스 테스트용"""
    return pd.DataFrame({
        "timestamp": [pd.Timestamp("2024-01-01")],
        "temperature": [25.0],
        "vibration": [0.5],
    })


@pytest.fixture
def all_nan_df():
    """모든 수치 값이 NaN인 DataFrame"""
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
        "temperature": [np.nan] * 5,
        "vibration": [np.nan] * 5,
    })


@pytest.fixture
def temperature_df():
    """온도 센서 전용 데이터"""
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
        "temperature": [25.0, 26.0, 27.0, 28.0, 29.0],
    })


@pytest.fixture
def vibration_df():
    """진동 센서 전용 데이터"""
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
        "vibration": [0.5, 0.6, 0.7, 0.8, 0.9],
    })


@pytest.fixture
def mismatched_timestamp_df():
    """타임스탬프가 불일치하는 두 센서 데이터"""
    df1 = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
        "temperature": [25.0, 26.0, 27.0, 28.0, 29.0],
    })
    df2 = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01 02:00", periods=5, freq="h"),
        "vibration": [0.5, 0.6, 0.7, 0.8, 0.9],
    })
    return df1, df2
