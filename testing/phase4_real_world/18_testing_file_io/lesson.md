# 18. 파일 I/O와 데이터 파이프라인 테스트

## 학습 목표

이 레슨을 마치면 다음을 할 수 있습니다:

1. `tmp_path` 픽스처를 활용하여 파일 I/O 코드를 안전하게 테스트
2. CSV, JSON 파일 읽기/쓰기 함수에 대한 테스트 작성
3. ETL(Extract-Transform-Load) 파이프라인의 엔드-투-엔드 테스트 구성
4. 테스트 데이터 생성 및 관리 전략 수립

## 동기부여: 예지보전 관점

예지보전 시스템에서 데이터 파이프라인은 가장 중요한 인프라입니다:

1. **센서 CSV 수집**: 수천 개 센서에서 매초 생성되는 CSV 파일
2. **데이터 검증**: 스키마 위반, 범위 초과 값 감지
3. **변환 및 정제**: 결측값 처리, 단위 변환, 시간대 보정
4. **저장**: 처리된 데이터를 분석용 형식으로 저장

**파이프라인 오류의 실제 결과:**
- 잘못된 CSV 파싱으로 센서 ID가 뒤바뀜 -> 엉뚱한 장비에 알림 발생
- 인코딩 오류로 한글 장비명 깨짐 -> 현장 대응 지연
- 변환 단계에서 타임스탬프 누락 -> 시계열 분석 불가

## 핵심 개념 설명

### 1. tmp_path 픽스처 기본 사용법

```python
import pytest
import csv
import json


def test_write_and_read_csv(tmp_path):
    """tmp_path로 임시 CSV 파일 생성 및 읽기 테스트"""
    # tmp_path는 pathlib.Path 객체 - 테스트 후 자동 정리
    csv_file = tmp_path / "sensor_data.csv"

    # 테스트 데이터 쓰기
    csv_file.write_text(
        "timestamp,sensor_id,temperature\n"
        "2024-01-01 00:00:00,S001,25.0\n"
        "2024-01-01 01:00:00,S001,26.1\n"
    )

    # 파일이 존재하는지 확인
    assert csv_file.exists()

    # 내용 읽기 및 검증
    content = csv_file.read_text()
    assert "S001" in content
    assert "25.0" in content


def test_create_directory_structure(tmp_path):
    """테스트용 디렉토리 구조 생성"""
    # 중첩 디렉토리 생성
    data_dir = tmp_path / "raw" / "sensors"
    data_dir.mkdir(parents=True)

    # 여러 파일 생성
    for i in range(3):
        file_path = data_dir / f"sensor_{i:03d}.csv"
        file_path.write_text(f"timestamp,value\n2024-01-01,{25.0 + i}\n")

    # 파일 개수 확인
    csv_files = list(data_dir.glob("*.csv"))
    assert len(csv_files) == 3
```

### 2. CSV 파일 테스트

```python
def test_read_sensor_csv(tmp_path):
    """센서 CSV 파일 읽기 테스트"""
    csv_content = (
        "timestamp,sensor_id,temperature,vibration\n"
        "2024-01-01 00:00:00,S001,25.0,0.5\n"
        "2024-01-01 01:00:00,S001,26.1,0.6\n"
        "2024-01-01 02:00:00,S002,27.3,0.7\n"
    )
    csv_file = tmp_path / "test_sensor.csv"
    csv_file.write_text(csv_content)

    result = read_sensor_csv(str(csv_file))

    assert len(result) == 3
    assert "temperature" in result.columns
    assert result["sensor_id"].iloc[0] == "S001"
```

### 3. 데이터 검증 테스트

```python
def test_validate_data_valid():
    """유효한 데이터 검증"""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
        "sensor_id": ["S001", "S001", "S001"],
        "temperature": [25.0, 26.0, 27.0],
        "vibration": [0.5, 0.6, 0.7],
    })
    is_valid, errors = validate_data(df)
    assert is_valid
    assert len(errors) == 0


def test_validate_data_missing_column():
    """필수 열 누락 감지"""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
        "temperature": [25.0, 26.0, 27.0],
    })
    is_valid, errors = validate_data(df)
    assert not is_valid
    assert any("sensor_id" in err for err in errors)
```

### 4. 전체 ETL 파이프라인 테스트

```python
def test_full_pipeline(tmp_path):
    """ETL 파이프라인 엔드-투-엔드 테스트"""
    # 1. 입력 파일 준비
    input_file = tmp_path / "raw_data.csv"
    input_file.write_text(
        "timestamp,sensor_id,temperature,vibration\n"
        "2024-01-01 00:00:00,S001,25.0,0.5\n"
        "2024-01-01 01:00:00,S001,,0.6\n"  # 결측값
        "2024-01-01 02:00:00,S001,27.0,0.7\n"
    )

    # 2. 파이프라인 실행
    output_file = tmp_path / "processed_data.csv"
    result = run_pipeline(str(input_file), str(output_file))

    # 3. 결과 검증
    assert result["success"] is True
    assert output_file.exists()

    # 출력 파일 내용 검증
    output_df = pd.read_csv(str(output_file))
    assert output_df["temperature"].isna().sum() == 0  # 결측값 처리 완료
```

### 5. 테스트 데이터 관리 전략

```python
@pytest.fixture
def sample_csv_content():
    """재사용 가능한 테스트 CSV 내용"""
    return (
        "timestamp,sensor_id,temperature,vibration\n"
        "2024-01-01 00:00:00,S001,25.0,0.5\n"
        "2024-01-01 01:00:00,S001,26.1,0.6\n"
        "2024-01-01 02:00:00,S002,27.3,0.7\n"
    )


@pytest.fixture
def sample_csv_file(tmp_path, sample_csv_content):
    """테스트용 CSV 파일 생성 픽스처"""
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(sample_csv_content)
    return csv_file
```

## 실습 가이드

1. `src_data_pipeline.py`의 ETL 함수들을 살펴보세요
2. `test_data_pipeline.py`를 실행하여 모든 테스트가 통과하는지 확인하세요:
   ```bash
   pytest -v test_data_pipeline.py
   ```
3. 연습 문제에서 파이프라인 테스트를 직접 작성해보세요

## 연습 문제

### 연습 1: 손상된 CSV 파일 처리 테스트
잘못된 형식의 CSV 파일(빈 파일, 헤더만 있는 파일, 구분자가 다른 파일)을
`read_sensor_csv`가 올바르게 처리하는지 테스트하세요.

### 연습 2: 대용량 데이터 파이프라인 테스트
1000행의 테스트 데이터를 생성하고, 파이프라인이 올바르게
처리하는지 검증하는 테스트를 작성하세요.

### 연습 3: 에러 복구 테스트
입력 파일이 없을 때, 출력 경로가 잘못됐을 때 등
파이프라인의 에러 처리를 테스트하세요.

## 퀴즈

### Q1. `tmp_path`와 `tmpdir`의 차이점은?

**A)** `tmp_path`는 `pathlib.Path` 객체를 반환하고, `tmpdir`은 `py.path.local` 객체를
반환합니다. `tmp_path`가 더 현대적이고 Python 표준 라이브러리와 호환되므로 권장됩니다.
`tmpdir`은 레거시 호환을 위해 유지되고 있습니다.

### Q2. 테스트에서 실제 파일 시스템 대신 tmp_path를 사용하는 이유는?

**A)** 1) 테스트 격리: 각 테스트마다 독립적인 임시 디렉토리 제공
2) 자동 정리: 테스트 후 임시 파일 자동 삭제
3) 병렬 실행: 여러 테스트가 동시에 실행되어도 파일 충돌 없음
4) 크로스 플랫폼: OS별 임시 디렉토리 경로 차이를 자동 처리

### Q3. ETL 파이프라인 테스트에서 각 단계를 개별적으로 테스트해야 하는 이유는?

**A)** 1) 실패 지점 정확한 특정: E2E 테스트만으로는 어느 단계에서 실패했는지 알기 어려움
2) 엣지 케이스 집중 테스트: 각 단계의 특수한 입력 조합을 테스트 가능
3) 빠른 피드백: 단위 테스트는 빠르게 실행되므로 개발 속도 향상
4) 유지보수 용이: 한 단계 변경 시 해당 단계의 테스트만 수정하면 됨

## 정리 및 다음 주제 예고

이번 레슨에서 배운 내용:
- `tmp_path`를 활용한 안전한 파일 I/O 테스트
- CSV/JSON 파일 읽기/쓰기 테스트 패턴
- ETL 파이프라인의 단계별 및 E2E 테스트
- 테스트 데이터 생성 및 관리 전략

**다음 레슨 (19. 외부 API 상호작용 테스트)** 에서는:
- `unittest.mock`으로 HTTP 호출 모킹
- 재시도 로직 테스트
- 타임아웃 테스트
- API 에러 응답 처리 테스트
