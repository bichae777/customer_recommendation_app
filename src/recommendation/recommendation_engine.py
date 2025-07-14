import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional
import gc
import re


class SmartRecommendationEngine:
    """AI 기반 스마트 추천 엔진 - 중복 제거 및 상품명 기반 유사도 매칭"""

    def __init__(self):
        self.transactions = None
        self.products = None

        # 메모리 최적화: 작은 매트릭스만 유지
        self.user_item_matrix = None
        self.top_products = None

        # 상품 정보
        self.product_categories = {}
        self.category_products = defaultdict(list)
        self.brand_products = defaultdict(list)

        # 연관성 매핑
        self.frequent_pairs = {}
        self.category_associations = {}

        # 인기도
        self.popularity_scores = {}
        self.category_popularity = {}

        # AI 기반 연관성 매핑 (상품명 기반)
        self.smart_associations = {}

        self.is_fitted = False

        # 🧠 AI 기반 상품 연관성 규칙 (상품명 키워드 기반)
        self.smart_product_rules = {
            # 음식 + 음료 조합
            "pizza": [
                "cola",
                "coke",
                "pepsi",
                "beer",
                "soda",
                "sprite",
                "salad",
                "garlic bread",
            ],
            "chicken": ["cola", "coke", "beer", "fries", "potato", "coleslaw", "sauce"],
            "burger": [
                "fries",
                "potato",
                "cola",
                "coke",
                "onion",
                "ketchup",
                "mustard",
            ],
            "pasta": ["sauce", "cheese", "parmesan", "wine", "bread", "garlic"],
            "steak": ["wine", "potato", "mushroom", "sauce", "vegetables"],
            "fish": ["lemon", "rice", "vegetables", "wine", "sauce"],
            # 아침식사 조합
            "cereal": ["milk", "banana", "berries", "yogurt", "honey"],
            "bread": ["butter", "jam", "honey", "cheese", "ham", "egg"],
            "coffee": ["milk", "cream", "sugar", "cookie", "donut", "muffin"],
            "tea": ["honey", "lemon", "biscuit", "cookie", "cake"],
            # 간식 조합
            "chips": ["dip", "salsa", "beer", "soda", "cola"],
            "popcorn": ["movie", "soda", "candy", "chocolate"],
            "nuts": ["beer", "wine", "cheese", "crackers"],
            "chocolate": ["milk", "coffee", "cookie", "ice cream"],
            # 요리 재료 조합
            "tomato": ["basil", "mozzarella", "onion", "garlic", "pasta"],
            "onion": ["garlic", "tomato", "potato", "beef", "chicken"],
            "cheese": ["wine", "crackers", "bread", "tomato", "ham"],
            "egg": ["bacon", "bread", "milk", "cheese", "butter"],
            # 음료 조합
            "wine": ["cheese", "crackers", "grapes", "chocolate"],
            "beer": ["chips", "nuts", "pizza", "wings", "pretzel"],
            "milk": ["cereal", "cookie", "chocolate", "cake", "bread"],
            # 디저트 조합
            "ice cream": ["cone", "chocolate", "caramel", "nuts", "berries"],
            "cake": ["candle", "frosting", "berries", "cream", "coffee"],
            "cookie": ["milk", "coffee", "chocolate", "tea"],
        }

        # 카테고리 기반 AI 연관성
        self.category_ai_rules = {
            "DAIRY": ["CEREAL", "COOKIES", "COFFEE", "BREAD"],
            "MEAT": ["VEGETABLES", "POTATO", "SAUCE", "SPICES", "BREAD"],
            "BEVERAGES": ["SNACKS", "CHIPS", "NUTS", "COOKIES"],
            "FROZEN": ["BEVERAGES", "SNACKS", "BREAD"],
            "BAKERY": ["BUTTER", "JAM", "COFFEE", "TEA"],
            "PRODUCE": ["MEAT", "DAIRY", "SAUCE"],
            "SNACKS": ["BEVERAGES", "DAIRY"],
            "CANDY": ["BEVERAGES", "ICE CREAM"],
        }

        # 세그먼트별 전략
        self.segment_strategies = {
            "premium_loyal": {
                "focus": "personalized",
                "price_pref": "high",
                "diversity": 0.9,
            },
            "premium_focused": {
                "focus": "quality",
                "price_pref": "high",
                "diversity": 0.8,
            },
            "excellent_loyal": {
                "focus": "variety",
                "price_pref": "medium",
                "diversity": 1.0,
            },
            "excellent_general": {
                "focus": "balanced",
                "price_pref": "medium",
                "diversity": 0.9,
            },
            "general_value": {
                "focus": "popular",
                "price_pref": "low",
                "diversity": 0.8,
            },
            "at_risk": {"focus": "popular", "price_pref": "low", "diversity": 0.7},
            "new_customer": {
                "focus": "discovery",
                "price_pref": "medium",
                "diversity": 1.0,
            },
        }

    def fit(self, transactions: pd.DataFrame, products: pd.DataFrame):
        """AI 스마트 추천 엔진 학습"""
        print("🧠 AI 스마트 추천 엔진 학습 시작...")

        # 메모리 절약을 위해 작은 샘플만 사용
        if len(transactions) > 30000:
            self.transactions = transactions.sample(n=30000, random_state=42)
            print(f"  🎯 메모리 절약을 위해 {len(self.transactions):,}건으로 제한")
        else:
            self.transactions = transactions.copy()

        self.products = products.copy()
        print(f"  📦 전체 상품: {len(self.products):,}개")

        # 1. 기본 매핑 구축
        self._build_category_brand_mapping()

        # 2. AI 기반 스마트 연관성 구축
        self._build_smart_associations()

        # 3. 간단한 협업 필터링
        self._build_simple_collaborative()

        # 4. 인기도 계산
        self._calculate_popularity()

        # 메모리 정리
        gc.collect()

        self.is_fitted = True
        print("✅ AI 스마트 추천 엔진 학습 완료!")

    def _build_category_brand_mapping(self):
        """카테고리 및 브랜드 매핑 구축"""
        print("  📝 카테고리 및 브랜드 매핑...")

        for _, product in self.products.iterrows():
            product_id = product["product_id"]
            category = product["category"]
            brand = product["brand"]

            self.product_categories[product_id] = category
            self.category_products[category].append(product_id)
            self.brand_products[brand].append(product_id)

        print(
            f"    ✅ {len(self.category_products)}개 카테고리, {len(self.brand_products)}개 브랜드"
        )

    def _build_smart_associations(self):
        """🧠 AI 기반 스마트 연관성 구축 (초고속 버전)"""
        print("  🧠 AI 기반 상품 연관성 분석 (초고속 모드)...")

        # 🚀 극한 최적화: 상위 500개 상품만 분석
        if hasattr(self, "popularity_scores") and self.popularity_scores:
            # 인기도 기준 상위 500개
            top_products_by_popularity = sorted(
                self.popularity_scores.items(), key=lambda x: x[1], reverse=True
            )[:500]
            top_product_ids = [pid for pid, _ in top_products_by_popularity]
        else:
            # 랜덤 500개
            top_product_ids = (
                self.products["product_id"]
                .sample(n=min(500, len(self.products)), random_state=42)
                .tolist()
            )

        target_products = self.products[
            self.products["product_id"].isin(top_product_ids)
        ]

        print(
            f"    📊 분석 대상: {len(target_products):,}개 상품 (전체 {len(self.products):,}개 중)"
        )

        # 미리 카테고리별 상품 인덱스 구축 (성능 최적화)
        category_index = {}
        for category, product_ids in self.category_products.items():
            category_index[category.lower()] = product_ids[:10]  # 카테고리당 10개만

        # 상품명 기반 연관성 매핑 (병렬 처리 느낌으로)
        processed_count = 0
        for _, product in target_products.iterrows():
            product_id = product["product_id"]
            product_name = product["product_name"].lower()
            category = product["category"]

            # 간단한 키워드 매칭만 (복잡한 분석 제거)
            related_products = self._find_simple_related_products(
                product_name, category, product_id, category_index
            )
            if related_products:
                self.smart_associations[product_id] = related_products

            processed_count += 1
            if processed_count % 100 == 0:
                print(f"    📈 진행률: {processed_count:,}/{len(target_products):,}")

        print(f"    ✅ AI 연관성: {len(self.smart_associations)}개 상품")

    def _find_simple_related_products(
        self, product_name: str, category: str, exclude_id: str, category_index: dict
    ) -> List[Dict]:
        """간단한 연관 상품 찾기 (초고속 버전)"""
        related_products = []

        # 1. 핵심 키워드만 빠르게 매칭
        core_keywords = [
            "milk",
            "bread",
            "cheese",
            "beer",
            "coffee",
            "chicken",
            "pizza",
        ]
        found_keyword = None
        for keyword in core_keywords:
            if keyword in product_name:
                found_keyword = keyword
                break

        if found_keyword and found_keyword in self.smart_product_rules:
            # 연관 키워드 1개만 빠르게 처리
            related_keyword = self.smart_product_rules[found_keyword][0]  # 첫 번째만

            # 카테고리 인덱스에서 빠르게 검색
            for cat_name, product_ids in category_index.items():
                if related_keyword.lower() in cat_name:
                    for pid in product_ids[:2]:  # 2개만
                        if pid != exclude_id:
                            product_info = self.products[
                                self.products["product_id"] == pid
                            ]
                            if not product_info.empty:
                                product_info = product_info.iloc[0]
                                related_products.append(
                                    {
                                        "product_id": pid,
                                        "product_name": product_info["product_name"],
                                        "category": product_info["category"],
                                        "brand": product_info["brand"],
                                        "price": product_info.get("price", 5.0),
                                        "score": 0.8,
                                        "reason": f"AI 추천: {found_keyword}와 어울림",
                                        "similarity_to_query": 0.9,
                                    }
                                )
                                if len(related_products) >= 2:  # 2개면 충분
                                    return related_products
                    break

        return related_products

    def _find_smart_related_products(
        self, product_name: str, category: str, exclude_id: str
    ) -> List[Dict]:
        """상품명과 카테고리 기반으로 AI가 연관 상품 찾기 (최적화)"""
        related_products = []

        # 🚀 성능 최적화: 키워드 매칭을 더 효율적으로
        found_keywords = []
        for keyword in self.smart_product_rules.keys():
            if keyword in product_name:
                found_keywords.append(keyword)
                if len(found_keywords) >= 2:  # 최대 2개 키워드만
                    break

        # 1. 상품명 키워드 기반 연관성 (제한적으로)
        for keyword in found_keywords:
            related_keywords = self.smart_product_rules[keyword][:2]  # 상위 2개만
            for related_keyword in related_keywords:
                matching_products = self._find_products_by_keyword_fast(
                    related_keyword, exclude_id
                )
                related_products.extend(matching_products[:1])  # 각 키워드당 1개만
                if len(related_products) >= 3:  # 총 3개면 충분
                    break
            if len(related_products) >= 3:
                break

        # 2. 카테고리 기반 AI 연관성 (빠른 방식)
        if len(related_products) < 3:
            for main_cat, related_cats in self.category_ai_rules.items():
                if main_cat.lower() in category.lower():
                    for related_cat in related_cats[:1]:  # 상위 1개 카테고리만
                        cat_products = self._find_products_by_category_fast(
                            related_cat, exclude_id
                        )
                        related_products.extend(cat_products[:1])  # 각 카테고리당 1개만
                        if len(related_products) >= 3:
                            break
                    break

        return related_products[:3]  # 최대 3개만 반환

    def _find_products_by_keyword(self, keyword: str, exclude_id: str) -> List[Dict]:
        """키워드로 상품 찾기"""
        matching_products = []

        for _, product in self.products.iterrows():
            if product["product_id"] == exclude_id:
                continue

            searchable_text = f"{product['product_name']} {product['category']} {product['brand']}".lower()

            if keyword.lower() in searchable_text:
                popularity = self.popularity_scores.get(product["product_id"], 0.1)

                matching_products.append(
                    {
                        "product_id": product["product_id"],
                        "product_name": product["product_name"],
                        "category": product["category"],
                        "brand": product["brand"],
                        "price": product.get("price", 5.0),
                        "score": popularity * 0.8,
                        "reason": f"AI 추천: {keyword}와 잘 어울림",
                        "similarity_to_query": 0.9,
                    }
                )

        # 인기도순 정렬
        matching_products.sort(key=lambda x: x["score"], reverse=True)

    def _find_products_by_keyword_fast(
        self, keyword: str, exclude_id: str
    ) -> List[Dict]:
        """키워드로 상품 찾기 (고속 버전)"""
        matching_products = []

        # 🚀 성능 최적화: 인기 상품 중에서만 검색
        search_pool = (
            self.top_products[:1000]
            if hasattr(self, "top_products") and self.top_products
            else []
        )
        if not search_pool:
            search_pool = self.products["product_id"].tolist()[:1000]  # 처음 1000개만

        count = 0
        for product_id in search_pool:
            if product_id == exclude_id or count >= 5:  # 최대 5개만 찾기
                continue

            product_info = self.products[self.products["product_id"] == product_id]
            if not product_info.empty:
                product_info = product_info.iloc[0]
                searchable_text = f"{product_info['product_name']} {product_info['category']} {product_info['brand']}".lower()

                if keyword.lower() in searchable_text:
                    popularity = self.popularity_scores.get(product_id, 0.1)

                    matching_products.append(
                        {
                            "product_id": product_id,
                            "product_name": product_info["product_name"],
                            "category": product_info["category"],
                            "brand": product_info["brand"],
                            "price": product_info.get("price", 5.0),
                            "score": popularity * 0.8,
                            "reason": f"AI 추천: {keyword}와 잘 어울림",
                            "similarity_to_query": 0.9,
                        }
                    )
                    count += 1

        return matching_products

    def _find_products_by_category_fast(
        self, category_keyword: str, exclude_id: str
    ) -> List[Dict]:
        """카테고리 키워드로 상품 찾기 (고속 버전)"""
        matching_products = []

        # 🚀 성능 최적화: 카테고리별 상품 수 제한
        for cat_name, product_ids in self.category_products.items():
            if category_keyword.lower() in cat_name.lower():
                for product_id in product_ids[:3]:  # 카테고리당 3개만 확인
                    if product_id == exclude_id:
                        continue

                    product_info = self.products[
                        self.products["product_id"] == product_id
                    ]
                    if not product_info.empty:
                        product_info = product_info.iloc[0]
                        popularity = self.popularity_scores.get(product_id, 0.1)

                        matching_products.append(
                            {
                                "product_id": product_id,
                                "product_name": product_info["product_name"],
                                "category": product_info["category"],
                                "brand": product_info["brand"],
                                "price": product_info.get("price", 5.0),
                                "score": popularity * 0.7,
                                "reason": f"AI 추천: {cat_name} 카테고리",
                                "similarity_to_query": 0.8,
                            }
                        )

                        if len(matching_products) >= 3:  # 총 3개면 충분
                            break
                break  # 첫 번째 매칭 카테고리만 사용

        return matching_products

    def _find_products_by_category(
        self, category_keyword: str, exclude_id: str
    ) -> List[Dict]:
        """카테고리 키워드로 상품 찾기"""
        matching_products = []

        for cat_name, product_ids in self.category_products.items():
            if category_keyword.lower() in cat_name.lower():
                for product_id in product_ids:
                    if product_id == exclude_id:
                        continue

                    product_info = self.products[
                        self.products["product_id"] == product_id
                    ]
                    if not product_info.empty:
                        product_info = product_info.iloc[0]
                        popularity = self.popularity_scores.get(product_id, 0.1)

                        matching_products.append(
                            {
                                "product_id": product_id,
                                "product_name": product_info["product_name"],
                                "category": product_info["category"],
                                "brand": product_info["brand"],
                                "price": product_info.get("price", 5.0),
                                "score": popularity * 0.7,
                                "reason": f"AI 추천: {cat_name} 카테고리",
                                "similarity_to_query": 0.8,
                            }
                        )

        # 인기도순 정렬
        matching_products.sort(key=lambda x: x["score"], reverse=True)
        return matching_products

    def _build_simple_collaborative(self):
        """간단한 협업 필터링"""
        print("  🤝 간단한 협업 필터링...")

        # 상위 활성 고객들만 사용
        customer_activity = self.transactions["customer_id"].value_counts()
        top_customers = customer_activity.head(500).index

        # 상위 인기 상품들만 사용
        product_activity = self.transactions["product_id"].value_counts()
        self.top_products = product_activity.head(1000).index.tolist()

        # 마켓 바스켓 분석 (간단하게)
        self._analyze_market_basket()

        print(
            f"    ✅ 상위 고객 {len(top_customers)}명, 상위 상품 {len(self.top_products)}개"
        )

    def _analyze_market_basket(self):
        """마켓 바스켓 분석"""
        baskets = (
            self.transactions.groupby("basket_id")["product_id"]
            .apply(list)
            .reset_index()
        )

        pair_counts = defaultdict(int)
        for basket in baskets["product_id"].head(3000):  # 처리량 제한
            if len(basket) > 1 and len(basket) < 10:
                for i in range(len(basket)):
                    for j in range(i + 1, len(basket)):
                        pair = tuple(sorted([basket[i], basket[j]]))
                        pair_counts[pair] += 1

        # 최소 지지도 적용
        min_support = max(1, len(baskets) * 0.01)
        self.frequent_pairs = {
            pair: count for pair, count in pair_counts.items() if count >= min_support
        }

    def _calculate_popularity(self):
        """인기도 계산"""
        print("  📊 인기도 계산...")

        product_counts = self.transactions["product_id"].value_counts()
        max_count = product_counts.max()
        self.popularity_scores = (product_counts / max_count).to_dict()

        # 카테고리별 인기도
        category_counts = defaultdict(int)
        for product_id, count in product_counts.items():
            category = self.product_categories.get(product_id, "UNKNOWN")
            category_counts[category] += count

        max_cat_count = max(category_counts.values())
        self.category_popularity = {
            k: v / max_cat_count for k, v in category_counts.items()
        }

    def get_recommendations(
        self,
        customer_id: str,
        product_query: str = "",
        n_recommendations: int = 10,
        customer_segment: str = "general_value",
    ) -> List[Dict]:
        """스마트 추천 생성 (중복 제거 강화)"""
        if not self.is_fitted:
            raise ValueError("모델이 학습되지 않았습니다.")

        if product_query:
            return self._get_smart_query_recommendations(
                product_query, customer_id, customer_segment, n_recommendations
            )
        else:
            return self._get_personalized_recommendations(
                customer_id, customer_segment, n_recommendations
            )

    def _get_smart_query_recommendations(
        self, query: str, customer_id: str, segment: str, n_recommendations: int
    ) -> List[Dict]:
        """🧠 AI 스마트 검색어 기반 추천 (중복 제거 강화)"""
        query_lower = query.lower()
        strategy = self.segment_strategies.get(
            segment, self.segment_strategies["general_value"]
        )

        all_recommendations = []
        seen_products = set()  # 중복 제거를 위한 세트

        # 1. 직접 매칭 상품들 찾기
        direct_matches = self._find_direct_matches(query_lower)

        # 2. 각 매칭 상품에 대한 AI 스마트 연관 상품들
        for matched_product in direct_matches[:2]:  # 상위 2개만 사용
            if matched_product not in seen_products:
                # 매칭된 상품 자체 추가
                product_info = self.products[
                    self.products["product_id"] == matched_product
                ]
                if not product_info.empty:
                    product_info = product_info.iloc[0]
                    popularity = self.popularity_scores.get(matched_product, 0.1)

                    all_recommendations.append(
                        {
                            "product_id": matched_product,
                            "product_name": product_info["product_name"],
                            "category": product_info["category"],
                            "brand": product_info["brand"],
                            "price": product_info.get("price", 5.0),
                            "score": popularity + 0.5,  # 직접 매칭에 가산점
                            "reason": f'"{query}" 검색 결과',
                            "similarity_to_query": 1.0,
                        }
                    )
                    seen_products.add(matched_product)

                # AI 기반 연관 상품들 추가
                smart_related = self._get_ai_smart_related_products(
                    matched_product, query_lower
                )
                for rec in smart_related:
                    if rec["product_id"] not in seen_products:
                        all_recommendations.append(rec)
                        seen_products.add(rec["product_id"])

        # 3. 쿼리 키워드 기반 직접 AI 추천
        ai_direct_recommendations = self._get_ai_direct_recommendations(query_lower)
        for rec in ai_direct_recommendations:
            if rec["product_id"] not in seen_products:
                all_recommendations.append(rec)
                seen_products.add(rec["product_id"])

        # 4. 마켓 바스켓 기반 추천 (상위 매칭 상품들에 대해)
        basket_recommendations = self._get_basket_recommendations(direct_matches[:1])
        for rec in basket_recommendations:
            if rec["product_id"] not in seen_products:
                all_recommendations.append(rec)
                seen_products.add(rec["product_id"])

        # 5. 인기 상품으로 빈 자리 채우기
        if len(all_recommendations) < n_recommendations:
            popular_recommendations = self._get_popular_recommendations(
                n_recommendations - len(all_recommendations), exclude=seen_products
            )
            all_recommendations.extend(popular_recommendations)

        # 6. 다양성 확보 및 정렬
        diverse_recommendations = self._ensure_smart_diversity(
            all_recommendations, strategy["diversity"]
        )

        return diverse_recommendations[:n_recommendations]

    def _find_direct_matches(self, query: str) -> List[str]:
        """직접 매칭되는 상품들 찾기 (안전 버전)"""
        matched_products = []

        try:
            if self.products is None or len(self.products) == 0:
                print("    ⚠️ 상품 데이터가 없습니다.")
                return matched_products

            for _, product in self.products.iterrows():
                try:
                    searchable_text = f"{product.get('product_name', '')} {product.get('category', '')} {product.get('brand', '')}".lower()
                    if query in searchable_text:
                        matched_products.append(product.get("product_id", ""))
                        if len(matched_products) >= 10:  # 너무 많으면 제한
                            break
                except Exception as e:
                    continue  # 개별 상품 오류는 무시

        except Exception as e:
            print(f"    ⚠️ 직접 매칭 검색 오류: {e}")

        return matched_products

    def _get_ai_smart_related_products(self, product_id: str, query: str) -> List[Dict]:
        """AI가 미리 계산한 스마트 연관 상품들 가져오기 (안전 버전)"""
        try:
            if self.smart_associations and product_id in self.smart_associations:
                associations = self.smart_associations[product_id]
                if associations and isinstance(associations, list):
                    return associations
            return []
        except Exception as e:
            print(f"    ⚠️ AI 연관성 조회 오류: {e}")
            return []

    def _get_ai_direct_recommendations(self, query: str) -> List[Dict]:
        """🧠 AI가 쿼리를 보고 직접 연관 상품 추천"""
        recommendations = []

        # 쿼리에서 연관 키워드들 찾기
        related_keywords = []
        for keyword, associations in self.smart_product_rules.items():
            if keyword in query:
                related_keywords.extend(associations)

        # 연관 키워드들로 상품 찾기
        for related_keyword in related_keywords[:5]:  # 상위 5개 키워드만
            matching_products = self._find_products_by_keyword(
                related_keyword, exclude_id=""
            )
            recommendations.extend(matching_products[:1])  # 각 키워드당 1개만

        return recommendations

    def _get_basket_recommendations(self, product_ids: List[str]) -> List[Dict]:
        """마켓 바스켓 기반 추천"""
        recommendations = []

        for product_id in product_ids:
            for (item1, item2), count in self.frequent_pairs.items():
                related_id = None
                if product_id == item1:
                    related_id = item2
                elif product_id == item2:
                    related_id = item1

                if related_id:
                    product_info = self.products[
                        self.products["product_id"] == related_id
                    ]
                    if not product_info.empty:
                        product_info = product_info.iloc[0]
                        confidence = count / max(
                            self.popularity_scores.get(product_id, 1), 1
                        )

                        recommendations.append(
                            {
                                "product_id": related_id,
                                "product_name": product_info["product_name"],
                                "category": product_info["category"],
                                "brand": product_info["brand"],
                                "price": product_info.get("price", 5.0),
                                "score": confidence * 0.8,
                                "reason": "함께 구매하는 상품",
                                "similarity_to_query": 0.8,
                            }
                        )

        return recommendations

    def _ensure_smart_diversity(
        self, recommendations: List[Dict], diversity_factor: float
    ) -> List[Dict]:
        """🧠 스마트 다양성 확보 (카테고리, 브랜드, 가격대 분산)"""
        if not recommendations:
            return []

        # 점수 순으로 먼저 정렬
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        if diversity_factor < 0.6:
            # 다양성 낮으면 점수 순으로만
            return recommendations

        # 다양성 높으면 카테고리/브랜드별로 분산
        seen_categories = set()
        seen_brands = set()
        seen_products = set()
        diverse_recommendations = []

        # 1차: 카테고리 다양성 우선
        for rec in recommendations:
            category = rec["category"]
            brand = rec["brand"]
            product_id = rec["product_id"]

            if product_id not in seen_products:
                if (
                    category not in seen_categories or len(diverse_recommendations) < 3
                ):  # 처음 3개는 무조건 추가
                    diverse_recommendations.append(rec)
                    seen_categories.add(category)
                    seen_brands.add(brand)
                    seen_products.add(product_id)

        # 2차: 남은 자리는 브랜드 다양성으로
        for rec in recommendations:
            brand = rec["brand"]
            product_id = rec["product_id"]

            if (
                product_id not in seen_products and len(diverse_recommendations) < 8
            ):  # 최대 8개까지는 브랜드 다양성
                if brand not in seen_brands:
                    diverse_recommendations.append(rec)
                    seen_brands.add(brand)
                    seen_products.add(product_id)

        # 3차: 나머지 자리는 점수 순으로
        for rec in recommendations:
            product_id = rec["product_id"]
            if product_id not in seen_products and len(diverse_recommendations) < 10:
                diverse_recommendations.append(rec)
                seen_products.add(product_id)

        return diverse_recommendations

    def _get_personalized_recommendations(
        self, customer_id: str, segment: str, n_recommendations: int
    ) -> List[Dict]:
        """개인화 추천"""
        return self._get_popular_recommendations(n_recommendations)

    def _get_popular_recommendations(
        self, n_recommendations: int, exclude: set = None
    ) -> List[Dict]:
        """인기 상품 추천 (안전 버전)"""
        if exclude is None:
            exclude = set()

        recommendations = []

        try:
            if not self.popularity_scores:
                print("    ⚠️ 인기도 점수가 없습니다.")
                return recommendations

            popular_products = sorted(
                self.popularity_scores.items(), key=lambda x: x[1], reverse=True
            )

            for product_id, popularity in popular_products:
                if (
                    product_id not in exclude
                    and len(recommendations) < n_recommendations
                ):
                    try:
                        product_info = self.products[
                            self.products["product_id"] == product_id
                        ]
                        if not product_info.empty:
                            product_info = product_info.iloc[0]

                            recommendations.append(
                                {
                                    "product_id": product_id,
                                    "product_name": product_info.get(
                                        "product_name", f"Product {product_id}"
                                    ),
                                    "category": product_info.get("category", "Unknown"),
                                    "brand": product_info.get("brand", "Unknown"),
                                    "price": product_info.get("price", 5.0),
                                    "score": popularity,
                                    "reason": "인기 상품",
                                    "similarity_to_query": 0,
                                }
                            )
                    except Exception as e:
                        continue  # 개별 상품 오류는 무시

        except Exception as e:
            print(f"    ⚠️ 인기 상품 추천 오류: {e}")

        return recommendations

    def search_products(self, query: str, limit: int = 20) -> List[Dict]:
        """상품 검색 (안전 버전)"""
        if not query.strip():
            return []

        query_lower = query.lower()
        matched_products = []

        try:
            if self.products is None or len(self.products) == 0:
                return matched_products

            for _, product in self.products.iterrows():
                try:
                    searchable_text = f"{product.get('product_name', '')} {product.get('category', '')} {product.get('brand', '')}".lower()

                    if query_lower in searchable_text:
                        matched_products.append(
                            {
                                "product_id": product.get("product_id", ""),
                                "product_name": product.get(
                                    "product_name", "Unknown Product"
                                ),
                                "category": product.get("category", "Unknown"),
                                "brand": product.get("brand", "Unknown"),
                                "price": product.get("price", 5.0),
                                "description": product.get("description", ""),
                            }
                        )

                        if len(matched_products) >= limit:
                            break
                except Exception as e:
                    continue  # 개별 상품 오류는 무시

        except Exception as e:
            print(f"    ⚠️ 상품 검색 오류: {e}")

        return matched_products
