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

