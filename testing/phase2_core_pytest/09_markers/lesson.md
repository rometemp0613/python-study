# 09. Markers - 테스트 마커

## 1. 학습 목표

- pytest의 내장 마커(skip, skipif, xfail)를 이해하고 사용한다
- 커스텀 마커를 정의하고 테스트를 분류한다
- 마커 표현식(`-m`)으로 테스트를 선택적으로 실행한다
- 클래스/모듈 수준에서 마커를 적용한다
- `pyproject.toml` 또는 `pytest.ini`에 마커를 등록한다

## 2. 동기부여: 예지보전 관점

공장 설비 모니터링 시스템을 개발할 때 테스트를 분류해야 하는 경우가 많습니다:

- **빠른 단위 테스트**: 개별 함수 검증 (밀리초 단위)
- **느린 통합 테스트**: DB 연결, API 호출 포함 (초~분 단위)
- **특정 센서 종류별 테스트**: 온도, 진동, 압력 센서
- **환경 의존 테스트**: 특정 OS나 라이브러리가 필요한 테스트
- **아직 구현 중인 기능**: 예상 실패(xfail)로 표시

마커를 사용하면 **개발 중에는 빠른 테스트만, CI에서는 전체 테스트를**
효율적으로 실행할 수 있습니다.

## 3. 핵심 개념 설명

### 3.1 내장 마커: skip

조건 없이 테스트를 건너뛰려면 `@pytest.mark.skip`을 사용합니다.

```python
@pytest.mark.skip(reason="센서 하드웨어 미연결 상태")
def test_real_sensor_connection():
    """실제 센서 연결이 필요한 테스트"""
    sensor = connect_real_sensor()
    assert sensor.is_connected
```

### 3.2 내장 마커: skipif

조건부로 테스트를 건너뛰려면 `@pytest.mark.skipif`를 사용합니다.

```python
import sys

@pytest.mark.skipif(
    sys.platform != "linux",
    reason="리눅스 환경에서만 실행 가능"
)
def test_linux_specific_feature():
    """리눅스 전용 기능 테스트"""
    pass
```

### 3.3 내장 마커: xfail

아직 수정되지 않은 버그나 미구현 기능을 테스트할 때 `@pytest.mark.xfail`을 사용합니다.

```python
@pytest.mark.xfail(reason="음수 온도 처리 미구현")
def test_negative_temperature():
    """음수 온도 처리 테스트"""
    result = process_temperature(-10)
    assert result == "below_zero"  # 아직 구현 안 됨

@pytest.mark.xfail(strict=True)
def test_strict_xfail():
    """strict=True면 예상대로 실패해야 하고, 성공하면 XPASS로 실패 처리"""
    assert False
```

### 3.4 커스텀 마커 정의

```python
# pytest.ini 또는 pyproject.toml에 등록
# [tool.pytest.ini_options]
# markers = [
#     "slow: 느린 테스트",
#     "integration: 통합 테스트",
#     "sensor: 센서 관련 테스트",
# ]

@pytest.mark.slow
def test_full_data_analysis():
    """전체 데이터 분석 (느린 테스트)"""
    pass

@pytest.mark.integration
def test_database_connection():
    """DB 연결 테스트"""
    pass

@pytest.mark.sensor
def test_temperature_reading():
    """온도 센서 테스트"""
    pass
```

### 3.5 마커 표현식으로 선택 실행

```bash
# slow 마커가 있는 테스트만 실행
pytest -m slow

# slow가 아닌 테스트만 실행
pytest -m "not slow"

# integration과 sensor 마커가 모두 있는 테스트만
pytest -m "integration and sensor"

# integration 또는 sensor 마커가 있는 테스트
pytest -m "integration or sensor"
```

### 3.6 클래스/모듈 수준 마커

```python
# 클래스의 모든 테스트에 마커 적용
@pytest.mark.integration
class TestDatabaseIntegration:
    def test_connect(self):
        pass

    def test_query(self):
        pass

# 모듈의 모든 테스트에 마커 적용
pytestmark = pytest.mark.slow
```

## 4. 실습 가이드

### 실습 1: 마커별 실행

```bash
# 모든 테스트 실행
pytest test_markers_demo.py -v

# slow 테스트만 실행
pytest test_markers_demo.py -v -m slow

# slow 테스트를 제외하고 실행
pytest test_markers_demo.py -v -m "not slow"

# 센서 관련 테스트만 실행
pytest test_markers_demo.py -v -m sensor
```

### 실습 2: 등록된 마커 확인

```bash
pytest --markers
```

### 실습 3: xfail 동작 확인

```bash
pytest test_markers_demo.py -v -k "xfail"
```

## 5. 연습 문제

### 연습 1: skipif 활용
Python 버전에 따라 조건부로 건너뛰는 테스트를 작성하세요.

### 연습 2: 커스텀 마커 분류
설비 종류별(motor, pump, conveyor) 커스텀 마커를 만들고,
각 설비에 맞는 테스트를 작성하세요.

### 연습 3: 마커 조합
여러 마커를 조합하여 테스트를 분류하고, 마커 표현식으로
특정 그룹만 실행해 보세요.

## 6. 퀴즈

### Q1. skip vs skipif
다음 중 맞는 설명은?

A) skip은 항상 건너뛰고, skipif는 조건이 참일 때만 건너뛴다
B) skip은 테스트를 삭제하고, skipif는 비활성화한다
C) 두 마커 모두 테스트 결과에 표시되지 않는다
D) skipif는 런타임에만 평가된다

**정답: A** - skip은 무조건, skipif는 조건부로 테스트를 건너뜁니다.

### Q2. xfail strict 모드
`@pytest.mark.xfail(strict=True)`에서 테스트가 예상과 달리 성공하면?

A) PASSED로 표시된다
B) XPASS로 표시되고 테스트 스위트가 실패한다
C) 무시된다
D) 경고만 표시된다

**정답: B** - strict=True일 때 예상 실패 테스트가 성공하면 XPASS로 표시되고 실패로 간주됩니다.

### Q3. 마커 표현식
`pytest -m "not slow and not integration"`은?

A) slow 또는 integration 마커가 있는 테스트만 실행
B) slow와 integration 마커가 모두 없는 테스트만 실행
C) 마커가 없는 테스트만 실행
D) 모든 테스트를 실행

**정답: B** - not으로 두 마커를 모두 제외한 나머지 테스트를 실행합니다.

## 7. 정리 및 다음 주제 예고

### 이번 단원 정리
- **skip/skipif**: 테스트를 무조건/조건부로 건너뛰기
- **xfail**: 예상 실패를 명시적으로 표시
- **커스텀 마커**: 테스트를 목적별로 분류
- **마커 표현식**: and, or, not으로 선택적 실행
- **클래스/모듈 마커**: 범위 단위로 마커 적용
- **마커 등록**: pyproject.toml에서 마커를 문서화

### 다음 주제: 10. 임시 파일과 디렉토리
다음 단원에서는 `tmp_path`와 `tmp_path_factory`를 사용하여
테스트 중 파일 입출력을 안전하게 처리하는 방법을 배웁니다.
센서 데이터 CSV 파일, 설정 JSON 파일 등을 테스트할 수 있습니다.
