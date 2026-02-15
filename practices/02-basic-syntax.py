# =============================================================
# 02. Python 기본 문법 복습 - 예지보전 예제
# =============================================================

# %% [1] 변수와 자료형
# -------------------------------------------------------------
# Python의 기본 자료형: int, float, str, bool

# 센서 정보
sensor_id = "VIB-001"          # str: 센서 ID
temperature = 72.5              # float: 온도 (°C)
vibration = 3.2                 # float: 진동 (mm/s)
rpm = 1500                      # int: 분당 회전수
is_running = True               # bool: 가동 여부

# type()으로 자료형 확인
print("=== 변수와 자료형 ===")
print(f"sensor_id: {sensor_id} → {type(sensor_id).__name__}")
print(f"temperature: {temperature} → {type(temperature).__name__}")
print(f"vibration: {vibration} → {type(vibration).__name__}")
print(f"rpm: {rpm} → {type(rpm).__name__}")
print(f"is_running: {is_running} → {type(is_running).__name__}")

# f-string: 문자열 안에 변수를 넣는 방법
# f"텍스트 {변수}" 형태로 사용
print(f"\n센서 {sensor_id}: 온도={temperature}°C, 진동={vibration}mm/s")


# %% [2] 자료형 변환
# -------------------------------------------------------------
# 센서에서 데이터가 문자열로 들어오는 경우가 많음

raw_value = "85.3"  # 센서에서 문자열로 받은 온도값
print("\n=== 자료형 변환 ===")
print(f"변환 전: {raw_value} ({type(raw_value).__name__})")

temp_value = float(raw_value)  # str → float
print(f"변환 후: {temp_value} ({type(temp_value).__name__})")

# 숫자 → 문자열
alarm_code = 42
alarm_msg = "에러 코드: " + str(alarm_code)  # int → str
print(alarm_msg)


# %% [3] 조건문 (if / elif / else)
# -------------------------------------------------------------
# 센서 값에 따라 설비 상태를 판단하는 가장 기본적인 방법

vibration = 7.5  # mm/s

print("\n=== 조건문: 진동 상태 판단 ===")
print(f"현재 진동값: {vibration} mm/s")

if vibration < 2.0:
    status = "정상"
elif vibration < 5.0:
    status = "주의"
elif vibration < 10.0:
    status = "경고"
else:
    status = "위험"

print(f"설비 상태: {status}")

# 비교 연산자: <, >, <=, >=, ==, !=
# 논리 연산자: and, or, not

# 복합 조건: 온도도 높고 진동도 높으면 즉시 정지
temperature = 95.0
vibration = 12.0

if temperature > 90 and vibration > 10:
    print(f"\n즉시 정지 필요! (온도={temperature}°C, 진동={vibration}mm/s)")
elif temperature > 90 or vibration > 10:
    print(f"\n주의 관찰 필요 (온도={temperature}°C, 진동={vibration}mm/s)")


# %% [4] 반복문 (for / while)
# -------------------------------------------------------------

# --- for문: 여러 센서를 순회하며 체크 ---
print("\n=== for문: 센서 순회 ===")

sensor_readings = [2.1, 4.8, 7.3, 1.5, 11.2, 3.9]

for i, reading in enumerate(sensor_readings):
    if reading > 10:
        label = "⚠ 위험"
    elif reading > 5:
        label = "! 경고"
    else:
        label = "  정상"

    print(f"  센서 {i+1}: {reading:5.1f} mm/s  [{label}]")

# enumerate(): 인덱스와 값을 동시에 가져옴
# f"{reading:5.1f}": 소수점 1자리, 전체 5자리 폭으로 정렬

# --- range(): 숫자 범위 생성 ---
print("\n=== range() 활용 ===")
for hour in range(0, 24, 6):  # 0, 6, 12, 18
    print(f"  {hour:02d}:00 점검")
# range(시작, 끝, 간격) - 끝은 포함하지 않음

# --- while문: 조건이 만족될 때까지 반복 ---
print("\n=== while문: 온도 감시 ===")

temp = 80.0
cycle = 0

while temp < 95.0:
    temp += 3.5  # 매 사이클마다 3.5도 상승
    cycle += 1
    print(f"  사이클 {cycle}: {temp:.1f}°C")

print(f"  → {cycle}번째 사이클에서 임계온도(95°C) 도달!")

# --- break와 continue ---
print("\n=== break: 이상치 발견 시 즉시 중단 ===")

readings = [2.1, 3.5, 2.8, 15.0, 3.2, 2.9]

for i, val in enumerate(readings):
    if val > 10:
        print(f"  센서 {i+1}에서 이상치 발견! ({val} mm/s) → 점검 중단")
        break
    print(f"  센서 {i+1}: {val} mm/s OK")


# %% [5] 함수 (def)
# -------------------------------------------------------------
# 반복되는 로직을 함수로 묶으면 재사용 가능

print("\n=== 함수 정의와 호출 ===")


def check_vibration(value, threshold=10.0):
    """진동값을 받아서 상태를 반환하는 함수.

    Args:
        value: 진동 측정값 (mm/s)
        threshold: 위험 임계값 (기본값: 10.0)

    Returns:
        상태 문자열 ("정상", "주의", "경고", "위험")
    """
    if value < threshold * 0.2:
        return "정상"
    elif value < threshold * 0.5:
        return "주의"
    elif value < threshold:
        return "경고"
    else:
        return "위험"


# 함수 호출
test_values = [1.5, 4.2, 8.7, 12.3]
for val in test_values:
    result = check_vibration(val)
    print(f"  {val:5.1f} mm/s → {result}")

# threshold를 바꿔서 호출 (키워드 인자)
print("\n  [threshold=5.0으로 변경]")
for val in test_values:
    result = check_vibration(val, threshold=5.0)
    print(f"  {val:5.1f} mm/s → {result}")


# %% [6] 함수 - 여러 값 반환
# -------------------------------------------------------------

print("\n=== 함수: 여러 값 반환 ===")


def analyze_sensor(readings):
    """센서 데이터의 기본 통계를 계산하는 함수.

    Args:
        readings: 측정값 리스트

    Returns:
        (최솟값, 최댓값, 평균값) 튜플
    """
    min_val = min(readings)
    max_val = max(readings)
    avg_val = sum(readings) / len(readings)
    return min_val, max_val, avg_val


data = [72.1, 73.5, 75.2, 74.8, 76.1, 71.9, 78.3]

# 여러 값을 한 번에 받기 (언패킹)
lo, hi, avg = analyze_sensor(data)
print(f"  온도 분석: 최저={lo}°C, 최고={hi}°C, 평균={avg:.1f}°C")


# %% [7] 종합 실습: 간단한 설비 모니터링
# -------------------------------------------------------------

print("\n" + "=" * 50)
print("종합 실습: 설비 모니터링 리포트")
print("=" * 50)


def generate_report(sensor_name, readings, threshold):
    """센서 데이터를 분석하여 리포트를 출력하는 함수."""
    lo, hi, avg = analyze_sensor(readings)
    abnormal_count = 0

    for val in readings:
        if check_vibration(val, threshold) == "위험":
            abnormal_count += 1

    print(f"\n[{sensor_name}]")
    print(f"  측정 횟수: {len(readings)}회")
    print(f"  범위: {lo} ~ {hi} mm/s")
    print(f"  평균: {avg:.2f} mm/s")
    print(f"  이상 횟수: {abnormal_count}회")

    if abnormal_count > 0:
        ratio = abnormal_count / len(readings) * 100
        print(f"  이상 비율: {ratio:.1f}% → 정밀 점검 필요!")
    else:
        print(f"  상태: 양호")


# 실제 데이터로 리포트 생성
generate_report(
    "1호기 베어링",
    [2.1, 3.5, 2.8, 4.1, 3.2, 2.9, 3.8, 4.5],
    threshold=10.0,
)

generate_report(
    "2호기 모터",
    [5.2, 7.8, 11.3, 9.5, 12.1, 8.4, 6.7, 10.8],
    threshold=10.0,
)


def analyze_pressure(pressure):
    if pressure < 100:
        return "저압"
    elif pressure < 200:
        return "정상"
    elif pressure < 300:
        return "고압"
    else:
        return "위험"

def print_above_avg(pressures):
    total = 0
    for ele in enumerate(pressures):
        total += ele
    avg = total/len(pressures)
    
    for ele in enumerate(pressures):
        if(ele > avg): 
            print(ele)

pressures = [150, 210, 95, 180, 310, 275, 190]
for i, ele in enumerate(pressures):
    print(f"센서{i+1} 값: {ele}, 상태: {analyze_pressure(ele)}")

