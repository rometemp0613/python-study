"""
연습문제 25: Snapshot/회귀 테스트

이 연습에서는 스냅샷 테스트 패턴을 직접 구현한다.
TODO 부분을 채워서 테스트를 완성하라.
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


# =============================================================================
# 연습 1: JSON 스냅샷 비교 유틸리티
# =============================================================================

class TestSnapshotUtility:
    """
    JSON 기반 스냅샷 비교 유틸리티를 구현하라.
    """

    def test_save_and_compare_snapshot(self, tmp_path):
        """
        TODO: 다음 워크플로우를 구현하라:
        1. 함수 출력을 JSON 파일로 저장 (첫 실행)
        2. 같은 함수를 다시 실행하여 출력 생성
        3. 저장된 JSON과 새 출력을 비교
        4. 일치하면 PASS

        힌트:
        - tmp_path / "snapshot.json"에 저장
        - json.dump()와 json.load() 사용
        - generate_sensor_report()를 2번 호출하여 결과 비교
        """
        pytest.skip("TODO: 스냅샷 저장/비교를 구현하세요")

    def test_detect_snapshot_change(self, tmp_path):
        """
        TODO: 출력이 변경되었을 때 감지하는 테스트를 작성하라.

        1. 첫 번째 센서 데이터로 스냅샷 저장
        2. 다른 센서 데이터로 리포트 생성
        3. 스냅샷과 비교하여 불일치 확인
        """
        pytest.skip("TODO: 스냅샷 변경 감지를 구현하세요")


# =============================================================================
# 연습 2: 비결정적 데이터 처리
# =============================================================================

class TestNonDeterministicSnapshot:
    """
    비결정적 데이터가 포함된 출력의 스냅샷 테스트.
    """

    def test_snapshot_with_filtered_fields(self):
        """
        TODO: 비결정적 필드를 제거한 후 스냅샷을 비교하라.

        시나리오:
        - 리포트에 "generated_at" 같은 시간 정보가 있다고 가정
        - 시간 필드를 제거하고 나머지를 비교

        힌트:
        - 리포트 생성 후 특정 키를 pop()으로 제거
        - 제거된 결과끼리 비교
        """
        pytest.skip("TODO: 비결정적 필드 필터링을 구현하세요")

    def test_snapshot_structure_only(self):
        """
        TODO: 값이 아닌 구조(키, 타입)만 비교하는 스냅샷을 작성하라.

        힌트:
        - 결과의 키 집합이 기대와 동일한지
        - 각 값의 타입이 기대와 동일한지
        """
        pytest.skip("TODO: 구조 스냅샷을 구현하세요")


# =============================================================================
# 연습 3: 스냅샷 업데이트 워크플로우
# =============================================================================

class TestSnapshotUpdateWorkflow:
    """
    스냅샷 업데이트 시뮬레이션.
    """

    def test_update_snapshot_on_intentional_change(self, tmp_path):
        """
        TODO: 의도적 변경 시 스냅샷을 업데이트하는 워크플로우를 구현하라.

        1. 초기 스냅샷 저장
        2. 함수 출력이 변경됨 (예: 다른 데이터 사용)
        3. 불일치 확인
        4. 새 출력으로 스냅샷 덮어쓰기 (업데이트)
        5. 업데이트된 스냅샷으로 다시 비교 → 일치

        힌트:
        - 스냅샷 파일 경로: tmp_path / "updated_snapshot.json"
        """
        pytest.skip("TODO: 스냅샷 업데이트 워크플로우를 구현하세요")
