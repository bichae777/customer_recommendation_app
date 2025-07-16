def display_minimal_chat_history():
    """최소한 안전 채팅 히스토리 표시 - 스타일 개선"""

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

                # 추천 상품 표시 (스타일 개선)
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
                                product_name = str(
                                    rec.get("product_name", "Unknown Product")
                                )
                                category = str(rec.get("category", "Unknown"))
                                brand = str(rec.get("brand", "Unknown"))
                                price = rec.get("price", 5.0)
                                reason = str(rec.get("reason", "AI 추천"))

                                # 개선된 상품 카드 스타일
                                st.markdown(
                                    f"""
                                    <div style="
                                        border: 2px solid #e1e5e9; 
                                        border-radius: 12px; 
                                        padding: 16px; 
                                        margin: 8px 0;
                                        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                                        transition: transform 0.2s ease;
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
            continue  # 문제 있는 메시지는 건너뛰기
