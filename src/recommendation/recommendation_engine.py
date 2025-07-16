# src/recommendation/recommendation_engine.py
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class UltraMinimalRecommendationEngine:
    def __init__(self):
        self.products = None
        self.vectorizer = None
        self.tfidf_matrix = None

    def fit(self, transactions, products):
        self.products = products

        # 상품명과 서브카테고리를 결합한 텍스트로 TF-IDF 벡터화
        product_text = (
            products["product_name"].fillna("")
            + " "
            + products["sub_category"].fillna("")
            + " "
            + products["category"].fillna("")
        ).str.lower()

        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        self.tfidf_matrix = self.vectorizer.fit_transform(product_text)

    def get_recommendations(
        self,
        customer_id,
        product_query,
        n_recommendations=6,
        customer_segment="general_value",
    ):
        if self.products is None or self.vectorizer is None:
            return []

        try:
            # 쿼리를 벡터화
            query_vector = self.vectorizer.transform([product_query.lower()])

            # 코사인 유사도 계산
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

            # 유사도가 높은 순으로 정렬
            similar_indices = similarities.argsort()[::-1]

            # 상위 n개 추천 상품 선택
            recommendations = []
            count = 0

            for idx in similar_indices:
                if count >= n_recommendations:
                    break

                if similarities[idx] > 0.1:  # 최소 유사도 임계값
                    product = self.products.iloc[idx]

                    recommendations.append(
                        {
                            "product_id": product["product_id"],
                            "product_name": product["product_name"],
                            "category": product["category"],
                            "sub_category": product["sub_category"],
                            "brand": product.get("brand", "Store Brand"),
                            "price": float(product.get("price", 5.0)),
                            "reason": f"{product_query} 관련 추천",
                            "similarity_to_query": float(similarities[idx]),
                        }
                    )
                    count += 1

            # 추천이 부족하면 인기 상품으로 채우기
            if len(recommendations) < n_recommendations:
                popular_products = self.products.sample(
                    n_recommendations - len(recommendations)
                )

                for _, product in popular_products.iterrows():
                    recommendations.append(
                        {
                            "product_id": product["product_id"],
                            "product_name": product["product_name"],
                            "category": product["category"],
                            "sub_category": product["sub_category"],
                            "brand": product.get("brand", "Store Brand"),
                            "price": float(product.get("price", 5.0)),
                            "reason": "인기 상품 추천",
                            "similarity_to_query": 0.5,
                        }
                    )

            return recommendations

        except Exception as e:
            print(f"추천 생성 오류: {e}")
            return []
