import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
import traceback


def render_chat_interface(
    customer_manager, recommendation_engine, selected_customer, customer_segment=None
):
    """초경량 채팅 인터페이스"""

    st.subheader("💬 AI 상품 추천 채팅")

    # 채팅 히스토리 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 기본 세그먼트 설정
    segment = customer_segment if customer_segment else "general_value"

    # 고객 정보 표시
    if selected_customer:
        st.info(f"🎯 선택된 고객: {selected_customer} ({segment})")
    else:
        st.warning("고객을 먼저 선택해주세요.")

    # 빠른 추천 버튼들
    st.markdown("**빠른 추천:**")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("�� 유제품", key="quick_dairy"):
            st.session_state.quick_query = "milk"
    with col2:
        if st.button("🍞 빵류", key="quick_bread"):
            st.session_state.quick_query = "bread"
    with col3:
        if st.button("🍺 음료", key="quick_beverage"):
            st.session_state.quick_query = "beverage"
    with col4:
        if st.button("☕ 커피", key="quick_coffee"):
            st.session_state.quick_query = "coffee"

    # 채팅 입력
    user_input = st.chat_input("상품명을 입력하세요 (예: milk, bread, coffee...)")

    # 빠른 쿼리 처리
    try:
        if "quick_query" in st.session_state:
            user_input = st.session_state.quick_query
            del st.session_state.quick_query
    except:
        pass

    # 사용자 입력 처리
    if user_input:
        # 사용자 메시지 추가
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": str(user_input),
                "timestamp": str(pd.Timestamp.now()),
            }
        )

        # 추천 생성 시도
        try:
            with st.spinner("🤖 AI가 추천을 생성하는 중..."):
                recommendations = get_minimal_recommendations(
                    recommendation_engine=recommendation_engine,
                    customer_id=(
                        str(selected_customer) if selected_customer else "default"
                    ),
                    query=str(user_input),
                    segment=str(segment),
                )

                # 응답 메시지 생성
                rec_count = len(recommendations) if recommendations else 0

                if rec_count > 0:
                    response_content = f"'{user_input}' 검색 결과 {rec_count}개의 추천 상품을 찾았습니다!"
                else:
                    response_content = f"'{user_input}'와 관련된 상품을 찾지 못했습니다. 다른 검색어를 시도해보세요."

                # AI 응답 추가
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": str(response_content),
                        "recommendations": recommendations,
                        "timestamp": str(pd.Timestamp.now()),
                    }
                )

        except Exception as e:
            st.error(f"추천 생성 중 오류: {str(e)}")

            # 에러 응답 추가
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": "죄송합니다. 시스템에 일시적인 문제가 발생했습니다.",
                    "recommendations": [],
                    "timestamp": str(pd.Timestamp.now()),
                }
            )

    # 채팅 기록 지우기 버튼
    if st.button("🗑️ 채팅 기록 지우기", key="clear_chat_unique"):
        st.session_state.chat_history = []
        st.rerun()

    # 채팅 히스토리 표시
    display_minimal_chat_history()


def get_minimal_recommendations(
    recommendation_engine, customer_id: str, query: str, segment: str
) -> List[Dict]:
    """최소한 안전 추천 생성"""

    recommendations = []

    try:
        # 추천 엔진 체크
        if recommendation_engine is None:
            return []

        if not hasattr(recommendation_engine, "get_recommendations"):
            return []

        # 추천 생성
        result = recommendation_engine.get_recommendations(
            customer_id=str(customer_id),
            product_query=str(query),
            n_recommendations=6,
            customer_segment=str(segment),
        )

        # 결과 처리
        if result is None:
            return []

        if not isinstance(result, list):
            return []

        # 각 추천을 안전하게 변환
        safe_recommendations = []

        for item in result:
            try:
                if isinstance(item, dict):
                    product_id = item.get("product_id")
                    if product_id:
                        safe_item = {
                            "product_id": str(product_id),
                            "product_name": str(item.get("product_name", "Unknown Product")),
                            "category": str(item.get("category", "Unknown")),
                            "sub_category": str(item.get("sub_category", "Unknown")),
                            "brand": str(item.get("brand", "Unknown")),
                            "price": 5.0,
                            "reason": str(item.get("reason", "AI 추천")),
                            "similarity_to_query": 0.8,
                        }

                        # 가격 안전 변환
                        try:
                            price_val = item.get("price")
                            if price_val is not None:
                                safe_item["price"] = float(price_val)
                        except:
                            safe_item["price"] = 5.0

                        # 유사도 안전 변환
                        try:
                            sim_val = item.get("similarity_to_query")
                            if sim_val is not None:
                                safe_item["similarity_to_query"] = float(sim_val)
                        except:
                            safe_item["similarity_to_query"] = 0.8

                        safe_recommendations.append(safe_item)
            except:
                continue

        return safe_recommendations

    except Exception as e:
        st.error(f"추천 엔진 오류: {str(e)}")
        return []


def display_minimal_chat_history():
    """최소한 안전 채팅 히스토리 표시"""

    # 채팅 히스토리 체크
    history_count = 0
    try:
        history_count = len(st.session_state.chat_history)
    except:
        history_count = 0

    if history_count == 0:
        st.markdown(
            "👋 안녕하세요! 상품명을 입력하시면 AI가 관련 상품을 추천해드립니다."
        )
        return

    # 채팅 메시지 표시
    for idx in range(history_count):
        try:
            message = st.session_state.chat_history[idx]

            role = str(message.get("role", "user"))
            content = str(message.get("content", ""))

            if role == "user":
                # 사용자 메시지
                st.markdown(
                    f"""
                    <div style="
                        display: flex; 
                        justify-content: flex-end; 
                        margin: 10px 0;
                    ">
                        <div style="
                            background: #007acc; 
                            color: white; 
                            padding: 10px 15px; 
                            border-radius: 18px 18px 4px 18px; 
                            max-width: 70%;
                            font-size: 14px;
                        ">
                            {content}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:  # assistant
                # AI 응답 메시지
                st.markdown(
                    f"""
                    <div style="
                        display: flex; 
                        justify-content: flex-start; 
                        margin: 10px 0;
                    ">
                        <div style="
                            background: #f0f0f0; 
                            color: #333; 
                            padding: 10px 15px; 
                            border-radius: 18px 18px 18px 4px; 
                            max-width: 70%;
                            font-size: 14px;
                        ">
                            🤖 {content}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # 추천 상품 표시
                try:
                    recommendations = message.get("recommendations", [])
                    rec_count = len(recommendations) if recommendations else 0

                    if rec_count > 0:
                        st.markdown("**🛍️ 추천 상품:**")

                        # 최대 4개까지만 표시
                        display_count = min(rec_count, 4)

                        for i in range(display_count):
                            try:
                                rec = recommendations[i]
                                product_name = str(rec.get("product_name", "Unknown Product"))
                                category = str(rec.get("category", "Unknown"))
                                sub_category = str(rec.get("sub_category", "Unknown"))
                                brand = str(rec.get("brand", "Unknown"))
                                price = rec.get("price", 5.0)
                                reason = str(rec.get("reason", "AI 추천"))

                                # 상품 카드 표시
                                st.markdown(
                                    f"""
                                    <div style="
                                        border: 2px solid #e1e5e9; 
                                        border-radius: 12px; 
                                        padding: 16px; 
                                        margin: 8px 0;
                                        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                                    ">
                                        <div style="
                                            font-size: 16px;
                                            font-weight: bold;
                                            color: #2c3e50;
                                            margin-bottom: 8px;
                                        ">
                                            🛒 {product_name}
                                        </div>
                                        <div style="
                                            font-size: 14px;
                                            color: #5a6c7d;
                                            margin-bottom: 4px;
                                        ">
                                            <span style="background: #e3f2fd; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                                                {category}
                                            </span>
                                            <span style="background: #f3e5f5; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 4px;">
                                                {sub_category}
                                            </span>
                                            <span style="margin-left: 8px; font-weight: 500;">
                                                {brand}
                                            </span>
                                        </div>
                                        <div style="
                                            display: flex;
                                            justify-content: space-between;
                                            align-items: center;
                                            margin-top: 8px;
                                        ">
                                            <span style="
                                                font-size: 18px;
                                                font-weight: bold;
                                                color: #e74c3c;
                                            ">
                                                ${price:.2f}
                                            </span>
                                            <span style="
                                                font-size: 12px;
                                                color: #7f8c8d;
                                                font-style: italic;
                                            ">
                                                {reason}
                                            </span>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            except:
                                continue
                except:
                    pass
        except:
            continue
