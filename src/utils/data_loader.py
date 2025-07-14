import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from typing import Tuple
import gc


class RealDataLoader:
    """Categorical 오류 수정된 dunnhumby 데이터셋 전용 로더"""

    def __init__(self, data_path: str = "data/raw"):
        self.data_path = data_path

    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """메모리 효율적인 데이터 로딩"""
        print("📊 메모리 최적화된 dunnhumby 데이터셋 로딩 중...")

        # 1. 실제 데이터 파일들 로딩
        raw_data = self._load_real_files()

        # 2. 메모리 효율적인 전처리
        transactions = self._process_real_transactions(raw_data)
        products = self._process_real_products(raw_data)
        customers = self._process_real_customers(raw_data, transactions)

        # 메모리 정리
        del raw_data
        gc.collect()

        print(f"✅ 거래 데이터: {len(transactions):,}건")
        print(f"✅ 고객 데이터: {len(customers):,}명")
        print(f"✅ 상품 데이터: {len(products):,}개")

        return transactions, customers, products

    def _load_real_files(self) -> dict:
        """메모리 효율적인 CSV 파일 로딩"""
        files = {
            "transactions": "transaction_data.csv",
            "products": "product.csv",
            "households": "hh_demographic.csv",
        }

        raw_data = {}

        for key, filename in files.items():
            file_path = os.path.join(self.data_path, filename)
            if os.path.exists(file_path):
                if key == "transactions":
                    # 거래 데이터는 청크 단위로 읽어서 샘플링
                    print(f"  📊 {filename} 청크 단위 로딩 중...")
                    chunks = []
                    chunk_size = 50000  # 더 작게 설정
                    total_rows = 0

                    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                        total_rows += len(chunk)

                        # 5%만 샘플링 (메모리 절약)
                        if len(chunk) > 2500:
                            chunk = chunk.sample(n=2500, random_state=42)

                        chunks.append(chunk)

                        # 최대 20만 행까지만
                        if total_rows >= 200000:
                            break

                        if len(chunks) % 10 == 0:
                            print(f"    처리 중... {total_rows:,}행")

                    df = pd.concat(chunks, ignore_index=True)
                    print(
                        f"  ✅ {filename}: 원본 {total_rows:,}행 → 샘플 {len(df):,}행"
                    )
                else:
                    # 상품, 고객 데이터는 전체 로딩
                    df = pd.read_csv(file_path)
                    print(f"  ✅ {filename}: {len(df):,}행")

                raw_data[key] = df
            else:
                print(f"  ❌ {filename}: 파일 없음")
                raw_data[key] = pd.DataFrame()

        return raw_data

    def _process_real_transactions(self, raw_data: dict) -> pd.DataFrame:
        """거래 데이터 전처리 (Categorical 오류 수정)"""
        df = raw_data["transactions"].copy()

        if df.empty:
            raise ValueError("transaction_data.csv 파일이 없거나 비어있습니다.")

        print("📋 거래 데이터 전처리...")

        # 필요한 컬럼만 유지
        essential_columns = [
            "household_key",
            "PRODUCT_ID",
            "BASKET_ID",
            "SALES_VALUE",
            "QUANTITY",
            "DAY",
        ]
        available_columns = [col for col in essential_columns if col in df.columns]
        df = df[available_columns]

        # 컬럼명 변경
        df = df.rename(
            columns={
                "household_key": "customer_id",
                "PRODUCT_ID": "product_id",
                "BASKET_ID": "basket_id",
                "SALES_VALUE": "amount",
                "QUANTITY": "quantity",
                "DAY": "day",
            }
        )

        # 결측값 먼저 제거
        df = df.dropna(subset=["customer_id", "product_id"])

        # 데이터 타입 변환 (Categorical 사용 안함)
        df["customer_id"] = df["customer_id"].astype(str)
        df["product_id"] = df["product_id"].astype(str)
        df["basket_id"] = df["basket_id"].astype(str)
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df["quantity"] = (
            pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)
        )

        # 이상값 제거
        df = df[(df["amount"] > 0) & (df["amount"] < 1000)]
        df = df[df["quantity"] <= 20]

        # 날짜 생성
        base_date = datetime(2023, 1, 1)
        df["transaction_date"] = pd.to_datetime(base_date) + pd.to_timedelta(
            df["day"] - 1, unit="D"
        )

        # 거래 ID와 채널 추가
        df["transaction_id"] = range(1, len(df) + 1)
        df["channel"] = "offline"

        # 최종 결측값 제거
        df = df.dropna(subset=["amount"])

        print(f"  ✅ 전처리 완료: {len(df):,}건")
        return df

    def _process_real_products(self, raw_data: dict) -> pd.DataFrame:
        """상품 데이터 전처리 (Categorical 오류 수정)"""
        df = raw_data["products"].copy()

        if df.empty:
            raise ValueError("product.csv 파일이 없거나 비어있습니다.")

        print("🛍️ 상품 데이터 전처리...")

        # 필요한 컬럼만 유지
        essential_columns = ["PRODUCT_ID", "COMMODITY_DESC", "BRAND", "DEPARTMENT"]
        available_columns = [col for col in essential_columns if col in df.columns]
        df = df[available_columns]

        # 컬럼명 변경
        df = df.rename(
            columns={
                "PRODUCT_ID": "product_id",
                "COMMODITY_DESC": "category",
                "BRAND": "brand",
                "DEPARTMENT": "department",
            }
        )

        # 결측값 먼저 처리 (Categorical 변환 전에)
        df["category"] = df["category"].fillna("UNKNOWN")
        df["brand"] = df["brand"].fillna("Unknown")
        df["department"] = df["department"].fillna("GENERAL")

        # 데이터 타입 변환
        df["product_id"] = df["product_id"].astype(str)
        df["category"] = df["category"].astype(str)
        df["brand"] = df["brand"].astype(str)
        df["department"] = df["department"].astype(str)

        # 상품명 생성
        df["product_name"] = df["brand"] + " " + df["category"]

        # 빈 문자열 처리
        empty_mask = df["product_name"].str.strip() == "Unknown UNKNOWN"
        df.loc[empty_mask, "product_name"] = (
            "Product " + df.loc[empty_mask, "product_id"]
        )

        # 기본값들
        df["price"] = 5.0
        df["rating"] = 4.0
        df["description"] = df["category"] + " - " + df["brand"]

        print(f"  ✅ 상품 데이터 완료: {len(df):,}개")
        print(f"  📋 카테고리 수: {df['category'].nunique()}")
        print(f"  🏷️ 브랜드 수: {df['brand'].nunique()}")

        return df

    def _process_real_customers(
        self, raw_data: dict, transactions: pd.DataFrame
    ) -> pd.DataFrame:
        """고객 데이터 전처리 (Categorical 오류 수정)"""
        print("👥 고객 데이터 전처리...")

        # 인구통계 데이터
        demo_df = raw_data["households"].copy()
        if not demo_df.empty:
            demo_df = demo_df.rename(columns={"household_key": "customer_id"})
            demo_df["customer_id"] = demo_df["customer_id"].astype(str)

        # 거래 데이터에서 고객 추출 (활성 고객만)
        customer_activity = transactions["customer_id"].value_counts()
        active_customers = customer_activity[
            customer_activity >= 3
        ].index  # 3회 이상 구매로 완화

        all_customers_df = pd.DataFrame({"customer_id": active_customers})

        # 인구통계와 병합
        if not demo_df.empty:
            df = all_customers_df.merge(demo_df, on="customer_id", how="left")
        else:
            df = all_customers_df.copy()

        # 거래 통계 계산 (간소화)
        print("  📊 거래 통계 계산 중...")

        active_transactions = transactions[
            transactions["customer_id"].isin(active_customers)
        ]

        customer_stats = (
            active_transactions.groupby("customer_id")
            .agg(
                {
                    "amount": ["sum", "count"],
                    "transaction_date": ["min", "max"],
                    "basket_id": "nunique",
                }
            )
            .round(2)
        )

        customer_stats.columns = [
            "total_spent",
            "transaction_count",
            "first_purchase",
            "last_purchase",
            "visit_count",
        ]
        customer_stats = customer_stats.reset_index()

        # 통계와 병합
        df = df.merge(customer_stats, on="customer_id", how="left")

        # 간단한 RFM 분석
        print("  🎯 간단한 세그먼테이션...")

        # 결측값 먼저 처리
        df["total_spent"] = df["total_spent"].fillna(0)
        df["visit_count"] = df["visit_count"].fillna(1)
        df["transaction_count"] = df["transaction_count"].fillna(1)

        # 간단한 세그먼테이션 (복잡한 RFM 대신)
        def simple_segment(row):
            spent = row["total_spent"]
            visits = row["visit_count"]

            if spent >= 100 and visits >= 10:
                return "premium_loyal"
            elif spent >= 100:
                return "premium_focused"
            elif visits >= 10:
                return "excellent_loyal"
            elif spent >= 50:
                return "excellent_general"
            elif spent >= 20:
                return "general_value"
            elif visits >= 2:
                return "at_risk"
            else:
                return "new_customer"

        df["segment"] = df.apply(simple_segment, axis=1)
        df["frequency"] = df["visit_count"]
        df["rfm_score"] = 3.0  # 기본값

        print(f"  ✅ 고객 데이터 완료: {len(df):,}명")

        # 세그먼트별 분포 출력
        segment_counts = df["segment"].value_counts()
        print("  📊 세그먼트 분포:")
        for segment, count in segment_counts.items():
            print(f"    {segment}: {count}명")

        return df
