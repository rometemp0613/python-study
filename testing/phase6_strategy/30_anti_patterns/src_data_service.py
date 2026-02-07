"""
데이터 서비스 모듈

센서 데이터를 가져오고, 처리하고, 저장하는 파이프라인을 제공합니다.
테스트 안티패턴 학습을 위한 예시 코드입니다.
"""

import math
from typing import Any, Dict, List, Optional
from datetime import datetime


class DataService:
    """
    데이터 서비스

    센서 데이터의 수집, 처리, 저장 파이프라인을 관리합니다.
    """

    def __init__(self, storage: Optional[Any] = None):
        """
        데이터 서비스를 초기화합니다.

        Args:
            storage: 저장소 객체 (None이면 인메모리 저장소 사용)
        """
        self._storage = storage
        self._cache: Dict[str, List[float]] = {}
        self._results: Dict[str, Dict] = {}

    def get_sensor_data(self, sensor_id: str) -> List[float]:
        """
        센서 데이터를 가져옵니다.

        캐시에 있으면 캐시에서, 없으면 시뮬레이션 데이터를 생성합니다.

        Args:
            sensor_id: 센서 ID

        Returns:
            센서 측정값 리스트
        """
        # 캐시 확인
        if sensor_id in self._cache:
            return self._cache[sensor_id]

        # 시뮬레이션 데이터 생성 (실제로는 DB나 API에서 가져옴)
        data = self._generate_sample_data(sensor_id)
        self._cache[sensor_id] = data
        return data

    def process_data(self, data: List[float]) -> Dict[str, Any]:
        """
        센서 데이터를 처리합니다.

        통계 계산과 이상치 감지를 수행합니다.

        Args:
            data: 센서 측정값 리스트

        Returns:
            처리 결과 딕셔너리

        Raises:
            ValueError: 빈 데이터인 경우
        """
        if not data:
            raise ValueError("빈 데이터는 처리할 수 없습니다.")

        n = len(data)
        mean = sum(data) / n
        variance = sum((x - mean) ** 2 for x in data) / n
        std = math.sqrt(variance)

        # 이상치 감지 (3-시그마)
        anomalies = []
        if std > 0:
            anomalies = [x for x in data if abs(x - mean) > 3 * std]

        return {
            "mean": round(mean, 4),
            "std": round(std, 4),
            "min": min(data),
            "max": max(data),
            "count": n,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "processed_at": datetime.now().isoformat(),
        }

    def save_results(self, results: Dict[str, Any],
                     result_id: Optional[str] = None) -> str:
        """
        처리 결과를 저장합니다.

        Args:
            results: 처리 결과 딕셔너리
            result_id: 결과 ID (None이면 자동 생성)

        Returns:
            저장된 결과의 ID
        """
        if result_id is None:
            result_id = f"result_{len(self._results) + 1:04d}"

        self._results[result_id] = {
            "data": results,
            "saved_at": datetime.now().isoformat(),
        }

        return result_id

    def get_saved_result(self, result_id: str) -> Optional[Dict]:
        """
        저장된 결과를 조회합니다.

        Args:
            result_id: 결과 ID

        Returns:
            저장된 결과 또는 None
        """
        entry = self._results.get(result_id)
        if entry is None:
            return None
        return entry["data"]

    def run_analysis(self, sensor_id: str) -> Dict[str, Any]:
        """
        전체 분석 파이프라인을 실행합니다.

        데이터 수집 → 처리 → 저장의 전체 과정을 수행합니다.

        Args:
            sensor_id: 센서 ID

        Returns:
            분석 결과
        """
        # 1. 데이터 수집
        data = self.get_sensor_data(sensor_id)

        # 2. 데이터 처리
        results = self.process_data(data)

        # 3. 결과 저장
        result_id = self.save_results(results, result_id=f"analysis_{sensor_id}")

        return {
            "sensor_id": sensor_id,
            "result_id": result_id,
            "summary": {
                "mean": results["mean"],
                "std": results["std"],
                "anomaly_count": results["anomaly_count"],
            },
        }

    def _generate_sample_data(self, sensor_id: str) -> List[float]:
        """
        시뮬레이션 데이터를 생성합니다 (내부 메서드).

        실제 환경에서는 DB나 API에서 데이터를 가져옵니다.

        Args:
            sensor_id: 센서 ID

        Returns:
            샘플 데이터 리스트
        """
        # 센서 ID 기반으로 결정론적 데이터 생성
        base_value = hash(sensor_id) % 100 + 50  # 50~150 범위
        return [
            base_value + (i % 10) - 5
            for i in range(20)
        ]

    def clear_cache(self) -> None:
        """캐시를 초기화합니다."""
        self._cache.clear()
