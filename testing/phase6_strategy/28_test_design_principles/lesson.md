# 28. 테스트 설계 원칙

## 학습 목표
- FIRST 원칙 (Fast, Isolated, Repeatable, Self-validating, Timely)을 이해하고 적용할 수 있다
- AAA (Arrange-Act-Assert) / Given-When-Then 패턴을 사용할 수 있다
- 한 테스트에서 하나의 개념만 검증하는 방법을 익힌다
- 구현이 아닌 동작을 테스트하는 방법을 이해한다
- DRY와 가독성 사이의 균형을 잡을 수 있다

## 동기부여: 예지보전 관점

예지보전 시스템의 테스트 코드는 시간이 지남에 따라 수백, 수천 개로 늘어납니다. 테스트 설계가 잘못되면:
- 테스트 실행이 느려져 **피드백 주기가 길어집니다**
- 테스트 간 의존성으로 인해 **원인 파악이 어렵습니다**
- 구현 변경 시 **불필요한 테스트 수정이 필요합니다**
- 테스트 코드를 이해하기 어려워 **유지보수가 힘들어집니다**

좋은 테스트 설계는 예지보전 시스템의 신뢰성을 높이는 핵심입니다.

## 핵심 개념

### 1. FIRST 원칙

#### F - Fast (빠르게)
테스트는 빠르게 실행되어야 합니다. 느린 테스트는 자주 실행하지 않게 됩니다.

```python
# 나쁜 예: 느린 테스트
def test_느린_데이터_처리():
    import time
    time.sleep(2)  # 실제 대기
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    assert scheduler.get_next_maintenance("pump-001") is not None

# 좋은 예: 빠른 테스트
def test_빠른_데이터_처리():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    assert scheduler.get_next_maintenance("pump-001") is not None
```

#### I - Isolated (독립적)
각 테스트는 다른 테스트와 독립적이어야 합니다.

```python
# 나쁜 예: 테스트 간 공유 상태
shared_scheduler = MaintenanceScheduler()

def test_스케줄_추가():
    shared_scheduler.schedule_maintenance("pump-001", "high")
    # 이 테스트가 실패하면 아래 테스트도 영향받음

def test_스케줄_조회():
    # shared_scheduler에 의존 - 위 테스트 결과에 따라 달라짐
    result = shared_scheduler.get_next_maintenance("pump-001")
    assert result is not None

# 좋은 예: 독립적인 테스트
def test_스케줄_추가_독립():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    assert scheduler.get_next_maintenance("pump-001") is not None

def test_스케줄_조회_독립():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("motor-002", "medium")
    result = scheduler.get_next_maintenance("motor-002")
    assert result is not None
```

#### R - Repeatable (반복 가능)
테스트는 어떤 환경에서도 같은 결과를 내야 합니다.

```python
# 나쁜 예: 환경에 따라 결과가 달라짐
def test_오늘_날짜_의존():
    from datetime import date
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    # 실행 날짜에 따라 결과가 달라짐!
    result = scheduler.get_overdue_maintenances()

# 좋은 예: 날짜를 주입하여 반복 가능
def test_날짜_주입():
    from datetime import date
    scheduler = MaintenanceScheduler()
    fixed_date = date(2024, 1, 15)
    scheduler.schedule_maintenance("pump-001", "high", scheduled_date=fixed_date)
    # 항상 같은 결과
```

#### S - Self-validating (자체 검증)
테스트는 성공/실패를 자동으로 판단해야 합니다.

```python
# 나쁜 예: 수동 확인 필요
def test_출력_확인():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    print(scheduler.get_next_maintenance("pump-001"))  # 눈으로 확인?

# 좋은 예: assert로 자동 검증
def test_자동_검증():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    result = scheduler.get_next_maintenance("pump-001")
    assert result is not None
    assert result["equipment_id"] == "pump-001"
```

#### T - Timely (적시에)
테스트는 프로덕션 코드와 함께 (또는 그 전에) 작성해야 합니다.

### 2. AAA 패턴 (Arrange-Act-Assert)

```python
def test_유지보수_스케줄_AAA():
    # Arrange (준비): 테스트에 필요한 객체와 데이터를 준비
    scheduler = MaintenanceScheduler()
    equipment_id = "pump-001"
    priority = "high"

    # Act (실행): 테스트할 동작을 수행
    scheduler.schedule_maintenance(equipment_id, priority)

    # Assert (검증): 결과가 기대와 일치하는지 확인
    result = scheduler.get_next_maintenance(equipment_id)
    assert result is not None
    assert result["priority"] == "high"
```

### 3. Given-When-Then 패턴

BDD(Behavior-Driven Development) 스타일의 테스트 구조:

```python
def test_긴급_유지보수는_일반보다_먼저():
    # Given (주어진 조건): 일반과 긴급 유지보수가 스케줄되어 있을 때
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "low")
    scheduler.schedule_maintenance("pump-002", "critical")

    # When (동작): 다음 유지보수를 조회하면
    # (여러 장비 중 가장 우선순위 높은 것)
    # Then (결과): 긴급 유지보수가 먼저 나와야 한다
    # (get_next_maintenance는 장비별로 조회하므로, 각각 확인)
    result_pump1 = scheduler.get_next_maintenance("pump-001")
    result_pump2 = scheduler.get_next_maintenance("pump-002")
    assert result_pump1 is not None
    assert result_pump2 is not None
```

### 4. 한 테스트에 하나의 개념

```python
# 나쁜 예: 여러 개념을 한 테스트에
def test_스케줄러_모든_기능():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    assert scheduler.get_next_maintenance("pump-001") is not None  # 조회
    mid = scheduler.get_next_maintenance("pump-001")["id"]
    scheduler.cancel_maintenance(mid)                               # 취소
    assert scheduler.get_next_maintenance("pump-001") is None      # 취소 확인

# 좋은 예: 각 개념을 분리
def test_유지보수_스케줄링():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    assert scheduler.get_next_maintenance("pump-001") is not None

def test_유지보수_취소():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    mid = scheduler.get_next_maintenance("pump-001")["id"]
    scheduler.cancel_maintenance(mid)
    assert scheduler.get_next_maintenance("pump-001") is None
```

### 5. 동작 vs 구현 테스트

```python
# 나쁜 예: 구현 세부사항에 의존
def test_내부_리스트_확인():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    # 내부 구현에 의존 - 리팩토링 시 깨짐
    assert len(scheduler._schedules) == 1
    assert scheduler._schedules[0]["equipment_id"] == "pump-001"

# 좋은 예: 공개 인터페이스(동작)를 테스트
def test_공개_인터페이스():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")
    result = scheduler.get_next_maintenance("pump-001")
    assert result is not None
    assert result["equipment_id"] == "pump-001"
```

### 6. DRY vs 가독성

테스트에서는 약간의 중복이 가독성을 위해 허용됩니다.

```python
# 과도한 DRY: 이해하기 어려움
@pytest.fixture
def complex_setup():
    scheduler = MaintenanceScheduler()
    for eid, pri in [("p1", "high"), ("p2", "low"), ("p3", "critical")]:
        scheduler.schedule_maintenance(eid, pri)
    return scheduler

def test_복잡한_설정_사용(complex_setup):
    # complex_setup에 무엇이 있는지 한눈에 알기 어려움
    result = complex_setup.get_next_maintenance("p1")
    assert result is not None

# 적절한 균형: 약간의 중복이 있지만 읽기 쉬움
def test_명확한_설정():
    scheduler = MaintenanceScheduler()
    scheduler.schedule_maintenance("pump-001", "high")

    result = scheduler.get_next_maintenance("pump-001")
    assert result is not None
    assert result["equipment_id"] == "pump-001"
```

## 실습 가이드

### 실습 1: 좋은 설계와 나쁜 설계 비교

`test_good_design.py`와 `test_bad_design.py`를 비교해보세요:

```bash
# 두 파일 모두 통과하지만, 설계 품질이 다릅니다
pytest test_good_design.py -v
pytest test_bad_design.py -v
```

### 실습 2: 나쁜 테스트 리팩토링

`exercises/exercise_28.py`에서 나쁜 테스트를 FIRST 원칙에 맞게 리팩토링하세요.

## 연습 문제

### 연습 1: AAA 패턴 적용
주어진 테스트를 AAA 패턴으로 재구성하세요.

### 연습 2: 테스트 분리
여러 개념이 섞인 테스트를 각각의 독립적인 테스트로 분리하세요.

### 연습 3: 나쁜 테스트 리팩토링 (exercises/exercise_28.py)
안티패턴이 적용된 테스트를 좋은 설계 원칙에 맞게 개선하세요.

## 퀴즈

### Q1. FIRST 원칙에서 "I"가 의미하는 것은?
- A) Integrated (통합적)
- B) Isolated (독립적)
- C) Incremental (점진적)
- D) Interactive (상호작용적)

**정답: B**
Isolated - 각 테스트는 다른 테스트와 독립적이어야 합니다.

### Q2. AAA 패턴의 올바른 순서는?
- A) Assert → Arrange → Act
- B) Act → Assert → Arrange
- C) Arrange → Act → Assert
- D) Arrange → Assert → Act

**정답: C**
Arrange(준비) → Act(실행) → Assert(검증)

### Q3. 다음 중 동작(behavior) 테스트에 해당하는 것은?
- A) `assert len(obj._internal_list) == 3`
- B) `assert obj.get_count() == 3`
- C) `assert obj._cache is not None`
- D) `assert isinstance(obj._data, dict)`

**정답: B**
공개 메서드(get_count)를 통해 동작을 검증하는 것이 올바른 방법입니다.

## 정리 및 다음 주제 예고

### 이번 레슨 정리
- **FIRST 원칙**: Fast, Isolated, Repeatable, Self-validating, Timely
- **AAA 패턴**: Arrange(준비) → Act(실행) → Assert(검증)
- **한 테스트 = 한 개념**: 테스트 실패 시 원인을 명확히 파악
- **동작 테스트**: 내부 구현이 아닌 공개 인터페이스를 테스트
- **DRY vs 가독성**: 테스트에서는 약간의 중복이 가독성을 위해 허용

### 다음 주제: 29. Flaky 테스트 다루기
때때로 통과하고 때때로 실패하는 "불안정한" 테스트의 원인과 해결 방법을 알아봅니다.
