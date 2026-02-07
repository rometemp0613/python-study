"""
간단한 이상 탐지 모델 모듈

Z-score 기반 이상 탐지를 구현합니다.
외부 ML 라이브러리(sklearn 등) 없이 표준 라이브러리만 사용합니다.

공장 설비의 진동, 온도, 전류 데이터에서
이상 패턴을 감지하는 데 사용됩니다.
"""
import json
import math
import os
from typing import Optional


class SimpleAnomalyDetector:
    """
    Z-score 기반 간단한 이상 탐지기

    동작 원리:
    1. fit(): 정상 데이터의 평균과 표준편차를 학습
    2. predict(): 새 데이터의 Z-score(이상 점수)를 계산
    3. classify(): 임계값을 기준으로 정상(0)/이상(1) 분류

    Z-score = |x - mean| / std
    Z-score가 높을수록 평균에서 멀리 떨어진 이상 값
    """

    def __init__(self):
        """초기화 - 학습 전 상태"""
        self.mean: Optional[float] = None
        self.std: Optional[float] = None
        self.is_fitted: bool = False
        self.n_samples: int = 0

    def fit(self, data: list) -> None:
        """
        정상 데이터로 모델 학습

        평균과 표준편차(모집단 표준편차)를 계산합니다.

        Args:
            data: 정상 상태의 센서 값 리스트

        Raises:
            ValueError: 데이터가 비어있을 때
        """
        if not data:
            raise ValueError("학습 데이터가 비어있습니다")

        n = len(data)
        self.n_samples = n

        # 평균 계산
        self.mean = sum(data) / n

        # 모집단 표준편차 계산
        if n == 1:
            self.std = 0.0
        else:
            variance = sum((x - self.mean) ** 2 for x in data) / n
            self.std = math.sqrt(variance)

        self.is_fitted = True

    def predict(self, data: list) -> list:
        """
        이상 점수(Z-score) 계산

        각 데이터 포인트의 Z-score를 반환합니다.
        Z-score = |x - mean| / std

        std=0인 경우(모든 학습 데이터가 동일):
        - x == mean이면 Z-score = 0
        - x != mean이면 Z-score = float('inf')

        Args:
            data: 평가할 센서 값 리스트

        Returns:
            Z-score 리스트 (0 이상의 값)

        Raises:
            RuntimeError: 모델이 학습되지 않았을 때
            ValueError: 데이터가 비어있을 때
        """
        if not self.is_fitted:
            raise RuntimeError("모델이 학습되지 않았습니다. fit()을 먼저 호출하세요")

        if not data:
            raise ValueError("예측할 데이터가 비어있습니다")

        scores = []
        for x in data:
            if self.std == 0.0:
                # 표준편차가 0인 특별한 경우
                if x == self.mean:
                    scores.append(0.0)
                else:
                    scores.append(float("inf"))
            else:
                z_score = abs(x - self.mean) / self.std
                scores.append(z_score)

        return scores

    def classify(self, data: list, threshold: float = 3.0) -> list:
        """
        이진 분류 (정상=0, 이상=1)

        Z-score >= threshold이면 이상(1), 그렇지 않으면 정상(0).

        Args:
            data: 평가할 센서 값 리스트
            threshold: 이상 판정 Z-score 임계값 (기본: 3.0)

        Returns:
            분류 결과 리스트 (0 또는 1)
        """
        scores = self.predict(data)
        return [1 if score >= threshold else 0 for score in scores]

    def save_model(self, filepath: str) -> None:
        """
        모델 파라미터를 JSON 파일로 저장

        Args:
            filepath: 저장할 파일 경로

        Raises:
            RuntimeError: 모델이 학습되지 않았을 때
        """
        if not self.is_fitted:
            raise RuntimeError(
                "학습되지 않은 모델은 저장할 수 없습니다"
            )

        model_data = {
            "mean": self.mean,
            "std": self.std,
            "n_samples": self.n_samples,
            "is_fitted": self.is_fitted,
        }

        # 디렉토리가 없으면 생성
        dir_path = os.path.dirname(filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(model_data, f, indent=2, ensure_ascii=False)

    def load_model(self, filepath: str) -> None:
        """
        JSON 파일에서 모델 파라미터 로드

        Args:
            filepath: 모델 파일 경로

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            ValueError: 파일 형식이 올바르지 않을 때
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"모델 파일을 찾을 수 없습니다: {filepath}"
            )

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                model_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"모델 파일 JSON 파싱 실패: {e}") from e

        # 필수 필드 확인
        required_fields = ["mean", "std", "is_fitted"]
        for field in required_fields:
            if field not in model_data:
                raise ValueError(f"모델 파일에 필수 필드 누락: {field}")

        self.mean = float(model_data["mean"])
        self.std = float(model_data["std"])
        self.n_samples = int(model_data.get("n_samples", 0))
        self.is_fitted = bool(model_data["is_fitted"])

    def extract_features(self, raw_data: list) -> dict:
        """
        원시 센서 데이터에서 통계 특징 추출

        진동 분석에 일반적으로 사용되는 특징들을 계산합니다:
        - RMS (Root Mean Square): 신호의 에너지 수준
        - peak_to_peak: 최대 진폭 범위
        - std (표준편차): 신호의 변동성
        - mean (평균): 신호의 평균 수준
        - max_abs: 최대 절대값
        - crest_factor: 피크 대 RMS 비율

        Args:
            raw_data: 원시 센서 값 리스트

        Returns:
            특징 딕셔너리

        Raises:
            ValueError: 데이터가 비어있을 때
        """
        if not raw_data:
            raise ValueError("특징 추출할 데이터가 비어있습니다")

        n = len(raw_data)

        # 평균
        mean_val = sum(raw_data) / n

        # RMS (Root Mean Square)
        rms = math.sqrt(sum(x ** 2 for x in raw_data) / n)

        # 표준편차 (모집단)
        if n == 1:
            std_val = 0.0
        else:
            variance = sum((x - mean_val) ** 2 for x in raw_data) / n
            std_val = math.sqrt(variance)

        # 최대, 최소, 피크 대 피크
        max_val = max(raw_data)
        min_val = min(raw_data)
        peak_to_peak = max_val - min_val

        # 최대 절대값
        max_abs = max(abs(x) for x in raw_data)

        # 크레스트 팩터 (crest factor = peak / rms)
        if rms > 0:
            crest_factor = max_abs / rms
        else:
            crest_factor = 0.0

        return {
            "mean": mean_val,
            "std": std_val,
            "rms": rms,
            "peak_to_peak": peak_to_peak,
            "max_abs": max_abs,
            "crest_factor": crest_factor,
        }
