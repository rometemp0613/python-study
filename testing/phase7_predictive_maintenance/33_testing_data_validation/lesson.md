# 레슨 33: 데이터 유효성 검증 테스트

## 1. 학습 목표

이 레슨을 완료하면 다음을 할 수 있습니다:

- 센서 데이터의 스키마(컬럼, 타입)를 검증하는 테스트를 작성할 수 있다
- 물리적으로 가능한 범위(온도, 압력, 진동 등)를 검증하는 테스트를 작성할 수 있다
- 시계열 데이터의 갭(gap)을 탐지하는 로직을 테스트할 수 있다
- 데이터 완전성(completeness) 비율을 계산하고 검증할 수 있다
- ValidationResult 패턴으로 검증 결과를 구조화하는 방법을 이해한다

## 2. 동기부여 (예지보전 관점)

센서 데이터가 아무리 많아도 **유효하지 않은 데이터**가 모델에 입력되면 잘못된 예측이 발생합니다.

실제 공장에서 발생하는 데이터 품질 문제:
- **스키마 변경**: 센서 교체 후 컬럼명이나 단위가 바뀜
- **물리적 불가능 값**: 온도 센서가 -273.15도C 이하 (절대영도 이하)를 보고
- **데이터 갭**: 네트워크 장애로 30분간 데이터 수집 중단
- **시간 역전**: 타임스탬프가 순서대로 정렬되지 않음

이러한 문제를 **데이터 유효성 검증(Data Validation)**으로 사전에 걸러내야 합니다.
검증 로직 자체도 테스트 대상입니다 - 잘못된 검증기는 잘못된 데이터를 통과시킵니다.

## 3. 핵심 개념 설명

### 3.1 ValidationResult 패턴

검증 결과를 구조화하면 후속 처리가 쉬워집니다:

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ValidationResult:
    """검증 결과를 담는 데이터 클래스"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
```

테스트할 때는 결과 객체의 속성을 검증합니다:

```python
def test_유효한_데이터_검증_통과():
    validator = SensorDataValidator()
    result = validator.validate_range([25.0, 26.0], 0.0, 100.0, "temperature")

    assert result.is_valid is True
    assert len(result.errors) == 0
```

### 3.2 스키마 검증 테스트

데이터가 예상된 구조를 가지고 있는지 확인합니다:

```python
def test_스키마_검증_성공():
    validator = SensorDataValidator()
    data = {"timestamp": 1000.0, "temperature": 25.0, "vibration": 0.5}
    expected_columns = {
        "timestamp": float,
        "temperature": float,
        "vibration": float,
    }

    result = validator.validate_schema(data, expected_columns)
    assert result.is_valid is True

def test_스키마_검증_컬럼_누락():
    validator = SensorDataValidator()
    data = {"timestamp": 1000.0}  # temperature, vibration 누락
    expected_columns = {
        "timestamp": float,
        "temperature": float,
        "vibration": float,
    }

    result = validator.validate_schema(data, expected_columns)
    assert result.is_valid is False
    assert "temperature" in result.errors[0]
```

### 3.3 물리적 범위 검증

각 센서 타입에는 물리적으로 가능한 범위가 있습니다:

| 센서 타입 | 최소값 | 최대값 | 단위 |
|-----------|--------|--------|------|
| temperature | -40 | 200 | 도C |
| vibration | 0 | 50 | mm/s |
| pressure | 0 | 1000 | bar |
| current | 0 | 500 | A |
| rpm | 0 | 50000 | RPM |

```python
def test_온도_범위_초과():
    validator = SensorDataValidator()
    # 공장 환경에서 300도는 대부분의 센서 범위를 벗어남
    result = validator.validate_range(
        [25.0, 300.0, 26.0], -40, 200, "temperature"
    )

    assert result.is_valid is False
    assert any("300.0" in e for e in result.errors)
```

### 3.4 시계열 갭 탐지

연속적이어야 하는 시계열 데이터에서 갭을 찾습니다:

```python
from datetime import datetime, timedelta

def test_시계열_갭_탐지():
    validator = SensorDataValidator()
    # 1초 간격으로 수집되어야 하는데, 중간에 10초 갭
    timestamps = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 1),
        datetime(2024, 1, 1, 0, 0, 2),
        # 여기서 10초 갭 발생
        datetime(2024, 1, 1, 0, 0, 12),
        datetime(2024, 1, 1, 0, 0, 13),
    ]

    gaps = validator.detect_gaps(timestamps, max_gap_seconds=5)

    assert len(gaps) == 1
    assert gaps[0]["start"] == timestamps[2]
    assert gaps[0]["end"] == timestamps[3]
```

### 3.5 데이터 완전성 검증

예상 간격 대비 실제 데이터가 얼마나 완전한지 계산합니다:

```python
def test_데이터_완전성_100퍼센트():
    validator = SensorDataValidator()
    # 1초 간격으로 10개 데이터
    timestamps = [
        datetime(2024, 1, 1, 0, 0, i) for i in range(10)
    ]

    completeness = validator.validate_completeness(
        timestamps, expected_interval=1
    )

    assert completeness == pytest.approx(100.0)
```

### 3.6 선언적 검증 개념 (참고)

실무에서는 pandera, Great Expectations 같은 도구로 선언적 검증을 합니다:

```python
# 개념 설명 (실제 사용하지는 않음)
# pandera 스타일의 선언적 스키마
schema = {
    "temperature": {"min": -40, "max": 200, "type": float, "nullable": False},
    "vibration": {"min": 0, "max": 50, "type": float, "nullable": False},
}
```

이 레슨에서는 직접 검증 로직을 구현하여 원리를 이해합니다.

## 4. 실습 가이드

### 단계 1: 소스 코드 분석
`src_data_validator.py`를 열어 다음을 확인하세요:
- `ValidationResult` 데이터클래스의 구조
- `SENSOR_RANGES` 딕셔너리의 물리적 범위 정의
- 각 검증 메서드의 입력/출력 형태

### 단계 2: 테스트 패턴 파악
`test_data_validator.py`에서 다음 패턴을 확인하세요:
- 유효한 데이터 / 유효하지 않은 데이터 / 경계값 테스트
- `ValidationResult` 객체의 속성(is_valid, errors, warnings) 검증

### 단계 3: 테스트 실행
```bash
cd phase7_predictive_maintenance/33_testing_data_validation
pytest test_data_validator.py -v
```

### 단계 4: 연습 문제 풀기
`exercises/exercise_33.py`에서 TODO를 완성하세요.

## 5. 연습 문제

### 연습 1: 다중 센서 스키마 검증
여러 센서의 데이터를 한번에 검증하는 테스트를 작성하세요.
온도, 진동, 압력 센서의 데이터가 모두 올바른 스키마를 가지는지 확인합니다.

### 연습 2: 시계열 갭 탐지 및 완전성 검증
30분 동안 1초 간격으로 수집된 데이터에서 갭을 찾고,
데이터 완전성 비율이 95% 이상인지 검증하는 테스트를 작성하세요.

### 연습 3: 복합 센서 리딩 검증
단일 센서 리딩(timestamp, sensor_type, value 포함)이
모든 규칙을 통과하는지 종합적으로 검증하는 테스트를 작성하세요.

## 6. 퀴즈

### Q1. 물리적 범위 검증이 중요한 이유는?
- A) 코드 가독성을 높이기 위해
- B) 센서 고장이나 통신 오류로 인한 비현실적 값을 걸러내기 위해
- C) 데이터 저장 용량을 줄이기 위해
- D) 실시간 처리 속도를 높이기 위해

**정답: B** - 센서 오류, 통신 장애, 전기적 노이즈 등으로 인해
물리적으로 불가능한 값(음의 압력, 절대영도 이하 온도 등)이 수집될 수 있습니다.

### Q2. ValidationResult에 errors와 warnings를 분리하는 이유는?
- A) 코드가 복잡해 보이게 하기 위해
- B) errors는 처리 불가능한 문제, warnings는 주의가 필요하지만 처리 가능한 문제를 구분하기 위해
- C) errors만 있으면 충분하므로 불필요하다
- D) 테스트를 더 많이 작성하기 위해

**정답: B** - errors는 데이터를 사용할 수 없는 심각한 문제(범위 초과 등),
warnings는 데이터 사용은 가능하지만 주의가 필요한 문제(완전성 90% 등)를 나타냅니다.

### Q3. 시계열 데이터에서 갭 탐지가 필요한 이유는?
- A) 데이터 포맷을 맞추기 위해
- B) 연속성이 보장되지 않으면 시계열 분석(트렌드, FFT 등)의 결과가 왜곡되기 때문
- C) 갭이 있으면 파일 크기가 줄어들기 때문
- D) 데이터베이스 성능을 위해

**정답: B** - 시계열 분석 알고리즘은 데이터가 일정한 간격으로 연속적이라고 가정합니다.
갭이 있으면 트렌드 분석, 주파수 분석 등의 결과가 왜곡됩니다.

## 7. 정리 및 다음 주제 예고

### 이번 레슨 정리
- `ValidationResult` 패턴으로 검증 결과를 구조화하는 방법을 배웠습니다
- 스키마, 물리적 범위, 시계열 갭, 완전성 등 다양한 차원의 데이터 유효성 검증을 테스트했습니다
- 유효/무효/경계값에 대한 체계적인 테스트 전략을 익혔습니다

### 다음 주제: 예측 모델 테스트 (레슨 34)
다음 레슨에서는 예측 모델(Predictive Model)을 테스트합니다.
모델 학습, 예측, 평가, 저장/로딩 등 ML 파이프라인 전체를 테스트하는 방법을 다룹니다.
