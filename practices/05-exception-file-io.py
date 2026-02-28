# 05. 예외 처리 & 파일 I/O
# 센서 데이터를 다루면서 예외 처리와 파일 I/O를 배워보자!

# ============================================
# 1) 기본 try/except
# ============================================
print("=" * 50)
print("1) 기본 try/except")
print("=" * 50)

raw_value = "N/A"

try:
    temperature = float(raw_value)
except ValueError:
    print(f"잘못된 센서 값: {raw_value}")
    temperature = None

print(f"결과: temperature = {temperature}")
print()

# ============================================
# 2) 여러 예외 잡기
# ============================================
print("=" * 50)
print("2) 여러 예외 잡기")
print("=" * 50)

def read_sensor_data(filepath):
    try:
        with open(filepath, "r") as f:
            data = f.read()
        value = float(data.strip())
        return value
    except FileNotFoundError:
        print(f"  파일 없음: {filepath}")
        return None
    except ValueError:
        print(f"  숫자 변환 실패")
        return None
    except Exception as e:
        print(f"  예상치 못한 에러: {e}")
        return None

# 존재하지 않는 파일 읽기 시도
result = read_sensor_data("없는파일.txt")
print(f"결과: {result}")
print()

# ============================================
# 3) else와 finally
# ============================================
print("=" * 50)
print("3) else와 finally")
print("=" * 50)

for raw in ["72.5", "N/A", "85.0"]:
    print(f"  입력값: {raw}")
    try:
        value = float(raw)
    except ValueError:
        print(f"    -> 변환 실패!")
    else:
        print(f"    -> 변환 성공: {value}")
    finally:
        print(f"    -> 처리 완료 (항상 실행)")
    print()

# ============================================
# 4) with문 & 파일 쓰기/읽기
# ============================================
print("=" * 50)
print("4) with문 & 파일 쓰기/읽기")
print("=" * 50)

# 파일 쓰기
with open("sensor_log.txt", "w") as f:
    f.write("2026-02-28 10:00 모터 온도: 72.5°C\n")
    f.write("2026-02-28 10:01 모터 온도: 73.1°C\n")
    f.write("2026-02-28 10:02 모터 온도: 85.0°C\n")
print("sensor_log.txt 파일 생성 완료!")

# 파일 읽기
with open("sensor_log.txt", "r") as f:
    content = f.read()
print("파일 내용:")
print(content)

# 파일 추가(append)
with open("sensor_log.txt", "a") as f:
    f.write("2026-02-28 10:03 모터 온도: 91.2°C [경고]\n")
print("한 줄 추가 후:")
with open("sensor_log.txt", "r") as f:
    print(f.read())

# ============================================
# 5) CSV 파일 다루기
# ============================================
print("=" * 50)
print("5) CSV 파일 다루기")
print("=" * 50)

import csv

# CSV 쓰기
sensor_data = [
    ["timestamp", "temperature", "vibration"],
    ["2026-02-28 10:00", 72.5, 2.8],
    ["2026-02-28 10:01", 73.1, 3.0],
    ["2026-02-28 10:02", 85.0, 4.5],
    ["2026-02-28 10:03", 91.2, 6.1],
]

with open("sensor_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(sensor_data)
print("sensor_data.csv 생성 완료!")

# CSV 읽기
print("\nCSV 읽기 결과:")
with open("sensor_data.csv", "r") as f:
    reader = csv.reader(f)
    header = next(reader)  # 첫 줄 헤더
    print(f"  헤더: {header}")
    for row in reader:
        timestamp, temp, vib = row
        print(f"  {timestamp}: 온도={temp}°C, 진동={vib}mm/s")
print()

# ============================================
# 6) 커스텀 예외
# ============================================
print("=" * 50)
print("6) 커스텀 예외")
print("=" * 50)

class SensorError(Exception):
    """센서 관련 에러의 기본 클래스"""
    pass

class SensorOutOfRange(SensorError):
    """센서 값이 허용 범위를 벗어남"""
    def __init__(self, sensor_name, value, min_val, max_val):
        self.sensor_name = sensor_name
        self.value = value
        super().__init__(
            f"{sensor_name}: {value} (허용 범위: {min_val}~{max_val})"
        )

def check_temperature(value):
    if not (0 <= value <= 150):
        raise SensorOutOfRange("온도센서", value, 0, 150)
    return value

# 정상 값 테스트
try:
    result = check_temperature(72.5)
    print(f"  정상: {result}°C")
except SensorOutOfRange as e:
    print(f"  경고: {e}")

# 비정상 값 테스트
try:
    result = check_temperature(200)
    print(f"  정상: {result}°C")
except SensorOutOfRange as e:
    print(f"  경고: {e}")

# ============================================
# 7) 종합 실습: CSV 읽고 검증하기
# ============================================
print()
print("=" * 50)
print("7) 종합 실습: CSV 읽고 검증하기")
print("=" * 50)

def process_sensor_csv(filepath):
    """센서 CSV 파일을 읽고 온도를 검증하는 함수"""
    results = []

    try:
        with open(filepath, "r") as f:
            reader = csv.reader(f)
            header = next(reader)

            for row in reader:
                timestamp, temp_str, vib_str = row
                try:
                    temp = float(temp_str)
                    check_temperature(temp)
                    results.append({
                        "timestamp": timestamp,
                        "temperature": temp,
                        "status": "정상"
                    })
                except ValueError:
                    results.append({
                        "timestamp": timestamp,
                        "temperature": None,
                        "status": "데이터 오류"
                    })
                except SensorOutOfRange:
                    results.append({
                        "timestamp": timestamp,
                        "temperature": temp,
                        "status": "범위 초과!"
                    })
    except FileNotFoundError:
        print(f"  파일을 찾을 수 없습니다: {filepath}")
        return []

    return results

# 아까 만든 CSV 파일로 테스트
results = process_sensor_csv("sensor_data.csv")
for r in results:
    print(f"  {r['timestamp']}: {r['temperature']}°C -> [{r['status']}]")

# 정리: 생성한 임시 파일 삭제
import os
os.remove("sensor_log.txt")
os.remove("sensor_data.csv")
print("\n임시 파일 정리 완료!")
print("\n학습 끝! 수고했어! 🎉")


# ============================================
# 연습 1) 안전한 숫자 변환 함수
# ============================================

def safe_float(value, default=0.0):
    """문자열을 float으로 변환. 실패하면 default 반환."""
    # 여기에 코드 작성
    try:
        temperature = float(value)
    except ValueError:
        print(f"잘못된 센서 값: {value}")
        temperature = None
    else:
        print(f"올바른 센서 값: {value}")
    finally:
        return temperature
    pass

print(safe_float("72.5"))
print(safe_float("N/A"))
print(safe_float("",-1.0))



# ============================================
# 연습 2) 설비 로그 파일 쓰기
# ============================================

logs = [
    {"name": "모터A", "temp":72.5, "status": "정상"},
    {"name": "모터B", "temp": 95.3, "status": "경고"},
    {"name": "펌프C", "temp": 45.0, "status": "정상"},
]

with open("sensor_log.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(sensor_data)

with open("sensor_log.csv", "r") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        timestamp, temp, vib = row
        print(f"{timestamp}: 온도={temp}, 진동={vib}")


# ============================================
# 연습 3) 커스텀 예외 만들기
# 진동 센서의 허용 범위는 0~10mm/s야. VibrationOutOfRange 예외를
#   만들고 검증 함수를 작성해봐:
# ============================================

class SensorError(Exception):
    """센서 관련 에러의 기본 클래스"""
    pass

class VibrationOutOfRange(SensorError):
    """진동 값이 허용 범위를 벗어남"""
    def __init__(self, sensor_name, value, min_val, max_val):
        self.sensor_name = sensor_name
        self.value = value
        super().__init__(
            f"{sensor_name}: {value} (허용 범위: {min_val}~{max_val})"
        )

def check_vibration(value):
    if not (2.0 <= value <= 4.0):
        raise VibrationOutOfRange("진동센서", value, 2.0, 4.0)
    return value

try:
    check_vibration(5)
except VibrationOutOfRange as e:
    print(f"경고: {e}")
    