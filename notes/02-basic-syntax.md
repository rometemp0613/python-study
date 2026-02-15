# 02. Python 기본 문법 복습

> 날짜: 2026-02-16
> 목표: 변수, 자료형, 조건문, 반복문, 함수 복습 (예지보전 맥락)

---

## 핵심 정리

### 자료형

| 타입 | 예시 | 용도 |
|------|------|------|
| `int` | `1500` | 정수 (RPM, 개수) |
| `float` | `72.5` | 소수 (온도, 진동값) |
| `str` | `"VIB-001"` | 문자열 (센서 ID, 상태) |
| `bool` | `True` | 참/거짓 (가동 여부) |

- `type(x)`: 자료형 확인
- `float("85.3")`, `str(42)`, `int(3.7)`: 형변환
- `f"온도: {temp}°C"`: f-string 포매팅

### 조건문

```python
if vibration < 2.0:
    status = "정상"
elif vibration < 5.0:
    status = "주의"
else:
    status = "경고"
```

- 비교: `<`, `>`, `<=`, `>=`, `==`, `!=`
- 논리: `and`, `or`, `not`

### 반복문

```python
# 리스트 직접 순회
for val in readings:

# 인덱스 + 값 동시에
for i, val in enumerate(readings):

# 숫자 범위
for i in range(0, 24, 6):   # 0, 6, 12, 18

# 조건까지 반복
while temp < 95.0:

# 중단
break     # 루프 즉시 탈출
continue  # 이번 회차 건너뛰기
```

### 함수

```python
def check_vibration(value, threshold=10.0):
    """docstring: 함수 설명."""
    if value < threshold:
        return "정상"
    return "위험"

# 여러 값 반환
def analyze(data):
    return min(data), max(data), sum(data)/len(data)

lo, hi, avg = analyze(data)  # 언패킹
```

- 기본값 인자는 반드시 뒤에: `def f(a, b=10):` ✓ / `def f(a=10, b):` ✗
- docstring: `def` 바로 다음 줄에 `"""설명"""` → VS Code 자동완성 팝업에 표시됨

---

## 자주 헷갈리는 것

| 하고 싶은 것 | 맞는 것 | 틀리기 쉬운 것 |
|---|---|---|
| 리스트 순회 | `for x in mylist:` | `for x in range(mylist):` |
| 인덱스+값 | `for i, x in enumerate(mylist):` | `for i, x in range(mylist):` |
| 리스트 길이 | `len(mylist)` | `count(mylist)` |
| 내장함수명 변수 | `total = 0` | `sum = 0` (내장함수 덮어씀) |

---

## 실습 파일

- `practices/02-basic-syntax.py`
