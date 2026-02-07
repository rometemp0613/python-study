"""
연습 문제 06: 출력 캡처 테스트

센서 모니터링 보고서 출력과 로깅을 테스트하세요.
capsys와 caplog fixture를 활용합니다.

실행 방법:
    pytest exercises/exercise_06.py -v
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
    """일일 보고서를 stdout으로 출력한다.

    Args:
        date: 보고서 날짜 문자열
        sensor_summaries: 센서별 요약 리스트
            [{"sensor_id": ..., "avg": ..., "status": ...}, ...]
    """
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
    """긴급 알람을 stderr로 출력한다.

    Args:
        sensor_id: 센서 ID
        message: 알람 메시지
    """
    sys.stderr.write(f"[긴급 알람] {sensor_id}: {message}\n")


def log_maintenance_event(equipment_id, event_type, description):
    """정비 이벤트를 로깅한다.

    Args:
        equipment_id: 설비 ID
        event_type: 이벤트 유형 ("정기점검", "긴급수리", "부품교체")
        description: 상세 설명
    """
    if event_type == "긴급수리":
        logger.error(f"[정비][{equipment_id}] {event_type}: {description}")
    elif event_type == "부품교체":
        logger.warning(f"[정비][{equipment_id}] {event_type}: {description}")
    else:
        logger.info(f"[정비][{equipment_id}] {event_type}: {description}")


def monitor_and_log(sensor_id, readings, threshold=80.0):
    """센서 데이터를 모니터링하고 결과를 출력 및 로깅한다.

    stdout으로 요약을 출력하고, logging으로 상세 정보를 기록한다.

    Args:
        sensor_id: 센서 ID
        readings: 읽기 값 리스트
        threshold: 임계값

    Returns:
        상태 문자열
    """
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
# TODO: 아래에 테스트를 작성하세요
# ============================================================

class TestPrintDailyReport:
    """일일 보고서 출력 테스트"""

    def test_보고서_헤더(self, capsys):
        """보고서에 날짜와 제목이 포함되어야 한다"""
        # TODO: print_daily_report를 호출하고 capsys로 출력 확인
        # 힌트: captured = capsys.readouterr()
        pytest.skip("TODO: 보고서 헤더 테스트를 구현하세요")

    def test_센서_정보_출력(self, capsys):
        """각 센서의 정보가 출력되어야 한다"""
        # TODO: 센서 요약 데이터를 전달하고 출력 확인
        pytest.skip("TODO: 센서 정보 출력 테스트를 구현하세요")

    def test_센서_수_출력(self, capsys):
        """총 센서 수가 출력되어야 한다"""
        # TODO: "총 센서 수" 문자열 확인
        pytest.skip("TODO: 센서 수 출력 테스트를 구현하세요")


class TestPrintAlarmToStderr:
    """긴급 알람 출력 테스트"""

    def test_stderr_알람_출력(self, capsys):
        """알람이 stderr로 출력되어야 한다"""
        # TODO: capsys로 stderr 출력 확인
        # 힌트: captured.err로 stderr 내용 확인
        pytest.skip("TODO: stderr 알람 출력 테스트를 구현하세요")

    def test_stdout에는_출력_없음(self, capsys):
        """알람은 stdout에는 출력되지 않아야 한다"""
        # TODO: captured.out이 빈 문자열인지 확인
        pytest.skip("TODO: stdout 미출력 테스트를 구현하세요")


class TestLogMaintenanceEvent:
    """정비 이벤트 로깅 테스트"""

    def test_긴급수리_에러_로그(self, caplog):
        """긴급수리는 ERROR 레벨로 로깅되어야 한다"""
        # TODO: caplog.at_level(logging.ERROR)를 사용하세요
        pytest.skip("TODO: 긴급수리 에러 로그 테스트를 구현하세요")

    def test_부품교체_경고_로그(self, caplog):
        """부품교체는 WARNING 레벨로 로깅되어야 한다"""
        # TODO: caplog을 사용하여 WARNING 레벨 확인
        pytest.skip("TODO: 부품교체 경고 로그 테스트를 구현하세요")

    def test_정기점검_정보_로그(self, caplog):
        """정기점검은 INFO 레벨로 로깅되어야 한다"""
        # TODO: caplog을 사용하여 INFO 레벨 확인
        pytest.skip("TODO: 정기점검 정보 로그 테스트를 구현하세요")


class TestMonitorAndLog:
    """모니터링 및 로깅 통합 테스트"""

    def test_정상_데이터_출력과_로그(self, capsys, caplog):
        """정상 데이터에 대해 stdout과 로그를 동시에 확인한다"""
        # TODO: capsys와 caplog 모두 사용
        pytest.skip("TODO: 정상 데이터 통합 테스트를 구현하세요")

    def test_임계값_초과_경고(self, capsys, caplog):
        """임계값 초과 시 stdout 경고와 ERROR 로그를 확인한다"""
        # TODO: 높은 온도 데이터로 테스트
        pytest.skip("TODO: 임계값 초과 경고 테스트를 구현하세요")
