# 04. 객체지향 프로그래밍 (OOP)

> 날짜: 2026-02-17
> 목표: 클래스, 상속, 캡슐화, 다형성 (예지보전 맥락)

---

## OOP 4대 개념 요약

| 개념 | 키워드 | 한 줄 요약 |
|------|--------|-----------|
| 클래스/객체 | `class`, `__init__`, `self` | 설계도로 객체 찍어내기 |
| 상속 | `class 자식(부모)`, `super()` | 공통 기능 물려받고 확장 |
| 캡슐화 | `_`, `__`, `@property` | 내부 데이터 보호 + 검증 |
| 다형성 | 오버라이딩 | 같은 메서드명, 객체마다 다른 동작 |

---

## 클래스와 객체

```python
class Motor:
    def __init__(self, name, temp, rpm):   # 생성자
        self.name = name                    # 속성
        self.temp = temp
        self.rpm = rpm

    def check_status(self):                 # 메서드
        if self.temp > 90:
            return "주의"
        return "정상"

m1 = Motor("모터A", 82, 1750)   # 객체 생성
m1.check_status()                # 메서드 호출 (self 안 넣음!)
```

- `self`는 파이썬이 자동으로 넣어줌
- `m1.check_status()` → 내부적으로 `Motor.check_status(m1)`

---

## 상속

```python
class Equipment:          # 부모
    def __init__(self, name, temp):
        self.name = name
        self.temp = temp

    def check_temp(self):
        if self.temp > 90:
            return "과열 주의"
        return "정상"

class Motor(Equipment):   # 자식 (Equipment 상속)
    def __init__(self, name, temp, rpm):
        super().__init__(name, temp)   # 부모 생성자 호출
        self.rpm = rpm                 # 자식만의 속성
```

- `super().__init__()` 안 하면 부모 속성이 초기화 안 됨

---

## 캡슐화

```python
class Motor:
    def __init__(self, temp):
        self._temp = temp         # _ : "건드리지 마" 약속

    @property
    def temp(self):               # 읽을 때
        return self._temp

    @temp.setter
    def temp(self, value):        # 쓸 때 (검증 가능)
        if value < -40 or value > 300:
            print("잘못된 온도")
            return
        self._temp = value

m = Motor(82)
m.temp = 95      # 속성처럼 쓰지만, 내부에서 검증됨
m.temp = -500    # "잘못된 온도" → 값 안 바뀜
```

### 언더스코어 규칙

| 표기 | 의미 | 접근 |
|------|------|------|
| `self.temp` | 공개 | 자유 |
| `self._temp` | 보호 (약속) | 가능하지만 자제 |
| `self.__temp` | Name Mangling | `_클래스명__temp`로만 접근 |

---

## 다형성

```python
class Motor(Equipment):
    def diagnose(self):        # 같은 이름
        return "RPM 체크"

class Pump(Equipment):
    def diagnose(self):        # 같은 이름, 다른 동작
        return "유량 체크"

# 종류 상관없이 같은 코드로 처리
for eq in [Motor(...), Pump(...)]:
    eq.diagnose()              # 각자 알아서 동작
```

---

## 유용한 함수

- `isinstance(obj, Class)` - 객체가 특정 클래스인지 확인 (상속 포함)
- `type(obj)` - 객체의 정확한 클래스 확인 (상속 미포함)

---

## 실습 파일

- `practices/04-oop.py`
