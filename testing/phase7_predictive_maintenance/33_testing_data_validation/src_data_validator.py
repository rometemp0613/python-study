"""
센서 데이터 유효성 검증 모듈

공장 설비 센서에서 수집된 데이터의 유효성을 검증합니다.
스키마 검증, 물리적 범위 검증, 시계열 갭 탐지, 완전성 검사를 제공합니다.

외부 라이브러리 없이 Python 표준 라이브러리만 사용합니다.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class ValidationResult:
    """
    검증 결과를 담는 데이터 클래스

    Attributes:
        is_valid: 검증 통과 여부
        errors: 심각한 문제 목록 (데이터 사용 불가)
        warnings: 주의 필요한 문제 목록 (데이터 사용 가능하지만 주의)
    """
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# 센서 타입별 물리적 범위 정의
# 각 센서가 측정할 수 있는 물리적 한계값
SENSOR_RANGES: Dict[str, Dict[str, float]] = {
    "temperature": {
        "min": -40.0,     # 산업용 센서 최소 측정 범위 (도C)
        "max": 200.0,     # 산업용 센서 최대 측정 범위 (도C)
        "unit": "°C",
    },
    "vibration": {
        "min": 0.0,       # 진동 속도 최소 (mm/s)
        "max": 50.0,      # 진동 속도 최대 (mm/s)
        "unit": "mm/s",
    },
    "pressure": {
        "min": 0.0,       # 압력 최소 (bar)
        "max": 1000.0,    # 압력 최대 (bar)
        "unit": "bar",
    },
    "current": {
        "min": 0.0,       # 전류 최소 (A)
        "max": 500.0,     # 전류 최대 (A)
        "unit": "A",
    },
    "rpm": {
        "min": 0.0,       # 회전수 최소
        "max": 50000.0,   # 회전수 최대
        "unit": "RPM",
    },
}


class SensorDataValidator:
    """
    센서 데이터 유효성 검증기

    데이터 품질을 보장하기 위한 다양한 검증 기능을 제공합니다.
    """

    def validate_schema(
        self,
        data: Dict[str, Any],
        expected_columns: Dict[str, type],
    ) -> ValidationResult:
        """
        데이터의 스키마(컬럼 존재 여부 및 타입)를 검증합니다.

        Args:
            data: 검증할 데이터 딕셔너리
            expected_columns: 예상 컬럼명과 타입 딕셔너리
                예: {"timestamp": float, "temperature": float}

        Returns:
            ValidationResult: 검증 결과
        """
        result = ValidationResult()

        # 필수 컬럼 존재 여부 확인
        for col_name, col_type in expected_columns.items():
            if col_name not in data:
                result.is_valid = False
                result.errors.append(
                    f"필수 컬럼 '{col_name}'이(가) 누락되었습니다"
                )
            elif not isinstance(data[col_name], col_type):
                # int는 float의 서브타입으로 취급
                if col_type == float and isinstance(data[col_name], int):
                    result.warnings.append(
                        f"컬럼 '{col_name}'의 타입이 int입니다 "
                        f"(float 기대, 자동 변환 가능)"
                    )
                else:
                    result.is_valid = False
                    result.errors.append(
                        f"컬럼 '{col_name}'의 타입이 올바르지 않습니다: "
                        f"기대 {col_type.__name__}, 실제 {type(data[col_name]).__name__}"
                    )

        # 예상하지 않은 컬럼 확인 (경고만)
        extra_columns = set(data.keys()) - set(expected_columns.keys())
        if extra_columns:
            result.warnings.append(
                f"예상하지 않은 컬럼이 있습니다: {extra_columns}"
            )

        return result

    def validate_range(
        self,
        values: List[float],
        min_val: float,
        max_val: float,
        sensor_type: str,
    ) -> ValidationResult:
        """
        값들이 물리적으로 가능한 범위 내에 있는지 검증합니다.

        Args:
            values: 검증할 값 리스트
            min_val: 허용 최소값
            max_val: 허용 최대값
            sensor_type: 센서 타입 (에러 메시지에 사용)

        Returns:
            ValidationResult: 검증 결과
        """
        result = ValidationResult()

        if not values:
            result.warnings.append("검증할 데이터가 비어있습니다")
            return result

        for idx, value in enumerate(values):
            if value is None:
                result.is_valid = False
                result.errors.append(
                    f"인덱스 {idx}: {sensor_type} 값이 None입니다"
                )
            elif value < min_val or value > max_val:
                result.is_valid = False
                result.errors.append(
                    f"인덱스 {idx}: {sensor_type} 값 {value}이(가) "
                    f"허용 범위({min_val}~{max_val})를 벗어났습니다"
                )

        # 범위 내이지만 극단값에 가까운 경우 경고
        if values and result.is_valid:
            range_size = max_val - min_val
            warning_margin = range_size * 0.1  # 범위의 10% 이내면 경고

            for idx, value in enumerate(values):
                if value is not None:
                    if value < min_val + warning_margin:
                        result.warnings.append(
                            f"인덱스 {idx}: {sensor_type} 값 {value}이(가) "
                            f"하한({min_val})에 근접합니다"
                        )
                    elif value > max_val - warning_margin:
                        result.warnings.append(
                            f"인덱스 {idx}: {sensor_type} 값 {value}이(가) "
                            f"상한({max_val})에 근접합니다"
                        )

        return result

    def detect_gaps(
        self,
        timestamps: List[datetime],
        max_gap_seconds: float,
    ) -> List[Dict[str, Any]]:
        """
        시계열 타임스탬프에서 갭(gap)을 탐지합니다.

        Args:
            timestamps: 정렬된 datetime 리스트
            max_gap_seconds: 허용 최대 갭 (초)

        Returns:
            갭 정보 리스트:
            [{"start": datetime, "end": datetime, "gap_seconds": float}, ...]
        """
        if len(timestamps) < 2:
            return []

        gaps = []

        for i in range(len(timestamps) - 1):
            diff = (timestamps[i + 1] - timestamps[i]).total_seconds()

            if diff > max_gap_seconds:
                gaps.append({
                    "start": timestamps[i],
                    "end": timestamps[i + 1],
                    "gap_seconds": diff,
                })

        return gaps

    def validate_completeness(
        self,
        timestamps: List[datetime],
        expected_interval: float,
    ) -> float:
        """
        시계열 데이터의 완전성 비율을 계산합니다.

        예상 간격 기준으로 데이터가 얼마나 완전한지 백분율로 반환합니다.

        Args:
            timestamps: datetime 리스트
            expected_interval: 예상 수집 간격 (초)

        Returns:
            완전성 비율 (0.0 ~ 100.0)

        Raises:
            ValueError: 타임스탬프가 2개 미만일 때
        """
        if len(timestamps) < 2:
            raise ValueError(
                "완전성 계산에는 최소 2개의 타임스탬프가 필요합니다"
            )

        # 전체 시간 범위
        total_seconds = (timestamps[-1] - timestamps[0]).total_seconds()

        if total_seconds <= 0:
            raise ValueError("타임스탬프가 시간순으로 정렬되어야 합니다")

        # 예상 데이터 포인트 수
        expected_count = int(total_seconds / expected_interval) + 1

        # 실제 데이터 포인트 수
        actual_count = len(timestamps)

        # 완전성 비율 (100%를 넘지 않도록)
        completeness = min(100.0, (actual_count / expected_count) * 100.0)

        return completeness

    def validate_sensor_reading(
        self, reading: Dict[str, Any]
    ) -> ValidationResult:
        """
        단일 센서 리딩의 유효성을 종합적으로 검증합니다.

        검증 항목:
        1. 필수 필드 존재 (timestamp, sensor_type, value)
        2. sensor_type이 알려진 타입인지
        3. value가 해당 센서의 물리적 범위 내인지
        4. timestamp가 유효한 datetime인지

        Args:
            reading: 센서 리딩 딕셔너리
                {
                    "timestamp": datetime,
                    "sensor_type": str,
                    "value": float,
                }

        Returns:
            ValidationResult: 검증 결과
        """
        result = ValidationResult()

        # 1. 필수 필드 확인
        required_fields = ["timestamp", "sensor_type", "value"]
        for field_name in required_fields:
            if field_name not in reading:
                result.is_valid = False
                result.errors.append(
                    f"필수 필드 '{field_name}'이(가) 누락되었습니다"
                )

        if not result.is_valid:
            return result  # 필수 필드가 없으면 추가 검증 불가

        # 2. timestamp 유효성 확인
        ts = reading["timestamp"]
        if not isinstance(ts, datetime):
            result.is_valid = False
            result.errors.append(
                f"timestamp가 datetime 타입이 아닙니다: {type(ts).__name__}"
            )

        # 미래 시각 검증 (현재 + 1일 이후면 경고)
        if isinstance(ts, datetime):
            if ts > datetime.now() + timedelta(days=1):
                result.warnings.append(
                    f"timestamp가 미래 시각입니다: {ts}"
                )

        # 3. sensor_type 유효성 확인
        sensor_type = reading["sensor_type"]
        if sensor_type not in SENSOR_RANGES:
            result.is_valid = False
            result.errors.append(
                f"알 수 없는 센서 타입입니다: '{sensor_type}'. "
                f"지원 타입: {list(SENSOR_RANGES.keys())}"
            )
            return result

        # 4. value 범위 검증
        value = reading["value"]
        if not isinstance(value, (int, float)):
            result.is_valid = False
            result.errors.append(
                f"value가 숫자 타입이 아닙니다: {type(value).__name__}"
            )
            return result

        sensor_range = SENSOR_RANGES[sensor_type]
        if value < sensor_range["min"] or value > sensor_range["max"]:
            result.is_valid = False
            result.errors.append(
                f"{sensor_type} 값 {value}이(가) 허용 범위"
                f"({sensor_range['min']}~{sensor_range['max']} "
                f"{sensor_range['unit']})를 벗어났습니다"
            )

        return result
