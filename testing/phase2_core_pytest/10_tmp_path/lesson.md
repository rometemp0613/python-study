# 10. 임시 파일과 디렉토리 (tmp_path)

## 1. 학습 목표

- `tmp_path` fixture로 테스트용 임시 디렉토리를 사용한다
- `tmp_path_factory`로 세션/모듈 수준의 임시 디렉토리를 생성한다
- 파일 입출력(CSV, JSON) 테스트 패턴을 익힌다
- 테스트 후 자동 정리되는 안전한 파일 테스트를 작성한다

## 2. 동기부여: 예지보전 관점

예지보전 시스템에서는 다양한 파일 입출력이 필요합니다:
- **센서 데이터 CSV 파일**: 대량의 시계열 데이터 읽기/쓰기
- **설정 JSON 파일**: 장비 설정, 임계값 설정
- **로그 파일**: 센서 이벤트 로그 파싱
- **보고서 파일**: 분석 결과 내보내기

실제 파일 시스템에 테스트 파일을 만들면 다른 테스트에 영향을 주거나
정리가 안 될 수 있습니다. `tmp_path`를 사용하면:
- 각 테스트마다 **고유한 임시 디렉토리**가 자동 생성됨
- 테스트 종료 후 (일정 기간 뒤) **자동 정리**됨
- **다른 테스트와 격리**된 환경에서 파일 작업 가능

## 3. 핵심 개념 설명

### 3.1 tmp_path 기본 사용법

`tmp_path`는 pytest가 제공하는 내장 fixture로, `pathlib.Path` 객체를 반환합니다.

```python
def test_create_file(tmp_path):
    """tmp_path는 각 테스트마다 고유한 임시 디렉토리"""
    # 파일 생성
    file = tmp_path / "sensor_data.txt"
    file.write_text("TEMP-001,72.5,normal\n")

    # 파일 읽기
    content = file.read_text()
    assert "TEMP-001" in content
```

### 3.2 tmp_path로 CSV 파일 테스트

```python
import csv

def test_write_csv(tmp_path):
    csv_file = tmp_path / "readings.csv"

    # CSV 쓰기
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sensor_id", "value", "status"])
        writer.writerow(["TEMP-001", "72.5", "normal"])

    # CSV 읽기 및 검증
    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["sensor_id"] == "TEMP-001"
```

### 3.3 tmp_path로 JSON 파일 테스트

```python
import json

def test_json_config(tmp_path):
    config_file = tmp_path / "config.json"

    # JSON 쓰기
    config = {"thresholds": {"temperature": 80, "vibration": 7}}
    config_file.write_text(json.dumps(config, ensure_ascii=False))

    # JSON 읽기 및 검증
    loaded = json.loads(config_file.read_text())
    assert loaded["thresholds"]["temperature"] == 80
```

### 3.4 tmp_path_factory

`tmp_path_factory`는 여러 임시 디렉토리를 만들 수 있고, session 스코프 fixture에서도 사용 가능합니다.

```python
@pytest.fixture(scope="session")
def shared_data_dir(tmp_path_factory):
    """세션 전체에서 공유하는 데이터 디렉토리"""
    return tmp_path_factory.mktemp("shared_data")

def test_with_shared_dir(shared_data_dir):
    file = shared_data_dir / "test.txt"
    file.write_text("shared content")
    assert file.exists()
```

### 3.5 디렉토리 구조 생성

```python
def test_directory_structure(tmp_path):
    """복잡한 디렉토리 구조 생성"""
    # 서브 디렉토리 생성
    data_dir = tmp_path / "data" / "sensors"
    data_dir.mkdir(parents=True)

    # 여러 파일 생성
    for sensor_id in ["TEMP-001", "VIBR-002", "PRESS-003"]:
        file = data_dir / f"{sensor_id}.csv"
        file.write_text(f"timestamp,value\n2024-01-01,25.0\n")

    # 파일 개수 확인
    csv_files = list(data_dir.glob("*.csv"))
    assert len(csv_files) == 3
```

## 4. 실습 가이드

### 실습 1: CSV 읽기/쓰기

```bash
pytest test_file_handler.py -v -k "csv"
```

### 실습 2: JSON 설정 관리

```bash
pytest test_file_handler.py -v -k "json"
```

### 실습 3: 로그 파일 처리

```bash
pytest test_file_handler.py -v -k "log"
```

## 5. 연습 문제

### 연습 1: CSV 센서 데이터 쓰기/읽기
`write_sensor_csv`와 `read_sensor_csv` 함수를 tmp_path를 사용하여 테스트하세요.

### 연습 2: JSON 설정 파일
장비 설정을 JSON 파일로 저장/로드하는 함수를 테스트하세요.

### 연습 3: 센서 로그 파일 파싱
텍스트 로그 파일을 생성하고 파싱하는 테스트를 작성하세요.

## 6. 퀴즈

### Q1. tmp_path의 타입
`tmp_path` fixture가 반환하는 객체의 타입은?

A) `str`
B) `os.path`
C) `pathlib.Path`
D) `tempfile.TemporaryDirectory`

**정답: C** - `tmp_path`는 `pathlib.Path` 객체를 반환합니다.

### Q2. tmp_path vs tmp_path_factory
다음 중 `tmp_path_factory`가 필요한 경우는?

A) 단일 테스트에서 임시 파일이 필요할 때
B) session 스코프의 fixture에서 임시 디렉토리가 필요할 때
C) 임시 파일을 수동으로 삭제해야 할 때
D) 파일 이름을 지정해야 할 때

**정답: B** - `tmp_path`는 function 스코프이므로, session 스코프에서는 `tmp_path_factory`를 사용해야 합니다.

### Q3. tmp_path 격리
각 테스트의 `tmp_path`에 대한 설명으로 맞는 것은?

A) 모든 테스트가 같은 디렉토리를 공유한다
B) 각 테스트마다 고유한 디렉토리가 생성된다
C) 이전 테스트의 파일이 남아있다
D) 수동으로 생성해야 한다

**정답: B** - 각 테스트마다 고유한 임시 디렉토리가 자동 생성되어 완전히 격리됩니다.

## 7. 정리 및 다음 주제 예고

### 이번 단원 정리
- **tmp_path**: 각 테스트마다 고유한 `pathlib.Path` 임시 디렉토리 제공
- **tmp_path_factory**: session/module 스코프에서 임시 디렉토리 생성
- **CSV/JSON 테스트**: tmp_path를 활용한 안전한 파일 읽기/쓰기 테스트
- **자동 정리**: 테스트 종료 후 임시 파일은 자동 관리됨
- **격리**: 각 테스트는 서로 다른 디렉토리를 사용하여 완전히 격리

### 다음 주제: 11. pytest 설정
다음 단원에서는 `pyproject.toml`, `pytest.ini`, `conftest.py`를 통해
pytest를 프로젝트에 맞게 설정하는 방법을 배웁니다.
테스트 경로, 마커 등록, 기본 옵션 등을 구성할 수 있습니다.
