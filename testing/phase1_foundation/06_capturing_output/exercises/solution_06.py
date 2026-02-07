"""
연습 문제 06: 풀이

센서 모니터링 보고서 출력과 로깅 테스트 풀이.

실행 방법:
    pytest exercises/solution_06.py -v
"""

import logging
import sys
import pytest

# 모듈 레벨 로거
logger = logging.getLogger(__name__)


# ============================================================
# 테스트 대상 함수들
# ============================================================

def print_daily_report(date, sensor_summaries):
    """일일 보고서를 stdout으로 출력한다."""
    print(f"{'='*40}")
    print(f"일일 설비 모니터링 보고서 - {date}")
    print(f"{'='*40}")

    for summary in sensor_summaries:
        sid = summary.get("sensor_id", "UNKNOWN")
        avg = summary.get("avg", 0)
        status = summary.get("status", "미확인")
        print(f"  {sid}: 평균 {avg:.1f} [{status}]")

    print(f"총 센서 수: {len(sensor_summaries)}개")


def print_alarm_to_stderr(sensor_id, message):
    """긴급 알람을 stderr로 출력한다."""
    sys.stderr.write(f"[긴급 알람] {sensor_id}: {message}\n")


def log_maintenance_event(equipment_id, event_type, description):
    """정비 이벤트를 로깅한다."""
    if event_type == "긴급수리":
        logger.error(f"[정비][{equipment_id}] {event_type}: {description}")
    elif event_type == "부품교체":
        logger.warning(f"[정비][{equipment_id}] {event_type}: {description}")
    else:
        logger.info(f"[정비][{equipment_id}] {event_type}: {description}")


def monitor_and_log(sensor_id, readings, threshold=80.0):
    """센서 데이터를 모니터링하고 결과를 출력 및 로깅한다."""
    if not readings:
        print(f"[{sensor_id}] 데이터 없음")
        logger.warning(f"[{sensor_id}] 빈 데이터 수신")
        return "no_data"

    avg = sum(readings) / len(readings)
    max_val = max(readings)

    print(f"[{sensor_id}] 평균: {avg:.1f}, 최대: {max_val:.1f}")
    logger.info(f"[{sensor_id}] 데이터 처리 - 평균: {avg:.2f}")

    if max_val >= threshold:
        print(f"[{sensor_id}] 경고: 임계값 초과!")
        logger.error(f"[{sensor_id}] 임계값 {threshold} 초과: {max_val}")
        return "alert"

    logger.debug(f"[{sensor_id}] 정상 범위 내")
    return "normal"


# ============================================================
# 테스트 코드 (풀이)
# ============================================================

class TestPrintDailyReport:
    """일일 보고서 출력 테스트"""

    def test_보고서_헤더(self, capsys):
        """보고서에 날짜와 제목이 포함되어야 한다"""
        summaries = [
            {"sensor_id": "TEMP-001", "avg": 25.0, "status": "정상"},
        ]
        print_daily_report("2024-01-15", summaries)

        captured = capsys.readouterr()
        assert "2024-01-15" in captured.out
        assert "일일 설비 모니터링 보고서" in captured.out
        assert "=" in captured.out  # 구분선

    def test_센서_정보_출력(self, capsys):
        """각 센서의 정보가 출력되어야 한다"""
        summaries = [
            {"sensor_id": "TEMP-001", "avg": 25.5, "status": "정상"},
            {"sensor_id": "VIB-001", "avg": 3.2, "status": "주의"},
        ]
        print_daily_report("2024-01-15", summaries)

        captured = capsys.readouterr()
        assert "TEMP-001" in captured.out
        assert "25.5" in captured.out
        assert "정상" in captured.out
        assert "VIB-001" in captured.out
        assert "3.2" in captured.out
        assert "주의" in captured.out

    def test_센서_수_출력(self, capsys):
        """총 센서 수가 출력되어야 한다"""
        summaries = [
            {"sensor_id": "TEMP-001", "avg": 25.0, "status": "정상"},
            {"sensor_id": "VIB-001", "avg": 3.0, "status": "정상"},
            {"sensor_id": "PRESS-001", "avg": 14.7, "status": "정상"},
        ]
        print_daily_report("2024-01-15", summaries)

        captured = capsys.readouterr()
        assert "3개" in captured.out

    def test_빈_보고서(self, capsys):
        """센서가 없어도 보고서 형식은 유지되어야 한다"""
        print_daily_report("2024-01-15", [])

        captured = capsys.readouterr()
        assert "0개" in captured.out
        assert captured.err == ""


class TestPrintAlarmToStderr:
    """긴급 알람 출력 테스트"""

    def test_stderr_알람_출력(self, capsys):
        """알람이 stderr로 출력되어야 한다"""
        print_alarm_to_stderr("TEMP-001", "과열 위험")

        captured = capsys.readouterr()
        assert "TEMP-001" in captured.err
        assert "과열 위험" in captured.err
        assert "[긴급 알람]" in captured.err

    def test_stdout에는_출력_없음(self, capsys):
        """알람은 stdout에는 출력되지 않아야 한다"""
        print_alarm_to_stderr("TEMP-001", "과열 위험")

        captured = capsys.readouterr()
        assert captured.out == ""


class TestLogMaintenanceEvent:
    """정비 이벤트 로깅 테스트"""

    def test_긴급수리_에러_로그(self, caplog):
        """긴급수리는 ERROR 레벨로 로깅되어야 한다"""
        with caplog.at_level(logging.ERROR):
            log_maintenance_event("MOTOR-001", "긴급수리", "베어링 파손")

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert "MOTOR-001" in caplog.records[0].message
        assert "긴급수리" in caplog.records[0].message
        assert "베어링 파손" in caplog.records[0].message

    def test_부품교체_경고_로그(self, caplog):
        """부품교체는 WARNING 레벨로 로깅되어야 한다"""
        with caplog.at_level(logging.WARNING):
            log_maintenance_event("MOTOR-001", "부품교체", "필터 교환")

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "WARNING"
        assert "부품교체" in caplog.records[0].message

    def test_정기점검_정보_로그(self, caplog):
        """정기점검은 INFO 레벨로 로깅되어야 한다"""
        with caplog.at_level(logging.INFO):
            log_maintenance_event("MOTOR-001", "정기점검", "월간 점검 수행")

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "INFO"
        assert "정기점검" in caplog.records[0].message

    def test_로그_메시지_형식(self, caplog):
        """로그 메시지에 [정비] 태그와 설비 ID가 포함되어야 한다"""
        with caplog.at_level(logging.INFO):
            log_maintenance_event("PUMP-003", "정기점검", "오일 확인")

        assert "[정비]" in caplog.records[0].message
        assert "PUMP-003" in caplog.records[0].message


class TestMonitorAndLog:
    """모니터링 및 로깅 통합 테스트"""

    def test_정상_데이터_출력과_로그(self, capsys, caplog):
        """정상 데이터에 대해 stdout과 로그를 동시에 확인한다"""
        with caplog.at_level(logging.INFO):
            result = monitor_and_log("TEMP-001", [25.0, 30.0, 35.0])

        # stdout 확인
        captured = capsys.readouterr()
        assert "TEMP-001" in captured.out
        assert "평균:" in captured.out
        assert "최대:" in captured.out

        # 로그 확인
        assert any("데이터 처리" in r.message for r in caplog.records)

        # 결과 확인
        assert result == "normal"

    def test_임계값_초과_경고(self, capsys, caplog):
        """임계값 초과 시 stdout 경고와 ERROR 로그를 확인한다"""
        with caplog.at_level(logging.ERROR):
            result = monitor_and_log("TEMP-002", [25.0, 30.0, 85.0])

        # stdout에 경고 메시지
        captured = capsys.readouterr()
        assert "경고" in captured.out
        assert "임계값 초과" in captured.out

        # ERROR 레벨 로그
        error_records = [r for r in caplog.records if r.levelname == "ERROR"]
        assert len(error_records) >= 1
        assert "임계값" in error_records[0].message

        # 결과
        assert result == "alert"

    def test_빈_데이터_처리(self, capsys, caplog):
        """빈 데이터에 대해 적절한 출력과 로그를 생성한다"""
        with caplog.at_level(logging.WARNING):
            result = monitor_and_log("TEMP-003", [])

        captured = capsys.readouterr()
        assert "데이터 없음" in captured.out

        assert any("빈 데이터" in r.message for r in caplog.records)
        assert result == "no_data"
