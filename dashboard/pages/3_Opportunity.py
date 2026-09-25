from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import streamlit as st
from app.config import settings
from app.database import SessionLocal, init_db
from app.models import Apartment, Transaction
from app.services.finance_service import FinanceProfile, buying_power
from app.services.opportunity_service import classify_opportunity
from app.services.price_analysis_service import analyze_transactions

st.set_page_config(page_title="Opportunity - Real Estate Radar", page_icon="🎯", layout="wide")
st.title("🎯 Opportunity")
st.info("기회 판정은 실거래·거래량·출퇴근·입력 자금 조건의 일치 여부입니다. 가격 상승 예측이 아닙니다.")

finance_path = Path(__file__).resolve().parents[2] / "data" / "user_finance.json"
profile = FinanceProfile()
if finance_path.exists():
    profile = FinanceProfile(**json.loads(finance_path.read_text(encoding="utf-8")))
power = buying_power(profile)

init_db()
with SessionLocal() as db:
    apartments = db.query(Apartment).join(Apartment.watchlist).all()
    rows = []
    for apt in apartments:
        watch = apt.watchlist
        area = watch.preferred_area_min if watch and watch.preferred_area_min else 59.0
        transactions = db.query(Transaction).filter_by(apartment_id=apt.id).all()
        stats = analyze_transactions(transactions, area)
        result = classify_opportunity(stats, power, apt.yeouido_commute_min, settings.target_commute_min)
        rows.append({
            "판정": result.status,
            "단지": apt.name,
            "관심 면적군": f"{area:.1f}㎡",
            "최근 실거래(억)": stats.latest_price / 100_000_000 if stats.latest_price else None,
            "12개월 평균(억)": stats.avg_12m / 100_000_000 if stats.avg_12m else None,
            "여의도(분)": apt.yeouido_commute_min,
            "근거": " · ".join(result.reasons) if result.reasons else "-",
        })

if not rows:
    st.caption("Watchlist에 단지를 등록하고 데이터를 수집하면 판정표가 표시됩니다.")
else:
    order = {"OPPORTUNITY": 0, "WATCH": 1, "NORMAL": 2}
    df = pd.DataFrame(sorted(rows, key=lambda r: order[r["판정"]]))
    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        column_config={
            "최근 실거래(억)": st.column_config.NumberColumn(format="%.2f"),
            "12개월 평균(억)": st.column_config.NumberColumn(format="%.2f"),
        },
    )
