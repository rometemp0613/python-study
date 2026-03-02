"""센서 모듈 - 설비 센서 데이터를 읽고 관리하는 모듈"""

import random

# 모듈 레벨 상수
MAX_TEMP: float = 100.0
MAX_VIBRATION: float = 10.0
MAX_PRESSURE: float = 11.0

def read_temperature(sensor_id: str) -> float:
    """센서에서 온도(°C)를 읽어옴"""
    # 실제로는 하드웨어에서 읽지만, 시뮬레이션
    base_temp = 65.0
    noise = random.uniform(-5.0, 15.0)
    return round(base_temp + noise, 1)


def read_vibration(sensor_id: str) -> float:
    """센서에서 진동값(mm/s)을 읽어옴"""
    base_vib = 2.0
    noise = random.uniform(-1.0, 5.0)
    return round(base_vib + noise, 2)

def read_pressure(sensor_id: str) -> float:
    """센서에서 압력값(MPa)을 읽어옴"""
    base_pres = 5.0
    noise = random.uniform(-1.0, 3.0)
    return round(base_pres + noise, 2)

def get_all_readings(sensor_id: str) -> dict[str, float]:
    """센서의 모든 측정값을 딕셔너리로 반환"""
    return {
        "temperature": read_temperature(sensor_id),
        "vibration": read_vibration(sensor_id),
        "pressure": read_pressure(sensor_id),
    }


# 이 파일을 직접 실행할 때만 동작하는 테스트 코드
if __name__ == "__main__":
    print("=== 센서 모듈 테스트 ===")
    test_id = "TEST-001"
    print(f"온도: {read_temperature(test_id)}°C")
    print(f"진동: {read_vibration(test_id)} mm/s")
    print(f"전체: {get_all_readings(test_id)}")
