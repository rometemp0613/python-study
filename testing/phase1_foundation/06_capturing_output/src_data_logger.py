"""
데이터 로거 모듈

센서 데이터 처리 과정에서 print() 출력과 logging 모듈을 사용하는 함수들.
capsys와 caplog fixture를 학습하기 위한 예제.
"""

import logging
import sys

# 모듈 레벨 로거 설정
logger = logging.getLogger(__name__)


def print_sensor_summary(sensor_data):
    """센서 데이터 요약을 stdout으로 출력한다.

    Args:
        sensor_data: 센서 데이터 딕셔너리
            {"sensor_id": ..., "readings": [...], "unit": ...}
    """
    sensor_id = sensor_data.get("sensor_id", "UNKNOWN")
    readings = sensor_data.get("readings", [])
    unit = sensor_data.get("unit", "")

    print(f"=== 센서 요약: {sensor_id} ===")
    print(f"읽기 횟수: {len(readings)}회")

    if readings:
        avg = sum(readings) / len(readings)
        print(f"평균값: {avg:.2f} {unit}")
        print(f"최소값: {min(readings):.2f} {unit}")
        print(f"최대값: {max(readings):.2f} {unit}")
    else:
        print("데이터 없음")

    print(f"=== 요약 끝 ===")


def print_error_report(errors):
    """에러 보고서를 stderr로 출력한다.

    Args:
        errors: 에러 정보 리스트
            [{"sensor_id": ..., "error": ..., "timestamp": ...}, ...]
    """
    if not errors:
        return

    sys.stderr.write(f"[에러 보고서] 총 {len(errors)}건의 에러 발생\n")
    for error in errors:
        sys.stderr.write(
            f"  - [{error.get('sensor_id', 'UNKNOWN')}] "
            f"{error.get('error', '알 수 없는 에러')}\n"
        )


def log_data_processing(sensor_id, readings):
    """데이터 처리 과정을 로깅한다.

    다양한 로그 레벨을 사용하여 처리 과정을 기록한다.

    Args:
        sensor_id: 센서 ID
        readings: 읽기 값 리스트

    Returns:
        처리된 데이터 딕셔너리
    """
    logger.debug(f"[{sensor_id}] 데이터 처리 시작 - {len(readings)}건")

    if not readings:
        logger.warning(f"[{sensor_id}] 빈 데이터 수신")
        return {"sensor_id": sensor_id, "status": "no_data"}

    # 기본 통계 계산
    avg = sum(readings) / len(readings)
    max_val = max(readings)
    min_val = min(readings)

    logger.info(f"[{sensor_id}] 데이터 처리 완료 - 평균: {avg:.2f}")

    # 이상 온도 확인
    if max_val > 80:
        logger.error(f"[{sensor_id}] 위험 온도 감지: {max_val}도")
    elif max_val > 60:
        logger.warning(f"[{sensor_id}] 주의 온도 감지: {max_val}도")

    logger.debug(f"[{sensor_id}] 통계 - 최소: {min_val}, 최대: {max_val}")

    return {
        "sensor_id": sensor_id,
        "status": "processed",
        "mean": round(avg, 4),
        "min": min_val,
        "max": max_val,
    }


def log_alert(sensor_id, alert_type, message, level="WARNING"):
    """알림 로그를 기록한다.

    Args:
        sensor_id: 센서 ID
        alert_type: 알림 유형 ("temperature", "vibration", "pressure")
        message: 알림 메시지
        level: 로그 레벨 문자열 (기본: "WARNING")
    """
    log_message = f"[알림][{alert_type}][{sensor_id}] {message}"

    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = level_map.get(level.upper(), logging.WARNING)
    logger.log(log_level, log_message)


def process_and_report(sensor_data_list):
    """여러 센서 데이터를 처리하고 보고서를 출력한다.

    stdout으로 요약 출력, logging으로 상세 로그 기록을 동시에 수행한다.

    Args:
        sensor_data_list: 센서 데이터 딕셔너리 리스트

    Returns:
        처리 결과 리스트
    """
    print(f"센서 데이터 일괄 처리 시작: {len(sensor_data_list)}개 센서")

    results = []
    error_count = 0

    for sensor_data in sensor_data_list:
        sensor_id = sensor_data.get("sensor_id", "UNKNOWN")
        readings = sensor_data.get("readings", [])

        try:
            result = log_data_processing(sensor_id, readings)
            results.append(result)
        except Exception as e:
            logger.error(f"[{sensor_id}] 처리 실패: {str(e)}")
            error_count += 1

    print(f"처리 완료: 성공 {len(results)}건, 실패 {error_count}건")

    if error_count > 0:
        sys.stderr.write(f"경고: {error_count}건의 처리 실패 발생\n")

    return results
