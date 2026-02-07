"""
연습문제 25 정답: Snapshot/회귀 테스트

각 연습의 완성된 풀이.
"""

import json
import os
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src_report_generator import (
    generate_sensor_report,
    generate_alert_summary,
    generate_maintenance_schedule,
)


# 공통 테스트 데이터
SENSOR_DATA_A = {
    "sensor_id": "VIB_001",
    "sensor_type": "vibration",
    "values": [1.0, 2.0, 3.0, 4.0, 5.0],
    "unit": "mm/s",
    "location": "A동 모터실",
}

SENSOR_DATA_B = {
    "sensor_id": "TEMP_001",
    "sensor_type": "temperature",
    "values": [50.0, 55.0, 60.0, 65.0, 70.0],
    "unit": "C",
    "location": "B동 열교환기",
}


# =============================================================================
# 연습 1 정답: JSON 스냅샷 비교 유틸리티
# =============================================================================

class TestSnapshotUtility:
    """JSON 기반 스냅샷 비교 유틸리티"""

    def test_save_and_compare_snapshot(self, tmp_path):
        """스냅샷 저장 후 비교"""
        snapshot_path = tmp_path / "snapshot.json"

        # 1. 첫 실행: 출력 생성 및 저장
        first_output = generate_sensor_report(SENSOR_DATA_A)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(first_output, f, ensure_ascii=False, indent=2)

        # 2. 두 번째 실행: 같은 입력으로 다시 생성
        second_output = generate_sensor_report(SENSOR_DATA_A)

        # 3. 스냅샷 로드
        with open(snapshot_path, "r", encoding="utf-8") as f:
            saved_snapshot = json.load(f)

        # 4. 비교: 동일한 입력이므로 일치해야 함
        assert second_output == saved_snapshot

    def test_detect_snapshot_change(self, tmp_path):
        """출력 변경 감지"""
        snapshot_path = tmp_path / "snapshot.json"

        # 1. 첫 번째 데이터로 스냅샷 저장
        first_output = generate_sensor_report(SENSOR_DATA_A)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(first_output, f, ensure_ascii=False, indent=2)

        # 2. 다른 데이터로 리포트 생성
        different_output = generate_sensor_report(SENSOR_DATA_B)

        # 3. 스냅샷 로드
        with open(snapshot_path, "r", encoding="utf-8") as f:
            saved_snapshot = json.load(f)

        # 4. 불일치 확인
        assert different_output != saved_snapshot, (
            "다른 입력인데 출력이 같으면 안 됩니다"
        )


# =============================================================================
# 연습 2 정답: 비결정적 데이터 처리
# =============================================================================

class TestNonDeterministicSnapshot:
    """비결정적 데이터가 포함된 스냅샷 테스트"""

    def test_snapshot_with_filtered_fields(self):
        """비결정적 필드를 제거한 후 비교"""
        # 리포트 생성
        report1 = generate_sensor_report(SENSOR_DATA_A)
        report2 = generate_sensor_report(SENSOR_DATA_A)

        # 비결정적 필드가 있다고 가정하고 제거 시뮬레이션
        # (실제로는 시간, UUID 등)
        def remove_nondeterministic(d):
            """비결정적 필드를 제거한 복사본 반환"""
            filtered = dict(d)
            # 예시: "timestamp", "request_id" 등을 제거
            for key in ["timestamp", "request_id", "generated_at"]:
                filtered.pop(key, None)
            return filtered

        filtered1 = remove_nondeterministic(report1)
        filtered2 = remove_nondeterministic(report2)

        # 비결정적 필드 제거 후에는 동일해야 함
        assert filtered1 == filtered2

    def test_snapshot_structure_only(self):
        """구조(키, 타입)만 비교하는 스냅샷"""
        report = generate_sensor_report(SENSOR_DATA_A)

        # 기대하는 구조 정의
        expected_structure = {
            "sensor_id": str,
            "sensor_type": str,
            "location": str,
            "statistics": dict,
            "status": str,
            "unit": str,
        }

        expected_stat_structure = {
            "count": int,
            "mean": float,
            "std_dev": float,
            "min": float,
            "max": float,
            "range": float,
        }

        # 키 집합 비교
        assert set(report.keys()) == set(expected_structure.keys())

        # 타입 비교
        for key, expected_type in expected_structure.items():
            assert isinstance(report[key], expected_type), (
                f"{key}의 타입이 {expected_type}이 아닌 {type(report[key])}"
            )

        # statistics 내부 구조 비교
        stats = report["statistics"]
        assert set(stats.keys()) == set(expected_stat_structure.keys())
        for key, expected_type in expected_stat_structure.items():
            assert isinstance(stats[key], (int, float)), (
                f"statistics.{key}의 타입이 숫자가 아님: {type(stats[key])}"
            )


# =============================================================================
# 연습 3 정답: 스냅샷 업데이트 워크플로우
# =============================================================================

class TestSnapshotUpdateWorkflow:
    """스냅샷 업데이트 워크플로우 시뮬레이션"""

    def test_update_snapshot_on_intentional_change(self, tmp_path):
        """의도적 변경 시 스냅샷 업데이트"""
        snapshot_path = tmp_path / "updated_snapshot.json"

        # 1. 초기 스냅샷 저장 (데이터 A)
        initial_output = generate_sensor_report(SENSOR_DATA_A)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(initial_output, f, ensure_ascii=False, indent=2)

        # 2. 새로운 데이터(B)로 변경된 출력
        changed_output = generate_sensor_report(SENSOR_DATA_B)

        # 3. 스냅샷 로드 및 불일치 확인
        with open(snapshot_path, "r", encoding="utf-8") as f:
            old_snapshot = json.load(f)
        assert changed_output != old_snapshot, "변경이 감지되어야 함"

        # 4. 스냅샷 업데이트 (의도적 변경이므로)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(changed_output, f, ensure_ascii=False, indent=2)

        # 5. 업데이트된 스냅샷으로 재비교 → 일치
        new_output = generate_sensor_report(SENSOR_DATA_B)
        with open(snapshot_path, "r", encoding="utf-8") as f:
            updated_snapshot = json.load(f)

        assert new_output == updated_snapshot, (
            "업데이트 후에는 스냅샷과 일치해야 합니다"
        )
