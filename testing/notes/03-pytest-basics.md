# 03. pytest 기본기

## 왜 pytest?

unittest 대비 장점:
- 클래스 상속 불필요 (함수만으로 OK)
- `assert` 하나로 모든 비교 처리 (assertEqual, assertTrue 등 20개+ 불필요)
- 실패 시 자동으로 상세한 차이점 표시
- fixture로 더 유연한 셋업/정리

---

## 테스트 발견 규칙 (Test Discovery)

pytest가 자동으로 테스트를 찾는 3가지 규칙:

```
1. 파일명:  test_*.py  또는  *_test.py
2. 함수명:  test_ 로 시작
3. 클래스:  Test 로 시작 (대문자 T, __init__ 없어야 함)
```

---

## assert 매직

```python
assert result == "정상"           # 동등 비교
assert temperature < 100          # 크기 비교
assert "Motor" in equipment_list  # 포함 여부
assert sensor is not None         # None 확인
assert len(readings) == 10        # 길이
assert is_running                 # 불리언
```

실패 시 pytest가 자동으로 상세 비교를 보여줌:
```
>       assert check_alarm(85) == "정상"
E       AssertionError: assert '경고' == '정상'
```

---

## pytest.approx() — 부동소수점 비교

```python
# 기본 사용 (기본 허용오차 1e-6)
assert 0.1 + 0.2 == pytest.approx(0.3)

# 절대 오차 지정
assert calc_rms(data) == pytest.approx(4.527, abs=0.01)

# 상대 오차 지정 (1%)
assert calc_rms(data) == pytest.approx(4.527, rel=0.01)

# 리스트도 지원
assert result == pytest.approx([2.0, 3.0, 4.0])
```

**주의**: 딕셔너리 리스트에는 `pytest.approx()` 안 맞음 → 그냥 `==` 사용

---

## pytest.raises() — 예외 검증

```python
# 기본
with pytest.raises(ZeroDivisionError):
    divide(10, 0)

# 메시지까지 검증 (match)
with pytest.raises(ValueError, match="최소 2개"):
    detect_anomaly([25.0])
```

**주의**: `with` 블록 안에서 `assert` 불필요. 함수 호출만 하면 됨.

---

## @pytest.mark.parametrize — 여러 입력값

```python
@pytest.mark.parametrize("celsius, fahrenheit", [
    (0, 32.0),        # 케이스 1
    (100, 212.0),     # 케이스 2
    (-40, -40.0),     # 케이스 3
])
def test_변환(celsius, fahrenheit):
    assert celsius_to_fahrenheit(celsius) == pytest.approx(fahrenheit)
```

리스트에 데이터를 넣고, 함수에서는 **한 번만 assert**. 한 줄 추가 = 테스트 케이스 추가!

---

## 주요 CLI 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `-v` | 상세 출력 | `pytest -v` |
| `-x` | 첫 실패에서 멈춤 | `pytest -x` |
| `-s` | print() 출력 보기 | `pytest -s` |
| `-k` | 이름 패턴 필터 | `pytest -k "alarm and not warning"` |
| `--lf` | 마지막 실패만 재실행 | `pytest --lf` |
| `--ff` | 실패한 것 먼저 실행 | `pytest --ff` |
| 특정 파일 | 파일 지정 | `pytest test_sensor.py` |
| 특정 함수 | `::` 구분 | `pytest test_sensor.py::test_read_temperature` |

조합 가능: `pytest -v -x -s test_sensor.py -k "alarm"`

---

## 주의사항 & 흔한 실수

1. **pytest.skip()을 안 지움**: TODO 템플릿에서 assert 작성 후 skip() 남겨두면 테스트가 실행 안 됨
2. **pytest.approx()를 딕셔너리에 사용**: 숫자/리스트 전용. 딕셔너리는 `==`로 비교
3. **pytest.raises() 안에서 assert 사용**: 불필요. 함수 호출만 하면 됨
4. **parametrize 리스트 비우기**: 데이터를 리스트에 넣어야 parametrize가 동작함
