# 4차시: OOP 실습 - 공장 설비 모니터링 시스템
# 클래스, 상속, 캡슐화, 다형성을 활용해서 설비 모니터링 시스템을 만들어보자!

# ============================================================
# 실습 1: 기본 클래스 만들기
# 센서는 ID, 위치, 측정값 리스트를 가지고 있어.
# ============================================================

class Sensor:
    def __init__(self, sensor_id, location):
        self.sensor_id = sensor_id
        self.location = location
        self.readings = []       # 측정값을 저장할 리스트

    def add_reading(self, value):
        """측정값 추가"""
        self.readings.append(value)

    def get_average(self):
        """평균값 계산"""
        if not self.readings:
            return 0
        return sum(self.readings) / len(self.readings)

    def get_latest(self):
        """최신 측정값"""
        if not self.readings:
            return None
        return self.readings[-1]

    def summary(self):
        """센서 요약 정보"""
        avg = self.get_average()
        latest = self.get_latest()
        return f"[{self.sensor_id}] 위치: {self.location}, 최신값: {latest}, 평균: {avg:.1f}"


# 사용해보기
s1 = Sensor("TEMP-001", "1호기 모터")
s1.add_reading(72.1)
s1.add_reading(73.5)
s1.add_reading(75.2)

print(s1.summary())
print(f"측정 횟수: {len(s1.readings)}개")

# 예상 결과:
# [TEMP-001] 위치: 1호기 모터, 최신값: 75.2, 평균: 73.6
# 측정 횟수: 3개


# ============================================================
# 실습 2: 상속 - 센서 종류별 클래스
# 온도센서, 진동센서는 각각 다른 임계치와 판단 기준이 있어.
# ============================================================

class TempSensor(Sensor):
    """온도 센서"""
    def __init__(self, sensor_id, location, threshold=90):
        super().__init__(sensor_id, location)
        self.threshold = threshold

    def diagnose(self):
        latest = self.get_latest()
        if latest is None:
            return "데이터 없음"
        if latest > self.threshold:
            return f"과열 경고! ({latest}°C > {self.threshold}°C)"
        return f"정상 ({latest}°C)"


class VibSensor(Sensor):
    """진동 센서"""
    def __init__(self, sensor_id, location, threshold=7.0):
        super().__init__(sensor_id, location)
        self.threshold = threshold

    def diagnose(self):
        latest = self.get_latest()
        if latest is None:
            return "데이터 없음"
        if latest > self.threshold:
            return f"진동 이상! ({latest}mm/s > {self.threshold}mm/s)"
        return f"정상 ({latest}mm/s)"


# 사용해보기
temp = TempSensor("TEMP-001", "1호기 모터")
temp.add_reading(85.0)
temp.add_reading(92.3)     # 임계치 초과!

vib = VibSensor("VIB-001", "1호기 모터")
vib.add_reading(3.2)
vib.add_reading(4.1)

print()
print(temp.summary())      # 부모 메서드 사용 가능
print(temp.diagnose())     # 자식 고유 메서드
print()
print(vib.summary())
print(vib.diagnose())

# 예상 결과:
# [TEMP-001] 위치: 1호기 모터, 최신값: 92.3, 평균: 88.6
# 과열 경고! (92.3°C > 90°C)
#
# [VIB-001] 위치: 1호기 모터, 최신값: 4.1, 평균: 3.6
# 정상 (4.1mm/s)


# ============================================================
# 실습 3: 캡슐화 - 임계치 보호
# 임계치를 아무 값이나 넣으면 안 돼. 검증 로직을 넣어보자.
# ============================================================

class SafeTempSensor(Sensor):
    """임계치가 보호된 온도 센서"""
    def __init__(self, sensor_id, location, threshold=90):
        super().__init__(sensor_id, location)
        self._threshold = threshold

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        if value < 0 or value > 500:
            print(f"잘못된 임계치: {value}°C (0~500 범위만 가능)")
            return
        print(f"임계치 변경: {self._threshold}°C -> {value}°C")
        self._threshold = value

    def diagnose(self):
        latest = self.get_latest()
        if latest is None:
            return "데이터 없음"
        if latest > self._threshold:
            return f"과열 경고! ({latest}°C > {self._threshold}°C)"
        return f"정상 ({latest}°C)"


# 사용해보기
print()
s = SafeTempSensor("TEMP-002", "2호기")
s.add_reading(85.0)

print(f"현재 임계치: {s.threshold}°C")
s.threshold = 80           # 정상 변경
s.threshold = -100         # 거부됨!
s.threshold = 9999         # 거부됨!
print(f"최종 임계치: {s.threshold}°C")

# 예상 결과:
# 현재 임계치: 90°C
# 임계치 변경: 90°C -> 80°C
# 잘못된 임계치: -100°C (0~500 범위만 가능)
# 잘못된 임계치: 9999°C (0~500 범위만 가능)
# 최종 임계치: 80°C


# ============================================================
# 실습 4: 다형성 - 전체 설비 점검
# 센서 종류가 달라도 diagnose() 하나로 전부 점검!
# ============================================================

import random
random.seed(42)

# 공장의 모든 센서
sensors = [
    TempSensor("TEMP-001", "1호기 모터"),
    TempSensor("TEMP-002", "2호기 모터"),
    VibSensor("VIB-001", "1호기 모터"),
    VibSensor("VIB-002", "3호기 펌프"),
]

# 센서 데이터 입력 (실제로는 센서에서 자동 수집)
for s in sensors:
    if isinstance(s, TempSensor):
        for _ in range(5):
            s.add_reading(round(random.uniform(70, 100), 1))
    else:
        for _ in range(5):
            s.add_reading(round(random.uniform(1, 10), 1))

# 다형성: 같은 코드로 전부 점검!
print()
print("=" * 50)
print("         공장 설비 일일 점검 리포트")
print("=" * 50)

alert_count = 0
for s in sensors:
    result = s.diagnose()
    status_mark = "[OK]" if "정상" in result else "[!!]"
    print(f"  {status_mark} {s.sensor_id} ({s.location}): {result}")
    if "정상" not in result:
        alert_count += 1

print("=" * 50)
print(f"  알람 발생: {alert_count}건")

#%%
#  ---
#   연습 문제 1: PressureSensor 클래스 만들기

#   Sensor를 상속받아서 압력 센서 클래스를 만들어봐.

#   조건:
#   - 임계치 기본값: 200 (단위: kPa)
#   - diagnose() 메서드: 최신값이 임계치를 넘으면 "압력 초과! (250kPa > 200kPa)", 아니면 "정상 (150kPa)"

class PressureSensor(Sensor):
    def __init__(self, sensor_id, location, threshold=200):
        super().__init__(sensor_id, location)
        self.threshold = threshold

    def diagnose(self):
        latest = self.get_latest()
        if(latest > self.threshold):
            return f"압력 초과! ({latest}kPa > {self.threshold}kPa)"
        else:
            return f"정상 ({latest}kPa)"
    
p = PressureSensor("PRESS-001", "2호기 컴프레서")
p.add_reading(180)
p.add_reading(250)
print(p.diagnose())  # 압력 초과! (250kPa > 200kPa)

    

#   ---
#   연습 문제 2: 설비(Equipment) 클래스

#   설비 하나에 센서 여러 개가 달려있는 구조를 만들어봐.

#   조건:
#   - Equipment 클래스: name(설비명), sensors(센서 리스트)
#   - add_sensor(sensor) 메서드: 센서 추가
#   - full_report() 메서드: 모든 센서의 diagnose() 결과를 출력

#   class Equipment:
#       # 여기를 채워봐!
#       pass

class Equipment:
    def __init__(self, name):
        self.name = name
        self.sensors = []

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def full_report(self):
        print(f"=== {self.name} 점검 ===")
        for s in self.sensors:
            print(s.diagnose())

# 테스트
motor = Equipment("1호기 모터")
motor.add_sensor(TempSensor("TEMP-001", "1호기 모터"))
motor.add_sensor(VibSensor("VIB-001", "1호기 모터"))

# 데이터 넣기
motor.sensors[0].add_reading(92.3)
motor.sensors[1].add_reading(8.5)

motor.full_report()
# 예상 결과:
# === 1호기 모터 점검 ===
# TEMP-001: 과열 경고! (92.3°C > 90°C)
# VIB-001: 진동 이상! (8.5mm/s > 7.0mm/s)

#   ---
#   연습 문제 3: 캡슐화 적용

#   연습 문제 1에서 만든 PressureSensor에 캡슐화를 적용해봐.

#   조건:
#   - 임계치를 _threshold로 보호
#   - @property와 @threshold.setter 사용
#   - 임계치 범위: 0 ~ 1000 kPa만 허용

class SafePressureSensor(Sensor):
    def __init__(self, sensor_id, location, threshold=200):
        super().__init__(sensor_id, location)
        self._threshold = threshold

    def diagnose(self):
        latest = self.get_latest()
        if(latest > self.threshold):
            return f"압력 초과! ({latest}kPa > {self.threshold}kPa)"
        else:
            return f"정상 ({latest}kPa)"
        
    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        if value < 0 or value > 1000:
            print(f"잘못된 임계치: {value}°C (0~1000 범위만 가능)")
            return
        print(f"임계치 변경: {self._threshold}°C -> {value}°C")
        self._threshold = value

#   ---
# %%
