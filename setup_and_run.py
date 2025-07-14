#!/usr/bin/env python3
"""
고객 군집별 추천시스템 프로젝트 설정 및 실행 스크립트
"""

import os
import sys
import subprocess
import json


def create_project_structure():
    """프로젝트 폴더 구조 생성"""

    # 프로젝트 폴더 구조 정의
    folders = [
        "customer_recommendation_app",
        "customer_recommendation_app/data",
        "customer_recommendation_app/data/raw",
        "customer_recommendation_app/data/processed",
        "customer_recommendation_app/models",
        "customer_recommendation_app/src",
        "customer_recommendation_app/src/utils",
        "customer_recommendation_app/src/recommendation",
        "customer_recommendation_app/src/customer",
        "customer_recommendation_app/streamlit_app",
        "customer_recommendation_app/streamlit_app/pages",
        "customer_recommendation_app/streamlit_app/components",
        "customer_recommendation_app/config",
        "customer_recommendation_app/notebooks",
        "customer_recommendation_app/tests",
        "customer_recommendation_app/assets",
        "customer_recommendation_app/assets/images",
    ]

    # 폴더 생성
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ 폴더 생성: {folder}")

    # __init__.py 파일 생성
    init_files = [
        "customer_recommendation_app/src/__init__.py",
        "customer_recommendation_app/src/utils/__init__.py",
        "customer_recommendation_app/src/recommendation/__init__.py",
        "customer_recommendation_app/src/customer/__init__.py",
        "customer_recommendation_app/streamlit_app/__init__.py",
        "customer_recommendation_app/streamlit_app/pages/__init__.py",
        "customer_recommendation_app/streamlit_app/components/__init__.py",
    ]

    for init_file in init_files:
        with open(init_file, "w", encoding="utf-8") as f:
            f.write("# -*- coding: utf-8 -*-\n")
        print(f"✅ __init__.py 생성: {init_file}")


def create_core_files():
    """핵심 파일들 생성"""

    # main.py 생성
    main_py_content = '''import streamlit as st
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
from src.recommendation.recommendation_engine import RecommendationEngine
from src.utils.data_generator import DataGenerator
from streamlit_app.components.customer_profile import render_customer_profile
from streamlit_app.components.chat_interface import render_chat_interface

# 페이지 설정
st.set_page_config(
    page_title="고객 군집별 추천시스템",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
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
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """데이터 로딩 (캐시됨)"""
    data_gen = DataGenerator()
    
    # 샘플 데이터 생성
    transactions = data_gen.generate_transactions(n_customers=100, n_transactions=5000)
    customers = data_gen.generate_customers(n_customers=100)
    products = data_gen.generate_products(n_products=500)
    
    return transactions, customers, products

@st.cache_resource
def initialize_system():
    """시스템 초기화 (캐시됨)"""
    transactions, customers, products = load_data()
    
    # 고객 관리자 초기화
    customer_manager = CustomerManager()
    customer_manager.load_data(customers, transactions)
    
    # 추천 엔진 초기화
    recommendation_engine = RecommendationEngine()
    recommendation_engine.fit(transactions, products)
    
    return customer_manager, recommendation_engine, customers, products, transactions

def main():
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🛍️ 고객 군집별 추천시스템</h1>
        <p>AI 기반 개인화 상품 추천 서비스</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 시스템 초기화
    try:
        customer_manager, recommendation_engine, customers, products, transactions = initialize_system()
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
        st.stop()
    
    # 레이아웃 구성
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 👥 고객 목록")
        
        # 세그먼트 필터
        segments = customers['segment'].unique()
        selected_segment = st.selectbox(
            "세그먼트 필터",
            ["전체"] + list(segments)
        )
        
        # 고객 목록 필터링
        if selected_segment != "전체":
            filtered_customers = customers[customers['segment'] == selected_segment]
        else:
            filtered_customers = customers
        
        # 고객 카드 렌더링
        if 'selected_customer' not in st.session_state:
            st.session_state.selected_customer = None
        
        for idx, customer in filtered_customers.head(20).iterrows():
            with st.container():
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    st.markdown(f"""
                    <div class="customer-card">
                        <strong>고객 {customer['customer_id']}</strong><br>
                        <small>{customer['segment']}</small><br>
                        <small>💰 ${customer['total_spent']:,.0f} | 📦 {customer['frequency']}회</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_b:
                    if st.button("선택", key=f"btn_{customer['customer_id']}"):
                        st.session_state.selected_customer = customer['customer_id']
                        st.rerun()
    
    with col2:
        if st.session_state.selected_customer:
            # 선택된 고객 정보
            customer_id = st.session_state.selected_customer
            customer_info = customers[customers['customer_id'] == customer_id].iloc[0]
            
            # 탭 구성
            tab1, tab2 = st.tabs(["👤 고객 프로필", "💬 상품 추천 채팅"])
            
            with tab1:
                render_customer_profile(
                    customer_info, 
                    customer_manager, 
                    transactions, 
                    products
                )
            
            with tab2:
                render_chat_interface(
                    customer_id,
                    recommendation_engine,
                    products,
                    customer_info
                )
        else:
            st.markdown("""
            <div style="text-align: center; padding: 4rem; color: #6c757d;">
                <h3>👈 왼쪽에서 고객을 선택해주세요</h3>
                <p>고객을 선택하면 프로필과 추천 서비스를 이용하실 수 있습니다.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
'''

    with open(
        "customer_recommendation_app/streamlit_app/main.py", "w", encoding="utf-8"
    ) as f:
        f.write(main_py_content)
    print("✅ main.py 생성 완료")


def create_requirements():
    """requirements.txt 생성"""
    requirements = """streamlit==1.28.0
pandas==2.1.0
numpy==1.24.3
scikit-learn==1.3.0
plotly==5.15.0
seaborn==0.12.2
matplotlib==3.7.2
altair==5.0.1
python-dotenv==1.0.0
pillow==10.0.0"""

    with open(
        "customer_recommendation_app/requirements.txt", "w", encoding="utf-8"
    ) as f:
        f.write(requirements)
    print("✅ requirements.txt 생성 완료")


def create_config():
    """config.json 생성"""
    config = {
        "app": {
            "title": "고객 군집별 추천시스템",
            "description": "AI 기반 개인화 상품 추천 시스템",
            "version": "1.0.0",
        },
        "model": {
            "min_interactions": 5,
            "n_recommendations": 10,
            "similarity_threshold": 0.3,
        },
        "segments": {
            "premium_loyal": "프리미엄 장기 고객",
            "premium_focused": "프리미엄 집중 고객",
            "excellent_loyal": "우수 충성 고객",
            "excellent_general": "우수 일반 고객",
            "general_value": "일반 가성비 고객",
            "at_risk": "이탈 위험 고객",
            "new_customer": "신규 유입 고객",
        },
    }

    with open(
        "customer_recommendation_app/config/config.json", "w", encoding="utf-8"
    ) as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("✅ config.json 생성 완료")


def create_readme():
    """README.md 생성"""
    readme = """# 고객 군집별 추천시스템

## 프로젝트 개요
AI 기반 고객 세그먼트별 개인화 상품 추천 시스템

## 주요 기능
- 고객 프로필 및 세그먼트 분석
- 구매 이력 기반 개인화 추천
- 실시간 채팅 UI 상품 검색
- 연관 상품 추천

## 설치 및 실행

### 1. 프로젝트 설정
```bash
# 이 스크립트 실행
python setup_and_run.py setup
```

### 2. 의존성 설치
```bash
cd customer_recommendation_app
pip install -r requirements.txt
```

### 3. 앱 실행
```bash
# 메인 앱 실행
streamlit run streamlit_app/main.py

# 또는 스크립트로 실행
python ../setup_and_run.py run
```

## 프로젝트 구조
```
customer_recommendation_app/
├── data/                           # 데이터 파일
│   ├── raw/                       # 원시 데이터
│   └── processed/                 # 전처리된 데이터
├── models/                        # 학습된 모델
├── src/                          # 핵심 로직
│   ├── customer/                 # 고객 관리
│   ├── recommendation/           # 추천 엔진
│   └── utils/                    # 유틸리티
├── streamlit_app/               # Streamlit 앱
│   ├── components/              # UI 컴포넌트
│   ├── pages/                   # 페이지
│   └── main.py                  # 메인 앱
├── config/                      # 설정 파일
├── notebooks/                   # 분석 노트북
└── tests/                       # 테스트 코드
```

## 사용법

### 1. 고객 선택
- 왼쪽 사이드바에서 세그먼트 필터링
- 고객 카드를 클릭하여 선택

### 2. 고객 프로필 확인
- 고객 기본 정보
- 구매 패턴 분석
- 선호 카테고리
- 최근 구매 이력

### 3. 상품 추천 채팅
- 채팅 인터페이스에서 상품명 입력
- AI가 개인화된 추천 상품 제시
- 연관 상품 및 대안 상품 추천

## 개발팀
- 채윤님: 고객 군집별 상품 연관성 분석
- 이정님: 쿠폰 및 캠페인 최적화

## 기술 스택
- **Frontend**: Streamlit
- **Backend**: Python
- **ML**: scikit-learn, NumPy, Pandas
- **Visualization**: Plotly, Matplotlib
"""

    with open("customer_recommendation_app/README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print("✅ README.md 생성 완료")


def copy_source_files():
    """소스 파일들 복사"""

    # 여기서는 실제로는 각 파일을 개별적으로 생성해야 합니다
    # 이전에 만든 아티팩트들의 내용을 파일로 저장하는 코드가 필요합니다

    print("📝 소스 파일 생성 가이드:")
    print("1. customer_manager.py를 src/customer/ 폴더에 저장")
    print("2. recommendation_engine.py를 src/recommendation/ 폴더에 저장")
    print("3. data_generator.py를 src/utils/ 폴더에 저장")
    print("4. customer_profile.py를 streamlit_app/components/ 폴더에 저장")
    print("5. chat_interface.py를 streamlit_app/components/ 폴더에 저장")


def install_dependencies():
    """의존성 설치"""
    try:
        os.chdir("customer_recommendation_app")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )
        print("✅ 의존성 설치 완료")
    except subprocess.CalledProcessError as e:
        print(f"❌ 의존성 설치 실패: {e}")
    except Exception as e:
        print(f"❌ 오류: {e}")


def run_app():
    """앱 실행"""
    try:
        os.chdir("customer_recommendation_app")
        subprocess.run(["streamlit", "run", "streamlit_app/main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 앱 실행 실패: {e}")
    except FileNotFoundError:
        print("❌ streamlit이 설치되지 않았습니다. 먼저 의존성을 설치하세요.")
    except Exception as e:
        print(f"❌ 오류: {e}")


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python setup_and_run.py [setup|install|run|all]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "setup":
        print("🏗️ 프로젝트 설정 시작...")
        create_project_structure()
        create_core_files()
        create_requirements()
        create_config()
        create_readme()
        copy_source_files()
        print("\n🎉 프로젝트 설정 완료!")
        print("📌 다음 단계:")
        print("1. python setup_and_run.py install")
        print("2. 소스 파일들을 각 폴더에 복사")
        print("3. python setup_and_run.py run")

    elif command == "install":
        print("📦 의존성 설치 시작...")
        install_dependencies()

    elif command == "run":
        print("🚀 앱 실행...")
        run_app()

    elif command == "all":
        print("🔧 전체 설정 및 실행...")
        create_project_structure()
        create_core_files()
        create_requirements()
        create_config()
        create_readme()
        copy_source_files()
        print("\n⏳ 의존성 설치 중...")
        install_dependencies()
        print("\n🚀 앱 실행...")
        run_app()

    else:
        print("❌ 잘못된 명령어입니다.")
        print("사용 가능한 명령어: setup, install, run, all")


if __name__ == "__main__":
    main()
