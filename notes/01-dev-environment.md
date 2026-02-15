# 01. 개발 환경 설정

> 날짜: 2026-02-16
> 목표: Windows/Mac 공용 Python 개발환경 구축

---

## 왜 이 구성인가?

현업에서는 "내 PC에선 되는데 서버에선 안 돼요"가 가장 흔한 문제.
처음부터 **가상환경 + 패키지 버전 잠금**을 습관 들이면 이런 일을 방지할 수 있다.

### 도구 선택 근거

| 도구 | 역할 | 선택 이유 |
|------|------|-----------|
| **WSL2** (Windows) | Linux 환경 | Mac의 터미널과 동일한 환경 제공 |
| **uv** | Python 버전 + 가상환경 + 패키지 관리 | pyenv+venv+pip을 하나로 대체, 10~100배 빠름 |
| **VS Code** | 에디터 | Python/Jupyter 통합 지원, Win/Mac 동일 |
| **pyproject.toml** | 프로젝트 설정 | Python 표준 프로젝트 설정 파일 |

### Anaconda vs uv

| | Anaconda | uv |
|---|---|---|
| 장점 | 한 번에 다 설치 | 가볍고, 빠르고, 실무 표준 |
| 단점 | 무겁고(3GB+), 충돌 잦음 | 직접 설치 필요 |
| 현업 사용 | 레거시/데이터 분석팀 일부 | 2025~2026 신규 프로젝트 대세 |

---

## 세팅 순서 (처음부터 따라하기)

### 1. uv 설치

```bash
# Linux(WSL2) / Mac 공통
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 터미널을 새로 열거나:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

확인:
```bash
uv --version
# uv 0.10.2
```

### 2. 프로젝트 초기화

```bash
cd python-study
uv init --no-readme
```

생성되는 파일들:
- `pyproject.toml` — 프로젝트 설정 (이름, Python 버전, 의존성)
- `.python-version` — 사용할 Python 버전
- `main.py` — 샘플 파일 (삭제해도 됨)

### 3. 패키지 설치

```bash
uv add numpy pandas matplotlib seaborn jupyter ipykernel
```

이 명령어가 하는 일:
1. `.venv/` 가상환경 자동 생성
2. 패키지 설치
3. `pyproject.toml`에 의존성 기록
4. `uv.lock`에 정확한 버전 잠금

### 4. VS Code 설정

`.vscode/settings.json` 생성:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "jupyter.notebookFileRoot": "${workspaceFolder}",
    "[python]": {
        "editor.formatOnSave": true
    }
}
```

VS Code 필수 확장:
- **Python** (Microsoft)
- **Jupyter** (Microsoft)
- **Pylance** (Microsoft)

### 5. .gitignore 설정

```gitignore
__pycache__/
*.pyc
.pytest_cache/

# Virtual environment
.venv/

# Jupyter
.ipynb_checkpoints/
```

### 6. 다른 PC에서 환경 복원 (Mac 등)

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 저장소 클론 후
git clone <저장소 주소>
cd python-study

# 이 한 줄이면 동일한 환경 복원
uv sync
```

`uv.lock` 파일이 정확한 버전을 기록하고 있어서 어디서든 동일한 환경이 보장된다.

---

## 자주 쓰는 uv 명령어

| 명령어 | 용도 | 예시 |
|--------|------|------|
| `uv add 패키지` | 패키지 설치 | `uv add scikit-learn` |
| `uv remove 패키지` | 패키지 제거 | `uv remove seaborn` |
| `uv run python 파일.py` | 스크립트 실행 | `uv run python main.py` |
| `uv run jupyter notebook` | Jupyter 실행 | 브라우저에서 노트북 열기 |
| `uv sync` | 환경 복원 | 다른 PC에서 clone 후 |
| `uv lock` | lock 파일 갱신 | pyproject.toml 수동 수정 후 |
| `uv python list` | 설치 가능한 Python 버전 확인 | |
| `uv python install 3.11` | 다른 Python 버전 설치 | |

---

## 설치된 핵심 패키지

| 패키지 | 버전 | 용도 |
|--------|------|------|
| numpy | 2.4.2 | 수치 계산, 배열 연산 |
| pandas | 3.0.0 | 데이터프레임, 테이블 데이터 처리 |
| matplotlib | 3.10.8 | 그래프, 차트 시각화 |
| seaborn | 0.13.2 | 통계 시각화 (matplotlib 기반) |
| jupyter | 1.1.1 | 대화형 노트북 환경 |
| ipykernel | 7.2.0 | VS Code Jupyter 커널 연결 |

---

## 프로젝트 구조

```
python-study/
├── .python-version      ← Python 3.12 (uv가 관리)
├── .venv/               ← 가상환경 (git 제외)
├── .vscode/
│   └── settings.json    ← VS Code 자동 설정
├── .gitignore
├── pyproject.toml       ← 프로젝트 설정 + 의존성
├── uv.lock              ← 패키지 버전 잠금
├── CLAUDE.md
├── README.md            ← 진도 체크리스트
├── notes/               ← 학습 노트
├── logs/                ← 학습 일지
└── review/              ← 복습 카드
    ├── 1-new/
    ├── 2-practicing/
    └── 3-mastered/
```
