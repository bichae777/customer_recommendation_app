import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict


class DataGenerator:
    """샘플 데이터 생성기"""

    def __init__(self, random_seed: int = 42):
        """초기화"""
        np.random.seed(random_seed)
        random.seed(random_seed)

        # 상품 카테고리 정의
        self.categories = [
            "ELECTRONICS",
            "CLOTHING",
            "FOOD & BEVERAGE",
            "HOME & GARDEN",
            "BOOKS",
            "SPORTS",
            "BEAUTY",
            "TOYS",
            "AUTOMOTIVE",
            "HEALTH",
            "GROCERY",
            "MEAT",
            "PRODUCE",
            "DAIRY",
            "BEVERAGES",
            "SNACKS",
            "FROZEN",
            "BAKERY",
            "PERSONAL CARE",
            "CLEANING",
        ]

        # 상품명 템플릿
        self.product_templates = {
            "ELECTRONICS": [
                "스마트폰",
                "TV",
                "노트북",
                "태블릿",
                "이어폰",
                "스피커",
                "카메라",
            ],
            "CLOTHING": [
                "티셔츠",
                "청바지",
                "운동화",
                "재킷",
                "원피스",
                "바지",
                "셔츠",
            ],
            "FOOD & BEVERAGE": ["커피", "차", "주스", "물", "우유", "맥주", "와인"],
            "GROCERY": ["쌀", "면", "빵", "시리얼", "과자", "라면", "통조림"],
            "MEAT": ["소고기", "돼지고기", "닭고기", "생선", "새우", "게", "오징어"],
            "PRODUCE": ["사과", "바나나", "오렌지", "포도", "딸기", "배", "키위"],
            "DAIRY": ["우유", "요거트", "치즈", "버터", "크림", "아이스크림"],
            "BEVERAGES": [
                "콜라",
                "사이다",
                "오렌지주스",
                "커피",
                "차",
                "물",
                "에너지드링크",
            ],
            "PERSONAL CARE": ["샴푸", "비누", "치약", "로션", "향수", "크림"],
            "HOME & GARDEN": ["청소기", "세탁기", "냉장고", "화분", "가구", "조명"],
        }

        # 세그먼트 정의
        self.segments = [
            "premium_loyal",
            "premium_focused",
            "excellent_loyal",
            "excellent_general",
            "general_value",
            "at_risk",
            "new_customer",
        ]

        # 세그먼트별 특성
        self.segment_characteristics = {
            "premium_loyal": {
                "spending_range": (100, 500),
                "frequency_range": (20, 50),
                "rfm_range": (10, 15),
            },
            "premium_focused": {
                "spending_range": (80, 300),
                "frequency_range": (5, 20),
                "rfm_range": (8, 12),
            },
            "excellent_loyal": {
                "spending_range": (50, 200),
                "frequency_range": (15, 40),
                "rfm_range": (8, 12),
            },
            "excellent_general": {
                "spending_range": (50, 150),
                "frequency_range": (10, 25),
                "rfm_range": (6, 10),
            },
            "general_value": {
                "spending_range": (20, 100),
                "frequency_range": (5, 20),
                "rfm_range": (4, 8),
            },
            "at_risk": {
                "spending_range": (30, 120),
                "frequency_range": (2, 10),
                "rfm_range": (2, 6),
            },
            "new_customer": {
                "spending_range": (10, 80),
                "frequency_range": (1, 8),
                "rfm_range": (1, 5),
            },
        }

    def generate_customers(self, n_customers: int = 100) -> pd.DataFrame:
        """고객 데이터 생성"""
        customers = []

        for i in range(1, n_customers + 1):
            # 세그먼트 할당
            segment = np.random.choice(
                self.segments, p=[0.05, 0.10, 0.15, 0.20, 0.25, 0.15, 0.10]
            )
            char = self.segment_characteristics[segment]

            # 고객 특성 생성
            total_spent = np.random.uniform(*char["spending_range"])
            frequency = np.random.randint(*char["frequency_range"])
            rfm_score = np.random.uniform(*char["rfm_range"])

            # 가입일 생성
            days_ago = np.random.randint(30, 730)  # 1달~2년 전
            join_date = datetime.now() - timedelta(days=days_ago)

            customer = {
                "customer_id": i,
                "segment": segment,
                "total_spent": round(total_spent, 2),
                "frequency": frequency,
                "rfm_score": round(rfm_score, 1),
                "join_date": join_date,
                "age": np.random.randint(18, 70),
                "gender": np.random.choice(["M", "F"]),
                "city": np.random.choice(
                    ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]
                ),
            }

            customers.append(customer)

        return pd.DataFrame(customers)

    def generate_products(self, n_products: int = 500) -> pd.DataFrame:
        """상품 데이터 생성"""
        products = []

        for i in range(1, n_products + 1):
            # 카테고리 선택
            category = np.random.choice(self.categories)

            # 상품명 생성
            if category in self.product_templates:
                base_name = np.random.choice(self.product_templates[category])
                product_name = f"{base_name} {np.random.choice(['프리미엄', '스탠다드', '에코', '럭셔리', '베이직'])}"
            else:
                product_name = f"Product {i}"

            # 가격 설정 (카테고리별 차등)
            if category == "ELECTRONICS":
                price = np.random.uniform(50, 500)
            elif category in ["MEAT", "PRODUCE", "DAIRY"]:
                price = np.random.uniform(5, 50)
            elif category == "GROCERY":
                price = np.random.uniform(2, 30)
            else:
                price = np.random.uniform(10, 100)

            # 브랜드 생성
            brands = ["Brand A", "Brand B", "Brand C", "Brand D", "Brand E"]
            brand = np.random.choice(brands)

            product = {
                "product_id": i,
                "product_name": product_name,
                "category": category,
                "price": round(price, 2),
                "brand": brand,
                "description": f"{product_name} - {category} 카테고리의 {brand} 제품",
                "rating": round(np.random.uniform(3.0, 5.0), 1),
            }

            products.append(product)

        return pd.DataFrame(products)

    def generate_transactions(
        self, n_customers: int = 100, n_transactions: int = 5000
    ) -> pd.DataFrame:
        """거래 데이터 생성"""
        transactions = []

        # 고객과 상품 ID 범위
        customer_ids = list(range(1, n_customers + 1))
        product_ids = list(range(1, 501))  # 500개 상품 가정

        for _ in range(n_transactions):
            customer_id = np.random.choice(customer_ids)
            product_id = np.random.choice(product_ids)

            # 거래 날짜 (최근 1년)
            days_ago = np.random.randint(1, 365)
            transaction_date = datetime.now() - timedelta(days=days_ago)

            # 가격 설정 (상품에 따라)
            base_price = self._get_product_base_price(product_id)
            amount = base_price * np.random.uniform(0.8, 1.2)  # ±20% 변동

            # 수량
            quantity = np.random.choice(
                [1, 1, 1, 2, 2, 3], p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05]
            )

            transaction = {
                "transaction_id": len(transactions) + 1,
                "customer_id": customer_id,
                "product_id": product_id,
                "transaction_date": transaction_date,
                "quantity": quantity,
                "amount": round(amount * quantity, 2),
                "category": self._get_product_category(product_id),
                "channel": np.random.choice(["online", "offline"], p=[0.6, 0.4]),
            }

            transactions.append(transaction)

        return pd.DataFrame(transactions)

    def _get_product_base_price(self, product_id: int) -> float:
        """상품 기본 가격 추정"""
        # 간단한 해시 기반 가격 생성
        np.random.seed(product_id)
        price = np.random.uniform(5, 100)
        np.random.seed()  # 시드 리셋
        return price

    def _get_product_category(self, product_id: int) -> str:
        """상품 카테고리 추정"""
        # 간단한 해시 기반 카테고리 할당
        return self.categories[product_id % len(self.categories)]

    def generate_sample_data_files(self, output_dir: str = "data/raw"):
        """샘플 데이터 파일 생성"""
        import os

        os.makedirs(output_dir, exist_ok=True)

        # 데이터 생성
        customers = self.generate_customers(100)
        products = self.generate_products(500)
        transactions = self.generate_transactions(100, 5000)

        # 파일 저장
        customers.to_csv(f"{output_dir}/customers.csv", index=False, encoding="utf-8")
        products.to_csv(f"{output_dir}/products.csv", index=False, encoding="utf-8")
        transactions.to_csv(
            f"{output_dir}/transactions.csv", index=False, encoding="utf-8"
        )

        print(f"✅ 샘플 데이터 생성 완료:")
        print(f"   - 고객: {len(customers)}명")
        print(f"   - 상품: {len(products)}개")
        print(f"   - 거래: {len(transactions)}건")
        print(f"   - 저장 위치: {output_dir}/")

        return customers, products, transactions
