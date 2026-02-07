# 25. Snapshot/회귀 테스트

## 학습 목표

이 주제를 마치면 다음을 할 수 있게 된다:
- 스냅샷 테스트의 개념과 사용 시점을 이해한다
- 수동 스냅샷 비교 패턴을 구현할 수 있다
- syrupy 라이브러리의 기본 사용법을 안다
- 스냅샷 업데이트 워크플로우를 이해한다
- 스냅샷 테스트의 주의사항을 파악한다

## 동기부여 (예지보전 관점)

예지보전 시스템에서 스냅샷 테스트가 유용한 이유:

- **센서 리포트 생성 함수**의 출력 형식이 변경되면 즉시 감지해야 한다
- **알림 메시지 포맷**이 예상과 다르면 운영자가 혼란을 겪는다
- **유지보수 스케줄 JSON**의 구조가 달라지면 하류 시스템에 영향을 준다
- "이전과 같은 출력을 생성하는가?"를 자동으로 검증하는 것이 **회귀 테스트**의 핵심이다

## 핵심 개념

### 스냅샷 테스트란?

함수의 출력을 **파일로 저장(스냅샷)**하고, 이후 실행 시 **저장된 결과와 비교**하여
출력이 변경되었는지 확인하는 테스트 방법이다.

```
첫 실행:
  함수 출력 → 스냅샷 파일에 저장 ✓

이후 실행:
  함수 출력 → 스냅샷 파일과 비교
    동일 → PASS ✓
    다름 → FAIL! (의도적 변경인지 확인 필요)

의도적 변경 시:
  pytest --snapshot-update → 스냅샷 파일 갱신
```

### 언제 사용하는가?

```
적합한 경우:
  ✓ 구조화된 출력 (JSON, dict, 리포트)
  ✓ 포맷된 문자열 (로그 메시지, 알림 텍스트)
  ✓ 복잡한 데이터 구조 (중첩 딕셔너리, 리스트)
  ✓ API 응답 형식 검증

부적합한 경우:
  ✗ 시간/날짜 포함 출력 (매번 달라짐)
  ✗ 랜덤 요소 포함 (해시, UUID)
  ✗ 간단한 단일 값 (일반 assert로 충분)
  ✗ 외부 시스템 의존 출력
```

### syrupy 라이브러리

```bash
pip install syrupy
```

```python
# syrupy 사용 예시
def test_sensor_report(snapshot):
    """센서 리포트가 스냅샷과 일치하는지 확인"""
    report = generate_sensor_report(sample_data)
    assert report == snapshot

# 스냅샷 업데이트
# pytest --snapshot-update
```

syrupy는 `__snapshots__/` 디렉토리에 `.ambr` 파일로 스냅샷을 저장한다.

### 수동 스냅샷 패턴

syrupy 없이도 스냅샷 테스트를 구현할 수 있다:

```python
import json
import os

def load_expected_output(filename):
    """expected_outputs/ 디렉토리에서 기대 결과를 로드한다"""
    path = os.path.join(
        os.path.dirname(__file__),
        "expected_outputs",
        filename,
    )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_sensor_report_manual_snapshot():
    """수동 스냅샷 비교"""
    # 실제 출력
    actual = generate_sensor_report(sample_data)
    # 기대 출력 (파일에서 로드)
    expected = load_expected_output("sensor_report.json")
    # 비교
    assert actual == expected
```

### 스냅샷 업데이트 워크플로우

```
1. 코드를 변경한다
2. 테스트를 실행한다 → 스냅샷 불일치로 FAIL
3. 변경이 의도적인지 확인한다
   - 의도적이면: 스냅샷을 업데이트한다
   - 의도적이지 않으면: 코드를 수정한다
4. 업데이트된 스냅샷을 커밋한다
```

### 주의사항

```
1. 스냅샷을 맹목적으로 업데이트하지 말 것!
   → 변경 내용을 반드시 확인하고 의도적인지 판단

2. 비결정적 데이터를 제거할 것
   → 시간, 랜덤값, 프로세스 ID 등은 스냅샷 전에 고정

3. 스냅샷 파일을 코드 리뷰에 포함할 것
   → 스냅샷 변경은 코드 변경의 일부

4. 너무 큰 스냅샷은 피할 것
   → 수천 줄 스냅샷은 유지보수가 어려움
```

## 실습 가이드

### 실습 파일 구조

```
25_snapshot_testing/
├── lesson.md                 # 이 파일
├── src_report_generator.py   # 리포트 생성 함수들
├── test_snapshot_demo.py     # 스냅샷 테스트 데모
├── expected_outputs/         # 기대 출력 파일
│   ├── sensor_report.json
│   ├── alert_summary.txt
│   └── maintenance_schedule.json
└── exercises/
    ├── exercise_25.py        # 연습문제
    └── solution_25.py        # 정답
```

### 실행 방법

```bash
# 수동 스냅샷 테스트 실행
pytest test_snapshot_demo.py -v

# syrupy 설치 시
pip install syrupy
pytest test_snapshot_demo.py -v --snapshot-update  # 첫 실행: 스냅샷 생성
pytest test_snapshot_demo.py -v                     # 이후: 비교
```

## 연습 문제

### 연습 1: 스냅샷 비교 함수
JSON 파일로 기대 결과를 저장하고, 실제 출력과 비교하는 유틸리티 함수를 작성하라.

### 연습 2: 비결정적 데이터 처리
시간 정보가 포함된 출력에서 시간을 제거/고정하고 스냅샷 비교하는 테스트를 작성하라.

### 연습 3: 스냅샷 업데이트
함수 출력이 변경되었을 때 스냅샷을 업데이트하는 워크플로우를 구현하라.

## 퀴즈

### Q1. 스냅샷 테스트와 일반 단위 테스트의 차이점은?
<details>
<summary>정답 보기</summary>

- **단위 테스트**: 개발자가 기대 값을 직접 assert에 작성
  - `assert result == {"status": "normal", "priority": 5}`
- **스냅샷 테스트**: 기대 값을 파일에 저장하고 자동 비교
  - `assert result == snapshot` (또는 파일에서 로드)

스냅샷 테스트는 복잡한 출력의 회귀를 감지하기에 좋지만,
"왜 이 값이어야 하는가"를 표현하지 못한다는 한계가 있다.
</details>

### Q2. 스냅샷을 맹목적으로 업데이트하면 어떤 문제가 있는가?
<details>
<summary>정답 보기</summary>

의도하지 않은 변경(버그)이 스냅샷에 반영되어,
이후 테스트에서 버그가 "정상"으로 통과할 수 있다.

예: 리포트에서 소수점 자릿수가 바뀌었는데 확인 없이 업데이트하면,
정밀도 문제가 있는 코드가 통과하게 된다.
</details>

### Q3. 스냅샷 테스트에서 비결정적 데이터를 처리하는 방법은?
<details>
<summary>정답 보기</summary>

1. **고정**: 시간은 `freezegun`이나 `time-machine`으로 고정
2. **제거**: 비교 전 비결정적 필드를 삭제
3. **마스킹**: 특정 필드를 고정 값으로 대체 (예: UUID → "***")
4. **정규식 매칭**: 패턴으로 비교 (날짜 형식만 확인)

```python
# 예: 비결정적 필드 제거 후 비교
actual = generate_report()
actual.pop("timestamp", None)  # 시간 제거
actual.pop("request_id", None) # ID 제거
assert actual == expected
```
</details>

## 정리 및 다음 주제 예고

### 오늘 배운 핵심
- **스냅샷 테스트**: 출력을 파일로 저장하고 이후 비교
- **회귀 감지**: 출력이 의도치 않게 변경되면 실패
- **수동 패턴**: JSON 파일로 기대 결과 관리
- **syrupy**: pytest 플러그인으로 자동 스냅샷 관리
- **주의**: 맹목적 업데이트 금지, 비결정적 데이터 처리 필수

### 다음 주제: 26. 비동기 코드 테스트
`async`/`await` 기반의 비동기 코드를 테스트하는 방법을 배운다.
센서 데이터의 비동기 수집, 동시 모니터링 등 실시간 시스템의
테스트 패턴을 알아본다.
