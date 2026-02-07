"""
스냅샷/회귀 테스트 데모.

이 파일은 수동 스냅샷 비교 패턴으로 회귀 테스트를 구현한다.
expected_outputs/ 디렉토리의 파일과 실제 출력을 비교한다.

syrupy가 설치된 경우의 사용법도 주석으로 안내한다.

실행 방법:
    pytest test_snapshot_demo.py -v
"""

import json
import os
import pytest

from src_report_generator import (
    generate_sensor_report,
    generate_alert_summary,
    generate_maintenance_schedule,
)


# =============================================================================
# 유틸리티 함수
# =============================================================================

# 기대 출력 파일 디렉토리 경로
EXPECTED_DIR = os.path.join(os.path.dirname(__file__), "expected_outputs")


def load_expected_json(filename: str) -> dict:
    """expected_outputs 디렉토리에서 JSON 파일을 로드한다"""
    filepath = os.path.join(EXPECTED_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_expected_text(filename: str) -> str:
    """expected_outputs 디렉토리에서 텍스트 파일을 로드한다"""
    filepath = os.path.join(EXPECTED_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


# =============================================================================
# 테스트 데이터 (픽스처)
# =============================================================================

@pytest.fixture
def sample_sensor_data():
    """센서 데이터 샘플"""
    return {
        "sensor_id": "VIB_001",
        "sensor_type": "vibration",
        "values": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "unit": "mm/s",
        "location": "A동 2층 모터실",
    }


@pytest.fixture
def sample_alerts():
    """알림 데이터 샘플"""
    return [
        {
            "equipment_id": "MOTOR_001",
            "alert_type": "critical",
            "message": "베어링 온도 임계값 초과",
        },
        {
            "equipment_id": "PUMP_002",
            "alert_type": "warning",
            "message": "진동 수준 증가 추세",
        },
        {
            "equipment_id": "TURBINE_003",
            "alert_type": "info",
            "message": "정기 점검 예정일 도래",
        },
    ]


@pytest.fixture
def sample_equipment_list():
    """설비 목록 샘플"""
    return [
        {
            "equipment_id": "TURBINE_001",
            "name": "C동 터빈",
            "status": "normal",
            "last_maintenance_days_ago": 30,
            "maintenance_interval_days": 90,
        },
        {
            "equipment_id": "MOTOR_001",
            "name": "A동 주요 모터",
            "status": "danger",
            "last_maintenance_days_ago": 45,
            "maintenance_interval_days": 60,
        },
        {
            "equipment_id": "PUMP_002",
            "name": "B동 보조 펌프",
            "status": "normal",
            "last_maintenance_days_ago": 75,
            "maintenance_interval_days": 90,
        },
        {
            "equipment_id": "PUMP_003",
            "name": "냉각수 펌프",
            "status": "warning",
            "last_maintenance_days_ago": 100,
            "maintenance_interval_days": 90,
        },
    ]


# =============================================================================
# 수동 스냅샷 테스트 (syrupy 없이)
# =============================================================================

class TestSensorReportSnapshot:
    """센서 리포트 스냅샷 테스트"""

    def test_sensor_report_matches_snapshot(self, sample_sensor_data):
        """센서 리포트가 기대 출력과 일치하는지 확인"""
        # 실제 출력 생성
        actual = generate_sensor_report(sample_sensor_data)

        # 기대 출력 로드
        expected = load_expected_json("sensor_report.json")

        # 스냅샷 비교
        assert actual == expected, (
            "센서 리포트가 스냅샷과 다릅니다!\n"
            f"실제: {json.dumps(actual, ensure_ascii=False, indent=2)}\n"
            f"기대: {json.dumps(expected, ensure_ascii=False, indent=2)}"
        )

        # === syrupy 사용 시 동일한 테스트 ===
        # def test_sensor_report_syrupy(self, sample_sensor_data, snapshot):
        #     actual = generate_sensor_report(sample_sensor_data)
        #     assert actual == snapshot

    def test_empty_sensor_data_structure(self):
        """빈 센서 데이터의 리포트 구조 검증"""
        actual = generate_sensor_report({
            "sensor_id": "EMPTY_001",
            "sensor_type": "temperature",
            "values": [],
            "unit": "C",
            "location": "미지정",
        })

        # 구조 스냅샷 (값이 아닌 키 구조만 검증)
        expected_keys = {"sensor_id", "sensor_type", "location",
                        "statistics", "status", "unit"}
        assert set(actual.keys()) == expected_keys

        expected_stat_keys = {"count", "mean", "std_dev", "min", "max", "range"}
        assert set(actual["statistics"].keys()) == expected_stat_keys

        # 빈 데이터의 특정 값 검증
        assert actual["status"] == "no_data"
        assert actual["statistics"]["count"] == 0


class TestAlertSummarySnapshot:
    """알림 요약 스냅샷 테스트"""

    def test_alert_summary_matches_snapshot(self, sample_alerts):
        """알림 요약이 기대 출력과 일치하는지 확인"""
        actual = generate_alert_summary(sample_alerts)
        expected = load_expected_text("alert_summary.txt")

        # 줄 단위로 비교하면 디버깅이 쉬움
        actual_lines = actual.strip().split("\n")
        expected_lines = expected.strip().split("\n")

        assert len(actual_lines) == len(expected_lines), (
            f"줄 수가 다릅니다: 실제={len(actual_lines)}, 기대={len(expected_lines)}"
        )

        for i, (a_line, e_line) in enumerate(zip(actual_lines, expected_lines)):
            assert a_line == e_line, (
                f"줄 {i + 1}이 다릅니다:\n"
                f"  실제: '{a_line}'\n"
                f"  기대: '{e_line}'"
            )

    def test_empty_alerts_summary(self):
        """알림 없을 때의 요약 형식"""
        actual = generate_alert_summary([])
        assert "활성 알림 없음" in actual
        assert "===" in actual


class TestMaintenanceScheduleSnapshot:
    """유지보수 스케줄 스냅샷 테스트"""

    def test_schedule_matches_snapshot(self, sample_equipment_list):
        """유지보수 스케줄이 기대 출력과 일치하는지 확인"""
        actual = generate_maintenance_schedule(sample_equipment_list)
        expected = load_expected_json("maintenance_schedule.json")

        assert len(actual) == len(expected), (
            f"스케줄 항목 수가 다릅니다: 실제={len(actual)}, 기대={len(expected)}"
        )

        for i, (a_item, e_item) in enumerate(zip(actual, expected)):
            assert a_item == e_item, (
                f"스케줄 항목 {i}이 다릅니다:\n"
                f"  실제: {a_item}\n"
                f"  기대: {e_item}"
            )

    def test_schedule_priority_order(self, sample_equipment_list):
        """스케줄이 우선순위 순으로 정렬되는지 확인"""
        schedule = generate_maintenance_schedule(sample_equipment_list)

        priority_order = {"urgent": 0, "scheduled": 1, "routine": 2, "deferred": 3}
        priorities = [priority_order[s["priority"]] for s in schedule]

        # 정렬된 상태여야 한다
        assert priorities == sorted(priorities), (
            f"우선순위 순서가 올바르지 않습니다: "
            f"{[s['priority'] for s in schedule]}"
        )

    def test_empty_equipment_list(self):
        """빈 설비 목록은 빈 스케줄"""
        schedule = generate_maintenance_schedule([])
        assert schedule == []


# =============================================================================
# 부분 스냅샷 테스트 (핵심 필드만 비교)
# =============================================================================

class TestPartialSnapshot:
    """
    전체 스냅샷 대신 핵심 필드만 비교하는 패턴.

    비결정적 필드(시간, ID 등)가 있을 때 유용하다.
    """

    def test_sensor_report_structure(self, sample_sensor_data):
        """리포트의 구조와 핵심 값만 검증"""
        report = generate_sensor_report(sample_sensor_data)

        # 구조 검증
        assert "sensor_id" in report
        assert "statistics" in report
        assert "status" in report

        # 핵심 통계만 검증
        stats = report["statistics"]
        assert stats["count"] == 10
        assert stats["min"] == 1.0
        assert stats["max"] == 10.0
        assert stats["mean"] == pytest.approx(5.5)

    def test_alert_summary_contains_all_alerts(self, sample_alerts):
        """요약에 모든 알림이 포함되는지만 검증"""
        summary = generate_alert_summary(sample_alerts)

        # 모든 장비 ID가 포함되는지
        for alert in sample_alerts:
            assert alert["equipment_id"] in summary
            assert alert["message"] in summary

    def test_schedule_contains_all_equipment(self, sample_equipment_list):
        """스케줄에 모든 설비가 포함되는지 검증"""
        schedule = generate_maintenance_schedule(sample_equipment_list)

        scheduled_ids = {s["equipment_id"] for s in schedule}
        expected_ids = {e["equipment_id"] for e in sample_equipment_list}

        assert scheduled_ids == expected_ids
