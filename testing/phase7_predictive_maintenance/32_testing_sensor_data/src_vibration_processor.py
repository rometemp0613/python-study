"""
진동 데이터 처리 모듈

공장 설비의 진동 센서에서 수집된 데이터를 처리하는 클래스입니다.
CSV 파일 로딩, 데이터 클리닝, 이상치 제거, 리샘플링, 특징 추출 등의
전체 파이프라인을 제공합니다.

외부 라이브러리 없이 Python 표준 라이브러리만 사용합니다.
"""

import csv
import math
import statistics
import json
from typing import List, Dict, Optional, Any


class VibrationDataProcessor:
    """
    진동 센서 데이터 처리기

    설비 예지보전을 위한 진동 데이터의 수집, 전처리, 특징 추출을 담당합니다.
    """

    def load_csv(self, filepath: str) -> List[Dict[str, float]]:
        """
        CSV 파일에서 진동 데이터를 로딩합니다.

        Args:
            filepath: CSV 파일 경로 (timestamp, amplitude 컬럼 필요)

        Returns:
            딕셔너리 리스트 [{"timestamp": float, "amplitude": float}, ...]

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            ValueError: CSV 형식이 올바르지 않을 때
        """
        data = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                # 헤더 검증
                if reader.fieldnames is None:
                    raise ValueError("CSV 파일이 비어있습니다")

                required_columns = {"timestamp", "amplitude"}
                actual_columns = set(reader.fieldnames)
                missing = required_columns - actual_columns
                if missing:
                    raise ValueError(
                        f"필수 컬럼이 누락되었습니다: {missing}"
                    )

                for row_num, row in enumerate(reader, start=2):
                    try:
                        data.append({
                            "timestamp": float(row["timestamp"]),
                            "amplitude": float(row["amplitude"]),
                        })
                    except (ValueError, TypeError) as e:
                        raise ValueError(
                            f"{row_num}행 데이터 변환 오류: {e}"
                        )
        except FileNotFoundError:
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")

        return data

    def clean_data(self, data: List[Optional[float]]) -> List[float]:
        """
        결측치(None)를 선형 보간으로 채웁니다.

        선형 보간: 양쪽의 유효한 값을 이용하여 비례적으로 채움
        첫 번째/마지막 값이 None인 경우 가장 가까운 유효값으로 채움

        Args:
            data: None을 포함할 수 있는 float 리스트

        Returns:
            None이 제거된 float 리스트

        Raises:
            ValueError: 데이터가 비어있거나 모든 값이 None일 때
        """
        if not data:
            raise ValueError("데이터가 비어있습니다")

        if all(v is None for v in data):
            raise ValueError("모든 값이 결측치입니다")

        result = list(data)

        # 유효한 값의 인덱스 찾기
        valid_indices = [i for i, v in enumerate(result) if v is not None]

        if not valid_indices:
            raise ValueError("모든 값이 결측치입니다")

        # 시작 부분의 None을 첫 번째 유효값으로 채움
        first_valid = valid_indices[0]
        for i in range(first_valid):
            result[i] = result[first_valid]

        # 끝 부분의 None을 마지막 유효값으로 채움
        last_valid = valid_indices[-1]
        for i in range(last_valid + 1, len(result)):
            result[i] = result[last_valid]

        # 중간 부분의 None을 선형 보간
        for idx in range(len(valid_indices) - 1):
            start = valid_indices[idx]
            end = valid_indices[idx + 1]

            if end - start > 1:
                # 사이에 None이 있는 경우
                start_val = result[start]
                end_val = result[end]
                gap = end - start

                for i in range(start + 1, end):
                    # 선형 보간 계산
                    fraction = (i - start) / gap
                    result[i] = start_val + fraction * (end_val - start_val)

        return result

    def remove_outliers(
        self, data: List[float], method: str = "iqr"
    ) -> List[float]:
        """
        통계적 방법으로 이상치를 제거합니다.

        IQR 방법: Q1 - 1.5*IQR ~ Q3 + 1.5*IQR 범위 밖의 값을 제거

        Args:
            data: float 리스트
            method: 이상치 제거 방법 ("iqr" 지원)

        Returns:
            이상치가 제거된 float 리스트

        Raises:
            ValueError: 지원하지 않는 method이거나 데이터가 부족할 때
        """
        if method != "iqr":
            raise ValueError(f"지원하지 않는 방법입니다: {method}")

        if len(data) < 4:
            # 데이터가 너무 적으면 이상치 판단 불가
            return list(data)

        sorted_data = sorted(data)
        n = len(sorted_data)

        # Q1 (25번째 백분위수)
        q1_idx = n * 0.25
        if q1_idx == int(q1_idx):
            q1 = sorted_data[int(q1_idx)]
        else:
            lower = int(q1_idx)
            upper = lower + 1
            fraction = q1_idx - lower
            q1 = sorted_data[lower] + fraction * (
                sorted_data[min(upper, n - 1)] - sorted_data[lower]
            )

        # Q3 (75번째 백분위수)
        q3_idx = n * 0.75
        if q3_idx == int(q3_idx):
            q3 = sorted_data[int(q3_idx)]
        else:
            lower = int(q3_idx)
            upper = lower + 1
            fraction = q3_idx - lower
            q3 = sorted_data[lower] + fraction * (
                sorted_data[min(upper, n - 1)] - sorted_data[lower]
            )

        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        return [x for x in data if lower_bound <= x <= upper_bound]

    def resample(self, data: List[float], target_freq: int) -> List[float]:
        """
        데이터를 목표 주파수로 리샘플링합니다.

        원본 데이터의 길이를 원래 주파수로 간주하고,
        target_freq에 맞게 균등하게 샘플을 선택하거나 보간합니다.

        Args:
            data: 원본 데이터
            target_freq: 목표 샘플 수 (주파수 비율)

        Returns:
            리샘플링된 데이터

        Raises:
            ValueError: 데이터가 비어있거나 target_freq가 0 이하일 때
        """
        if not data:
            raise ValueError("데이터가 비어있습니다")

        if target_freq <= 0:
            raise ValueError("목표 주파수는 양수여야 합니다")

        original_len = len(data)

        if target_freq == original_len:
            return list(data)

        # 목표 길이 계산 (비율 기반)
        # 원본 데이터 길이를 원래 주파수로 간주
        ratio = target_freq / original_len
        target_len = max(1, int(original_len * ratio))

        result = []
        for i in range(target_len):
            # 원본 데이터에서의 위치 계산
            pos = i * (original_len - 1) / max(1, target_len - 1)
            lower_idx = int(pos)
            upper_idx = min(lower_idx + 1, original_len - 1)
            fraction = pos - lower_idx

            # 선형 보간
            value = data[lower_idx] + fraction * (
                data[upper_idx] - data[lower_idx]
            )
            result.append(value)

        return result

    def calculate_rms(self, data: List[float]) -> float:
        """
        RMS(Root Mean Square)를 계산합니다.

        RMS = sqrt(mean(x^2))
        진동 신호의 전체 에너지 수준을 나타냅니다.

        Args:
            data: float 리스트

        Returns:
            RMS 값

        Raises:
            ValueError: 데이터가 비어있을 때
        """
        if not data:
            raise ValueError("데이터가 비어있습니다")

        mean_squares = sum(x ** 2 for x in data) / len(data)
        return math.sqrt(mean_squares)

    def calculate_kurtosis(self, data: List[float]) -> float:
        """
        첨도(Kurtosis)를 계산합니다.

        첨도는 분포의 뾰족한 정도를 나타냅니다.
        정규분포의 첨도는 3이며, 이보다 큰 값은 충격 성분이 많음을 의미합니다.
        (excess kurtosis = kurtosis - 3)

        Fisher 정의를 사용합니다 (정규분포 = 0).

        Args:
            data: float 리스트

        Returns:
            초과 첨도(excess kurtosis) 값

        Raises:
            ValueError: 데이터가 3개 미만일 때
        """
        n = len(data)
        if n < 4:
            raise ValueError("첨도 계산에는 최소 4개의 데이터가 필요합니다")

        mean = statistics.mean(data)
        std = statistics.stdev(data)

        if std == 0:
            return 0.0

        # 4차 모멘트 기반 첨도 계산
        m4 = sum((x - mean) ** 4 for x in data) / n
        m2 = sum((x - mean) ** 2 for x in data) / n

        # excess kurtosis (Fisher 정의: 정규분포 = 0)
        kurtosis = (m4 / (m2 ** 2)) - 3.0

        return kurtosis

    def calculate_peak_to_peak(self, data: List[float]) -> float:
        """
        Peak-to-Peak 값을 계산합니다.

        최대값과 최소값의 차이로, 진동의 전체 진폭 범위를 나타냅니다.

        Args:
            data: float 리스트

        Returns:
            Peak-to-Peak 값

        Raises:
            ValueError: 데이터가 비어있을 때
        """
        if not data:
            raise ValueError("데이터가 비어있습니다")

        return max(data) - min(data)

    def calculate_crest_factor(self, data: List[float]) -> float:
        """
        Crest Factor를 계산합니다.

        Crest Factor = peak / RMS
        충격 성분의 비율을 나타냅니다. 높은 CF는 날카로운 충격이 있음을 의미합니다.

        Args:
            data: float 리스트

        Returns:
            Crest Factor 값

        Raises:
            ValueError: 데이터가 비어있거나 RMS가 0일 때
        """
        if not data:
            raise ValueError("데이터가 비어있습니다")

        rms = self.calculate_rms(data)

        if rms == 0:
            raise ValueError("RMS가 0이므로 Crest Factor를 계산할 수 없습니다")

        peak = max(abs(x) for x in data)
        return peak / rms

    def extract_all_features(self, data: List[float]) -> Dict[str, float]:
        """
        모든 특징값을 한번에 추출합니다.

        Args:
            data: float 리스트

        Returns:
            특징값 딕셔너리:
            {
                "rms": float,
                "kurtosis": float,
                "peak_to_peak": float,
                "crest_factor": float,
                "mean": float,
                "std": float,
                "max": float,
                "min": float,
            }

        Raises:
            ValueError: 데이터가 충분하지 않을 때
        """
        if not data:
            raise ValueError("데이터가 비어있습니다")

        if len(data) < 4:
            raise ValueError("특징 추출에는 최소 4개의 데이터가 필요합니다")

        features = {
            "rms": self.calculate_rms(data),
            "kurtosis": self.calculate_kurtosis(data),
            "peak_to_peak": self.calculate_peak_to_peak(data),
            "crest_factor": self.calculate_crest_factor(data),
            "mean": statistics.mean(data),
            "std": statistics.stdev(data),
            "max": max(data),
            "min": min(data),
        }

        return features
