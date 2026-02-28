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
- **튜플 (tuple)**: `(1, 2, 3)` 형태. 리스트와 비슷하지만 변경 불가. 고정 데이터(스펙, 기록)에 사용.
- **dict.items()**: 딕셔너리의 키+값을 동시에 순회. `for k, v in data.items():`. 키만은 `.keys()`, 값만은 `.values()`.
- **리스트 컴프리헨션**: `[val for val in data if 조건]`. for문을 한 줄로 압축. 대괄호 `[]` 사용.
- **딕셔너리 컴프리헨션**: `{k: v for k, v in data.items() if 조건}`. 중괄호 `{}` + 콜론 `:` 사용.
- **집합 컴프리헨션**: `{val for val in data}`. 중괄호 `{}`만 사용. 콜론 없으면 집합.
- **zip()**: 여러 리스트를 묶어서 동시 순회. `for a, b in zip(list1, list2):`. 딕셔너리 만들기: `dict(zip(keys, values))`.
- **lambda**: 이름 없는 한 줄 함수. `lambda x: x[1]`은 `def f(x): return x[1]`과 같음. `sorted()`의 `key` 인자에 자주 사용.

## 2026-02-17 (객체지향 프로그래밍)

- **class**: 객체의 설계도. `class Motor:` 형태로 정의. 이름은 대문자로 시작 (관례).
- **__init__()**: 생성자. 객체가 만들어질 때 자동 실행되는 메서드. 속성 초기화에 사용.
- **상속 (inheritance)**: `class Motor(Equipment):`처럼 부모 클래스의 속성과 메서드를 물려받는 것.
- **@property**: 메서드를 속성처럼 쓸 수 있게 하는 데코레이터. `m.temp`처럼 읽되 내부에서 로직 실행 가능.
- **@setter**: `@temp.setter`로 값 대입 시 검증 로직 추가. 기존 코드 변경 없이 나중에 검증 추가 가능.
- **캡슐화 (encapsulation)**: 내부 데이터를 보호하고 정해진 방법으로만 접근하게 하는 것.
- **_ (단일 언더스코어)**: `self._temp`처럼 "외부에서 직접 접근하지 마"라는 약속 (강제는 아님).
- **__ (이중 언더스코어, name mangling)**: `self.__temp`는 `_클래스명__temp`로 이름이 변경됨. 상속 시 충돌 방지용.
- **다형성 (polymorphism)**: 같은 이름의 메서드를 호출하는데, 객체에 따라 다르게 동작하는 것.
- **오버라이딩 (overriding)**: 부모 메서드를 자식이 같은 이름으로 재정의하는 것.
- **isinstance()**: `isinstance(obj, Class)`로 객체가 특정 클래스인지 확인. 상속받은 자식도 True.

## 2026-02-28 (예외 처리 & 파일 I/O)

- **try/except**: 예외가 발생할 수 있는 코드를 `try`에 넣고, 발생 시 `except`에서 처리. 구체적 예외부터 위에 배치.
- **else (try문)**: `try` 블록에서 예외가 발생하지 않았을 때만 실행되는 블록. 에러 범위를 좁힐 수 있음.
- **finally**: `try` 블록의 결과와 상관없이 무조건 실행. 파일 닫기, DB 연결 해제 등 리소스 정리에 사용.
- **with문 (컨텍스트 매니저)**: `with open(...) as f:` 형태로 리소스를 자동 정리. 블록 끝나면 `close()` 자동 호출, 예외 발생 시에도 안전.
- **파일 모드 (r/w/a/x)**: `r`=읽기, `w`=쓰기(덮어씀), `a`=추가(이어씀), `x`=배타적 생성(파일 있으면 에러). `w` 모드는 기존 데이터 삭제되므로 주의.
- **csv.writer / csv.reader**: `csv` 모듈로 CSV 파일 읽기/쓰기. `writerow()`로 한 줄씩, `DictReader`로 컬럼명 기반 접근 가능.
- **커스텀 예외**: `class MyError(Exception): pass` 형태로 `Exception`을 상속해서 만드는 사용자 정의 예외. 계층 구조로 분류 가능.
- **raise**: `raise ValueError("메시지")` 형태로 직접 예외를 발생시키는 키워드. 조건 검증 실패 시 사용.
- **Exception 상속**: 커스텀 예외는 반드시 `Exception` (또는 그 하위 클래스)을 상속. `__init__`에서 속성 추가, `super().__init__(메시지)` 호출.
