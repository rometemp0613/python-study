"""
데이터 처리 모듈 테스트

conftest.py의 공유 fixture를 활용하고,
체계적인 네이밍과 구조를 따르는 테스트 예제.
"""

import pytest
from src_data_processor import (
    normalize_readings,
    filter_outliers,
    aggregate_sensor_data,
    check_thresholds,
    generate_summary_report,
)


# ============================================================
# 정규화 테스트
# ============================================================

class TestNormalizeReadings:
    """센서 읽기 값 정규화 테스트"""

    def test_기본_정규화(self):
        """기본적인 0~1 정규화가 올바르게 동작해야 한다"""
        readings = [0, 25, 50, 75, 100]
        result = normalize_readings(readings)
        assert result == pytest.approx([0.0, 0.25, 0.5, 0.75, 1.0])

    def test_사용자_정의_범위(self):
        """min_val, max_val을 지정하여 정규화"""
        readings = [50, 75, 100]
        result = normalize_readings(readings, min_val=0, max_val=200)
        assert result == pytest.approx([0.25, 0.375, 0.5])

    def test_동일값_정규화(self):
        """모든 값이 같으면 0.5로 정규화"""
        readings = [50, 50, 50]
        result = normalize_readings(readings)
        assert result == [0.5, 0.5, 0.5]

    def test_빈_리스트_예외(self):
        """빈 리스트 입력 시 ValueError 발생"""
        with pytest.raises(ValueError, match="비어있습니다"):
            normalize_readings([])

    def test_fixture_활용(self, sample_sensor_data):
        """conftest.py의 fixture를 사용한 테스트"""
        readings = sample_sensor_data["readings"]
        result = normalize_readings(readings)

        # 모든 정규화된 값이 0~1 범위 내인지 확인
        assert all(0 <= v <= 1 for v in result)
        assert len(result) == len(readings)


# ============================================================
# 이상치 필터링 테스트
# ============================================================

class TestFilterOutliers:
    """이상치 필터링 테스트"""

    def test_이상치_제거(self):
        """명백한 이상치가 제거되어야 한다"""
        readings = [25, 25, 25, 25, 25, 25, 25, 25, 500]  # 500은 명백한 이상치
        result = filter_outliers(readings)
        assert 500 not in result
        assert len(result) < len(readings)

    def test_정상_데이터_유지(self):
        """이상치가 없으면 모든 데이터가 유지되어야 한다"""
        readings = [25.0, 25.1, 24.9, 25.0, 25.2]
        result = filter_outliers(readings)
        assert len(result) == len(readings)

    def test_동일값_유지(self):
        """모든 값이 같으면 모두 유지되어야 한다"""
        readings = [50.0, 50.0, 50.0]
        result = filter_outliers(readings)
        assert result == [50.0, 50.0, 50.0]

    def test_단일값_유지(self):
        """단일 값은 그대로 유지되어야 한다"""
        readings = [42.0]
        result = filter_outliers(readings)
        assert result == [42.0]

    def test_빈_리스트_예외(self):
        """빈 리스트 입력 시 ValueError 발생"""
        with pytest.raises(ValueError):
            filter_outliers([])

    def test_multiplier_조절(self):
        """multiplier 값에 따라 필터링 강도가 달라져야 한다"""
        readings = [25, 25, 25, 30, 25]

        # 높은 multiplier: 더 관대 → 30이 유지될 수 있음
        result_lenient = filter_outliers(readings, multiplier=5.0)

        # 낮은 multiplier: 더 엄격 → 30이 제거될 수 있음
        result_strict = filter_outliers(readings, multiplier=0.5)

        assert len(result_lenient) >= len(result_strict)

    def test_원본_데이터_변경_없음(self):
        """원본 리스트가 변경되지 않아야 한다"""
        readings = [25, 25, 25, 100]
        original = readings.copy()
        filter_outliers(readings)
        assert readings == original


# ============================================================
# 데이터 집계 테스트
# ============================================================

class TestAggregateSensorData:
    """센서 데이터 집계 테스트"""

    def test_다중_센서_집계(self, sample_multi_sensor_data):
        """여러 센서의 데이터가 올바르게 집계되어야 한다"""
        result = aggregate_sensor_data(sample_multi_sensor_data)

        # 3개 센서의 결과가 있어야 함
        assert len(result) == 3
        assert "TEMP-001" in result
        assert "VIB-001" in result
        assert "PRESS-001" in result

    def test_집계_통계값(self, sample_multi_sensor_data):
        """각 센서의 통계값이 올바르게 계산되어야 한다"""
        result = aggregate_sensor_data(sample_multi_sensor_data)

        # 온도 센서: [25.0, 25.5, 26.0]
        temp_stats = result["TEMP-001"]
        assert temp_stats["mean"] == pytest.approx(25.5, abs=0.01)
        assert temp_stats["min"] == 25.0
        assert temp_stats["max"] == 26.0
        assert temp_stats["count"] == 3

    def test_빈_읽기_데이터(self, empty_readings):
        """읽기 데이터가 없는 센서의 집계"""
        result = aggregate_sensor_data([empty_readings])

        stats = result["TEMP-999"]
        assert stats["mean"] is None
        assert stats["count"] == 0

    def test_빈_리스트_예외(self):
        """빈 센서 데이터 리스트 입력 시 ValueError 발생"""
        with pytest.raises(ValueError, match="비어있습니다"):
            aggregate_sensor_data([])


# ============================================================
# 임계값 확인 테스트
# ============================================================

class TestCheckThresholds:
    """임계값 확인 테스트"""

    def test_온도_임계값_초과(self, sample_config):
        """온도가 임계값을 초과하면 exceeded=True"""
        sensor_data = {
            "sensor_type": "temperature",
            "readings": [75.0, 78.0, 85.0],  # 85 > 80 (임계값)
        }
        result = check_thresholds(sensor_data, sample_config)
        assert result["exceeded"] is True
        assert result["max_value"] == 85.0
        assert result["threshold"] == 80.0

    def test_온도_임계값_미만(self, sample_config):
        """온도가 임계값 미만이면 exceeded=False"""
        sensor_data = {
            "sensor_type": "temperature",
            "readings": [25.0, 30.0, 40.0],
        }
        result = check_thresholds(sensor_data, sample_config)
        assert result["exceeded"] is False

    def test_진동_임계값_확인(self, sample_config):
        """진동 임계값이 올바르게 적용되어야 한다"""
        sensor_data = {
            "sensor_type": "vibration",
            "readings": [2.0, 3.0, 8.0],  # 8.0 > 7.1 (임계값)
        }
        result = check_thresholds(sensor_data, sample_config)
        assert result["exceeded"] is True
        assert result["threshold"] == 7.1

    def test_알_수_없는_센서_타입(self, sample_config):
        """알 수 없는 센서 타입에 대해 exceeded=False"""
        sensor_data = {
            "sensor_type": "unknown",
            "readings": [100.0],
        }
        result = check_thresholds(sensor_data, sample_config)
        assert result["exceeded"] is False

    def test_fixture_조합(self, sample_sensor_data, sample_config):
        """conftest.py의 여러 fixture를 조합하여 사용"""
        result = check_thresholds(sample_sensor_data, sample_config)
        # 샘플 데이터의 온도(25도 부근)는 임계값(80도) 미만
        assert result["exceeded"] is False


# ============================================================
# 요약 보고서 테스트
# ============================================================

class TestGenerateSummaryReport:
    """요약 보고서 생성 테스트"""

    def test_정상_보고서(self, sample_multi_sensor_data, sample_config):
        """정상 데이터에 대한 보고서 생성"""
        report = generate_summary_report(
            sample_multi_sensor_data, sample_config
        )
        assert report["total_sensors"] == 3
        assert isinstance(report["alerts"], list)
        assert isinstance(report["summary"], dict)

    def test_빈_데이터_보고서(self, sample_config):
        """빈 데이터에 대한 보고서"""
        report = generate_summary_report([], sample_config)
        assert report["total_sensors"] == 0
        assert report["alerts"] == []

    def test_알림_생성(self, sample_config):
        """임계값 초과 시 알림이 생성되어야 한다"""
        data = [
            {
                "sensor_id": "TEMP-HIGH",
                "sensor_type": "temperature",
                "readings": [85.0, 90.0, 95.0],
            }
        ]
        report = generate_summary_report(data, sample_config)
        assert len(report["alerts"]) == 1
        assert report["alerts"][0]["sensor_id"] == "TEMP-HIGH"
