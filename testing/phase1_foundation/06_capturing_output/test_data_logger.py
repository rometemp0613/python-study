"""
데이터 로거 모듈 테스트

capsys, capfd, caplog fixture를 활용한 출력 캡처 테스트.
"""

import logging
import pytest
from src_data_logger import (
    print_sensor_summary,
    print_error_report,
    log_data_processing,
    log_alert,
    process_and_report,
)


# ============================================================
# capsys 테스트 - stdout/stderr 캡처
# ============================================================

class TestPrintSensorSummary:
    """센서 요약 출력 테스트 (capsys 활용)"""

    def test_stdout_정상_출력(self, capsys):
        """센서 요약이 stdout으로 올바르게 출력되어야 한다"""
        sensor_data = {
            "sensor_id": "TEMP-001",
            "readings": [25.0, 30.0, 35.0],
            "unit": "celsius",
        }
        print_sensor_summary(sensor_data)

        captured = capsys.readouterr()

        # stdout 확인
        assert "TEMP-001" in captured.out
        assert "3회" in captured.out
        assert "30.00 celsius" in captured.out  # 평균
        assert "25.00 celsius" in captured.out  # 최소
        assert "35.00 celsius" in captured.out  # 최대

        # stderr에는 출력 없음
        assert captured.err == ""

    def test_stdout_빈_데이터(self, capsys):
        """빈 데이터에 대해 '데이터 없음'이 출력되어야 한다"""
        sensor_data = {
            "sensor_id": "TEMP-002",
            "readings": [],
            "unit": "celsius",
        }
        print_sensor_summary(sensor_data)

        captured = capsys.readouterr()
        assert "데이터 없음" in captured.out
        assert "0회" in captured.out

    def test_stdout_구분선(self, capsys):
        """요약 출력에 시작/끝 구분선이 있어야 한다"""
        sensor_data = {
            "sensor_id": "TEMP-003",
            "readings": [20.0],
            "unit": "celsius",
        }
        print_sensor_summary(sensor_data)

        captured = capsys.readouterr()
        assert "=== 센서 요약" in captured.out
        assert "=== 요약 끝 ===" in captured.out


class TestPrintErrorReport:
    """에러 보고서 출력 테스트 (stderr 캡처)"""

    def test_stderr_에러_출력(self, capsys):
        """에러 보고서가 stderr로 출력되어야 한다"""
        errors = [
            {"sensor_id": "TEMP-001", "error": "통신 끊김"},
            {"sensor_id": "VIB-002", "error": "범위 초과"},
        ]
        print_error_report(errors)

        captured = capsys.readouterr()

        # stderr에 에러 정보가 있어야 함
        assert "2건" in captured.err
        assert "TEMP-001" in captured.err
        assert "통신 끊김" in captured.err
        assert "VIB-002" in captured.err

        # stdout에는 출력 없음
        assert captured.out == ""

    def test_stderr_에러_없음(self, capsys):
        """에러가 없으면 아무것도 출력하지 않아야 한다"""
        print_error_report([])

        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""


# ============================================================
# caplog 테스트 - logging 캡처
# ============================================================

class TestLogDataProcessing:
    """데이터 처리 로깅 테스트 (caplog 활용)"""

    def test_log_정상_처리(self, caplog):
        """정상 데이터 처리 시 INFO 로그가 기록되어야 한다"""
        with caplog.at_level(logging.INFO):
            result = log_data_processing("TEMP-001", [25.0, 30.0, 35.0])

        # INFO 레벨 로그 확인
        assert any(
            record.levelname == "INFO" and "처리 완료" in record.message
            for record in caplog.records
        )

        # 결과 확인
        assert result["status"] == "processed"

    def test_log_빈_데이터_경고(self, caplog):
        """빈 데이터 수신 시 WARNING 로그가 기록되어야 한다"""
        with caplog.at_level(logging.WARNING):
            result = log_data_processing("TEMP-002", [])

        assert any(
            record.levelname == "WARNING" and "빈 데이터" in record.message
            for record in caplog.records
        )
        assert result["status"] == "no_data"

    def test_log_위험_온도_에러(self, caplog):
        """위험 온도 감지 시 ERROR 로그가 기록되어야 한다"""
        with caplog.at_level(logging.ERROR):
            log_data_processing("TEMP-003", [25.0, 30.0, 85.0])

        # ERROR 레벨 로그 확인
        error_records = [r for r in caplog.records if r.levelname == "ERROR"]
        assert len(error_records) >= 1
        assert "위험 온도" in error_records[0].message
        assert "85" in error_records[0].message

    def test_log_주의_온도_경고(self, caplog):
        """주의 온도 감지 시 WARNING 로그가 기록되어야 한다"""
        with caplog.at_level(logging.WARNING):
            log_data_processing("TEMP-004", [25.0, 30.0, 65.0])

        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        assert len(warning_records) >= 1
        assert "주의 온도" in warning_records[0].message

    def test_log_디버그_레벨(self, caplog):
        """DEBUG 레벨로 설정하면 DEBUG 로그도 캡처된다"""
        with caplog.at_level(logging.DEBUG):
            log_data_processing("TEMP-005", [25.0, 30.0])

        # DEBUG 로그 확인
        debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
        assert len(debug_records) >= 1
        assert "처리 시작" in debug_records[0].message

    def test_log_센서_ID_포함(self, caplog):
        """모든 로그에 센서 ID가 포함되어야 한다"""
        with caplog.at_level(logging.DEBUG):
            log_data_processing("SENSOR-XYZ", [25.0])

        for record in caplog.records:
            assert "SENSOR-XYZ" in record.message


class TestLogAlert:
    """알림 로그 테스트"""

    def test_log_경고_알림(self, caplog):
        """WARNING 레벨 알림이 기록되어야 한다"""
        with caplog.at_level(logging.WARNING):
            log_alert("TEMP-001", "temperature", "온도 초과", level="WARNING")

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "WARNING"
        assert "[알림]" in caplog.records[0].message
        assert "temperature" in caplog.records[0].message

    def test_log_에러_알림(self, caplog):
        """ERROR 레벨 알림이 기록되어야 한다"""
        with caplog.at_level(logging.ERROR):
            log_alert("TEMP-001", "temperature", "과열 위험", level="ERROR")

        assert caplog.records[0].levelname == "ERROR"

    def test_log_크리티컬_알림(self, caplog):
        """CRITICAL 레벨 알림이 기록되어야 한다"""
        with caplog.at_level(logging.CRITICAL):
            log_alert("TEMP-001", "temperature", "긴급 정지", level="CRITICAL")

        assert caplog.records[0].levelname == "CRITICAL"
        assert "긴급 정지" in caplog.records[0].message

    def test_log_record_tuples(self, caplog):
        """record_tuples로 로그를 검증한다"""
        with caplog.at_level(logging.WARNING):
            log_alert("VIB-001", "vibration", "진동 이상", level="WARNING")

        # (로거 이름, 레벨, 메시지) 형태의 튜플
        assert len(caplog.record_tuples) == 1
        logger_name, level, message = caplog.record_tuples[0]
        assert level == logging.WARNING
        assert "진동 이상" in message


# ============================================================
# stdout + logging 동시 테스트
# ============================================================

class TestProcessAndReport:
    """일괄 처리 및 보고서 테스트 (capsys + caplog 동시 사용)"""

    def test_stdout과_logging_동시_확인(self, capsys, caplog):
        """stdout 출력과 로그를 동시에 확인한다"""
        sensor_data_list = [
            {
                "sensor_id": "TEMP-001",
                "readings": [25.0, 30.0],
            },
            {
                "sensor_id": "VIB-001",
                "readings": [3.0, 4.0],
            },
        ]

        with caplog.at_level(logging.INFO):
            results = process_and_report(sensor_data_list)

        # stdout 확인
        captured = capsys.readouterr()
        assert "2개 센서" in captured.out
        assert "처리 완료" in captured.out

        # 로그 확인
        assert any("처리 완료" in r.message for r in caplog.records)

        # 결과 확인
        assert len(results) == 2

    def test_stdout_여러_번_읽기(self, capsys):
        """readouterr()를 여러 번 호출하여 순차적으로 출력을 확인한다"""
        # 첫 번째 출력
        print("1단계: 데이터 수집")
        captured = capsys.readouterr()
        assert "1단계" in captured.out

        # 두 번째 출력 (이전 출력은 이미 소비됨)
        print("2단계: 데이터 분석")
        captured = capsys.readouterr()
        assert "2단계" in captured.out
        assert "1단계" not in captured.out  # 이미 소비됨

    def test_caplog_초기화(self, caplog):
        """caplog.clear()로 로그를 초기화할 수 있다"""
        with caplog.at_level(logging.INFO):
            log_data_processing("TEMP-001", [25.0])

            # 로그 확인
            assert len(caplog.records) > 0

            # 로그 초기화
            caplog.clear()
            assert len(caplog.records) == 0

            # 새로운 로그 기록
            log_data_processing("TEMP-002", [30.0])
            assert len(caplog.records) > 0
            assert any("TEMP-002" in r.message for r in caplog.records)
