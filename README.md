# 고객 군집별 추천시스템

## 프로젝트 개요
AI 기반 고객 세그먼트별 개인화 상품 추천 시스템

## 주요 기능
- 🎯 고객 프로필 및 세그먼트 분석
- 🛍️ 구매 이력 기반 개인화 추천  
- 💬 실시간 채팅 UI 상품 검색
- 🔗 연관 상품 추천

## 설치 및 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# Streamlit 앱 실행
streamlit run streamlit_app/main.py
```

## 프로젝트 구조
```
customer_recommendation_app/
├── data/                   # 데이터 파일
├── models/                 # 학습된 모델
├── src/                    # 핵심 로직
├── streamlit_app/          # Streamlit 앱
├── config/                 # 설정 파일
├── notebooks/              # 분석 노트북
└── tests/                  # 테스트 코드
```

## 개발팀
- 채윤님: 고객 군집별 상품 연관성 분석
- 이정님: 쿠폰 및 캠페인 최적화
