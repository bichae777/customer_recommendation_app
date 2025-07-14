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

from src.customer.customer_manager import CustomerManager
from src.utils.data_loader import UltraMinimalDataLoader
from src.recommendation.recommendation_engine import UltraMinimalRecommendationEngine
from streamlit_app.components.customer_profile import render_customer_profile
from streamlit_app.components.chat_interface import render_chat_interface

# 페이지 설정
st.set_page_config(
    page_title="고객 군집별 추천시스템",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 CSS (폰트 색상 수정)
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .customer-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #333333 !important;  /* 검은색 폰트 */
    }
    .customer-card:hover {
        background: #e9ecef;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        text-align: center;
        color: #333333 !important;  /* 검은색 폰트 */
    }
    .metric-card h2, .metric-card h3, .metric-card h4 {
        color: #333333 !important;  /* 제목도 검은색 */
    }
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #dee2e6;
        height: 500px;
        overflow-y: auto;
    }
    .product-recommendation {
        background: #f8f9fa;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid #28a745;
        color: #333333 !important;  /* 검은색 폰트 */
    }
    .loading-message {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
        color: #333333 !important;  /* 검은색 폰트 */
    }
    /* Streamlit 기본 요소들 폰트 색상 수정 */
    .stDataFrame, .stTable {
        color: #333333 !important;
    }
    .stDataFrame tbody tr td {
        color: #333333 !important;
    }
    /* 메트릭 카드 내부 텍스트 */
    .metric-card * {
        color: #333333 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# 세그먼트 매핑 (영어 -> 한글)
SEGMENT_MAPPING = {
    "premium_loyal": "프리미엄 장기 고객",
    "premium_focused": "프리미엄 집중 고객",
    "excellent_loyal": "우수 충성 고객",
    "excellent_general": "우수 일반 고객",
    "general_value": "일반 가성비 고객",
    "at_risk": "이탈 위험 고객",
    "new_customer": "신규 유입 고객",
}

# 역방향 매핑 (한글 -> 영어)
REVERSE_SEGMENT_MAPPING = {v: k for k, v in SEGMENT_MAPPING.items()}


@st.cache_data
def load_real_data():
    """실제 데이터 로딩 (캐시됨)"""
    try:
        data_loader = UltraMinimalDataLoader()
        transactions, customers, products = data_loader.load_all_data()
        return transactions, customers, products, None
    except Exception as e:
        error_msg = f"데이터 로딩 중 오류 발생: {str(e)}"
        print(error_msg)
        return None, None, None, error_msg


@st.cache_resource
def initialize_system():
    """시스템 초기화 (캐시됨)"""
    transactions, customers, products, error = load_real_data()

    if error:
        return None, None, None, None, None, error

    if transactions is None or customers is None or products is None:
        return None, None, None, None, None, "데이터 로딩 실패"

    try:
        # 고객 관리자 초기화
        customer_manager = CustomerManager()
        customer_manager.load_data(customers, transactions)

        # 추천 엔진 초기화 (클래스명 변경)
        recommendation_engine = UltraMinimalRecommendationEngine()
        recommendation_engine.fit(transactions, products)

        return (
            customer_manager,
            recommendation_engine,
            customers,
            products,
            transactions,
            None,
        )

    except Exception as e:
        error_msg = f"시스템 초기화 중 오류: {str(e)}"
        return None, None, None, None, None, error_msg


def show_loading_message():
    """로딩 메시지 표시"""
    st.markdown(
        """
    <div class="loading-message">
        <h3>📊 데이터 로딩 중...</h3>
        <p>실제 CSV 파일에서 데이터를 읽어오고 있습니다.</p>
        <p>최초 실행 시 시간이 걸릴 수 있습니다.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def show_error_message(error: str):
    """오류 메시지 표시"""
    st.error(
        f"""
    **시스템 초기화 오류**
    
    {error}
    
    **해결 방법:**
    1. `data/raw/` 폴더에 CSV 파일들이 있는지 확인
    2. 파일 권한 확인
    3. 의존성 패키지 재설치: `pip install -r requirements.txt`
    """
    )


def main():
    # 헤더
    st.markdown(
        """
    <div class="main-header">
        <h1>🛍️ 고객 군집별 추천시스템</h1>
        <p>AI 기반 개인화 상품 추천 서비스</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 로딩 메시지 표시
    loading_placeholder = st.empty()
    with loading_placeholder:
        show_loading_message()

    # 시스템 초기화
    try:
        (
            customer_manager,
            recommendation_engine,
            customers,
            products,
            transactions,
            error,
        ) = initialize_system()

        # 로딩 메시지 제거
        loading_placeholder.empty()

        if error:
            show_error_message(error)
            st.stop()

        if customer_manager is None:
            st.error("시스템 초기화에 실패했습니다.")
            st.stop()

    except Exception as e:
        loading_placeholder.empty()
        show_error_message(str(e))
        st.stop()

    # 성공적으로 로딩된 경우 데이터 요약 표시
    st.success(
        f"✅ 데이터 로딩 완료: 고객 {len(customers):,}명, 상품 {len(products):,}개, 거래 {len(transactions):,}건"
    )

    # 레이아웃 구성
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 👥 고객 목록")

        # 세그먼트 필터 (한글로 표시)
        if "segment" in customers.columns:
            # 영어 세그먼트를 한글로 변환
            korean_segments = [
                SEGMENT_MAPPING.get(seg, seg) for seg in customers["segment"].unique()
            ]
            korean_segments = sorted(list(set(korean_segments)))  # 중복 제거 및 정렬
        else:
            korean_segments = []

        selected_korean_segment = st.selectbox(
            "세그먼트 필터", ["전체"] + korean_segments
        )

        # 한글 세그먼트를 영어로 변환하여 필터링
        if selected_korean_segment != "전체":
            english_segment = REVERSE_SEGMENT_MAPPING.get(
                selected_korean_segment, selected_korean_segment
            )
            filtered_customers = customers[customers["segment"] == english_segment]
        else:
            filtered_customers = customers

        # 고객 카드 렌더링
        if "selected_customer" not in st.session_state:
            st.session_state.selected_customer = None

        # 고객 정보 표시 개선
        for idx, customer in filtered_customers.head(20).iterrows():
            with st.container():
                col_a, col_b = st.columns([3, 1])

                with col_a:
                    # 안전한 값 가져오기
                    customer_id = customer.get("customer_id", idx)
                    segment = customer.get("segment", "알 수 없음")
                    total_spent = customer.get("total_spent", 0)
                    frequency = customer.get("frequency", 0)

                    # 세그먼트 한글명 표시
                    segment_display = SEGMENT_MAPPING.get(segment, segment)

                    st.markdown(
                        f"""
                    <div class="customer-card">
                        <strong>고객 {customer_id}</strong><br>
                        <small>{segment_display}</small><br>
                        <small>💰 ${total_spent:,.0f} | 📦 {frequency}회</small>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with col_b:
                    if st.button("선택", key=f"btn_{customer_id}"):
                        st.session_state.selected_customer = customer_id
                        st.rerun()

        # 선택된 고객이 없으면 첫 번째 고객 자동 선택
        if st.session_state.selected_customer is None and not filtered_customers.empty:
            st.session_state.selected_customer = filtered_customers.iloc[0][
                "customer_id"
            ]

    with col2:
        if st.session_state.selected_customer:
            # 선택된 고객 정보
            customer_id = st.session_state.selected_customer
            customer_info = customers[customers["customer_id"] == customer_id]

            if customer_info.empty:
                st.error(f"고객 ID {customer_id}를 찾을 수 없습니다.")
                st.stop()

            customer_info = customer_info.iloc[0]

            # 탭 구성
            tab1, tab2 = st.tabs(["👤 고객 프로필", "💬 상품 추천 채팅"])

            with tab1:
                try:
                    render_customer_profile(
                        customer_info, customer_manager, transactions, products
                    )
                except Exception as e:
                    st.error(f"고객 프로필 렌더링 오류: {e}")
                    st.write("디버그 정보:")
                    st.write(f"고객 정보: {customer_info}")
                    st.write(f"오류 상세: {str(e)}")

            with tab2:
                try:
                    render_chat_interface(
                        customer_id, recommendation_engine, products, customer_info
                    )
                except Exception as e:
                    st.error(f"채팅 인터페이스 오류: {e}")
                    st.write("디버그 정보:")
                    st.write(f"고객 ID: {customer_id}")
        else:
            st.markdown(
                """
            <div style="text-align: center; padding: 4rem; color: #6c757d;">
                <h3>👈 왼쪽에서 고객을 선택해주세요</h3>
                <p>고객을 선택하면 프로필과 추천 서비스를 이용하실 수 있습니다.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
