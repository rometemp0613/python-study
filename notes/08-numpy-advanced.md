# NumPy 심화 — 통계 함수, 난수, 선형대수

센서가 하루에 만 개씩 데이터를 쏟아내는데, 이걸 어떻게 한 줄로 요약할까?
"평균 72°C, 표준편차 3.2°C, 최대 85°C" — NumPy 통계 함수가 해준다.

---

## 1. 통계 함수 — 데이터를 숫자 하나로 요약하기

### 기본 통계 함수

```python
import numpy as np

# 모터 온도 센서: 1주일, 하루 5회 측정
temps = np.array([
    [72, 73, 71, 74, 72],  # 월
    [73, 75, 74, 76, 75],  # 화
    [71, 72, 70, 73, 71],  # 수
    [80, 82, 81, 83, 82],  # 목 ← 뭔가 이상?
    [74, 75, 73, 76, 74],  # 금
])

np.mean(temps)      # 전체 평균
np.std(temps)       # 표준편차 (데이터가 얼마나 흩어져 있나)
np.var(temps)       # 분산 (표준편차의 제곱)
np.median(temps)    # 중앙값 (이상치에 덜 민감!)
np.min(temps)       # 최솟값
np.max(temps)       # 최댓값
```

### axis로 방향 지정하기

```python
# 요일별 평균 (각 행의 평균) → axis=1
daily_avg = np.mean(temps, axis=1)
# [72.4, 74.6, 71.4, 81.6, 74.4]
#                     ↑ 목요일만 확 높다!

# 측정 시간대별 평균 (각 열의 평균) → axis=0
time_avg = np.mean(temps, axis=0)
```

> 1차원 배열에는 axis 불필요! `axis=1` 쓰면 AxisError 나니까 주의.

### 분위수 & IQR 이상치 탐지

센서 데이터에서 "비정상" 값을 찾는 가장 기본적인 방법이 IQR이다.

```python
q1 = np.percentile(daily_avg, 25)   # 25% 지점 (Q1)
q3 = np.percentile(daily_avg, 75)   # 75% 지점 (Q3)
iqr = q3 - q1                       # 사분위 범위

lower = q1 - 1.5 * iqr              # 하한선
upper = q3 + 1.5 * iqr              # 상한선

# 이 범위(약 99.3%)를 벗어나면 이상치!
abnormal_days = np.where(daily_avg > upper)[0]
print(f"이상 감지: {abnormal_days + 1}일차")  # → 4일차(목)
```

```
IQR 이상치 탐지 원리:
├── lower ────── Q1 ──── 중앙값 ──── Q3 ────── upper ──┤
  이상치 영역     ←─── 정상 범위 (약 99.3%) ───→     이상치 영역
```

### 상관계수 — 두 센서 사이의 관계

모터 온도가 올라가면 진동도 올라갈까? 상관계수로 확인한다.

```python
motor_temp = np.array([72, 74, 71, 81, 74])
vibration  = np.array([2.1, 2.3, 2.0, 3.5, 2.2])

corr = np.corrcoef(motor_temp, vibration)
print(corr[0, 1])  # 0.99 → 거의 완벽한 양의 상관!
```

| 상관계수 값 | 의미 |
|------------|------|
| +1에 가까움 | 같이 올라감 (양의 상관) |
| 0에 가까움 | 관계 없음 |
| -1에 가까움 | 하나 올라가면 하나 내려감 (음의 상관) |

---

## 2. 난수 생성 — 가짜 센서 데이터 만들기

모델을 테스트하려면 실제와 비슷한 가짜 데이터가 필요하다.

### 기본 사용법

```python
# 재현 가능한 난수 생성기 만들기
rng = np.random.default_rng(seed=42)

# 균등분포 (0~1 사이 랜덤)
uniform = rng.random(5)

# 정규분포 — 실제 센서 데이터와 비슷!
# loc=평균, scale=표준편차, size=개수
fake_temps = rng.normal(loc=72, scale=3, size=1000)

# 정수 랜덤
random_ints = rng.integers(0, 100, size=10)
```

### seed를 고정하는 이유: 재현성(reproducibility)

```python
rng1 = np.random.default_rng(seed=42)
rng2 = np.random.default_rng(seed=42)
print(rng1.random(3))  # [0.773... 0.438... 0.858...]
print(rng2.random(3))  # [0.773... 0.438... 0.858...] ← 동일!
```

같은 seed → 같은 난수 → 누가 돌려도 같은 결과.
논문이나 실험 보고서에서 항상 seed를 명시하는 이유가 이것이다.

### 실습: 이상 데이터 혼합 시뮬레이션

```python
rng = np.random.default_rng(seed=42)

# 정상 데이터 900개 + 이상 데이터 100개
normal = rng.normal(loc=70, scale=2, size=900)
abnormal = rng.normal(loc=90, scale=5, size=100)
combined = np.concatenate([normal, abnormal])   # 리스트로 묶어서 전달!

print(f"전체 평균: {combined.mean():.1f}")  # 70보다 높을 것 (이상치 때문)
print(f"전체 개수: {len(combined)}")        # 1000
```

> `np.concatenate(a, b)` (X) → `np.concatenate([a, b])` (O) — 리스트로 묶기!

### 옛날 방식 vs 새 방식

```python
# 옛날 (인터넷에 많이 보이지만 비추)
np.random.seed(42)
np.random.randn(5)

# 새 방식 (권장) — Generator 객체 사용
rng = np.random.default_rng(42)
rng.standard_normal(5)
```

---

## 3. 선형대수 — 행렬 연산과 연립방정식

### 행렬 곱 & 전치

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

A @ B     # 행렬 곱 (권장 문법)
A.T       # 전치행렬 (행 ↔ 열 뒤집기)
```

> 주의: `[[1,2],[3,4]]`는 파이썬 리스트! `.T`나 `@`는 `np.array()`로 감싸야 사용 가능.

### 연립방정식 풀기 — 센서 보정 예시

```
2x + 3y = 100   (센서A 방정식)
4x + 1y = 120   (센서B 방정식)
```

```python
A = np.array([[2, 3], [4, 1]])
b = np.array([100, 120])

x = np.linalg.solve(A, b)
print(x)  # [26. 16.] → 실제온도=26, 보정계수=16
```

### 선형대수 함수 정리표

| 함수 | 설명 | 비고 |
|------|------|------|
| `A @ B` | 행렬 곱 | `np.dot(A, B)`와 동일 |
| `A.T` | 전치행렬 | 행↔열 교환 |
| `np.linalg.det(A)` | 행렬식 | 0이면 역행렬 없음 |
| `np.linalg.inv(A)` | 역행렬 | det=0이면 에러! |
| `np.linalg.solve(A, b)` | 연립방정식 풀기 | Ax = b |
| `np.linalg.eig(A)` | 고유값/고유벡터 | PCA에서 사용 |

---

## 주의사항 & 흔한 실수

- **1차원에 axis**: `size=100`으로 만든 배열에 `axis=1` → AxisError. axis 생략하기
- **리스트 vs ndarray**: `[[1,2],[3,4]]`에 `.T` → 안 됨. `np.array()`로 감싸야 함
- **concatenate 문법**: `np.concatenate(a, b)` (X) → `np.concatenate([a, b])` (O)
- **행렬식 0 체크**: `np.linalg.det(A)`가 0이면 역행렬 불가. `inv()` 전에 확인하기
- **난수 방식**: 새 코드에서는 `np.random.seed()` 대신 `default_rng(seed)` 사용
- **출력 잊지 말기**: 통계 값을 변수에 저장만 하고 `print()` 안 하면 결과를 볼 수 없음!
