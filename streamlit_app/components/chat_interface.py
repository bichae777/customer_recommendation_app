def get_minimal_recommendations(
    recommendation_engine, customer_id: str, query: str, segment: str
) -> List[Dict]:
    """최소한 안전 추천 생성 - 디버깅 강화"""

    recommendations = []

    try:
        # 디버깅 정보 추가
        st.write(f"🔍 검색어: {query}")
        st.write(f"👤 고객 ID: {customer_id}")
        st.write(f"📊 세그먼트: {segment}")

        # 추천 엔진 체크
        if recommendation_engine is None:
            st.error("추천 엔진이 None입니다.")
            return []

        if not hasattr(recommendation_engine, "get_recommendations"):
            st.error("추천 엔진에 get_recommendations 메소드가 없습니다.")
            return []

        # 추천 생성 전 상태 확인
        if hasattr(recommendation_engine, "products"):
            st.write(f"📦 로드된 상품 수: {len(recommendation_engine.products)}")
            # 상품 이름에 '우유'가 포함된 상품 찾기
            if hasattr(recommendation_engine.products, "product_name"):
                milk_products = recommendation_engine.products[
                    recommendation_engine.products["product_name"].str.contains(
                        "우유", na=False
                    )
                ]
                st.write(f"🥛 우유 관련 상품: {len(milk_products)}개")
                if len(milk_products) > 0:
                    st.write(milk_products[["product_name", "category"]].head())

        # 추천 생성
        result = recommendation_engine.get_recommendations(
            customer_id=str(customer_id),
            product_query=str(query),
            n_recommendations=6,
            customer_segment=str(segment),
        )

        # 결과 디버깅
        st.write(f"📋 추천 결과 타입: {type(result)}")
        st.write(f"📋 추천 결과 길이: {len(result) if result else 0}")

        # 나머지 처리 로직은 동일...
        if result is None:
            st.warning("추천 엔진에서 None을 반환했습니다.")
            return []

        if not isinstance(result, list):
            st.warning(f"추천 결과가 리스트가 아닙니다: {type(result)}")
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
                            "product_name": str(
                                item.get("product_name", "Unknown Product")
                            ),
                            "category": str(item.get("category", "Unknown")),
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

                        safe_recommendations.append(safe_item)
            except Exception as e:
                st.error(f"추천 아이템 처리 오류: {str(e)}")
                continue

        return safe_recommendations

    except Exception as e:
        st.error(f"추천 엔진 오류: {str(e)}")
        st.error(f"오류 상세: {traceback.format_exc()}")
        return []
