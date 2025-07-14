import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List


def render_customer_profile(
    customer_info: Dict,
    customer_manager,
    transactions: pd.DataFrame,
    products: pd.DataFrame,
):
    """고객 프로필 렌더링"""

    customer_id = customer_info["customer_id"]

    # 고객 기본 정보
    st.markdown("### 👤 고객 기본 정보")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
        <div class="metric-card">
            <h4 style="color: #333333 !important;">고객 ID</h4>
            <h2 style="color: #333333 !important;">{customer_id}</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        segment_info = customer_manager.get_segment_info(customer_info["segment"])
        st.markdown(
            f"""
        <div class="metric-card">
            <h4 style="color: #333333 !important;">세그먼트</h4>
            <h3 style="color: {segment_info.get('color', '#333333')} !important;">{segment_info.get('name', '알 수 없음')}</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="metric-card">
            <h4 style="color: #333333 !important;">총 구매금액</h4>
            <h2 style="color: #333333 !important;">${customer_info.get('total_spent', 0):,.0f}</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div class="metric-card">
            <h4 style="color: #333333 !important;">구매 빈도</h4>
            <h2 style="color: #333333 !important;">{customer_info.get('frequency', 0)}회</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # 세그먼트 설명
    st.markdown("### 🎯 세그먼트 특성")
    segment_info = customer_manager.get_segment_info(customer_info["segment"])

    st.info(
        f"""
    **{segment_info.get('name', '알 수 없음')}**
    
    {segment_info.get('description', '설명이 없습니다.')}
    
    **추천 전략:** {segment_info.get('strategy', 'general')}
    """
    )

    # 고객 통계
    try:
        stats = customer_manager.get_customer_statistics(customer_id)

        st.markdown("### 📊 구매 패턴 분석")

        col1, col2 = st.columns(2)

        with col1:
            # 구매 빈도 패턴
            pattern_mapping = {
                "very_frequent": "매우 자주 (주 1회 이상)",
                "frequent": "자주 (월 1-4회)",
                "regular": "정기적 (분기 1-4회)",
                "infrequent": "가끔 (연 1-4회)",
                "single_purchase": "단일 구매",
                "no_data": "데이터 없음",
                "error": "계산 오류",
            }

            pattern_text = pattern_mapping.get(
                stats["purchase_frequency"]["purchase_pattern"], "알 수 없음"
            )

            st.metric(
                "구매 패턴",
                pattern_text,
                f"평균 {stats['purchase_frequency']['avg_days_between_purchases']}일 간격",
            )

        with col2:
            if stats["last_transaction_date"]:
                days_since = stats["days_since_last_purchase"]
                st.metric(
                    "마지막 구매",
                    f"{days_since}일 전",
                    stats["last_transaction_date"].strftime("%Y-%m-%d"),
                )
            else:
                st.metric("마지막 구매", "구매 이력 없음", "")

        # 선호 카테고리
        if stats["favorite_categories"]:
            st.markdown("### 🛍️ 선호 카테고리")

            categories_df = pd.DataFrame(stats["favorite_categories"])

            fig = px.bar(
                categories_df,
                x="category",
                y="total_spent",
                title="카테고리별 구매 금액",
                color="purchase_count",
                color_continuous_scale="viridis",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            # 상세 테이블
            st.markdown("**카테고리별 상세 정보**")
            display_df = categories_df.copy()
            display_df["total_spent"] = display_df["total_spent"].apply(
                lambda x: f"${x:,.2f}"
            )
            display_df["avg_amount"] = display_df["avg_amount"].apply(
                lambda x: f"${x:,.2f}"
            )
            display_df.columns = [
                "카테고리",
                "총 구매금액",
                "구매 횟수",
                "평균 구매금액",
            ]
            st.dataframe(display_df, use_container_width=True)

        # 월별 구매 트렌드
        if stats["monthly_spending"]:
            st.markdown("### 📈 월별 구매 트렌드")

            monthly_data = []
            for month, amount in stats["monthly_spending"].items():
                monthly_data.append({"월": month, "구매금액": amount})

            if monthly_data:
                monthly_df = pd.DataFrame(monthly_data)
                monthly_df = monthly_df.sort_values("월")

                fig = px.line(
                    monthly_df,
                    x="월",
                    y="구매금액",
                    title="월별 구매 금액 추이",
                    markers=True,
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

        # 계절별 패턴
        if stats["seasonal_patterns"]:
            st.markdown("### 🌸 계절별 구매 패턴")

            season_mapping = {
                "spring": "봄",
                "summer": "여름",
                "autumn": "가을",
                "winter": "겨울",
            }

            seasonal_data = []
            for season, amount in stats["seasonal_patterns"].items():
                seasonal_data.append(
                    {"계절": season_mapping.get(season, season), "구매금액": amount}
                )

            if seasonal_data:
                seasonal_df = pd.DataFrame(seasonal_data)

                fig = px.pie(
                    seasonal_df,
                    values="구매금액",
                    names="계절",
                    title="계절별 구매 비중",
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"통계 정보를 불러오는 중 오류가 발생했습니다: {e}")
        st.write("디버그 정보:")
        st.write(f"Customer ID: {customer_id}")
        st.write(f"Error: {str(e)}")

    # 최근 구매 이력 (수정)
    st.markdown("### 🛒 최근 구매 이력")

    try:
        recent_transactions = customer_manager.get_customer_transactions(
            customer_id, limit=20
        )

        if not recent_transactions.empty:
            # 상품 정보와 매핑해서 상품명 추가
            display_transactions = recent_transactions.copy()

            # 상품명 매핑
            product_names = {}
            for _, product in products.iterrows():
                product_names[product["product_id"]] = product.get(
                    "product_name", f"Product {product['product_id']}"
                )

            display_transactions["product_name"] = display_transactions[
                "product_id"
            ].map(lambda x: product_names.get(x, f"Product {x}"))

            # 표시할 컬럼 선택 및 정렬
            display_columns = []
            if "transaction_date" in display_transactions.columns:
                display_columns.append("transaction_date")
            if "product_name" in display_transactions.columns:
                display_columns.append("product_name")
            if "category" in display_transactions.columns:
                display_columns.append("category")
            if "quantity" in display_transactions.columns:
                display_columns.append("quantity")
            if "amount" in display_transactions.columns:
                display_columns.append("amount")
            if "channel" in display_transactions.columns:
                display_columns.append("channel")

            if display_columns:
                display_df = display_transactions[display_columns].copy()

                # 날짜 포맷팅
                if "transaction_date" in display_df.columns:
                    display_df["transaction_date"] = pd.to_datetime(
                        display_df["transaction_date"]
                    ).dt.strftime("%Y-%m-%d")

                # 금액 포맷팅
                if "amount" in display_df.columns:
                    display_df["amount"] = display_df["amount"].apply(
                        lambda x: f"${x:,.2f}" if pd.notna(x) else "$0.00"
                    )

                # 컬럼명 한글화
                column_mapping = {
                    "transaction_date": "구매일",
                    "product_name": "상품명",
                    "category": "카테고리",
                    "quantity": "수량",
                    "amount": "금액",
                    "channel": "구매채널",
                }

                display_df = display_df.rename(
                    columns={
                        k: v
                        for k, v in column_mapping.items()
                        if k in display_df.columns
                    }
                )

                # 테이블 표시
                st.dataframe(display_df, use_container_width=True, height=300)

                # 구매 통계 요약
                col1, col2, col3 = st.columns(3)

                with col1:
                    total_amount = (
                        recent_transactions["amount"].sum()
                        if "amount" in recent_transactions.columns
                        else 0
                    )
                    st.metric("최근 구매 총액", f"${total_amount:,.2f}")

                with col2:
                    avg_amount = (
                        recent_transactions["amount"].mean()
                        if "amount" in recent_transactions.columns
                        else 0
                    )
                    st.metric("평균 구매 금액", f"${avg_amount:,.2f}")

                with col3:
                    unique_products = (
                        recent_transactions["product_id"].nunique()
                        if "product_id" in recent_transactions.columns
                        else 0
                    )
                    st.metric("구매한 상품 종류", f"{unique_products}개")
            else:
                st.warning("표시할 수 있는 컬럼이 없습니다.")
                st.write("사용 가능한 컬럼:", list(recent_transactions.columns))
        else:
            st.info("구매 이력이 없습니다.")

    except Exception as e:
        st.error(f"구매 이력을 불러오는 중 오류가 발생했습니다: {e}")
        st.write("디버그 정보:")
        st.write(f"Customer ID: {customer_id}")
        st.write(f"Error type: {type(e).__name__}")
        st.write(f"Error message: {str(e)}")

    # 유사 고객
    st.markdown("### 👥 유사한 고객들")

    try:
        similar_customers = customer_manager.search_similar_customers(
            customer_id, top_n=5
        )

        if similar_customers:
            for i, similar in enumerate(similar_customers, 1):
                with st.expander(f"유사 고객 {i}: 고객 {similar['customer_id']}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "총 구매금액", f"${similar.get('total_spent', 0):,.0f}"
                        )

                    with col2:
                        st.metric("구매 빈도", f"{similar.get('frequency', 0)}회")

                    with col3:
                        segment_info = customer_manager.get_segment_info(
                            similar["segment"]
                        )
                        st.write(
                            f"**세그먼트:** {segment_info.get('name', '알 수 없음')}"
                        )
        else:
            st.info("유사한 고객을 찾을 수 없습니다.")

    except Exception as e:
        st.warning(f"유사 고객 검색 중 오류: {e}")


def get_product_name(product_id: int, products: pd.DataFrame) -> str:
    """상품 ID로 상품명 조회"""
    try:
        product = products[products["product_id"] == product_id]
        if not product.empty:
            return product.iloc[0].get("product_name", f"Product {product_id}")
        else:
            return f"Product {product_id}"
    except Exception:
        return f"Product {product_id}"
