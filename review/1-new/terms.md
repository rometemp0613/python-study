# 새로 배운 용어/개념

## 2026-02-16 (개발 환경 설정)

- **uv**: Python 버전 관리 + 가상환경 + 패키지 설치를 하나로 합친 도구. Rust로 작성, pip보다 10~100배 빠름.
- **가상환경 (venv)**: 프로젝트마다 독립된 패키지 공간을 만드는 것. 프로젝트 간 패키지 충돌 방지.
- **pyproject.toml**: Python 프로젝트의 표준 설정 파일. 프로젝트 이름, Python 버전, 의존성 패키지 등을 기록.
- **uv.lock**: 설치된 패키지의 정확한 버전을 잠금(lock). 다른 PC에서도 동일한 환경 재현 보장.
- **uv sync**: lock 파일 기반으로 환경을 복원하는 명령어. 다른 PC에서 clone 후 이것만 실행하면 됨.
- **uv add**: 패키지 설치 명령어. pyproject.toml과 uv.lock을 자동 업데이트.
- **uv run**: 가상환경 안에서 명령어를 실행. `uv run python main.py` 형태로 사용.
- **ipykernel**: VS Code에서 Jupyter 노트북을 실행할 때 Python 커널을 연결해주는 패키지.
- **WSL2 (Windows Subsystem for Linux)**: Windows 안에서 Linux 환경을 실행하는 기능. Mac과 동일한 개발환경을 만들 수 있음.

## 2026-02-16 (기본 문법 복습)

- **f-string**: `f"온도: {temp}°C"` 형태로 문자열 안에 변수를 넣는 방법. Python 3.6+.
- **enumerate()**: 리스트 순회 시 인덱스와 값을 동시에 반환. `for i, val in enumerate(mylist):`.
- **range(start, stop, step)**: 숫자 범위 생성. stop은 포함하지 않음. 리스트가 아닌 숫자만 받음.
- **기본값 인자 (default argument)**: `def func(a, b=10):` 처럼 함수 인자에 기본값 지정. 반드시 일반 인자 뒤에 와야 함.
- **docstring**: 함수 정의 바로 아래 `"""설명"""` 으로 작성. VS Code 자동완성 팝업에 표시됨.
- **언패킹 (unpacking)**: `lo, hi, avg = analyze(data)` 처럼 여러 반환값을 한 번에 변수에 할당.

## 2026-02-16 (자료구조)

- **슬라이싱 (slicing)**: `data[1:4]`로 리스트 일부를 잘라냄. 끝 인덱스는 미포함. `data[:3]`(앞 3개), `data[-2:]`(뒤 2개).
- **sort() vs sorted()**: `sort()`는 원본을 변경, `sorted()`는 원본 유지하고 새 리스트 반환.
- **튜플 (tuple)**: `(1, 2, 3)` 형태. 리스트와 비슷하지만 변경 불가. 고정 데이터(스펙, 기록)에 사용.
- **dict.get(키, 기본값)**: 딕셔너리에서 키가 없을 때 에러 대신 기본값 반환. `sensor.get("status", "미설정")`.
- **dict.items()**: 딕셔너리의 키+값을 동시에 순회. `for k, v in data.items():`. 키만은 `.keys()`, 값만은 `.values()`.
- **집합 연산**: `a & b`(교집합), `a | b`(합집합), `a - b`(차집합). 알람 분석에서 "연속 알람", "신규 알람" 구할 때 유용.
- **리스트 컴프리헨션**: `[val for val in data if 조건]`. for문을 한 줄로 압축. 대괄호 `[]` 사용.
- **딕셔너리 컴프리헨션**: `{k: v for k, v in data.items() if 조건}`. 중괄호 `{}` + 콜론 `:` 사용.
- **집합 컴프리헨션**: `{val for val in data}`. 중괄호 `{}`만 사용. 콜론 없으면 집합.
- **zip()**: 여러 리스트를 묶어서 동시 순회. `for a, b in zip(list1, list2):`. 딕셔너리 만들기: `dict(zip(keys, values))`.
- **lambda**: 이름 없는 한 줄 함수. `lambda x: x[1]`은 `def f(x): return x[1]`과 같음. `sorted()`의 `key` 인자에 자주 사용.
