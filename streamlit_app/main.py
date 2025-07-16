def initialize_system():
    """시스템 초기화 - 디버깅 강화"""
    try:
        with st.spinner("🔥 초경량 시스템 초기화 중..."):
            # 데이터 로더 초기화
            data_loader = UltraMinimalDataLoader()

            # 추천 엔진 초기화
            recommendation_engine = UltraMinimalRecommendationEngine()

            # 데이터 로딩
            customers, transactions, products = data_loader.load_data()

            # 데이터 검증
            st.write("📊 **데이터 로딩 상태:**")
            st.write(f"- 고객 수: {len(customers):,}명")
            st.write(f"- 거래 수: {len(transactions):,}건")
            st.write(f"- 상품 수: {len(products):,}개")

            # 상품 데이터 샘플 확인
            if len(products) > 0:
                st.write("🛍️ **상품 데이터 샘플:**")
                st.dataframe(products.head())

                # 우유 관련 상품 확인
                if "product_name" in products.columns:
                    milk_products = products[
                        products["product_name"].str.contains(
                            "우유|milk", case=False, na=False
                        )
                    ]
                    st.write(f"🥛 우유 관련 상품: {len(milk_products)}개")
                    if len(milk_products) > 0:
                        st.dataframe(milk_products[["product_name", "category"]].head())

            # 추천 엔진 학습
            recommendation_engine.fit(transactions, products)

            # 세션 상태에 저장
            st.session_state.customers = customers
            st.session_state.transactions = transactions
            st.session_state.products = products
            st.session_state.recommendation_engine = recommendation_engine
            st.session_state.system_initialized = True

            st.success("✅ 초경량 시스템 로딩 완료!")
            return True

    except Exception as e:
        st.error(f"시스템 초기화 오류: {str(e)}")
        st.error(f"오류 상세: {traceback.format_exc()}")
        return False


# main.py에 추가
st.markdown(
    """
<style>
    /* 다크모드 대응 */
    .stApp > div {
        background-color: var(--background-color);
    }
    
    /* 추천 카드 호버 효과 */
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* 텍스트 가독성 개선 */
    .product-title {
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
</style>
""",
    unsafe_allow_html=True,
)
