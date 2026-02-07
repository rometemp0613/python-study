"""
센서 임계값 설정 모듈

환경 변수와 JSON 설정 파일에서 센서 임계값을 로드하고,
시간 기반 알림 활성화 여부를 판단합니다.

외부 의존성 없이 표준 라이브러리만 사용합니다.
"""
import json
import os
from datetime import datetime
from typing import Any, Optional


# 기본 임계값 설정
DEFAULT_THRESHOLDS = {
    "temperature": {"warning": 80.0, "critical": 95.0},
    "vibration": {"warning": 5.0, "critical": 10.0},
    "current": {"warning": 15.0, "critical": 20.0},
}

# 환경 변수 이름 매핑
ENV_VAR_MAP = {
    "temperature": {
        "warning": "SENSOR_TEMP_WARNING",
        "critical": "SENSOR_TEMP_CRITICAL",
    },
    "vibration": {
        "warning": "SENSOR_VIB_WARNING",
        "critical": "SENSOR_VIB_CRITICAL",
    },
    "current": {
        "warning": "SENSOR_CURR_WARNING",
        "critical": "SENSOR_CURR_CRITICAL",
    },
}


class ThresholdConfig:
    """
    센서 임계값 설정 관리자

    설정 우선순위:
    1. 환경 변수 (최우선)
    2. 설정 파일
    3. 기본값 (fallback)

    사용 예시:
        config = ThresholdConfig()
        config.load_from_file("config.json")
        config.load_from_env()  # 환경 변수로 덮어쓰기

        threshold = config.get_threshold("temperature")
        if sensor_value > threshold["critical"]:
            send_alert(...)
    """

    def __init__(self):
        """기본값으로 초기화"""
        # 기본 임계값 복사
        self.thresholds = {}
        for sensor_type, values in DEFAULT_THRESHOLDS.items():
            self.thresholds[sensor_type] = values.copy()

        # 알림 활성 시간 (기본: 00시~24시, 즉 항상 활성)
        self.alert_start_hour = 0
        self.alert_end_hour = 24

    def load_from_env(self) -> None:
        """
        환경 변수에서 임계값 로드

        설정된 환경 변수만 덮어씁니다.
        잘못된 값(숫자가 아닌 문자열)이 있으면 ValueError를 발생시킵니다.

        환경 변수 이름:
            SENSOR_TEMP_WARNING, SENSOR_TEMP_CRITICAL
            SENSOR_VIB_WARNING, SENSOR_VIB_CRITICAL
            SENSOR_CURR_WARNING, SENSOR_CURR_CRITICAL
            ALERT_START_HOUR, ALERT_END_HOUR

        Raises:
            ValueError: 환경 변수 값이 숫자로 변환할 수 없을 때
        """
        for sensor_type, env_vars in ENV_VAR_MAP.items():
            for level, env_name in env_vars.items():
                env_value = os.environ.get(env_name)
                if env_value is not None:
                    try:
                        parsed_value = float(env_value)
                    except ValueError:
                        raise ValueError(
                            f"환경 변수 '{env_name}'의 값 '{env_value}'을(를) "
                            f"숫자로 변환할 수 없습니다"
                        )
                    if sensor_type not in self.thresholds:
                        self.thresholds[sensor_type] = {}
                    self.thresholds[sensor_type][level] = parsed_value

        # 알림 시간 설정
        start_hour = os.environ.get("ALERT_START_HOUR")
        if start_hour is not None:
            try:
                self.alert_start_hour = int(start_hour)
            except ValueError:
                raise ValueError(
                    f"환경 변수 'ALERT_START_HOUR'의 값 '{start_hour}'을(를) "
                    f"정수로 변환할 수 없습니다"
                )

        end_hour = os.environ.get("ALERT_END_HOUR")
        if end_hour is not None:
            try:
                self.alert_end_hour = int(end_hour)
            except ValueError:
                raise ValueError(
                    f"환경 변수 'ALERT_END_HOUR'의 값 '{end_hour}'을(를) "
                    f"정수로 변환할 수 없습니다"
                )

    def load_from_file(self, filepath: str) -> None:
        """
        JSON 설정 파일에서 임계값 로드

        파일 형식:
        {
            "thresholds": {
                "temperature": {"warning": 80.0, "critical": 95.0},
                ...
            },
            "alert_hours": {"start": 8, "end": 22}
        }

        Args:
            filepath: JSON 설정 파일 경로

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            ValueError: JSON 파싱 실패 또는 잘못된 형식일 때
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"설정 파일을 찾을 수 없습니다: {filepath}"
            )

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 실패: {e}") from e

        # 임계값 로드
        if "thresholds" in data:
            for sensor_type, values in data["thresholds"].items():
                if sensor_type not in self.thresholds:
                    self.thresholds[sensor_type] = {}
                for level, value in values.items():
                    if not isinstance(value, (int, float)):
                        raise ValueError(
                            f"임계값은 숫자여야 합니다: "
                            f"{sensor_type}.{level} = {value}"
                        )
                    self.thresholds[sensor_type][level] = float(value)

        # 알림 시간 로드
        if "alert_hours" in data:
            alert_hours = data["alert_hours"]
            if "start" in alert_hours:
                self.alert_start_hour = int(alert_hours["start"])
            if "end" in alert_hours:
                self.alert_end_hour = int(alert_hours["end"])

    def get_threshold(self, sensor_type: str) -> dict:
        """
        특정 센서 타입의 임계값 조회

        Args:
            sensor_type: 센서 타입 ("temperature", "vibration", "current")

        Returns:
            {"warning": float, "critical": float} 딕셔너리

        Raises:
            KeyError: 알 수 없는 센서 타입일 때
        """
        if sensor_type not in self.thresholds:
            raise KeyError(
                f"알 수 없는 센서 타입: '{sensor_type}'. "
                f"사용 가능: {list(self.thresholds.keys())}"
            )
        return self.thresholds[sensor_type].copy()

    def is_alert_time(self) -> bool:
        """
        현재 시간이 알림 활성 시간인지 확인

        alert_start_hour <= 현재 시간 < alert_end_hour이면 True.
        start > end인 경우 (예: 22시~6시)도 올바르게 처리합니다.

        Returns:
            알림 활성 여부
        """
        current_hour = datetime.now().hour

        if self.alert_start_hour <= self.alert_end_hour:
            # 일반적인 경우: 8시~22시
            return self.alert_start_hour <= current_hour < self.alert_end_hour
        else:
            # 자정을 넘는 경우: 22시~6시
            return (
                current_hour >= self.alert_start_hour
                or current_hour < self.alert_end_hour
            )

    def check_value(
        self, sensor_type: str, value: float
    ) -> str:
        """
        센서 값의 상태 판정

        Args:
            sensor_type: 센서 타입
            value: 센서 측정값

        Returns:
            "normal", "warning", 또는 "critical"
        """
        threshold = self.get_threshold(sensor_type)

        if value >= threshold["critical"]:
            return "critical"
        elif value >= threshold["warning"]:
            return "warning"
        else:
            return "normal"
