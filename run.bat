@echo off
echo 🛍️ 고객 군집별 추천시스템 시작...

REM 가상환경이 있으면 활성화
if exist venv (
    echo 📦 가상환경 활성화...
    call venv\Scripts\activate
)

REM 의존성 설치 확인
echo 📋 의존성 확인 중...
pip install -r requirements.txt --quiet

REM Streamlit 앱 실행
echo 🚀 Streamlit 앱 실행...
streamlit run streamlit_app/main.py

pause
