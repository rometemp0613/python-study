# 03. 자료구조

> 날짜: 2026-02-16
> 목표: 리스트, 튜플, 딕셔너리, 집합, 컴프리헨션 (예지보전 맥락)

---

## 4가지 자료구조 비교

| | 리스트 `list` | 튜플 `tuple` | 딕셔너리 `dict` | 집합 `set` |
|---|---|---|---|---|
| 문법 | `[1, 2, 3]` | `(1, 2, 3)` | `{"a": 1}` | `{1, 2, 3}` |
| 순서 | O | O | O (3.7+) | X |
| 변경 | O | X | O | O |
| 중복 | O | O | 키 X | X |
| 용도 | 측정값 모음 | 고정 스펙, 함수 반환 | 센서별 데이터 관리 | 중복 제거, 집합 연산 |

---

## 리스트 핵심

```python
# 인덱싱
data[0]       # 첫 번째
data[-1]      # 마지막

# 슬라이싱 [시작:끝] — 끝은 미포함
data[:3]      # 앞 3개
data[-2:]     # 뒤 2개

# 추가/삭제
data.append(값)       # 맨 뒤 추가
data.insert(위치, 값)  # 특정 위치 삽입 (뒤 원소 밀림)
data.pop()            # 맨 뒤 꺼내기 (제거+반환)
data.remove(값)       # 특정 값 제거 (첫 번째 일치)

# 정렬
data.sort()           # 원본 변경
sorted(data)          # 새 리스트 반환 (원본 유지)

# 유용한 것들
len(data)             # 길이
data.count(5)         # 5가 몇 개?
data.index(5)         # 5의 위치
5 in data             # 5가 있나? True/False
```

---

## 튜플 핵심

```python
spec = ("VIB-001", "진동센서", 0.0, 20.0)

# 인덱싱/슬라이싱은 리스트와 동일
spec[0]   # "VIB-001"

# 변경 불가
spec[0] = "X"  # ❌ TypeError

# 언패킹
sensor_id, sensor_type, min_val, max_val = spec

# 함수 반환값은 사실 튜플
def get_range(data):
    return min(data), max(data)  # 튜플 반환

lo, hi = get_range([2.1, 7.8])  # 바로 언패킹
```

---

## 딕셔너리 핵심

```python
sensor = {"id": "VIB-001", "threshold": 10.0}

# 접근
sensor["id"]                          # 키 없으면 KeyError
sensor.get("status", "미설정")         # 키 없으면 기본값 반환 ← 실무 필수

# 추가/수정/삭제
sensor["status"] = "active"           # 추가 또는 수정
del sensor["status"]                  # 삭제

# 순회 3가지
for key in sensor.keys():             # 키만
for value in sensor.values():         # 값만
for key, value in sensor.items():     # 키+값 ← 가장 많이 씀

# 카운팅 패턴
count = {}
count[key] = count.get(key, 0) + 1   # 키 없으면 0부터 시작
```

---

## 집합 핵심

```python
# 중복 제거
unique = set([1, 2, 2, 3, 3])  # {1, 2, 3}

# 집합 연산
a & b    # 교집합 (둘 다 있는 것)
a | b    # 합집합 (하나라도 있는 것)
a - b    # 차집합 (a에만 있는 것)

# in 연산은 집합이 리스트보다 훨씬 빠름
"VIB-001" in my_set
```

---

## 컴프리헨션 (Comprehension)

### 리스트 컴프리헨션

```python
# 기본
[val * 2 for val in readings]

# 필터링
[val for val in readings if val > 5.0]

# 조건부 변환
[f"{val}(위험)" if val > 10 else f"{val}" for val in readings]
```

### 딕셔너리 컴프리헨션

```python
# 두 리스트 → 딕셔너리
{k: v for k, v in zip(keys, values)}

# 필터링
{k: v for k, v in data.items() if v > 5.0}
```

### 집합 컴프리헨션

```python
{x.split("-")[0] for x in ["VIB-001", "TEMP-001"]}
# → {"VIB", "TEMP"}
```

### 컴프리헨션 vs for문

```python
# 컴프리헨션
warnings = [v for v in readings if v > 5.0]

# 같은 결과의 for문
warnings = []
for v in readings:
    if v > 5.0:
        warnings.append(v)
```

---

## zip() — 여러 리스트 동시 순회

```python
ids = ["VIB-001", "VIB-002"]
vals = [3.2, 8.7]

# 동시 순회
for id, val in zip(ids, vals):
    print(f"{id}: {val}")

# 딕셔너리 만들기
sensor_dict = dict(zip(ids, vals))
# {"VIB-001": 3.2, "VIB-002": 8.7}
```

---

## lambda — 이름 없는 한 줄 함수

```python
# lambda 버전
sorted(data.items(), key=lambda x: x[1], reverse=True)

# 같은 의미의 일반 함수
def get_value(x):
    return x[1]
sorted(data.items(), key=get_value, reverse=True)
```

`key=lambda x: x[1]`은 "각 원소의 두 번째 값을 기준으로 정렬"이라는 뜻.

---

## 실습 파일

- `practices/03-data-structures.py`
