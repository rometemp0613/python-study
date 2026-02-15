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
