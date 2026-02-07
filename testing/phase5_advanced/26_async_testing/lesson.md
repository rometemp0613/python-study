# 26. 비동기 코드 테스트

## 학습 목표

이 주제를 마치면 다음을 할 수 있게 된다:
- `async`/`await` 함수를 테스트하는 방법을 이해한다
- `pytest-asyncio`의 사용법을 안다
- `AsyncMock`으로 비동기 의존성을 모킹할 수 있다
- 비동기 픽스처를 작성할 수 있다
- 센서 데이터의 비동기 수집/모니터링을 테스트할 수 있다

## 동기부여 (예지보전 관점)

현대 공장 설비 모니터링 시스템에서 비동기 코드가 필요한 이유:

- **수백 개 센서를 동시에 읽어야** 한다 → `asyncio.gather()`
- **실시간 모니터링**은 지속적으로 데이터를 수집한다 → `async for`
- **외부 API 호출** (클라우드 서비스, 알림 시스템)은 비동기가 효율적이다
- **대량 데이터 처리** 시 I/O 대기 시간을 활용해야 한다

이 모든 비동기 코드를 올바르게 테스트해야 시스템의 신뢰성을 보장할 수 있다.

## 핵심 개념

### 비동기 함수 기초

```python
import asyncio

async def fetch_sensor_data(sensor_id):
    """비동기로 센서 데이터를 가져온다"""
    await asyncio.sleep(0.1)  # 네트워크 지연 시뮬레이션
    return {"sensor_id": sensor_id, "value": 42.0}

# 일반적인 호출
result = asyncio.run(fetch_sensor_data("VIB_001"))
```

### pytest-asyncio 사용법

```bash
pip install pytest-asyncio
```

```python
import pytest

# 방법 1: 데코레이터 사용
@pytest.mark.asyncio
async def test_fetch_sensor_data():
    """비동기 테스트 함수"""
    result = await fetch_sensor_data("VIB_001")
    assert result["sensor_id"] == "VIB_001"

# 방법 2: asyncio_mode = "auto" 설정 시 데코레이터 불필요
# pyproject.toml에서:
# [tool.pytest.ini_options]
# asyncio_mode = "auto"
```

### pytest-asyncio 없이 테스트하기

```python
import asyncio

def test_fetch_sensor_data_without_plugin():
    """asyncio.run()으로 비동기 함수 테스트"""
    result = asyncio.run(fetch_sensor_data("VIB_001"))
    assert result["sensor_id"] == "VIB_001"
```

### AsyncMock

Python 3.8+의 `unittest.mock.AsyncMock`은 비동기 함수를 모킹한다.

```python
from unittest.mock import AsyncMock

# 비동기 함수 모킹
mock_fetch = AsyncMock(return_value={"sensor_id": "VIB_001", "value": 42.0})

# await로 호출 가능
result = await mock_fetch("VIB_001")
assert result["value"] == 42.0

# 호출 확인
mock_fetch.assert_called_once_with("VIB_001")
```

### 비동기 픽스처

```python
import pytest

@pytest.fixture
async def async_sensor_client():
    """비동기 픽스처: 센서 클라이언트 생성/정리"""
    client = AsyncSensorClient()
    await client.connect()
    yield client
    await client.disconnect()

@pytest.mark.asyncio
async def test_with_async_fixture(async_sensor_client):
    """비동기 픽스처를 사용하는 테스트"""
    data = await async_sensor_client.read("VIB_001")
    assert data is not None
```

### 여러 비동기 작업 테스트

```python
@pytest.mark.asyncio
async def test_concurrent_sensor_reads():
    """여러 센서를 동시에 읽기"""
    sensor_ids = ["VIB_001", "TEMP_001", "PRES_001"]

    # asyncio.gather()로 동시 실행
    results = await asyncio.gather(
        *[fetch_sensor_data(sid) for sid in sensor_ids]
    )

    assert len(results) == 3
    assert all(r["sensor_id"] in sensor_ids for r in results)
```

### 타임아웃 테스트

```python
@pytest.mark.asyncio
async def test_sensor_timeout():
    """센서 읽기 타임아웃"""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(
            slow_sensor_read("VIB_001"),
            timeout=0.1,  # 0.1초 제한
        )
```

## 실습 가이드

### 실습 파일 구조

```
26_async_testing/
├── lesson.md               # 이 파일
├── src_async_sensor.py     # 비동기 센서 함수들
├── test_async_demo.py      # 비동기 테스트 데모
└── exercises/
    ├── exercise_26.py       # 연습문제
    └── solution_26.py       # 정답
```

### 실행 방법

```bash
# 기본 실행 (asyncio.run 사용 테스트)
pytest test_async_demo.py -v

# pytest-asyncio 설치 후
pip install pytest-asyncio
pytest test_async_demo.py -v
```

## 연습 문제

### 연습 1: AsyncMock 사용
센서 데이터 API를 AsyncMock으로 모킹하여, `collect_multiple_sensors()`가
올바르게 데이터를 수집하는지 테스트하라.

### 연습 2: 타임아웃 테스트
느린 센서 응답에 대한 타임아웃 처리를 테스트하라.

### 연습 3: 비동기 클래스 테스트
`AsyncSensorCollector` 클래스의 `start()`와 `stop()` 메서드를 테스트하라.

## 퀴즈

### Q1. AsyncMock과 Mock의 차이점은?
<details>
<summary>정답 보기</summary>

- `Mock`: 동기 함수를 모킹. 호출 시 즉시 `return_value` 반환.
- `AsyncMock`: 비동기 함수를 모킹. `await`로 호출해야 하며, 코루틴을 반환.

```python
from unittest.mock import Mock, AsyncMock

# Mock: 동기
sync_mock = Mock(return_value=42)
result = sync_mock()  # 42

# AsyncMock: 비동기
async_mock = AsyncMock(return_value=42)
result = await async_mock()  # 42 (await 필요)
```
</details>

### Q2. pytest-asyncio 없이 비동기 함수를 테스트하는 방법은?
<details>
<summary>정답 보기</summary>

`asyncio.run()`을 사용하여 동기 테스트 함수 안에서 비동기 함수를 실행한다:

```python
import asyncio

def test_async_function():
    result = asyncio.run(my_async_function())
    assert result == expected
```

또는 이벤트 루프를 직접 생성:
```python
def test_async_function():
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(my_async_function())
        assert result == expected
    finally:
        loop.close()
```
</details>

### Q3. 비동기 테스트에서 주의해야 할 점은?
<details>
<summary>정답 보기</summary>

1. **이벤트 루프 관리**: 테스트 간에 이벤트 루프가 공유되지 않도록 주의
2. **타임아웃 설정**: 비동기 작업이 무한 대기하지 않도록 타임아웃 필요
3. **리소스 정리**: `async with`, `yield`로 비동기 리소스를 적절히 정리
4. **동시성 문제**: `asyncio.gather()` 사용 시 에러 전파 처리
5. **모킹 대상**: `AsyncMock`과 `Mock`을 올바르게 구분
</details>

## 정리 및 다음 주제 예고

### 오늘 배운 핵심
- **pytest-asyncio**: `@pytest.mark.asyncio`로 비동기 테스트 작성
- **asyncio.run()**: 플러그인 없이 비동기 테스트하는 대안
- **AsyncMock**: 비동기 함수 모킹 (`await` 가능한 mock)
- **비동기 픽스처**: `async def fixture()` + `yield`
- **동시성 테스트**: `asyncio.gather()`, `asyncio.wait_for()`, 타임아웃

### 다음 주제: Phase 6 - 테스트 전략
Phase 5의 고급 기법을 마무리하고, Phase 6에서는 **TDD(Test-Driven Development)**,
**테스트 설계 원칙**, **Flaky 테스트 다루기**, **테스트 안티패턴** 등
실무에서 중요한 테스트 전략과 모범 사례를 학습한다.
