import pandas as pd
import numpy as np
from typing import Tuple, Dict
import os


class UltraMinimalDataLoader:
    """Streamlit Cloud 메모리 제한용 초경량 데이터 로더"""

    def __init__(self):
        self.customers = None
        self.transactions = None
        self.products = None

    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """초경량 데이터 로딩 (메모리 < 100MB)"""
        print("🔥 초경량 모드: 메모리 최적화 데이터 로딩...")

        try:
            # 1. 극소량 거래 데이터만 로딩 (1000건만)
            self.transactions = self._load_minimal_transactions()

            # 2. 최소 상품 데이터 (100개만)
            self.products = self._load_minimal_products()

            # 3. 기본 고객 데이터 생성
            self.customers = self._create_minimal_customers()

            print(
                f"✅ 로딩 완료: 고객 {len(self.customers)}명, 상품 {len(self.products)}개, 거래 {len(self.transactions)}건"
            )

            return self.customers, self.transactions, self.products

        except Exception as e:
            print(f"⚠️ 실제 데이터 로딩 실패: {e}")
            return self._create_dummy_data()

    def _load_minimal_transactions(self) -> pd.DataFrame:
        """최소 거래 데이터 로딩"""
        try:
            # 실제 파일이 있으면 극소량만 로딩
            file_path = "data/raw/transaction_data.csv"
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, nrows=1000)  # 1000행만
                df = df[
                    ["household_key", "BASKET_ID", "PRODUCT_ID", "SALES_VALUE", "DAY"]
                ].copy()
                df.columns = ["customer_id", "basket_id", "product_id", "price", "day"]
                return df
            else:
                return self._create_dummy_transactions()
        except:
            return self._create_dummy_transactions()

    def _load_minimal_products(self) -> pd.DataFrame:
        """최소 상품 데이터 로딩"""
        try:
            # 실제 파일이 있으면 극소량만 로딩
            file_path = "data/raw/product.csv"
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, nrows=100)  # 100행만
                df = df[["PRODUCT_ID", "COMMODITY_DESC", "BRAND"]].copy()
                df.columns = ["product_id", "category", "brand"]
                df["product_name"] = df["brand"] + " " + df["category"]
                df["price"] = np.random.uniform(1, 20, len(df))
                return df
            else:
                return self._create_dummy_products()
        except:
            return self._create_dummy_products()

    def _create_minimal_customers(self) -> pd.DataFrame:
        """최소 고객 데이터 생성"""
        customer_ids = self.transactions["customer_id"].unique()[:50]  # 50명만

        customers = []
        for customer_id in customer_ids:
            customer_transactions = self.transactions[
                self.transactions["customer_id"] == customer_id
            ]

            customers.append(
                {
                    "customer_id": customer_id,
                    "total_spent": customer_transactions["price"].sum(),
                    "purchase_frequency": len(customer_transactions),
                    "segment": np.random.choice(
                        ["premium_loyal", "general_value", "at_risk"], p=[0.1, 0.6, 0.3]
                    ),
                }
            )

        return pd.DataFrame(customers)

    def _create_dummy_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """더미 데이터 생성 (초경량)"""
        print("🎭 더미 데이터 생성 (초경량 모드)")

        # 더미 고객 (20명)
        customers = pd.DataFrame(
            {
                "customer_id": range(1, 21),
                "total_spent": np.random.uniform(50, 500, 20),
                "purchase_frequency": np.random.randint(1, 20, 20),
                "segment": np.random.choice(
                    ["premium_loyal", "general_value", "at_risk"], 20
                ),
            }
        )

        # 더미 상품 (50개)
        categories = ["DAIRY", "BREAD", "BEVERAGES", "MEAT", "SNACKS"]
        brands = ["Brand A", "Brand B", "Brand C"]

        products = []
        for i in range(50):
            category = np.random.choice(categories)
            brand = np.random.choice(brands)
            products.append(
                {
                    "product_id": i + 1,
                    "product_name": f"{brand} {category} Product {i+1}",
                    "category": category,
                    "brand": brand,
                    "price": np.random.uniform(2, 15),
                }
            )

        products = pd.DataFrame(products)

        # 더미 거래 (200건)
        transactions = []
        for i in range(200):
            transactions.append(
                {
                    "customer_id": np.random.randint(1, 21),
                    "product_id": np.random.randint(1, 51),
                    "basket_id": np.random.randint(1000, 9999),
                    "price": np.random.uniform(2, 15),
                    "day": np.random.randint(1, 365),
                }
            )

        transactions = pd.DataFrame(transactions)

        return customers, transactions, products

    def _create_dummy_transactions(self) -> pd.DataFrame:
        """더미 거래 데이터"""
        return pd.DataFrame(
            {
                "customer_id": np.random.randint(1, 21, 200),
                "product_id": np.random.randint(1, 51, 200),
                "basket_id": np.random.randint(1000, 9999, 200),
                "price": np.random.uniform(2, 15, 200),
                "day": np.random.randint(1, 365, 200),
            }
        )

    def _create_dummy_products(self) -> pd.DataFrame:
        """더미 상품 데이터"""
        categories = ["DAIRY", "BREAD", "BEVERAGES", "MEAT", "SNACKS"]

        return pd.DataFrame(
            {
                "product_id": range(1, 51),
                "product_name": [f"Product {i}" for i in range(1, 51)],
                "category": np.random.choice(categories, 50),
                "brand": np.random.choice(["Brand A", "Brand B"], 50),
                "price": np.random.uniform(2, 15, 50),
            }
        )
