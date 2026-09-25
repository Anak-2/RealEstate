@echo off
cd /d "%~dp0"

if not exist ".venv" (
    echo [1/2] Python 가상환경을 만드는 중입니다. 처음 한 번만 실행됩니다...
    py -3.12 -m venv .venv 2>nul || py -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

if not exist ".env" copy ".env.example" ".env" >nul
if not exist "data\watchlist.csv" copy "data\watchlist.example.csv" "data\watchlist.csv" >nul
if not exist "data\user_finance.json" copy "data\user_finance.example.json" "data\user_finance.json" >nul

python scripts\init_db.py

echo.
echo Real Estate Radar를 시작합니다. 잠시 후 브라우저가 자동으로 열립니다.
echo 종료하려면 이 검은 창을 닫으세요.
echo.
streamlit run dashboard\Home.py
pause
