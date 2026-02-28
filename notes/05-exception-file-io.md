# 05. 예외 처리 & 파일 I/O

> 날짜: 2026-02-28
> 목표: try/except/else/finally, with문, 파일 모드, csv 모듈, 커스텀 예외 (예지보전 맥락)

---

## 예외 처리 요약

| 키워드 | 역할 | 실행 조건 |
|--------|------|----------|
| `try` | 예외가 발생할 수 있는 코드 | 항상 실행 |
| `except` | 예외 발생 시 처리 | 예외 발생 시 |
| `else` | 예외 없을 때 실행 | 예외 미발생 시 |
| `finally` | 무조건 실행 (정리 작업) | 항상 실행 |

---

## try/except/else/finally

```python
try:
    temp = float(input("온도 입력: "))
    result = 100 / temp
except ValueError:
    print("숫자를 입력해주세요")
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다")
else:
    print(f"결과: {result}")       # 예외 없을 때만 실행
finally:
    print("측정 종료")              # 무조건 실행
```

- `except`는 여러 개 가능 (구체적인 예외부터 위에 배치)
- `except Exception as e:` 로 에러 메시지 받을 수 있음
- `else`는 try 성공 시에만 실행 → 에러 범위를 좁힐 수 있음
- `finally`는 파일 닫기, DB 연결 해제 등 정리 작업에 사용

---

## with문 (컨텍스트 매니저)

```python
# with문 사용 (권장)
with open("sensor_log.csv", "r") as f:
    data = f.read()
# 블록 끝나면 자동으로 f.close() 호출

# with문 없이 (비권장)
f = open("sensor_log.csv", "r")
try:
    data = f.read()
finally:
    f.close()    # 수동으로 닫아야 함
```

- `with`가 자동으로 `close()` 호출 → 리소스 누수 방지
- 예외가 발생해도 안전하게 닫힘
- 파일, DB 연결, 네트워크 소켓 등에 활용

---

## 파일 모드

| 모드 | 의미 | 파일 없으면 | 파일 있으면 |
|------|------|------------|------------|
| `"r"` | 읽기 (기본값) | FileNotFoundError | 처음부터 읽기 |
| `"w"` | 쓰기 | 새로 생성 | **덮어쓰기 (주의!)** |
| `"a"` | 추가 | 새로 생성 | 끝에 이어쓰기 |
| `"x"` | 배타적 생성 | 새로 생성 | FileExistsError |

```python
# 센서 데이터 기록 (추가 모드 - 기존 데이터 보존)
with open("vibration_log.txt", "a") as f:
    f.write(f"2026-02-28 14:30, 모터A, 진동: 4.2mm/s\n")

# 배타적 생성 - 실수로 기존 파일 덮어쓰기 방지
with open("report_20260228.txt", "x") as f:
    f.write("일일 점검 보고서\n")
```

---

## 파일 읽기/쓰기

```python
# 한 줄씩 읽기 (메모리 효율적 - 대용량 센서 로그에 적합)
with open("sensor_log.txt", "r") as f:
    for line in f:
        print(line.strip())

# 전체 읽기
with open("sensor_log.txt", "r") as f:
    content = f.read()       # 문자열 하나로
    # 또는
    lines = f.readlines()    # 줄 단위 리스트로

# 여러 줄 쓰기
with open("output.txt", "w") as f:
    f.write("첫 번째 줄\n")
    f.writelines(["두 번째\n", "세 번째\n"])
```

---

## csv 모듈

```python
import csv

# CSV 쓰기
with open("sensor_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["시간", "설비", "온도", "진동"])          # 헤더
    writer.writerow(["14:00", "모터A", 82.5, 3.1])
    writer.writerow(["14:05", "모터A", 83.2, 3.4])

# CSV 읽기
with open("sensor_data.csv", "r") as f:
    reader = csv.reader(f)
    header = next(reader)           # 헤더 건너뛰기
    for row in reader:
        time, equip, temp, vib = row
        print(f"{equip} - 온도: {temp}°C, 진동: {vib}mm/s")

# DictReader/DictWriter (딕셔너리로 읽고 쓰기)
with open("sensor_data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["설비"], row["온도"])   # 컬럼명으로 접근
```

- `newline=""` : Windows에서 빈 줄 방지용
- `DictReader`가 가독성 좋음 → 컬럼 순서 신경 안 써도 됨

---

## 커스텀 예외

```python
class SensorError(Exception):
    """센서 관련 기본 예외"""
    pass

class TemperatureAlarmError(SensorError):
    """온도 임계값 초과 시 발생"""
    def __init__(self, sensor_name, temp, threshold):
        self.sensor_name = sensor_name
        self.temp = temp
        self.threshold = threshold
        super().__init__(
            f"{sensor_name}: 온도 {temp}°C (임계값 {threshold}°C 초과)"
        )

class VibrationAlarmError(SensorError):
    """진동 임계값 초과 시 발생"""
    pass

# 사용
def check_temperature(name, temp, threshold=90):
    if temp > threshold:
        raise TemperatureAlarmError(name, temp, threshold)
    return "정상"

try:
    check_temperature("모터A", 105)
except TemperatureAlarmError as e:
    print(f"[경보] {e}")
    print(f"센서: {e.sensor_name}, 현재 온도: {e.temp}°C")
```

- `Exception`을 상속해서 만듦
- 상속 계층 구조로 예외를 분류하면 유지보수가 쉬움
- `raise`로 직접 예외를 발생시킴

---

## 예지보전 실무 패턴: 센서 로그 처리

```python
import csv
from datetime import datetime

class SensorReadError(Exception):
    pass

def process_sensor_log(filepath):
    """센서 로그 파일을 읽어서 이상 데이터를 분리"""
    normal = []
    anomalies = []

    try:
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    temp = float(row["온도"])
                    vib = float(row["진동"])
                except (ValueError, KeyError) as e:
                    anomalies.append({"row": row, "error": str(e)})
                    continue

                if temp > 90 or vib > 7.0:
                    anomalies.append({"row": row, "reason": "임계값 초과"})
                else:
                    normal.append(row)
    except FileNotFoundError:
        raise SensorReadError(f"파일 없음: {filepath}")

    return normal, anomalies
```

- 외부 `try`: 파일 존재 여부 처리
- 내부 `try`: 각 행의 데이터 파싱 에러 처리
- `continue`로 에러 행만 건너뛰고 나머지 계속 처리

---

## 실습 파일

- `practices/05-exception-file-io.py`
