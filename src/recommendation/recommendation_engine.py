import pandas as pd
import numpy as np
from typing import List, Dict
from collections import defaultdict


class UltraMinimalRecommendationEngine:
    """Streamlit Cloud용 초경량 추천 엔진 (메모리 < 50MB)"""

    def __init__(self):
        self.products = None
        self.transactions = None
        self.is_fitted = False

        # 초경량 추천 규칙
        self.simple_rules = {
            "우유": ["빵", "쿠키", "시리얼"],
            "milk": ["bread", "cookies", "cereal"],
            "빵": ["버터", "잼", "우유"],
            "bread": ["butter", "jam", "milk"],
            "맥주": ["치킨", "피자", "과자"],
            "beer": ["chicken", "pizza", "snacks"],
            "커피": ["우유", "설탕", "쿠키"],
            "coffee": ["milk", "sugar", "cookies"],
            "치킨": ["콜라", "맥주", "감자"],
            "chicken": ["cola", "beer", "potato"],
        }

    def fit(self, transactions: pd.DataFrame, products: pd.DataFrame):
        """초경량 학습"""
        print("🚀 초경량 추천 엔진 학습...")

        self.transactions = transactions.copy()
        self.products = products.copy()

        print(f"✅ 학습 완료: {len(products)}개 상품")
        self.is_fitted = True

    def get_recommendations(
        self,
        customer_id: str,
        product_query: str = "",
        n_recommendations: int = 6,
        customer_segment: str = "general_value",
    ) -> List[Dict]:
        """초경량 추천 생성"""

        if not product_query:
            return self._get_popular_products(n_recommendations)

        return self._get_simple_recommendations(product_query, n_recommendations)

    def _get_simple_recommendations(
        self, query: str, n_recommendations: int
    ) -> List[Dict]:
        """간단한 규칙 기반 추천"""
        recommendations = []

        # 1. 직접 매칭되는 상품들
        direct_matches = self._find_products_by_query(query)
        recommendations.extend(direct_matches[:2])

        # 2. 규칙 기반 연관 상품들
        rule_based = self._get_rule_based_recommendations(query)
        recommendations.extend(rule_based)

        # 3. 카테고리 기반 추천
        category_based = self._get_category_recommendations(query)
        recommendations.extend(category_based)

        # 중복 제거
        seen_ids = set()
        unique_recommendations = []

        for rec in recommendations:
            if rec["product_id"] not in seen_ids:
                unique_recommendations.append(rec)
                seen_ids.add(rec["product_id"])

                if len(unique_recommendations) >= n_recommendations:
                    break

        return unique_recommendations

    def _find_products_by_query(self, query: str) -> List[Dict]:
        """쿼리로 상품 찾기"""
        query_lower = query.lower()
        matches = []

        for _, product in self.products.iterrows():
            searchable = f"{product['product_name']} {product['category']} {product['brand']}".lower()

            if query_lower in searchable:
                matches.append(
                    {
                        "product_id": product["product_id"],
                        "product_name": product["product_name"],
                        "category": product["category"],
                        "brand": product["brand"],
                        "price": product["price"],
                        "score": 0.9,
                        "reason": f'"{query}" 검색 결과',
                        "similarity_to_query": 0.9,
                    }
                )

        return matches

    def _get_rule_based_recommendations(self, query: str) -> List[Dict]:
        """규칙 기반 추천"""
        query_lower = query.lower()
        related_keywords = self.simple_rules.get(query_lower, [])

        recommendations = []

        for keyword in related_keywords:
            matches = self._find_products_by_query(keyword)
            for match in matches[:1]:  # 각 키워드당 1개만
                match["reason"] = f"{query}와 잘 어울리는 {keyword}"
                match["similarity_to_query"] = 0.8
                recommendations.append(match)

        return recommendations

    def _get_category_recommendations(self, query: str) -> List[Dict]:
        """카테고리 기반 추천"""
        # 쿼리와 관련된 카테고리 찾기
        related_categories = []
        query_lower = query.lower()

        for _, product in self.products.iterrows():
            if query_lower in product["product_name"].lower():
                related_categories.append(product["category"])

        if not related_categories:
            return []

        # 해당 카테고리의 다른 상품들
        main_category = related_categories[0]
        recommendations = []

        for _, product in self.products.iterrows():
            if product["category"] == main_category:
                recommendations.append(
                    {
                        "product_id": product["product_id"],
                        "product_name": product["product_name"],
                        "category": product["category"],
                        "brand": product["brand"],
                        "price": product["price"],
                        "score": 0.7,
                        "reason": f"{main_category} 카테고리 상품",
                        "similarity_to_query": 0.7,
                    }
                )

        return recommendations[:3]

    def _get_popular_products(self, n_recommendations: int) -> List[Dict]:
        """인기 상품 추천"""
        if self.products is None or len(self.products) == 0:
            return []

        # 랜덤으로 인기 상품 선택 (실제로는 판매량 기반이어야 함)
        popular_products = self.products.sample(
            n=min(n_recommendations, len(self.products))
        )

        recommendations = []
        for _, product in popular_products.iterrows():
            recommendations.append(
                {
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "category": product["category"],
                    "brand": product["brand"],
                    "price": product["price"],
                    "score": 0.6,
                    "reason": "인기 상품",
                    "similarity_to_query": 0.5,
                }
            )

        return recommendations

    def search_products(self, query: str, limit: int = 10) -> List[Dict]:
        """상품 검색"""
        return self._find_products_by_query(query)[:limit]
