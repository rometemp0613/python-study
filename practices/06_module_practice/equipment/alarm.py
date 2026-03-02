"""알람 모듈 - 설비 상태를 판단하고 알람을 발생시키는 모듈"""

from typing import Optional


# 알람 레벨 상수
LEVEL_NORMAL: str = "정상"
LEVEL_WARNING: str = "경고"
LEVEL_CRITICAL: str = "위험"


def check_temperature(temp: float, warn: float = 80.0, critical: float = 95.0) -> str:
    """온도 기반 알람 레벨 판단"""
    if temp >= critical:
        return LEVEL_CRITICAL
    elif temp >= warn:
        return LEVEL_WARNING
    return LEVEL_NORMAL


def check_vibration(vib: float, warn: float = 5.0, critical: float = 8.0) -> str:
    """진동 기반 알람 레벨 판단"""
    if vib >= critical:
        return LEVEL_CRITICAL
    elif vib >= warn:
        return LEVEL_WARNING
    return LEVEL_NORMAL

def check_pressure(pres: float, warn: float = 7.0, critical: float = 9.0) -> str:
    """압력 기반 알람 레벨 판단"""
    if pres >= critical:
        return LEVEL_CRITICAL
    elif pres >= warn: 
        return LEVEL_WARNING
    return LEVEL_NORMAL

def generate_report(
    sensor_id: str,
    readings: dict[str, float],
    alarms: dict[str, str],
) -> str:
    """설비 상태 리포트 문자열 생성"""
    lines = [
        f"{'='*40}",
        f" 설비 상태 리포트: {sensor_id}",
        f"{'='*40}",
    ]

    for key, value in readings.items():
        alarm = alarms.get(key, "N/A")
        lines.append(f"  {key:>15}: {value:>8} | [{alarm}]")

    lines.append(f"{'='*40}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("=== 알람 모듈 테스트 ===")
    print(f"온도 70°C → {check_temperature(70)}")
    print(f"온도 85°C → {check_temperature(85)}")
    print(f"온도 98°C → {check_temperature(98)}")
