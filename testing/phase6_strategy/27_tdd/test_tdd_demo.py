"""
TDD 데모 테스트 - Red-Green-Refactor 사이클 시연

이 파일은 SensorAnomalyDetector를 TDD로 개발하는 과정을 보여줍니다.
각 테스트에는 어떤 TDD 사이클에서 작성되었는지 주석으로 표시되어 있습니다.

실행 방법:
    pytest test_tdd_demo.py -v
"""

import math
import pytest
from src_anomaly_detector_tdd import SensorAnomalyDetector


# =============================================================================
# 사이클 1: 빈 감지기 생성
# =============================================================================
# RED: SensorAnomalyDetector 클래스가 아직 없어서 ImportError 발생
# GREEN: 빈 클래스와 __init__, get_reading_count 메서드 구현
# REFACTOR: 타입 힌트 추가

class TestSensorAnomalyDetector_사이클1_생성:
    """사이클 1: 감지기 생성과 초기 상태 확인"""

    def test_새로운_감지기는_비어있다(self):
        """RED: 이 테스트를 먼저 작성 → ImportError로 실패"""
        detector = SensorAnomalyDetector()
        assert detector.get_reading_count() == 0

    def test_새로운_감지기의_이상치_카운트는_0이다(self):
        """RED: get_anomaly_count가 없어서 실패"""
        detector = SensorAnomalyDetector()
        assert detector.get_anomaly_count() == 0


# =============================================================================
# 사이클 2: 데이터 추가
# =============================================================================
# RED: add_reading 메서드가 없어서 AttributeError 발생
# GREEN: add_reading 메서드와 내부 리스트 구현
# REFACTOR: 없음 (코드가 충분히 단순)

class TestSensorAnomalyDetector_사이클2_데이터추가:
    """사이클 2: 측정값 추가 기능"""

    def test_데이터_하나_추가(self):
        """RED: add_reading 메서드가 없어서 실패"""
        detector = SensorAnomalyDetector()
        detector.add_reading(25.0)
        assert detector.get_reading_count() == 1

    def test_데이터_여러개_추가(self):
        """GREEN 후 추가 테스트: 여러 데이터 추가 확인"""
        detector = SensorAnomalyDetector()
        detector.add_reading(25.0)
        detector.add_reading(26.0)
        detector.add_reading(24.5)
        assert detector.get_reading_count() == 3


# =============================================================================
# 사이클 3: 입력값 검증
# =============================================================================
# RED: NaN 값을 넣어도 에러가 발생하지 않아서 실패
# GREEN: add_reading에 검증 로직 추가
# REFACTOR: 에러 메시지를 한국어로 개선

class TestSensorAnomalyDetector_사이클3_입력검증:
    """사이클 3: 잘못된 입력값 거부"""

    def test_NaN_값_거부(self):
        """RED: NaN이 그냥 추가되어 실패"""
        detector = SensorAnomalyDetector()
        with pytest.raises(ValueError, match="유한한 숫자"):
            detector.add_reading(float('nan'))

    def test_무한대_값_거부(self):
        """RED → GREEN: 무한대도 거부해야 함"""
        detector = SensorAnomalyDetector()
        with pytest.raises(ValueError):
            detector.add_reading(float('inf'))

    def test_음의_무한대_값_거부(self):
        """추가 테스트: 음의 무한대도 거부"""
        detector = SensorAnomalyDetector()
        with pytest.raises(ValueError):
            detector.add_reading(float('-inf'))

    def test_문자열_값_거부(self):
        """RED: 문자열 입력 시 TypeError 발생해야 함"""
        detector = SensorAnomalyDetector()
        with pytest.raises(TypeError, match="숫자 타입"):
            detector.add_reading("not_a_number")

    def test_정수값_허용(self):
        """GREEN: 정수도 유효한 입력"""
        detector = SensorAnomalyDetector()
        detector.add_reading(25)  # int도 허용
        assert detector.get_reading_count() == 1


# =============================================================================
# 사이클 4: 평균 계산
# =============================================================================
# RED: get_mean 메서드가 없어서 실패
# GREEN: 단순 평균 계산 구현
# REFACTOR: 빈 데이터 처리를 위해 ValueError 추가

class TestSensorAnomalyDetector_사이클4_평균:
    """사이클 4: 평균 계산"""

    def test_단일값_평균(self):
        """RED: get_mean이 없어서 실패"""
        detector = SensorAnomalyDetector()
        detector.add_reading(25.0)
        assert detector.get_mean() == 25.0

    def test_여러값_평균(self):
        """GREEN 후 검증: 여러 값의 평균"""
        detector = SensorAnomalyDetector()
        detector.add_reading(10.0)
        detector.add_reading(20.0)
        detector.add_reading(30.0)
        assert detector.get_mean() == 20.0

    def test_빈_데이터_평균_에러(self):
        """REFACTOR 중 추가: 빈 데이터에서 평균 계산 시 에러"""
        detector = SensorAnomalyDetector()
        with pytest.raises(ValueError, match="데이터가 없습니다"):
            detector.get_mean()


# =============================================================================
# 사이클 5: 표준편차 계산
# =============================================================================
# RED: get_std 메서드가 없어서 실패
# GREEN: 모표준편차 계산 구현
# REFACTOR: get_mean 재사용

class TestSensorAnomalyDetector_사이클5_표준편차:
    """사이클 5: 표준편차 계산"""

    def test_동일값_표준편차는_0(self):
        """RED: get_std가 없어서 실패"""
        detector = SensorAnomalyDetector()
        detector.add_reading(25.0)
        detector.add_reading(25.0)
        detector.add_reading(25.0)
        assert detector.get_std() == 0.0

    def test_표준편차_계산(self):
        """GREEN: 알려진 값으로 표준편차 검증"""
        detector = SensorAnomalyDetector()
        for v in [10.0, 20.0, 30.0]:
            detector.add_reading(v)
        # 모표준편차: sqrt(((10-20)^2 + (20-20)^2 + (30-20)^2) / 3)
        # = sqrt(200/3) ≈ 8.1650
        expected_std = math.sqrt(200.0 / 3.0)
        assert abs(detector.get_std() - expected_std) < 0.0001

    def test_빈_데이터_표준편차_에러(self):
        """REFACTOR: 빈 데이터 처리"""
        detector = SensorAnomalyDetector()
        with pytest.raises(ValueError, match="데이터가 없습니다"):
            detector.get_std()


# =============================================================================
# 사이클 6: 이상치 감지
# =============================================================================
# RED: is_anomaly 메서드가 없어서 실패
# GREEN: n-시그마 기반 이상치 감지 구현
# REFACTOR: n_sigma 매개변수 추가, 기본값 3

class TestSensorAnomalyDetector_사이클6_이상치감지:
    """사이클 6: 이상치 감지"""

    def test_정상값은_이상치가_아니다(self):
        """RED: is_anomaly가 없어서 실패"""
        detector = SensorAnomalyDetector()
        for v in [100.0, 101.0, 99.0, 100.5, 99.5]:
            detector.add_reading(v)
        # 평균 근처의 값은 이상치가 아님
        assert detector.is_anomaly(100.0) is False

    def test_극단값은_이상치이다(self):
        """GREEN: 평균에서 크게 벗어난 값은 이상치"""
        detector = SensorAnomalyDetector()
        for v in [100.0, 100.0, 100.0, 100.0, 100.0]:
            detector.add_reading(v)
        # 모든 값이 동일할 때, 다른 값은 이상치
        assert detector.is_anomaly(200.0) is True

    def test_시그마_배수_조정(self):
        """REFACTOR: n_sigma 매개변수로 민감도 조절"""
        detector = SensorAnomalyDetector()
        # 평균=100, 표준편차가 있는 데이터
        for v in [90.0, 95.0, 100.0, 105.0, 110.0]:
            detector.add_reading(v)

        mean = detector.get_mean()  # 100.0
        std = detector.get_std()    # ~7.07

        # 2시그마 범위 밖의 값
        test_value = mean + 2.5 * std
        assert detector.is_anomaly(test_value, n_sigma=2) is True
        # 3시그마 범위 안의 값
        assert detector.is_anomaly(test_value, n_sigma=3) is False

    def test_데이터_부족시_에러(self):
        """REFACTOR: 데이터가 2개 미만이면 에러"""
        detector = SensorAnomalyDetector()
        detector.add_reading(100.0)
        with pytest.raises(ValueError, match="최소 2개"):
            detector.is_anomaly(200.0)


# =============================================================================
# 사이클 7: 이상치 카운트
# =============================================================================
# RED: 이상치를 감지할 때마다 카운트가 증가하는지 확인
# GREEN: is_anomaly에서 이상치 발견 시 카운트 증가
# REFACTOR: reset 메서드 추가

class TestSensorAnomalyDetector_사이클7_이상치카운트:
    """사이클 7: 이상치 카운트 추적"""

    def test_이상치_감지시_카운트_증가(self):
        """RED: 이상치 카운트가 증가하지 않아서 실패"""
        detector = SensorAnomalyDetector()
        for v in [100.0, 100.0, 100.0, 100.0, 100.0]:
            detector.add_reading(v)

        detector.is_anomaly(200.0)  # 이상치 감지
        assert detector.get_anomaly_count() == 1

    def test_정상값은_카운트_증가_안함(self):
        """GREEN: 정상값 판별 시 카운트 유지"""
        detector = SensorAnomalyDetector()
        for v in [100.0, 101.0, 99.0, 100.5, 99.5]:
            detector.add_reading(v)

        detector.is_anomaly(100.0)  # 정상값
        assert detector.get_anomaly_count() == 0

    def test_여러_이상치_카운트(self):
        """GREEN: 여러 이상치 감지"""
        detector = SensorAnomalyDetector()
        for v in [100.0, 100.0, 100.0, 100.0, 100.0]:
            detector.add_reading(v)

        detector.is_anomaly(200.0)  # 이상치 1
        detector.is_anomaly(0.0)    # 이상치 2
        detector.is_anomaly(100.0)  # 정상값
        assert detector.get_anomaly_count() == 2

    def test_리셋_후_카운트_초기화(self):
        """REFACTOR: reset 기능 추가"""
        detector = SensorAnomalyDetector()
        for v in [100.0, 100.0, 100.0, 100.0, 100.0]:
            detector.add_reading(v)

        detector.is_anomaly(200.0)
        assert detector.get_anomaly_count() == 1

        detector.reset()
        assert detector.get_anomaly_count() == 0
        assert detector.get_reading_count() == 0


# =============================================================================
# 통합 테스트: 전체 시나리오
# =============================================================================

class TestSensorAnomalyDetector_통합:
    """전체 기능 통합 테스트"""

    def test_실제_센서_시나리오(self):
        """
        실제 공장 센서 시나리오:
        온도 센서가 정상 범위(70~80도)에서 동작하다가
        갑자기 120도를 기록하는 경우
        """
        detector = SensorAnomalyDetector()

        # 정상 운전 데이터 추가
        normal_readings = [72.0, 74.5, 73.2, 75.1, 74.8,
                           73.9, 75.5, 74.0, 73.5, 74.2]
        for reading in normal_readings:
            detector.add_reading(reading)

        # 통계 확인
        assert 73.0 < detector.get_mean() < 75.0
        assert detector.get_std() < 2.0

        # 정상 범위 값 - 이상치 아님
        assert detector.is_anomaly(75.0) is False

        # 비정상 값 - 이상치
        assert detector.is_anomaly(120.0) is True
        assert detector.get_anomaly_count() == 1

    def test_데이터_복사본_반환(self):
        """get_readings는 원본이 아닌 복사본을 반환해야 한다."""
        detector = SensorAnomalyDetector()
        detector.add_reading(25.0)

        readings = detector.get_readings()
        readings.append(999.0)  # 복사본 수정

        # 원본에는 영향 없음
        assert detector.get_reading_count() == 1
