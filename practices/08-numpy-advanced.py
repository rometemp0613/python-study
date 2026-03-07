"""
NumPy 심화 - 통계 함수, 난수, 선형대수
실습 + 연습 문제
"""
import numpy as np

# ============================================================
# 실습 예제: 모터 센서 시뮬레이션
# ============================================================

# 1. 가짜 센서 데이터 생성 (30일, 하루 24시간)
rng = np.random.default_rng(seed=42)
normal_temps = rng.normal(loc=72, scale=3, size=(30, 24))

# 15일차에 이상 발생 시뮬레이션 (온도 급등)
normal_temps[14, :] += 15  # 15일차 전체 +15도

# 2. 통계 요약
daily_avg = np.mean(normal_temps, axis=1)
daily_std = np.std(normal_temps, axis=1)
print("=== 일별 평균 온도 (처음 5일) ===")
for i in range(5):
    print(f"Day {i+1}: 평균 {daily_avg[i]:.1f}°C, 표준편차 {daily_std[i]:.1f}°C")

# 3. IQR로 이상 일자 탐지
q1 = np.percentile(daily_avg, 25)
q3 = np.percentile(daily_avg, 75)
iqr = q3 - q1
upper = q3 + 1.5 * iqr

abnormal_days = np.where(daily_avg > upper)[0]
print(f"\n정상 상한: {upper:.1f}°C")
print(f"이상 감지 일자: {abnormal_days + 1}일차")

# 4. 상관분석 - 온도와 진동
fake_vibration = normal_temps.mean(axis=1) * 0.05 + rng.normal(0, 0.1, 30)
corr = np.corrcoef(daily_avg, fake_vibration)[0, 1]
print(f"\n온도-진동 상관계수: {corr:.3f}")


# ============================================================
# 연습 문제 1: 센서 통계 리포트
# ============================================================
# rng.normal(loc=150, scale=10, size=100)으로 압력 센서 데이터 100개를 만들고:
# - 평균, 중앙값, 표준편차, 최솟값, 최댓값 출력
# - 상위 5% 값(np.percentile 95번째)을 구하고, 그 이상인 데이터 개수 세기

print("\n=== 연습 문제 1 ===")
# 여기에 코드를 작성하세요
rng = np.random.default_rng(seed=42)
normal_pres = rng.normal(loc=150, scale=10, size=100)

daily_avg = np.mean(normal_pres)
daily_med = np.median(normal_pres)
daily_std = np.std(normal_pres)
daily_min = np.min(normal_pres)
daily_max = np.max(normal_pres)

upper = np.percentile(normal_pres, 95)
abnormal_data = np.where(normal_pres > upper)[0]
print(abnormal_data.shape[0])

# ============================================================
# 연습 문제 2: 행렬 연습
# ============================================================
# 3x3 행렬 [[1,2,3],[4,5,6],[7,8,10]]의:
# - 전치행렬
# - 행렬식(determinant)
# - 역행렬

print("\n=== 연습 문제 2 ===")
# 여기에 코드를 작성하세요
arr = np.array([[1,2,3],
       [4,5,6],
       [7,8,10]])

print(arr.T)
print(np.linalg.det(arr))
print(np.linalg.inv(arr))

# ============================================================
# 연습 문제 3: 시뮬레이션 데이터 만들기
# ============================================================
# 평균 70, 표준편차 2인 정상 데이터 900개 +
# 평균 90, 표준편차 5인 이상 데이터 100개를 합쳐서
# 1000개짜리 배열 만들기
# 힌트: np.concatenate()

print("\n=== 연습 문제 3 ===")
# 여기에 코드를 작성하세요
rng = np.random.default_rng(seed=42)
data1 = rng.normal(loc=70, scale=2, size=900)
data2 = rng.normal(loc=90, scale=5, size=100)
arr = np.concatenate([data1, data2])
print(arr)