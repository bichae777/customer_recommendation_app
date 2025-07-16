# display_minimal_chat_history 함수에서 상품 카드 부분 수정
product_name = str(rec.get("product_name", "Unknown Product"))
category = str(rec.get("category", "Unknown"))
sub_category = str(rec.get("sub_category", "Unknown"))
brand = str(rec.get("brand", "Unknown"))
price = rec.get("price", 5.0)
reason = str(rec.get("reason", "AI 추천"))

# HTML 부분도 수정
st.markdown(
    f"""
<div style="...">
    <div style="...">
        🛒 {product_name}
    </div>
    <div style="...">
        <span style="...">
            {category}
        </span>
        <span style="...">
            {sub_category}
        </span>
        <span style="...">
            {brand}
        </span>
    </div>
    <div style="...">
        <span style="...">
            ${price:.2f}
        </span>
        <span style="...">
            {reason}
        </span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)
