# Python 학습 일지

예지보전(Predictive Maintenance) 특화 Python 학습 기록

---

## 2026-02-16 (Day 1) - 개발 환경 설정

### 오늘 한 것
- uv 설치 (Python 버전 + 가상환경 + 패키지 관리 올인원)
- 프로젝트 초기화 (`uv init`)
- 핵심 패키지 설치: numpy, pandas, matplotlib, seaborn, jupyter, ipykernel
- VS Code 설정 (`.vscode/settings.json`)
- VS Code WSL 연결 + 확장 설치 (Python, Jupyter, Pylance)
- `.gitignore` 업데이트

### 배운 것
- Anaconda 대신 uv를 쓰는 이유 (가볍고, 빠르고, 실무 표준)
- `pyproject.toml`이 프로젝트 설정의 중심
- `uv.lock`으로 Win/Mac 어디서든 동일한 환경 보장
- `uv sync` 한 줄이면 다른 PC에서 환경 복원
- VS Code에서 WSL 연결해야 Linux 환경으로 작업 가능
- WSL과 Windows의 VS Code 확장은 별도 관리됨

### 다음 할 것
- 기본 문법 복습 (변수, 자료형, 조건문, 반복문, 함수)

---

## 2026-02-16 (Day 1) - 기본 문법 복습

### 오늘 한 것
- 변수, 자료형, 형변환 복습
- 조건문 (if/elif/else, 복합 조건)
- 반복문 (for, while, enumerate, range, break)
- 함수 (def, 기본값 인자, 여러 값 반환, docstring)
- 종합 실습: 센서 데이터로 설비 모니터링 리포트 생성
- 연습 문제 3개 풀이

### 배운 것
- 리스트 순회는 `for x in mylist:` (range 아님)
- 인덱스+값은 `enumerate()` 사용
- 리스트 길이는 `len()` (count 아님)
- 내장함수 이름(sum 등)을 변수명으로 쓰면 안 됨
- 기본값 인자는 반드시 뒤에 와야 함

### 다음 할 것
- 자료구조 (리스트, 딕셔너리, 튜플, 집합, 컴프리헨션)

---

## 2026-02-16 (Day 1) - 자료구조

### 오늘 한 것
- 자료구조 4종 비교 학습 (리스트, 튜플, 딕셔너리, 집합)
- 컴프리헨션 3종 (리스트, 딕셔너리, 집합)
- zip(), lambda 학습
- 종합 실습: 설비 알람 분석 시스템
- 연습 문제 3개 풀이

### 배운 것
- 딕셔너리 순회 시 `.items()` 써야 키+값 동시 접근 가능
- `.get(키, 기본값)` 패턴으로 KeyError 방지
- 집합 연산으로 알람 분석 (교집합, 차집합)
- 컴프리헨션의 `[]` vs `{}` 괄호 종류가 결과 타입을 결정
- `lambda x: x[1]`은 이름 없는 한 줄 함수
- `sorted(data.items(), key=lambda x: x[1])`로 값 기준 정렬

### 다음 할 것
- 객체지향 프로그래밍 (클래스, 상속, 캡슐화, 다형성)

---

## 2026-02-17 (Day 2) - 객체지향 프로그래밍

### 오늘 한 것
- OOP 4대 개념 학습 (클래스/객체, 상속, 캡슐화, 다형성)
- 실습: 공장 설비 모니터링 시스템 (Sensor, TempSensor, VibSensor)
- 연습 문제 3개 풀이 (PressureSensor, Equipment, SafePressureSensor)
- 퀴즈 3개 통과

### 배운 것
- `class`로 설계도 만들고, 객체로 찍어내는 구조
- `self`는 파이썬이 자동으로 넣어줌 (호출 시 안 넣음)
- `super().__init__()`으로 부모 생성자 호출 필수
- `@property` + `@setter`로 속성처럼 쓰면서 검증 가능
- `_`는 약속으로 보호, `__`는 name mangling으로 강한 보호
- 다형성: 같은 메서드명으로 호출하면 객체마다 다르게 동작
- `isinstance()`로 객체의 클래스 확인

### 다음 할 것
- 예외 처리 & 파일 I/O (try/except, with문, 파일 읽기/쓰기)

---

## 2026-02-28 (Day 3) - 예외 처리 & 파일 I/O

### 오늘 한 것
- 예외 처리 구문 학습 (try/except/else/finally)
- with문 (컨텍스트 매니저)으로 안전한 파일 처리
- 파일 모드 4종 비교 (r/w/a/x)
- csv 모듈로 센서 데이터 읽기/쓰기
- 커스텀 예외 클래스 작성 (Exception 상속)
- 종합 실습: 센서 로그 파일 파싱 및 이상 데이터 분리

### 배운 것
- `try/except`는 구체적인 예외부터 위에 배치
- `else`는 예외 없을 때만 실행 → 에러 범위를 좁힐 수 있음
- `finally`는 무조건 실행 → 리소스 정리에 사용
- `with`문이 `close()`를 자동 호출 → 리소스 누수 방지
- `"w"` 모드는 기존 파일을 덮어쓰므로 주의, `"a"` 모드로 이어쓰기
- `"x"` 모드는 기존 파일이 있으면 에러 → 실수 방지
- `csv.DictReader`가 컬럼명으로 접근 가능해서 가독성 좋음
- `newline=""`은 Windows에서 CSV 빈 줄 방지용
- 커스텀 예외는 `Exception` 상속 후 `__init__`에서 속성 추가
- `raise`로 직접 예외를 발생시킴

### 다음 할 것
- NumPy 기초 (ndarray, 인덱싱, 브로드캐스팅, 벡터 연산)

---

