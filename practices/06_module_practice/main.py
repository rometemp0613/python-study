"""메인 실행 파일 - equipment 패키지를 활용한 설비 모니터링"""

# === import 방식 비교 ===

# 방법 1: 패키지에서 직접 가져오기 (__init__.py 덕분에 가능)
from equipment import get_all_readings, check_temperature, check_vibration, check_pressure, generate_report

# 방법 2: 모듈을 명시해서 가져오기 (더 명확함)
from equipment.sensor import MAX_TEMP, MAX_VIBRATION, MAX_PRESSURE

# 방법 3: 모듈 자체를 가져오기
from equipment import alarm


def monitor_equipment(sensor_ids: list[str]) -> None:
    """여러 설비를 한 번에 모니터링"""
    print("\n🏭 설비 모니터링 시스템 시작\n")

    for sensor_id in sensor_ids:
        # 센서 데이터 읽기
        readings = get_all_readings(sensor_id)

        # 알람 체크
        alarms = {
            "temperature": check_temperature(readings["temperature"]),
            "vibration": check_vibration(readings["vibration"]),
            "pressure": check_pressure(readings["pressure"]),
        }

        # 리포트 출력
        report = generate_report(sensor_id, readings, alarms)
        print(report)

        # 위험 알람이 있으면 추가 경고
        if alarm.LEVEL_CRITICAL in alarms.values():
            print(f"  ⚠️  [{sensor_id}] 즉시 점검 필요!\n")
        print()

    # 상수 활용 예시
    print(f"📋 허용 기준 - 온도: {MAX_TEMP}°C, 진동: {MAX_VIBRATION} mm/s, 압력: {MAX_PRESSURE} MPa")


if __name__ == "__main__":
    # 모니터링할 설비 목록
    equipment_list = ["MOTOR-001", "PUMP-002", "FAN-003"]
    monitor_equipment(equipment_list)
