from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
import pandas as pd
from sqlalchemy.orm import joinedload
from app.database import SessionLocal, init_db
from app.models import Apartment, Transaction
from app.services.env_service import get_env_value
from app.services.finance_service import FinanceProfile, buying_power
from app.services.price_analysis_service import analyze_transactions
from app.services.watchlist_service import WATCHLIST_PATH

st.set_page_config(page_title="Real Estate Radar", page_icon="🏠", layout="wide")
init_db()
st.title("🏠 Real Estate Radar")
st.caption("실거래 기반 매수 후보 탐지 · 가격 예측이나 투자 권유가 아닙니다")

finance_path = Path(__file__).resolve().parents[1] / "data" / "user_finance.json"
profile = FinanceProfile()
if finance_path.exists():
    profile = FinanceProfile(**json.loads(finance_path.read_text(encoding="utf-8")))
power = buying_power(profile)

with SessionLocal() as db:
    apartments = db.query(Apartment).options(joinedload(Apartment.watchlist)).all()
    tx_by_apt = {a.id: db.query(Transaction).filter_by(apartment_id=a.id).all() for a in apartments}
has_transactions = any(tx_by_apt.values())

has_api_key = bool(get_env_value("MOLIT_API_KEY"))
has_watchlist = WATCHLIST_PATH.exists() and WATCHLIST_PATH.stat().st_size > len("name,legal_dong_code,address,district,build_year,households,nearest_station,station_distance_m,yeouido_commute_min,latitude,longitude,preferred_area_min,preferred_area_max,target_price,priority,memo\n")
has_finance = finance_path.exists() and power > 0

steps = [
    ("① API 키 설정", has_api_key, "pages/0_Settings.py"),
    ("② 관심 단지 등록", has_watchlist, "pages/1_Watchlist.py"),
    ("③ 내 자금 입력", has_finance, "pages/2_My_Finance.py"),
    ("④ 데이터 수집", has_transactions, "pages/0_Settings.py"),
]
cols = st.columns(4)
for col, (label, done, page) in zip(cols, steps):
    with col:
        st.metric(label, "완료" if done else "필요")
        if not done:
            st.page_link(page, label="바로가기")

st.divider()
c1, c2 = st.columns(2)
c1.metric("입력 기준 예상 매수 가능 금액", f"{power / 100_000_000:.2f}억 원")
c2.caption("현금·대출 입력에 기반한 단순 계산이며 금융기관 심사를 대체하지 않습니다.")

rows = []
for apt in apartments:
    watch = apt.watchlist
    area = watch.preferred_area_min if watch and watch.preferred_area_min else 59.0
    stats = analyze_transactions(tx_by_apt[apt.id], area)
    rows.append({"단지": apt.name, "관심 면적군": f"{area:.1f}㎡", "최근 실거래": stats.latest_price / 100_000_000 if stats.latest_price else None, "12개월 평균": stats.avg_12m / 100_000_000 if stats.avg_12m else None, "24개월 고점 대비": stats.drawdown_from_24m_high, "최근 3개월 거래": stats.volume_3m, "직전 3개월 거래": stats.previous_volume_3m, "여의도(분)": apt.yeouido_commute_min})
if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df, width='stretch', hide_index=True, column_config={"최근 실거래": st.column_config.NumberColumn(format="%.2f억"), "12개월 평균": st.column_config.NumberColumn(format="%.2f억"), "24개월 고점 대비": st.column_config.NumberColumn(format="%.1%%")})
else:
    st.info("아직 등록된 관심 단지가 없습니다. 왼쪽 메뉴의 Watchlist에서 단지를 추가하세요.")

st.divider()
st.subheader("처음 사용하시나요?")
st.markdown("왼쪽 사이드바 메뉴 순서대로 진행하면 됩니다: **Settings → Watchlist → My_Finance → Settings(데이터 수집)**")
