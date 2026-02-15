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
