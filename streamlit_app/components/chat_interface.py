import streamlit as st
import traceback
from typing import List, Dict


# --- 채팅 인터페이스 (고속 + 실제 상품 매칭) ---
def render_chat_interface(
    customer_manager, recommendation_engine, selected_customer, customer_segment=None
):
    st.subheader("💬 AI 상품 추천 채팅 (고속 & 실상품 매칭)")
    # 대화 히스토리 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 사용자 입력
    user_input = st.chat_input("상품명을 입력하세요 (예: 우유, 빵, 치킨...)")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # AI 추천 생성 (고속, 최대 3개)
        try:
            recs = recommendation_engine.get_recommendations(
                customer_id=str(selected_customer),
                product_query=user_input,
                n_recommendations=3,
                customer_segment=str(customer_segment),
            )
        except Exception:
            recs = []
            tb = traceback.format_exc()
            st.error("🔴 추천 생성 오류 발생:")
            st.code(tb, language="bash")

        # 기본 추천 표시
        if recs:
            st.markdown("**🛍️ AI 추천 상품:**")
            for r in recs:
                name = r.get("product_name", "")
                cat = r.get("category", "")
                price = r.get("price", 0.0)
                st.markdown(f"- {name} | {cat} | ${price:.2f}")

        # 실제 상품 데이터 기반 유사 제안
        try:
            # recommendation_engine에서 제공하는 검색 함수 사용
            similar = recommendation_engine.search_products(user_input, limit=3)
        except Exception:
            similar = []
        if similar:
            st.markdown(f"**💡 '{user_input}'와(과) 유사한 실상품 제안:**")
            for p in similar:
                pname = p.get("product_name", p.get("COMMODITY_DESC", ""))
                pcat = p.get("category", p.get("DEPARTMENT", ""))
                st.markdown(f"- {pname} | {pcat}")

    # 대화 히스토리 출력
    for msg in st.session_state.chat_history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            st.markdown(
                f"<div style='text-align:right;color:white;background:#007acc;padding:8px;border-radius:8px'>{content}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='text-align:left;color:#333;background:#f0f0f0;padding:8px;border-radius:8px'>{content}</div>",
                unsafe_allow_html=True,
            )


# --- 메인 앱 ---
def main():
    st.title("🤖 고객 군집별 추천 시스템 (고속 Real)")
    st.sidebar.header("👥 고객 목록")
    selected_customer = st.sidebar.selectbox("고객 선택", options=["default"])
    customer_segment = "general_value"
    # recommendation_engine은 미리 fit된 인스턴스를 전달
    render_chat_interface(
        customer_manager=None,
        recommendation_engine=recommendation_engine,
        selected_customer=selected_customer,
        customer_segment=customer_segment,
    )


if __name__ == "__main__":
    main()
