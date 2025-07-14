import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter


def render_customer_profile(customer_data, transactions, products):
    """초경량 고객 프로필 렌더링"""

    try:
        customer_id = customer_data["customer_id"]

        st.subheader(f"👤 고객 {customer_id} 프로필")

        # 기본 정보 카드
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(label="고객 ID", value=str(customer_id))

        with col2:
            segment_korean = {
                "premium_loyal": "프리미엄 충성",
                "general_value": "일반 가성비",
                "at_risk": "이탈 위험",
                "excellent_loyal": "우수 충성",
                "new_customer": "신규 고객",
            }.get(customer_data["segment"], customer_data["segment"])

            st.metric(label="세그먼트", value=segment_korean)

        with col3:
            total_spent = customer_data.get("total_spent", 0)
            st.metric(label="총 구매금액", value=f"${total_spent:.2f}")

        with col4:
            purchase_freq = customer_data.get("purchase_frequency", 0)
            st.metric(label="구매 빈도", value=f"{purchase_freq}회")

        st.markdown("---")

        # 고객별 거래 데이터 필터링
        customer_transactions = transactions[transactions["customer_id"] == customer_id]

        if len(customer_transactions) == 0:
            st.warning("이 고객의 거래 데이터가 없습니다.")
            return

        # 두 컬럼으로 나누기
        col1, col2 = st.columns(2)

        with col1:
            # 📊 구매 패턴 분석
            st.subheader("📊 구매 패턴")

            # 구매 통계
            avg_purchase = customer_transactions["price"].mean()
            max_purchase = customer_transactions["price"].max()
            min_purchase = customer_transactions["price"].min()

            pattern_col1, pattern_col2 = st.columns(2)

            with pattern_col1:
                st.metric("평균 구매금액", f"${avg_purchase:.2f}")
                st.metric("최고 구매금액", f"${max_purchase:.2f}")

            with pattern_col2:
                st.metric("최저 구매금액", f"${min_purchase:.2f}")
                st.metric("총 거래건수", f"{len(customer_transactions)}건")

        with col2:
            # 🛍️ 선호 카테고리
            st.subheader("🛍️ 선호 카테고리")

            # 고객이 구매한 상품들의 카테고리 분석
            customer_product_ids = customer_transactions["product_id"].tolist()
            customer_products = products[
                products["product_id"].isin(customer_product_ids)
            ]

            if len(customer_products) > 0:
                category_counts = customer_products["category"].value_counts()

                if len(category_counts) > 0:
                    # 파이 차트
                    fig = px.pie(
                        values=category_counts.values,
                        names=category_counts.index,
                        title="구매 카테고리 분포",
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("카테고리 데이터가 없습니다.")
            else:
                st.info("구매한 상품 정보가 없습니다.")

        st.markdown("---")

        # 📈 구매 트렌드 (간단화)
        st.subheader("📈 구매 트렌드")

        if "day" in customer_transactions.columns:
            # 일별 구매 금액
            daily_spending = (
                customer_transactions.groupby("day")["price"].sum().reset_index()
            )

            if len(daily_spending) > 1:
                fig = px.line(
                    daily_spending,
                    x="day",
                    y="price",
                    title="일별 구매 금액 추이",
                    labels={"day": "일", "price": "구매 금액 ($)"},
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("구매 트렌드를 표시하기에 데이터가 부족합니다.")
        else:
            st.info("날짜 정보가 없어 트렌드를 표시할 수 없습니다.")

        # 🛒 최근 구매 이력
        st.subheader("🛒 구매 이력")

        # 구매 이력 테이블
        if len(customer_transactions) > 0:
            # 상품 정보와 조인
            purchase_history = customer_transactions.merge(
                products[["product_id", "product_name", "category", "brand"]],
                on="product_id",
                how="left",
            )

            # 최근 10건만 표시
            recent_purchases = purchase_history.tail(10)[
                ["product_name", "category", "brand", "price"]
            ].copy()
            recent_purchases.columns = ["상품명", "카테고리", "브랜드", "가격"]
            recent_purchases["가격"] = recent_purchases["가격"].apply(
                lambda x: f"${x:.2f}"
            )

            st.dataframe(recent_purchases, use_container_width=True, height=300)
        else:
            st.info("구매 이력이 없습니다.")

        # 👥 유사 고객 찾기 (간단화)
        st.subheader("👥 유사 고객")

        # 같은 세그먼트의 다른 고객들
        all_customers = st.session_state.customers
        similar_customers = all_customers[
            (all_customers["segment"] == customer_data["segment"])
            & (all_customers["customer_id"] != customer_id)
        ]

        if len(similar_customers) > 0:
            similar_sample = similar_customers.head(3)

            for _, similar_customer in similar_sample.iterrows():
                with st.expander(
                    f"고객 {similar_customer['customer_id']} ({similar_customer['segment']})"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "총 구매금액", f"${similar_customer['total_spent']:.2f}"
                        )

                    with col2:
                        st.metric(
                            "구매 빈도", f"{similar_customer['purchase_frequency']}회"
                        )
        else:
            st.info("유사한 고객을 찾지 못했습니다.")

    except Exception as e:
        st.error(f"고객 프로필 표시 중 오류 발생: {str(e)}")

        # 디버그 정보 (개발용)
        if st.checkbox("🔧 디버그 정보 표시", key="debug_profile"):
            st.code(
                f"""
고객 데이터: {customer_data}
거래 데이터 컬럼: {list(transactions.columns)}
상품 데이터 컬럼: {list(products.columns)}
오류: {str(e)}
            """
            )
