"""
Markers 데모 테스트

pytest 마커의 다양한 사용법을 시연한다:
1. 내장 마커: skip, skipif, xfail
2. 커스텀 마커: slow, integration, sensor
3. 클래스 수준 마커
4. 마커 조합
"""

import sys
import pytest
from src_equipment_monitor import EquipmentMonitor, EquipmentStatus


# ============================================================
# 1. 내장 마커: skip
# ============================================================

class TestSkipMarker:
    """skip 마커 사용 예제"""

    @pytest.mark.skip(reason="실제 센서 하드웨어가 없으므로 건너뜀")
    def test_real_sensor_connection(self):
        """실제 센서 연결 테스트 (항상 건너뜀)"""
        # 이 테스트는 실행되지 않음
        assert False  # 실행되면 안 됨

    def test_equipment_registration(self, monitor):
        """장비 등록 테스트 (항상 실행)"""
        status = monitor.register_equipment("TEST-001", "테스트 장비")
        assert status.equipment_id == "TEST-001"
        assert status.status == "idle"


# ============================================================
# 2. 내장 마커: skipif
# ============================================================

class TestSkipIfMarker:
    """skipif 마커 사용 예제"""

    @pytest.mark.skipif(
        sys.version_info < (3, 10),
        reason="Python 3.10 이상에서만 지원하는 기능"
    )
    def test_python310_feature(self, monitor):
        """Python 3.10+ 기능을 사용하는 테스트"""
        # match-case 문 등 3.10+ 기능 테스트
        status = monitor.register_equipment("PY310-001", "3.10 테스트")
        assert status.name == "3.10 테스트"

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Windows에서는 건너뜀 (POSIX 전용 기능)"
    )
    def test_posix_feature(self, monitor):
        """POSIX 환경 전용 테스트"""
        monitor.register_equipment("POSIX-001", "POSIX 장비")
        assert monitor.get_status("POSIX-001").status == "idle"


# ============================================================
# 3. 내장 마커: xfail
# ============================================================

class TestXfailMarker:
    """xfail 마커 사용 예제"""

    @pytest.mark.xfail(reason="음수 온도 처리 로직 미구현")
    def test_negative_temperature_handling(self, monitor):
        """음수 온도 처리 테스트 (예상 실패)"""
        monitor.register_equipment("XFAIL-001", "테스트 장비")
        # 음수 온도를 넣어도 현재는 running 상태로 판단됨
        monitor.update_sensor_data("XFAIL-001", temperature=-10.0)
        status = monitor.get_status("XFAIL-001")
        # 실제로는 "error" 또는 특수 상태여야 하지만 미구현
        assert status.status == "sub_zero"  # 아직 이 상태가 없으므로 실패

    @pytest.mark.xfail(strict=True, reason="알 수 없는 장비 조회 시 KeyError 발생해야 함")
    def test_unknown_equipment_raises_error(self, monitor):
        """등록되지 않은 장비 조회 시 에러 발생 (strict xfail)"""
        # 이 테스트는 반드시 실패해야 함 (strict=True)
        monitor.get_status("UNKNOWN-999")  # KeyError 발생
        assert False  # 여기까지 오면 안 됨


# ============================================================
# 4. 커스텀 마커: slow
# ============================================================

@pytest.mark.slow
class TestSlowOperations:
    """느린 작업 테스트 (slow 마커)"""

    def test_full_diagnostics(self, monitor_with_data):
        """전체 진단 실행 (느린 작업)"""
        result = monitor_with_data.run_full_diagnostics("MOTOR-001")
        assert result["equipment_id"] == "MOTOR-001"
        assert "temperature_check" in result
        assert "vibration_check" in result
        assert "overall_health" in result

    def test_monthly_report(self, monitor_with_data):
        """월간 보고서 생성 (느린 작업)"""
        equipment_ids = ["MOTOR-001", "PUMP-001", "CONV-001"]
        report = monitor_with_data.generate_monthly_report(equipment_ids)
        assert report["total_equipment"] == 3
        assert len(report["status_summary"]) == 3


# ============================================================
# 5. 커스텀 마커: integration
# ============================================================

@pytest.mark.integration
class TestIntegrationOperations:
    """외부 시스템 연동 테스트 (integration 마커)"""

    def test_send_alert(self, monitor_with_data):
        """알림 전송 테스트"""
        result = monitor_with_data.send_alert(
            "PUMP-001", "펌프 온도 경고: 90°C"
        )
        assert result["sent"] is True
        assert result["equipment_id"] == "PUMP-001"

    def test_sync_to_cloud(self, monitor_with_data):
        """클라우드 동기화 테스트"""
        result = monitor_with_data.sync_to_cloud("MOTOR-001")
        assert result["synced"] is True
        assert result["cloud_status"] == "uploaded"


# ============================================================
# 6. 커스텀 마커: sensor (센서별 분류)
# ============================================================

@pytest.mark.sensor
class TestSensorRelated:
    """센서 관련 테스트 (sensor 마커)"""

    def test_temperature_update(self, monitor_with_equipment):
        """온도 센서 업데이트"""
        monitor_with_equipment.update_sensor_data(
            "MOTOR-001", temperature=65.0
        )
        status = monitor_with_equipment.get_status("MOTOR-001")
        assert status.temperature == 65.0
        assert status.status == "running"

    def test_vibration_update(self, monitor_with_equipment):
        """진동 센서 업데이트"""
        monitor_with_equipment.update_sensor_data(
            "PUMP-001", vibration=5.0
        )
        status = monitor_with_equipment.get_status("PUMP-001")
        assert status.vibration == 5.0


# ============================================================
# 7. 장비별 커스텀 마커
# ============================================================

@pytest.mark.motor
def test_motor_registration(monitor):
    """모터 등록 테스트 (motor 마커)"""
    status = monitor.register_equipment("MOTOR-NEW", "신규 모터")
    assert status.equipment_id == "MOTOR-NEW"


@pytest.mark.pump
def test_pump_warning_status(monitor):
    """펌프 경고 상태 테스트 (pump 마커)"""
    monitor.register_equipment("PUMP-NEW", "신규 펌프")
    monitor.update_sensor_data("PUMP-NEW", temperature=85.0)
    status = monitor.get_status("PUMP-NEW")
    assert status.status == "warning"


@pytest.mark.conveyor
def test_conveyor_error_status(monitor):
    """컨베이어 에러 상태 테스트 (conveyor 마커)"""
    monitor.register_equipment("CONV-NEW", "신규 컨베이어")
    monitor.update_sensor_data("CONV-NEW", vibration=12.0)
    status = monitor.get_status("CONV-NEW")
    assert status.status == "error"


# ============================================================
# 8. 마커 조합
# ============================================================

@pytest.mark.slow
@pytest.mark.integration
def test_full_diagnostics_with_cloud_sync(monitor_with_data):
    """전체 진단 후 클라우드 동기화 (slow + integration 마커)"""
    # 느리고 외부 연동도 필요한 테스트
    diagnostics = monitor_with_data.run_full_diagnostics("MOTOR-001")
    sync_result = monitor_with_data.sync_to_cloud("MOTOR-001")
    assert diagnostics["overall_health"] == "good"
    assert sync_result["synced"] is True


@pytest.mark.sensor
@pytest.mark.motor
def test_motor_sensor_data(monitor):
    """모터 센서 데이터 테스트 (sensor + motor 마커)"""
    monitor.register_equipment("MOTOR-SENSOR", "센서 모터")
    monitor.update_sensor_data("MOTOR-SENSOR", temperature=70.0, vibration=4.0)
    status = monitor.get_status("MOTOR-SENSOR")
    assert status.temperature == 70.0
    assert status.vibration == 4.0
    assert status.status == "running"


# ============================================================
# 9. 마커 없는 테스트 (기본 단위 테스트)
# ============================================================

class TestBasicOperations:
    """마커 없는 기본 단위 테스트"""

    def test_duplicate_registration_error(self, monitor):
        """중복 등록 시 에러"""
        monitor.register_equipment("DUP-001", "장비")
        with pytest.raises(ValueError, match="이미 등록된"):
            monitor.register_equipment("DUP-001", "중복 장비")

    def test_unknown_equipment_error(self, monitor):
        """미등록 장비 조회 시 에러"""
        with pytest.raises(KeyError, match="등록되지 않은"):
            monitor.get_status("UNKNOWN-999")

    def test_maintenance_check(self, monitor):
        """정비 필요 여부 확인"""
        monitor.register_equipment("MAINT-001", "정비 대상 장비")
        status = monitor.get_status("MAINT-001")
        status.runtime_hours = 1200  # 1000시간 초과
        assert monitor.check_maintenance_needed("MAINT-001") is True

    def test_equipment_listing(self, monitor_with_equipment):
        """전체 장비 목록 조회"""
        all_eq = monitor_with_equipment.get_all_equipment()
        assert len(all_eq) == 3

    def test_equipment_filter_by_status(self, monitor_with_data):
        """상태별 장비 필터링"""
        warning_eq = monitor_with_data.get_equipment_by_status("warning")
        # PUMP-001이 warning 상태 (온도 90, 진동 8.5)
        assert len(warning_eq) >= 1
