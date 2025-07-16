# src/utils/data_loader.py
import pandas as pd
import numpy as np
import os


class UltraMinimalDataLoader:
    def load_data(self):
        try:
            # 실제 데이터 파일 로드
            base_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "raw"
            )

            # product.csv 로드
            product_df = pd.read_csv(os.path.join(base_path, "product.csv"))

            # transaction_data.csv 로드
            transaction_df = pd.read_csv(
                os.path.join(base_path, "transaction_data.csv")
            )

            # hh_demographic.csv 로드
            demographic_df = pd.read_csv(os.path.join(base_path, "hh_demographic.csv"))

            # 상품 데이터 전처리 - 실제 상품명 사용
            products = product_df.copy()
            products["product_name"] = products["COMMODITY_DESC"].fillna(
                "Unknown Product"
            )
            products["sub_category"] = products["SUB_COMMODITY_DESC"].fillna(
                "Unknown Sub-Category"
            )
            products["category"] = products["COMMODITY_DESC"].fillna("Unknown Category")

            # 가격 정보는 거래 데이터에서 평균 계산
            avg_prices = (
                transaction_df.groupby("PRODUCT_ID")["SALES_VALUE"].mean().reset_index()
            )
            avg_prices.columns = ["product_id", "avg_price"]

            # products 데이터프레임 정리
            products = products.rename(columns={"PRODUCT_ID": "product_id"})
            products = products.merge(avg_prices, on="product_id", how="left")
            products["price"] = products["avg_price"].fillna(5.0)
            products["brand"] = "Store Brand"  # 브랜드 정보가 없으면 기본값

            # 고객 데이터 생성 (demographic 기반)
            customers = demographic_df.copy()
            customers = customers.rename(columns={"household_key": "customer_id"})

            # 고객 세그먼트 생성 (소득과 가족 구성원 수 기반)
            def assign_segment(row):
                income = row.get("INCOME_DESC", "Unknown")
                household_size = row.get("HOUSEHOLD_SIZE_DESC", "Unknown")

                if "High" in str(income) or "100K+" in str(income):
                    return "premium_loyal"
                elif "Medium" in str(income) or "50-99K" in str(income):
                    return "excellent_general"
                elif "Low" in str(income) or "15-24K" in str(income):
                    return "general_value"
                else:
                    return "new_customer"

            customers["segment"] = customers.apply(assign_segment, axis=1)

            # 고객별 총 구매금액과 빈도 계산
            customer_stats = (
                transaction_df.groupby("household_key")
                .agg({"SALES_VALUE": ["sum", "count"], "BASKET_ID": "nunique"})
                .reset_index()
            )

            customer_stats.columns = [
                "customer_id",
                "total_spent",
                "total_transactions",
                "purchase_frequency",
            ]
            customers = customers.merge(customer_stats, on="customer_id", how="left")
            customers[["total_spent", "total_transactions", "purchase_frequency"]] = (
                customers[
                    ["total_spent", "total_transactions", "purchase_frequency"]
                ].fillna(0)
            )

            # 거래 데이터 정리
            transactions = transaction_df.copy()
            transactions = transactions.rename(
                columns={
                    "household_key": "customer_id",
                    "PRODUCT_ID": "product_id",
                    "QUANTITY": "quantity",
                    "SALES_VALUE": "price",
                }
            )

            return customers, transactions, products

        except Exception as e:
            print(f"실제 데이터 로드 실패: {e}")
            # 실패시 더미 데이터 반환
            return self._generate_dummy_data()

    def _generate_dummy_data(self):
        """실제 데이터 로드 실패시 더미 데이터 생성"""
        # 실제 상품명을 사용한 더미 데이터
        product_names = [
            "2% MILK",
            "WHOLE MILK",
            "SKIM MILK",
            "CHOCOLATE MILK",
            "WHITE BREAD",
            "WHEAT BREAD",
            "SOURDOUGH BREAD",
            "BAGELS",
            "COCA COLA",
            "PEPSI",
            "SPRITE",
            "ORANGE JUICE",
            "GROUND COFFEE",
            "INSTANT COFFEE",
            "TEA BAGS",
            "HOT CHOCOLATE",
        ]

        sub_categories = [
            "REDUCED FAT MILK",
            "REGULAR MILK",
            "FAT FREE MILK",
            "FLAVORED MILK",
            "SANDWICH BREAD",
            "SPECIALTY BREAD",
            "FRESH BREAD",
            "BREAKFAST BREAD",
            "CARBONATED DRINKS",
            "SOFT DRINKS",
            "FRUIT DRINKS",
            "JUICE",
            "COFFEE",
            "INSTANT BEVERAGES",
            "TEA",
            "HOT DRINKS",
        ]

        customers = pd.DataFrame(
            {
                "customer_id": range(1, 101),
                "segment": np.random.choice(
                    ["premium_loyal", "general_value", "at_risk", "excellent_general"],
                    100,
                ),
                "total_spent": np.random.uniform(50, 2000, 100),
                "purchase_frequency": np.random.randint(5, 50, 100),
            }
        )

        products = pd.DataFrame(
            {
                "product_id": range(1, len(product_names) + 1),
                "product_name": product_names,
                "sub_category": sub_categories[: len(product_names)],
                "category": [name.split()[-1] for name in product_names],
                "brand": np.random.choice(
                    ["Store Brand", "Premium Brand", "Value Brand"], len(product_names)
                ),
                "price": np.random.uniform(1, 15, len(product_names)),
            }
        )

        transactions = pd.DataFrame(
            {
                "customer_id": np.random.choice(range(1, 101), 500),
                "product_id": np.random.choice(range(1, len(product_names) + 1), 500),
                "quantity": np.random.randint(1, 5, 500),
                "price": np.random.uniform(1, 15, 500),
            }
        )

        return customers, transactions, products
