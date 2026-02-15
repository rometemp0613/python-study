# =============================================================
# 03. 자료구조 - 예지보전 예제
# =============================================================

# %% [1] 리스트 (list) - 순서가 있는 변경 가능한 컬렉션
# -------------------------------------------------------------
# 가장 많이 쓰는 자료구조. 센서 측정값처럼 순서대로 쌓이는 데이터에 적합.

print("=== 리스트 기초 ===")

# 생성
vibrations = [2.1, 3.5, 2.8, 4.1, 3.2]
print(f"원본: {vibrations}")

# 인덱싱 (0부터 시작)
print(f"첫 번째: {vibrations[0]}")   # 2.1
print(f"마지막: {vibrations[-1]}")    # 3.2 (-1은 뒤에서 첫 번째)

# 슬라이싱 [시작:끝] — 끝은 포함하지 않음
print(f"앞 3개: {vibrations[0:3]}")   # [2.1, 3.5, 2.8]
print(f"앞 3개: {vibrations[:3]}")    # 같은 결과 (0 생략 가능)
print(f"뒤 2개: {vibrations[-2:]}")   # [4.1, 3.2]

# 추가/삭제
vibrations.append(5.7)        # 맨 뒤에 추가
print(f"append 후: {vibrations}")

vibrations.insert(0, 1.5)     # 특정 위치에 삽입
print(f"insert(0) 후: {vibrations}")

removed = vibrations.pop()    # 맨 뒤 꺼내기 (제거 + 반환)
print(f"pop 후: {vibrations}, 꺼낸 값: {removed}")

vibrations.remove(3.5)        # 특정 값 제거 (첫 번째 일치하는 것만)
print(f"remove(3.5) 후: {vibrations}")

# 정렬
readings = [4.2, 1.8, 7.3, 2.1, 5.5]
readings.sort()                # 원본을 직접 정렬 (오름차순)
print(f"\nsort() 후: {readings}")

readings.sort(reverse=True)    # 내림차순
print(f"내림차순: {readings}")

# sorted()는 원본은 안 건드리고 새 리스트 반환
original = [4.2, 1.8, 7.3]
new_sorted = sorted(original)
print(f"\noriginal: {original}")       # 그대로
print(f"sorted:   {new_sorted}")       # 정렬된 새 리스트

# 유용한 메서드
nums = [3, 1, 4, 1, 5, 9, 2, 6, 5]
print(f"\nlen: {len(nums)}")            # 길이: 9
print(f"count(5): {nums.count(5)}")     # 5가 몇 개? 2
print(f"index(4): {nums.index(4)}")     # 4의 위치: 2
print(f"1 in nums: {1 in nums}")        # 1이 있나? True


# %% [2] 튜플 (tuple) - 순서가 있는 변경 불가능한 컬렉션
# -------------------------------------------------------------
# 한 번 만들면 수정 불가. 변하면 안 되는 데이터에 사용.
# 예: 센서 스펙, 고장 기록, 좌표 등

print("\n=== 튜플 기초 ===")

# 생성
sensor_spec = ("VIB-001", "진동센서", 0.0, 20.0)  # (ID, 타입, 최소, 최대)
print(f"센서 스펙: {sensor_spec}")

# 인덱싱, 슬라이싱은 리스트와 동일
print(f"센서 ID: {sensor_spec[0]}")
print(f"측정 범위: {sensor_spec[2]} ~ {sensor_spec[3]} mm/s")

# 변경 시도 → 에러!
# sensor_spec[0] = "VIB-002"  # TypeError: 'tuple' object does not support item assignment

# 언패킹 — 튜플의 진짜 강점
sensor_id, sensor_type, min_val, max_val = sensor_spec
print(f"\n언패킹: {sensor_id}, {sensor_type}, {min_val}~{max_val}")

# 함수가 여러 값을 반환할 때 사실 튜플이야
def get_range(data):
    return min(data), max(data)  # 튜플로 반환

result = get_range([2.1, 3.5, 7.8, 1.2])
print(f"\n반환값: {result}")              # (1.2, 7.8) — 튜플!
print(f"타입: {type(result).__name__}")   # tuple

lo, hi = get_range([2.1, 3.5, 7.8, 1.2])  # 바로 언패킹
print(f"언패킹: {lo} ~ {hi}")

# 리스트 vs 튜플: 언제 뭘 쓰나?
# 리스트: 데이터가 추가/삭제될 때 (측정값 모음)
# 튜플: 데이터가 고정일 때 (센서 스펙, 좌표, 기록)


# %% [3] 딕셔너리 (dict) - 키:값 쌍의 컬렉션
# -------------------------------------------------------------
# 가장 실무에서 많이 쓰는 자료구조 중 하나.
# "이름으로 찾기"가 가능해서 센서 ID별 데이터 관리에 딱.

print("\n=== 딕셔너리 기초 ===")

# 생성
sensor = {
    "id": "VIB-001",
    "type": "vibration",
    "location": "1호기 베어링",
    "threshold": 10.0,
    "unit": "mm/s",
}
print(f"센서 정보: {sensor}")

# 값 접근
print(f"\nID: {sensor['id']}")
print(f"위치: {sensor['location']}")

# get() — 키가 없어도 에러 안 남 (기본값 반환)
print(f"상태: {sensor.get('status', '미설정')}")  # 키 없으면 '미설정'

# 추가/수정
sensor["status"] = "active"        # 새 키 추가
sensor["threshold"] = 12.0         # 기존 값 수정
print(f"\n수정 후: {sensor}")

# 삭제
del sensor["unit"]                 # 키 삭제
print(f"삭제 후: {sensor}")

# 순회 — 3가지 방법
print("\n--- keys ---")
for key in sensor.keys():
    print(f"  {key}")

print("\n--- values ---")
for value in sensor.values():
    print(f"  {value}")

print("\n--- items (키+값) ---")
for key, value in sensor.items():
    print(f"  {key}: {value}")


# %% [4] 딕셔너리 실전 — 여러 센서 관리
# -------------------------------------------------------------

print("\n=== 딕셔너리 실전: 센서 관리 시스템 ===")

# 센서 ID를 키로, 측정값 리스트를 값으로
sensor_data = {
    "VIB-001": [2.1, 3.5, 2.8, 4.1, 3.2],
    "TEMP-001": [72.1, 73.5, 75.2, 74.8, 76.1],
    "PRESS-001": [150, 155, 148, 162, 158],
}

thresholds = {
    "VIB-001": 10.0,
    "TEMP-001": 90.0,
    "PRESS-001": 200.0,
}

# 모든 센서의 평균값과 상태를 출력
for sensor_id, readings in sensor_data.items():
    avg = sum(readings) / len(readings)
    threshold = thresholds[sensor_id]
    status = "정상" if avg < threshold else "주의"
    print(f"  {sensor_id}: 평균={avg:.1f}, 임계치={threshold}, 상태={status}")

# 딕셔너리 안에 딕셔너리 (중첩)
equipment = {
    "1호기": {
        "type": "모터",
        "sensors": ["VIB-001", "TEMP-001"],
        "status": "가동중",
    },
    "2호기": {
        "type": "펌프",
        "sensors": ["VIB-002", "PRESS-001"],
        "status": "점검중",
    },
}

print(f"\n1호기 타입: {equipment['1호기']['type']}")
print(f"1호기 센서: {equipment['1호기']['sensors']}")


# %% [5] 집합 (set) - 중복 없는 컬렉션
# -------------------------------------------------------------
# 중복 제거, 교집합/합집합 등에 유용.

print("\n=== 집합 기초 ===")

# 생성
alarm_today = {"VIB-001", "TEMP-001", "VIB-001", "PRESS-001", "TEMP-001"}
print(f"알람 발생 센서: {alarm_today}")  # 중복 자동 제거

# 리스트에서 중복 제거
raw_alarms = ["VIB-001", "TEMP-001", "VIB-001", "PRESS-001", "TEMP-001"]
unique_alarms = set(raw_alarms)
print(f"중복 제거: {unique_alarms}")
print(f"알람 종류 수: {len(unique_alarms)}")

# 집합 연산 — 진짜 유용한 부분
alarm_yesterday = {"VIB-001", "TEMP-002", "VIB-003"}
alarm_today = {"VIB-001", "TEMP-001", "PRESS-001"}

print(f"\n어제 알람: {alarm_yesterday}")
print(f"오늘 알람: {alarm_today}")

# 교집합: 어제도 오늘도 알람 (지속적인 문제)
print(f"연속 알람:    {alarm_yesterday & alarm_today}")

# 합집합: 어제 또는 오늘 알람 (전체 문제 센서)
print(f"전체 알람:    {alarm_yesterday | alarm_today}")

# 차집합: 오늘 새로 발생한 알람
print(f"신규 알람:    {alarm_today - alarm_yesterday}")

# 차집합: 어제는 있었는데 오늘은 없는 알람 (해결된 것)
print(f"해결된 알람:  {alarm_yesterday - alarm_today}")

# in 연산 — 집합이 리스트보다 훨씬 빠름
print(f"\nVIB-001 알람 있나? {'VIB-001' in alarm_today}")


# %% [6] 컴프리헨션 (Comprehension) - 한 줄로 데이터 가공
# -------------------------------------------------------------
# for문을 한 줄로 압축. 데이터 변환/필터링에 자주 사용.

print("\n=== 리스트 컴프리헨션 ===")

# 기본 형태: [표현식 for 변수 in 반복가능]
readings = [2.1, 3.5, 7.8, 1.2, 12.5, 4.3, 9.1]

# for문으로 쓰면
doubled = []
for val in readings:
    doubled.append(val * 2)
print(f"for문: {doubled}")

# 컴프리헨션으로 쓰면 (같은 결과)
doubled = [val * 2 for val in readings]
print(f"컴프리헨션: {doubled}")

# 조건 필터링: [표현식 for 변수 in 반복가능 if 조건]
warnings = [val for val in readings if val > 5.0]
print(f"\n5.0 초과: {warnings}")

# 변환 + 필터링 동시에
status_list = [
    f"{val:.1f}mm/s(위험)" if val > 10 else f"{val:.1f}mm/s"
    for val in readings
]
print(f"상태 표시: {status_list}")

# --- 딕셔너리 컴프리헨션 ---
print("\n=== 딕셔너리 컴프리헨션 ===")

sensor_ids = ["VIB-001", "VIB-002", "VIB-003"]
avg_values = [3.2, 8.7, 12.1]

# 두 리스트를 딕셔너리로 합치기
sensor_avg = {sid: avg for sid, avg in zip(sensor_ids, avg_values)}
print(f"센서별 평균: {sensor_avg}")

# 조건 필터링: 경고 이상만
warning_sensors = {sid: avg for sid, avg in sensor_avg.items() if avg > 5.0}
print(f"경고 센서: {warning_sensors}")

# --- 집합 컴프리헨션 ---
print("\n=== 집합 컴프리헨션 ===")

alarm_logs = ["VIB-001", "TEMP-001", "VIB-001", "VIB-002", "TEMP-001"]
unique_types = {log.split("-")[0] for log in alarm_logs}  # "VIB-001" → "VIB"
print(f"알람 타입 종류: {unique_types}")


# %% [7] zip() — 여러 리스트를 동시에 순회
# -------------------------------------------------------------
# 센서 데이터는 보통 여러 리스트로 나뉘어 있음. zip으로 묶으면 편함.

print("\n=== zip() 활용 ===")

timestamps = ["09:00", "10:00", "11:00", "12:00"]
temps = [72.1, 73.5, 75.2, 74.8]
vibs = [2.1, 3.5, 4.8, 7.2]

print("시간     온도    진동")
print("-" * 30)
for time, temp, vib in zip(timestamps, temps, vibs):
    print(f"{time}   {temp:5.1f}°C  {vib:4.1f}mm/s")


# %% [8] 종합 실습: 설비 알람 분석 시스템
# -------------------------------------------------------------

print("\n" + "=" * 50)
print("종합 실습: 설비 알람 분석")
print("=" * 50)

# 일주일간 알람 기록
weekly_alarms = {
    "월": ["VIB-001", "TEMP-001"],
    "화": ["VIB-001", "VIB-002", "TEMP-001"],
    "수": ["VIB-001"],
    "목": ["TEMP-002", "PRESS-001"],
    "금": ["VIB-001", "TEMP-001", "PRESS-001", "VIB-003"],
}

# 1. 전체 알람 센서 목록 (중복 제거)
all_sensors = set()
for day, sensors in weekly_alarms.items():
    all_sensors.update(sensors)  # 집합에 여러 원소 추가
print(f"\n이번 주 알람 발생 센서: {all_sensors}")
print(f"총 {len(all_sensors)}종류")

# 2. 센서별 알람 횟수 (딕셔너리)
alarm_count = {}
for day, sensors in weekly_alarms.items():
    for sensor in sensors:
        alarm_count[sensor] = alarm_count.get(sensor, 0) + 1

print(f"\n센서별 알람 횟수:")
for sensor, count in sorted(alarm_count.items(), key=lambda x: x[1], reverse=True):
    bar = "#" * count
    print(f"  {sensor:10s}: {bar} ({count}회)")

# 3. 3회 이상 알람 센서 (컴프리헨션)
frequent = {s: c for s, c in alarm_count.items() if c >= 3}
print(f"\n빈발 알람 (3회+): {frequent}")
print("→ 이 센서들은 정밀 점검 필요!")


# %%
# practice

temps = [72.1, 76.3, 74.5, 78.2, 71.8, 75.0, 80.1] 
warms = [val for val in temps if val >= 75.0]
print(warms)

ids = ["VIB-001", "VIB-002", "VIB-003"]
values = [3.2, 8.7, 12.1]
test_dict = {id: value for id, value in zip(ids, values)}
print(test_dict)

yesterday = ["VIB-001", "TEMP-001", "VIB-002"]
today = ["VIB-001", "PRESS-001", "TEMP-002"]

set_yesterday = set(yesterday)
set_today = set(today)

set_new = set_today - set_yesterday
print(set_new)
set_solved = set_yesterday - set_today
print(set_solved)
# %%
