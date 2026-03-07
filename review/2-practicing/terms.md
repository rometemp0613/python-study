# 복습 중인 용어/개념

## 2026-03-07 복습 퀴즈 통과 (1-new → 2-practicing)

- **enumerate()**: 리스트 순회 시 인덱스와 값을 동시에 반환. `for i, val in enumerate(mylist):`.
- **기본값 인자 (default argument)**: `def func(a, b=10):` 처럼 함수 인자에 기본값 지정. 호출 시 생략하면 기본값 사용.
- **zip()**: 여러 리스트를 묶어서 동시 순회. `dict(zip(keys, values))`로 딕셔너리 생성 가능.
- **@property**: 메서드를 속성처럼 괄호 없이 호출. `m.temp`처럼 읽되 내부에서 로직 실행 가능.
- **finally**: `try` 블록의 결과와 상관없이 무조건 실행. 리소스 정리에 사용.
- **f-string**: `f"온도: {temp}°C"` 형태. `$`가 아니라 `{}`만 쓴다 (JavaScript와 다름!).
