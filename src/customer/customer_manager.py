import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class CustomerManager:
    """고객 관리 및 세그먼테이션 클래스"""

    def __init__(self):
        self.customers = None
        self.transactions = None
        self.segment_strategies = {
            "premium_loyal": {
                "name": "프리미엄 장기 고객",
                "description": "높은 구매력과 충성도를 가진 VIP 고객",
                "strategy": "personalized_premium",
                "color": "#ff6b6b",
            },
            "premium_focused": {
                "name": "프리미엄 집중 고객",
                "description": "고가 상품을 선호하는 고객",
                "strategy": "quality_focused",
                "color": "#4ecdc4",
            },
            "excellent_loyal": {
                "name": "우수 충성 고객",
                "description": "꾸준한 구매 패턴을 보이는 고객",
                "strategy": "loyalty_balanced",
                "color": "#45b7d1",
            },
            "excellent_general": {
                "name": "우수 일반 고객",
                "description": "양호한 구매력을 가진 일반 고객",
                "strategy": "balanced_general",
                "color": "#96ceb4",
            },
            "general_value": {
                "name": "일반 가성비 고객",
                "description": "가격 대비 가치를 중시하는 고객",
                "strategy": "value_focused",
                "color": "#ffeaa7",
            },
            "at_risk": {
                "name": "이탈 위험 고객",
                "description": "구매 빈도가 감소한 고객",
                "strategy": "retention_focused",
                "color": "#fd79a8",
            },
            "new_customer": {
                "name": "신규 유입 고객",
                "description": "최근 가입한 신규 고객",
                "strategy": "exploration_focused",
                "color": "#a29bfe",
            },
        }

    def load_data(self, customers: pd.DataFrame, transactions: pd.DataFrame):
        """고객 및 거래 데이터 로딩"""
        self.customers = customers.copy()
        self.transactions = transactions.copy()

        # 날짜 컬럼 변환
        if "transaction_date" in self.transactions.columns:
            self.transactions["transaction_date"] = pd.to_datetime(
                self.transactions["transaction_date"]
            )

        print(f"✅ 고객 데이터 로딩: {len(self.customers)}명")
        print(f"✅ 거래 데이터 로딩: {len(self.transactions)}건")

    def get_customer_profile(self, customer_id: int) -> Dict:
        """고객 프로필 정보 조회"""
        if self.customers is None:
            raise ValueError("고객 데이터가 로딩되지 않았습니다.")

        customer = self.customers[self.customers["customer_id"] == customer_id]
        if customer.empty:
            raise ValueError(f"고객 ID {customer_id}를 찾을 수 없습니다.")

        customer_info = customer.iloc[0].to_dict()

        # 세그먼트 정보 추가
        segment = customer_info.get("segment", "unknown")
        if segment in self.segment_strategies:
            customer_info["segment_info"] = self.segment_strategies[segment]

        return customer_info

    def get_customer_transactions(
        self, customer_id: int, limit: int = 50
    ) -> pd.DataFrame:
        """고객의 최근 거래 내역 조회"""
        if self.transactions is None:
            raise ValueError("거래 데이터가 로딩되지 않았습니다.")

        customer_transactions = self.transactions[
            self.transactions["customer_id"] == customer_id
        ].sort_values("transaction_date", ascending=False)

        return customer_transactions.head(limit)

    def get_customer_statistics(self, customer_id: int) -> Dict:
        """고객 통계 정보 계산 (오류 수정)"""
        try:
            transactions = self.get_customer_transactions(customer_id, limit=1000)

            if transactions.empty:
                return {
                    "total_transactions": 0,
                    "total_amount": 0,
                    "avg_transaction_amount": 0,
                    "last_transaction_date": None,
                    "days_since_last_purchase": 0,
                    "favorite_categories": [],
                    "monthly_spending": {},
                    "purchase_frequency": {
                        "avg_days_between_purchases": 0,
                        "purchase_pattern": "no_data",
                    },
                    "seasonal_patterns": {},
                }

            # 기본 통계
            total_transactions = len(transactions)
            total_amount = transactions["amount"].sum()
            avg_transaction_amount = transactions["amount"].mean()
            last_transaction_date = transactions["transaction_date"].max()
            days_since_last_purchase = (
                (datetime.now() - last_transaction_date).days
                if pd.notna(last_transaction_date)
                else 0
            )

            # 구매 빈도 계산 (안전하게)
            purchase_frequency = self._calculate_purchase_frequency(transactions)

            # 기타 분석
            favorite_categories = self._get_favorite_categories(transactions)
            monthly_spending = self._get_monthly_spending(transactions)
            seasonal_patterns = self._analyze_seasonal_patterns(transactions)

            stats = {
                "total_transactions": total_transactions,
                "total_amount": float(total_amount) if pd.notna(total_amount) else 0,
                "avg_transaction_amount": (
                    float(avg_transaction_amount)
                    if pd.notna(avg_transaction_amount)
                    else 0
                ),
                "last_transaction_date": last_transaction_date,
                "days_since_last_purchase": days_since_last_purchase,
                "favorite_categories": favorite_categories,
                "monthly_spending": monthly_spending,
                "purchase_frequency": purchase_frequency,
                "seasonal_patterns": seasonal_patterns,
            }

            return stats

        except Exception as e:
            print(f"통계 계산 오류: {e}")
            # 오류 발생 시 기본값 반환
            return {
                "total_transactions": 0,
                "total_amount": 0,
                "avg_transaction_amount": 0,
                "last_transaction_date": None,
                "days_since_last_purchase": 0,
                "favorite_categories": [],
                "monthly_spending": {},
                "purchase_frequency": {
                    "avg_days_between_purchases": 0,
                    "purchase_pattern": "error",
                },
                "seasonal_patterns": {},
            }

    def _get_favorite_categories(
        self, transactions: pd.DataFrame, top_n: int = 5
    ) -> List[Dict]:
        """즐겨 구매하는 카테고리 분석"""
        try:
            if "category" not in transactions.columns or transactions.empty:
                return []

            category_stats = (
                transactions.groupby("category")
                .agg({"amount": ["sum", "count", "mean"]})
                .round(2)
            )

            category_stats.columns = ["total_spent", "purchase_count", "avg_amount"]
            category_stats = category_stats.sort_values("total_spent", ascending=False)

            favorite_categories = []
            for category, row in category_stats.head(top_n).iterrows():
                favorite_categories.append(
                    {
                        "category": str(category),
                        "total_spent": float(row["total_spent"]),
                        "purchase_count": int(row["purchase_count"]),
                        "avg_amount": float(row["avg_amount"]),
                    }
                )

            return favorite_categories

        except Exception as e:
            print(f"선호 카테고리 분석 오류: {e}")
            return []

    def _get_monthly_spending(self, transactions: pd.DataFrame) -> Dict:
        """월별 지출 패턴 분석"""
        try:
            if transactions.empty or "transaction_date" not in transactions.columns:
                return {}

            # 날짜 컬럼이 datetime이 아닌 경우 변환
            if not pd.api.types.is_datetime64_any_dtype(
                transactions["transaction_date"]
            ):
                transactions["transaction_date"] = pd.to_datetime(
                    transactions["transaction_date"]
                )

            transactions["year_month"] = transactions["transaction_date"].dt.to_period(
                "M"
            )
            monthly_spending = (
                transactions.groupby("year_month")["amount"].sum().to_dict()
            )

            # Period 객체를 문자열로 변환
            monthly_spending = {str(k): float(v) for k, v in monthly_spending.items()}

            return monthly_spending

        except Exception as e:
            print(f"월별 지출 분석 오류: {e}")
            return {}

    def _calculate_purchase_frequency(self, transactions: pd.DataFrame) -> Dict:
        """구매 빈도 분석 (오류 수정)"""
        try:
            if transactions.empty or "transaction_date" not in transactions.columns:
                return {"avg_days_between_purchases": 0, "purchase_pattern": "no_data"}

            # 날짜 컬럼이 datetime이 아닌 경우 변환
            if not pd.api.types.is_datetime64_any_dtype(
                transactions["transaction_date"]
            ):
                transactions = transactions.copy()
                transactions["transaction_date"] = pd.to_datetime(
                    transactions["transaction_date"]
                )

            # 고유한 날짜 추출
            unique_dates = (
                transactions["transaction_date"].dt.date.drop_duplicates().sort_values()
            )

            if len(unique_dates) < 2:
                return {
                    "avg_days_between_purchases": 0,
                    "purchase_pattern": "single_purchase",
                }

            # 구매 간격 계산
            intervals = []
            for i in range(1, len(unique_dates)):
                interval = (unique_dates.iloc[i] - unique_dates.iloc[i - 1]).days
                intervals.append(interval)

            if not intervals:
                return {
                    "avg_days_between_purchases": 0,
                    "purchase_pattern": "no_intervals",
                }

            avg_interval = np.mean(intervals)

            # 구매 패턴 분류
            if avg_interval <= 7:
                pattern = "very_frequent"  # 매우 자주
            elif avg_interval <= 30:
                pattern = "frequent"  # 자주
            elif avg_interval <= 90:
                pattern = "regular"  # 정기적
            else:
                pattern = "infrequent"  # 가끔

            return {
                "avg_days_between_purchases": round(float(avg_interval), 1),
                "purchase_pattern": pattern,
            }

        except Exception as e:
            print(f"구매 빈도 계산 오류: {e}")
            return {"avg_days_between_purchases": 0, "purchase_pattern": "error"}

    def _analyze_seasonal_patterns(self, transactions: pd.DataFrame) -> Dict:
        """계절별 구매 패턴 분석"""
        try:
            if transactions.empty or "transaction_date" not in transactions.columns:
                return {}

            # 날짜 컬럼이 datetime이 아닌 경우 변환
            if not pd.api.types.is_datetime64_any_dtype(
                transactions["transaction_date"]
            ):
                transactions = transactions.copy()
                transactions["transaction_date"] = pd.to_datetime(
                    transactions["transaction_date"]
                )

            # 월별 지출 계산
            transactions["month"] = transactions["transaction_date"].dt.month
            monthly_spending = transactions.groupby("month")["amount"].sum()

            # 계절별 분류
            seasons = {
                "spring": [3, 4, 5],  # 봄
                "summer": [6, 7, 8],  # 여름
                "autumn": [9, 10, 11],  # 가을
                "winter": [12, 1, 2],  # 겨울
            }

            seasonal_spending = {}
            for season, months in seasons.items():
                total = monthly_spending[monthly_spending.index.isin(months)].sum()
                seasonal_spending[season] = float(total) if pd.notna(total) else 0.0

            return seasonal_spending

        except Exception as e:
            print(f"계절별 분석 오류: {e}")
            return {}

    def get_segment_info(self, segment: str) -> Dict:
        """세그먼트 정보 조회"""
        return self.segment_strategies.get(
            segment,
            {
                "name": "알 수 없음",
                "description": "정의되지 않은 세그먼트",
                "strategy": "general",
                "color": "#95a5a6",
            },
        )

    def search_similar_customers(self, customer_id: int, top_n: int = 5) -> List[Dict]:
        """유사한 고객 찾기"""
        try:
            if self.customers is None:
                return []

            target_customer = self.customers[
                self.customers["customer_id"] == customer_id
            ]
            if target_customer.empty:
                return []

            target_segment = target_customer.iloc[0]["segment"]

            # 같은 세그먼트의 다른 고객들 찾기
            similar_customers = self.customers[
                (self.customers["segment"] == target_segment)
                & (self.customers["customer_id"] != customer_id)
            ].head(top_n)

            result = []
            for _, customer in similar_customers.iterrows():
                result.append(
                    {
                        "customer_id": int(customer["customer_id"]),
                        "segment": str(customer["segment"]),
                        "total_spent": float(customer.get("total_spent", 0)),
                        "frequency": int(customer.get("frequency", 0)),
                    }
                )

            return result

        except Exception as e:
            print(f"유사 고객 검색 오류: {e}")
            return []
