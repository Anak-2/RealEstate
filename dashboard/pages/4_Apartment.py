from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import plotly.express as px
import streamlit as st
from app.database import SessionLocal, init_db
from app.models import Apartment, Transaction
from app.services.price_analysis_service import analyze_transactions, area_group

st.set_page_config(page_title="단지 상세 - Real Estate Radar", page_icon="📈", layout="wide")
st.title("📈 단지 상세")

init_db()
with SessionLocal() as db:
    apartments = db.query(Apartment).order_by(Apartment.name).all()
    if not apartments:
        st.info("단지별 가격 그래프는 거래 데이터가 수집되면 표시됩니다.")
        st.stop()

    names = [a.name for a in apartments]
    selected_name = st.selectbox("단지 선택", names)
    apt = next(a for a in apartments if a.name == selected_name)
    transactions = db.query(Transaction).filter_by(apartment_id=apt.id).order_by(Transaction.contract_date).all()

if not transactions:
    st.info("이 단지는 아직 수집된 실거래가 없습니다.")
    st.stop()

df = pd.DataFrame([{
    "계약일": t.contract_date,
    "평형군(㎡)": area_group(t.area_m2),
    "면적(㎡)": t.area_m2,
    "층": t.floor,
    "가격(억)": t.price / 100_000_000,
    "상태": "취소" if t.status == "CANCELLED" else "정상",
} for t in transactions])

groups = sorted(df["평형군(㎡)"].unique())
group = st.selectbox("평형군(㎡) 선택", groups)
group_df = df[df["평형군(㎡)"] == group].sort_values("계약일")

anchor_area = group_df["면적(㎡)"].iloc[0]
stats = analyze_transactions(transactions, anchor_area)
c1, c2, c3, c4 = st.columns(4)
c1.metric("최근 실거래", f"{stats.latest_price / 100_000_000:.2f}억" if stats.latest_price else "-")
c2.metric("12개월 평균", f"{stats.avg_12m / 100_000_000:.2f}억" if stats.avg_12m else "-")
c3.metric("24개월 최고가", f"{stats.max_24m / 100_000_000:.2f}억" if stats.max_24m else "-")
c4.metric("24개월 고점 대비", f"{stats.drawdown_from_24m_high:.1%}" if stats.drawdown_from_24m_high is not None else "-")

fig = px.scatter(group_df, x="계약일", y="가격(억)", color="상태", hover_data=["면적(㎡)", "층"])
st.plotly_chart(fig, width='stretch')

st.subheader("실거래 내역")
st.dataframe(group_df.sort_values("계약일", ascending=False), width='stretch', hide_index=True)
