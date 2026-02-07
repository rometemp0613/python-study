"""
베어링 고장 예측 모델 모듈

통계 기반의 간단한 이상 탐지 모델로, 베어링의 건강 상태를 예측합니다.
학습 데이터의 정상 패턴(평균, 표준편차)을 기억하고,
새로운 데이터가 정상 패턴에서 얼마나 벗어났는지로 건강도를 판단합니다.

외부 라이브러리 없이 Python 표준 라이브러리만 사용합니다.
"""

import json
import math
import statistics
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any


@dataclass
class HealthMetrics:
    """
    모델 평가 지표를 담는 데이터 클래스

    Attributes:
        accuracy: 전체 정확도 (0.0 ~ 1.0)
        precision: 정밀도 - 고장 예측 중 실제 고장 비율
        recall: 재현율 - 실제 고장 중 탐지된 비율
        f1: F1 점수 - precision과 recall의 조화 평균
    """
    accuracy: float
    precision: float
    recall: float
    f1: float


class BearingFailurePredictor:
    """
    베어링 고장 예측기

    통계 기반 접근:
    1. fit(): 정상 데이터의 각 특징(feature) 평균/표준편차를 학습
    2. predict_health_score(): 새 데이터가 정상 패턴에서 얼마나 벗어났는지 점수 계산
    3. predict_rul(): 건강도 이력을 선형 외삽하여 잔여 수명 추정
    4. evaluate(): 이진 분류 성능 지표 계산
    """

    # 건강도 판정 임계값 (이 점수 이하면 "고장"으로 판정)
    HEALTH_THRESHOLD = 50.0

    # 특징 이름 목록
    FEATURE_NAMES = ["rms", "kurtosis", "crest_factor"]

    def __init__(self):
        """모델 초기화"""
        self.is_fitted: bool = False
        self.normal_params: Dict[str, Dict[str, float]] = {}
        # normal_params 구조:
        # {
        #     "rms": {"mean": 0.5, "std": 0.1},
        #     "kurtosis": {"mean": 0.2, "std": 0.05},
        #     "crest_factor": {"mean": 1.4, "std": 0.1},
        # }

    def fit(self, training_data: List[Dict[str, Any]]) -> None:
        """
        정상 데이터의 패턴을 학습합니다.

        label="normal"인 데이터만 사용하여 각 특징의 평균과 표준편차를 계산합니다.

        Args:
            training_data: 학습 데이터 리스트
                [{"rms": float, "kurtosis": float, "crest_factor": float,
                  "label": "normal"|"fault"}, ...]

        Raises:
            ValueError: 정상 데이터가 2개 미만일 때
        """
        # 정상 데이터만 필터링
        normal_data = [
            d for d in training_data if d.get("label") == "normal"
        ]

        if len(normal_data) < 2:
            raise ValueError(
                "정상(normal) 데이터가 최소 2개 이상 필요합니다. "
                f"현재: {len(normal_data)}개"
            )

        # 각 특징의 평균과 표준편차 계산
        self.normal_params = {}
        for feature in self.FEATURE_NAMES:
            values = [d[feature] for d in normal_data if feature in d]
            if len(values) >= 2:
                self.normal_params[feature] = {
                    "mean": statistics.mean(values),
                    "std": max(statistics.stdev(values), 1e-10),
                    # std가 0이면 나눗셈 오류 방지를 위해 최소값 설정
                }

        self.is_fitted = True

    def predict_health_score(self, features: Dict[str, float]) -> float:
        """
        특징값을 기반으로 건강도 점수(0~100)를 계산합니다.

        각 특징이 정상 패턴에서 얼마나 벗어났는지(z-score)를 계산하고,
        이를 0~100 점수로 변환합니다.

        0 = 매우 비정상 (고장 직전)
        100 = 완벽한 정상 상태

        Args:
            features: 특징 딕셔너리 {"rms": float, "kurtosis": float, ...}

        Returns:
            건강도 점수 (0.0 ~ 100.0)

        Raises:
            RuntimeError: 모델이 학습되지 않았을 때
        """
        if not self.is_fitted:
            raise RuntimeError("모델이 학습되지 않았습니다. fit()을 먼저 호출하세요.")

        # 각 특징의 z-score 계산
        z_scores = []
        for feature in self.FEATURE_NAMES:
            if feature in features and feature in self.normal_params:
                params = self.normal_params[feature]
                z = abs(features[feature] - params["mean"]) / params["std"]
                z_scores.append(z)

        if not z_scores:
            return 50.0  # 판단할 수 없으면 중간값

        # 평균 z-score를 건강도 점수로 변환
        # z-score가 0이면 100점(완벽 정상), z-score가 클수록 낮은 점수
        avg_z = statistics.mean(z_scores)

        # 시그모이드 유사 함수로 0~100 범위로 변환
        # z=0 → 100, z=3 → ~5, z=6+ → ~0
        score = 100.0 * math.exp(-0.5 * avg_z)
        score = max(0.0, min(100.0, score))

        return score

    def predict_rul(self, health_scores_history: List[float]) -> float:
        """
        건강도 이력을 기반으로 잔여 수명(RUL)을 추정합니다.

        단순 선형 외삽(linear extrapolation)을 사용합니다:
        건강도 하락 추세를 구하고, 임계값(HEALTH_THRESHOLD) 도달까지의 시간을 예측합니다.

        Args:
            health_scores_history: 시간순 건강도 점수 리스트
                (각 항목은 일정 간격의 측정값)

        Returns:
            잔여 수명 (남은 시간 단위 수, 양수)

        Raises:
            ValueError: 이력이 2개 미만이거나 건강도가 이미 임계값 이하일 때
        """
        if len(health_scores_history) < 2:
            raise ValueError(
                "RUL 예측에는 최소 2개의 건강도 이력이 필요합니다"
            )

        n = len(health_scores_history)
        current_health = health_scores_history[-1]

        # 이미 임계값 이하이면 RUL = 0
        if current_health <= self.HEALTH_THRESHOLD:
            return 0.0

        # 단순 선형 회귀로 하락 추세 계산
        # x = 시간 인덱스, y = 건강도 점수
        x_mean = (n - 1) / 2.0
        y_mean = statistics.mean(health_scores_history)

        # 기울기 계산
        numerator = sum(
            (i - x_mean) * (y - y_mean)
            for i, y in enumerate(health_scores_history)
        )
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            # 데이터가 1개뿐이거나 모든 x가 같은 경우 (발생하지 않아야 함)
            return float("inf")

        slope = numerator / denominator

        # 건강도가 증가하는 추세이면 (설비 상태 개선)
        if slope >= 0:
            # 하락하지 않으므로 RUL은 매우 큼
            return 999.0  # 실질적으로 무한

        # 현재 건강도에서 임계값까지의 시간 단위 계산
        # current_health + slope * rul = HEALTH_THRESHOLD
        rul = (self.HEALTH_THRESHOLD - current_health) / slope

        return max(0.0, rul)

    def evaluate(
        self,
        test_data: List[Dict[str, float]],
        true_labels: List[str],
    ) -> HealthMetrics:
        """
        테스트 데이터로 모델 성능을 평가합니다.

        건강도 점수가 HEALTH_THRESHOLD 이하이면 "fault",
        아니면 "normal"로 예측합니다.

        Args:
            test_data: 테스트 특징 데이터 리스트
            true_labels: 실제 라벨 리스트 ("normal" 또는 "fault")

        Returns:
            HealthMetrics: 성능 지표

        Raises:
            RuntimeError: 모델이 학습되지 않았을 때
            ValueError: 데이터와 라벨 수가 다를 때
        """
        if not self.is_fitted:
            raise RuntimeError("모델이 학습되지 않았습니다")

        if len(test_data) != len(true_labels):
            raise ValueError(
                f"데이터({len(test_data)})와 라벨({len(true_labels)}) 수가 다릅니다"
            )

        # 예측 수행
        predictions = []
        for features in test_data:
            score = self.predict_health_score(features)
            pred = "fault" if score <= self.HEALTH_THRESHOLD else "normal"
            predictions.append(pred)

        # 혼동 행렬(Confusion Matrix) 계산
        tp = 0  # True Positive: 고장을 고장으로 예측
        fp = 0  # False Positive: 정상을 고장으로 예측
        tn = 0  # True Negative: 정상을 정상으로 예측
        fn = 0  # False Negative: 고장을 정상으로 예측

        for pred, true in zip(predictions, true_labels):
            if pred == "fault" and true == "fault":
                tp += 1
            elif pred == "fault" and true == "normal":
                fp += 1
            elif pred == "normal" and true == "normal":
                tn += 1
            elif pred == "normal" and true == "fault":
                fn += 1

        # 지표 계산
        total = tp + fp + tn + fn
        accuracy = (tp + tn) / total if total > 0 else 0.0

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0

        return HealthMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1,
        )

    def save_model(self, filepath: str) -> None:
        """
        모델 파라미터를 JSON 파일로 저장합니다.

        Args:
            filepath: 저장 경로

        Raises:
            RuntimeError: 모델이 학습되지 않았을 때
        """
        if not self.is_fitted:
            raise RuntimeError("학습되지 않은 모델은 저장할 수 없습니다")

        model_data = {
            "is_fitted": self.is_fitted,
            "normal_params": self.normal_params,
            "health_threshold": self.HEALTH_THRESHOLD,
            "feature_names": self.FEATURE_NAMES,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(model_data, f, indent=2, ensure_ascii=False)

    def load_model(self, filepath: str) -> None:
        """
        JSON 파일에서 모델 파라미터를 로딩합니다.

        Args:
            filepath: 모델 파일 경로

        Raises:
            FileNotFoundError: 파일이 없을 때
            ValueError: 파일 형식이 올바르지 않을 때
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                model_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {filepath}")
        except json.JSONDecodeError as e:
            raise ValueError(f"잘못된 JSON 형식입니다: {e}")

        # 필수 키 검증
        required_keys = ["is_fitted", "normal_params"]
        for key in required_keys:
            if key not in model_data:
                raise ValueError(f"모델 파일에 '{key}'가 누락되었습니다")

        self.is_fitted = model_data["is_fitted"]
        self.normal_params = model_data["normal_params"]
