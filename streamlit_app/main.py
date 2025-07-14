import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.data_loader import UltraMinimalDataLoader
from src.recommendation.recommendation_engine import UltraMinimalRecommendationEngine
from streamlit_app.components.customer_profile import render_customer_profile
from streamlit_app.components.chat_interface import render_chat_interface

# 페이지 설정
st.set_page_config(
    page_title="🛍️ 고객 군집별 추천시스템",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 세그먼트 한글 매핑
SEGMENT_MAPPING = {
    "premium_loyal": "프리미엄 충성 고객",
    "premium_focused": "프리미엄 집중 고객",
    "excellent_loyal": "우수 충성 고객",
    "excellent_general": "우수 일반 고객",
    "general_value": "일반 가성비 고객",
    "at_risk": "이탈 위험 고객",
    "new_customer": "신규 고객",
}


def initialize_system():
    """시스템 초기화 - UltraMinimal 버전"""
    try:
        # 로딩 메시지
        with st.spinner("🔥 초경량 시스템 초기화 중..."):

            # 데이터 로더 초기화
            data_loader = UltraMinimalDataLoader()

            # 추천 엔진 초기화
            recommendation_engine = UltraMinimalRecommendationEngine()

            # 데이터 로딩 (메서드명 수정: load_data)
            customers, transactions, products = data_loader.load_data()

            # 추천 엔진 학습
            recommendation_engine.fit(transactions, products)

            # 세션 상태에 저장
            st.session_state.customers = customers
            st.session_state.transactions = transactions
            st.session_state.products = products
            st.session_state.recommendation_engine = recommendation_engine
            st.session_state.system_initialized = True

            st.success(
                f"✅ 초경량 시스템 로딩 완료: 고객 {len(customers):,}명, 상품 {len(products):,}개, 거래 {len(transactions):,}건"
            )
            return True

    except Exception as e:
        st.error(f"시스템 초기화 오류: {str(e)}")
        st.markdown(
            """
        **해결 방법:**
        1. 페이지를 새로고침해보세요
        2. 브라우저 캐시를 지워보세요
        3. 잠시 후 다시 시도해보세요
        """
        )
        return False


def create_customer_card(customer_row, segment_korean):
    """고객 카드 생성"""
    return f"""
    <div style="
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        cursor: pointer;
        transition: transform 0.2s;
    " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
        <h4 style="color: #333; margin: 0 0 10px 0;">고객 {customer_row['customer_id']}</h4>
        <p style="color: #666; margin: 5px 0;"><strong>세그먼트:</strong> {segment_korean}</p>
        <p style="color: #666; margin: 5px 0;"><strong>💰 총 구매금액:</strong> ${customer_row.get('total_spent', 0):.2f}</p>
        <p style="color: #666; margin: 5px 0;"><strong>📦 구매 빈도:</strong> {customer_row.get('purchase_frequency', 0)}회</p>
    </div>
    """


def main():
    """메인 애플리케이션"""

    # 타이틀
    st.markdown(
        """
    <div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0;">🛍️ 고객 군집별 추천시스템</h1>
        <p style="color: white; margin: 10px 0 0 0;">AI 기반 개인화 상품 추천 서비스 (초경량 버전)</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 시스템 초기화 확인
    if (
        "system_initialized" not in st.session_state
        or not st.session_state.system_initialized
    ):
        if not initialize_system():
            st.stop()

    # 사이드바: 고객 선택
    with st.sidebar:
        st.header("👥 고객 선택")

        customers = st.session_state.customers

        # 세그먼트 필터
        segments = ["전체"] + list(customers["segment"].unique())
        selected_segment = st.selectbox("📊 세그먼트 필터", segments)

        # 고객 필터링
        if selected_segment != "전체":
            filtered_customers = customers[customers["segment"] == selected_segment]
        else:
            filtered_customers = customers

        st.write(f"**고객 수: {len(filtered_customers)}명**")

        # 고객 카드 표시
        selected_customer = None

        for idx, (_, customer) in enumerate(filtered_customers.iterrows()):
            segment_korean = SEGMENT_MAPPING.get(
                customer["segment"], customer["segment"]
            )

            # 고객 카드 HTML
            card_html = create_customer_card(customer, segment_korean)
            st.markdown(card_html, unsafe_allow_html=True)

            # 선택 버튼
            if st.button(
                f"선택",
                key=f"select_{customer['customer_id']}",
                use_container_width=True,
            ):
                selected_customer = customer["customer_id"]
                st.session_state.selected_customer = selected_customer
                st.session_state.selected_customer_data = customer

    # 메인 영역
    if "selected_customer" in st.session_state:
        selected_customer = st.session_state.selected_customer
        customer_data = st.session_state.selected_customer_data

        # 탭 생성
        tab1, tab2 = st.tabs(["👤 고객 프로필", "💬 상품 추천 채팅"])

        with tab1:
            render_customer_profile(
                customer_data, st.session_state.transactions, st.session_state.products
            )

        with tab2:
            render_chat_interface(
                customer_manager=None,  # UltraMinimal에서는 불필요
                recommendation_engine=st.session_state.recommendation_engine,
                selected_customer=selected_customer,
                customer_segment=customer_data["segment"],
            )

    else:
        # 선택된 고객이 없을 때
        st.markdown(
            """
        <div style="text-align: center; padding: 3rem; color: #666;">
            <h2>👈 왼쪽에서 고객을 선택해주세요</h2>
            <p>고객을 선택하면 개인화된 프로필과 추천 서비스를 이용할 수 있습니다.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # 푸터
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 AI 추천시스템 v2.0 | 초경량 Streamlit Cloud 버전</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
