# 06. 출력 캡처

## 1. 학습 목표

- `capsys` fixture로 stdout/stderr 출력을 캡처하고 테스트할 수 있다
- `capfd` fixture의 역할과 `capsys`와의 차이를 이해한다
- `caplog` fixture로 logging 모듈의 로그를 캡처하고 검증할 수 있다
- 로그 레벨 설정과 함께 `caplog`를 활용할 수 있다
- print와 logging의 차이, 테스트에서의 각각의 처리 방법을 안다

## 2. 동기부여 (예지보전 관점)

예지보전 시스템은 실시간으로 많은 로그를 생성합니다:
- **데이터 처리 로그**: "센서 TEMP-001에서 5개 읽기 완료"
- **경고 로그**: "WARNING: 온도 80도 초과 감지"
- **에러 로그**: "ERROR: 센서 VIB-003 통신 실패"
- **디버그 로그**: "DEBUG: 이상치 감지 알고리즘 시작"

이러한 로그가 올바르게 출력되는지 테스트하는 것은 매우 중요합니다.
잘못된 로그 레벨이나 누락된 로그는 장애 대응을 어렵게 만듭니다.

## 3. 핵심 개념 설명

### 3.1 capsys - stdout/stderr 캡처

`capsys`는 pytest의 내장 fixture로, print()와 sys.stderr.write()의
출력을 캡처합니다.

```python
def process_data(data):
    """데이터를 처리하고 결과를 출력한다."""
    print(f"데이터 처리 시작: {len(data)}건")
    result = [d * 2 for d in data]
    print(f"데이터 처리 완료: {len(result)}건")
    return result

def test_데이터_처리_출력(capsys):
    """처리 과정의 출력을 확인한다"""
    process_data([1, 2, 3])

    # 캡처된 출력 확인
    captured = capsys.readouterr()

    assert "처리 시작" in captured.out
    assert "3건" in captured.out
    assert "처리 완료" in captured.out
    assert captured.err == ""  # stderr에는 출력 없음
```

### 3.2 capsys vs capfd

| fixture | 캡처 대상 | 사용 상황 |
|---------|----------|-----------|
| `capsys` | sys.stdout, sys.stderr | Python의 print() 등 |
| `capfd` | 파일 디스크립터 1, 2 | 서브프로세스, C 확장 등 |

대부분의 경우 `capsys`로 충분합니다.

### 3.3 caplog - 로그 캡처

```python
import logging

logger = logging.getLogger(__name__)

def monitor_temperature(sensor_id, temp):
    """온도를 모니터링하고 로그를 기록한다."""
    if temp >= 90:
        logger.error(f"[{sensor_id}] 위험 온도: {temp}도")
    elif temp >= 70:
        logger.warning(f"[{sensor_id}] 주의 온도: {temp}도")
    else:
        logger.info(f"[{sensor_id}] 정상 온도: {temp}도")

def test_온도_모니터링_로그(caplog):
    """로그 메시지를 검증한다"""
    with caplog.at_level(logging.INFO):
        monitor_temperature("TEMP-001", 85)

    # 로그 레코드 확인
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert "TEMP-001" in caplog.records[0].message
    assert "85" in caplog.records[0].message

    # 텍스트로 확인
    assert "주의 온도" in caplog.text
```

### 3.4 caplog의 주요 속성

```python
# caplog.records - LogRecord 객체 리스트
for record in caplog.records:
    record.levelname   # "INFO", "WARNING", "ERROR" 등
    record.message     # 로그 메시지
    record.levelno     # 로그 레벨 번호 (10=DEBUG, 20=INFO, ...)
    record.name        # 로거 이름

# caplog.text - 전체 로그 텍스트 (형식화된 문자열)
assert "경고" in caplog.text

# caplog.messages - 메시지만 추출한 리스트
assert "온도 초과" in caplog.messages[0]

# caplog.record_tuples - (logger_name, level, message) 튜플 리스트
assert ("sensor_module", logging.WARNING, "온도 초과") in caplog.record_tuples
```

### 3.5 로그 레벨 설정

```python
def test_디버그_로그(caplog):
    """DEBUG 레벨 로그도 캡처한다"""
    # DEBUG 레벨까지 캡처하도록 설정
    with caplog.at_level(logging.DEBUG):
        some_function()

    # 또는 특정 로거에 대해 설정
    with caplog.at_level(logging.DEBUG, logger="my_module"):
        some_function()
```

### 3.6 여러 번 캡처하기

```python
def test_여러_단계_출력(capsys):
    """여러 단계의 출력을 순차적으로 확인한다"""
    print("1단계 시작")
    captured = capsys.readouterr()
    assert "1단계" in captured.out

    print("2단계 시작")
    captured = capsys.readouterr()
    assert "2단계" in captured.out
    assert "1단계" not in captured.out  # 이전 출력은 이미 소비됨
```

## 4. 실습 가이드

### 실습 1: capsys 사용

```bash
pytest test_data_logger.py -v -k "stdout"
```

### 실습 2: caplog 사용

```bash
pytest test_data_logger.py -v -k "log"
```

### 실습 3: 로그 레벨별 테스트

```bash
pytest test_data_logger.py -v -k "level"
```

## 5. 연습 문제

### 연습 1: 보고서 출력 테스트
`exercises/exercise_06.py`에서 보고서 출력 함수의 stdout 출력을 테스트하세요.

### 연습 2: 로그 레벨 테스트
다양한 상황에서 적절한 로그 레벨이 사용되는지 테스트하세요.

### 연습 3: stderr 출력 테스트
에러 상황에서 stderr로 출력되는 내용을 테스트하세요.

## 6. 퀴즈

### Q1. capsys
`capsys.readouterr()`의 반환값은?
- A) stdout 문자열만
- B) stderr 문자열만
- C) (out, err) 네임드튜플
- D) 로그 레코드 리스트

**정답: C)** `readouterr()`는 `.out`과 `.err` 속성을 가진
네임드튜플을 반환합니다.

### Q2. caplog
`caplog.records[0].levelname`의 값이 될 수 있는 것은?
- A) `"print"`
- B) `"WARNING"`
- C) `20`
- D) `True`

**정답: B)** `levelname`은 문자열로, "DEBUG", "INFO", "WARNING",
"ERROR", "CRITICAL" 등이 됩니다. 숫자는 `levelno`입니다.

### Q3. capsys vs caplog
print()로 출력한 내용을 테스트하려면 어떤 fixture를 사용하나요?
- A) caplog
- B) capsys
- C) capfd
- D) tmp_path

**정답: B)** `capsys`는 stdout/stderr를 캡처하므로 print() 출력을
테스트할 때 사용합니다. `caplog`는 logging 모듈 전용입니다.

## 7. 정리 및 다음 주제 예고

### 이번 강의 핵심 정리
- `capsys`: stdout/stderr 캡처 → `readouterr()`로 확인
- `capfd`: 파일 디스크립터 수준 캡처 (서브프로세스 등)
- `caplog`: logging 모듈 로그 캡처 → records, text, messages로 확인
- `caplog.at_level()`로 캡처할 로그 레벨 설정
- print는 capsys, logging은 caplog으로 각각 테스트

### 다음 주제 예고
Phase 1 완료! 다음은 **Phase 2: pytest 핵심 기능**으로 넘어갑니다.
**07. Fixtures 심화** - pytest fixture의 고급 기능(scope, autouse,
yield fixture, fixture 팩토리 등)을 배웁니다.
