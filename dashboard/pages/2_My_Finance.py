from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import streamlit as st
from app.services.finance_service import FinanceProfile, buying_power

FINANCE_PATH = Path(__file__).resolve().parents[2] / "data" / "user_finance.json"

st.set_page_config(page_title="내 자금 - Real Estate Radar", page_icon="💰")
st.title("💰 내 자금")
st.caption("입력한 값은 이 컴퓨터의 data/user_finance.json에만 저장되며, 어디에도 전송되지 않습니다.")

profile = FinanceProfile()
if FINANCE_PATH.exists():
    profile = FinanceProfile(**json.loads(FINANCE_PATH.read_text(encoding="utf-8")))


def man_won(value: int) -> int:
    return value // 10_000


with st.form("finance_form"):
    st.markdown("금액은 **만 원** 단위로 입력하세요. (예: 1억 원 = 10000)")
    cash = st.number_input("보유 현금(만 원)", min_value=0, value=man_won(profile.cash), step=100)
    company_loan_limit = st.number_input("사내대출 한도(만 원)", min_value=0, value=man_won(profile.company_loan_limit), step=100)
    company_loan_balance = st.number_input("사내대출 기사용 잔액(만 원)", min_value=0, value=man_won(profile.company_loan_balance), step=100)
    mortgage_limit = st.number_input("예상 주택담보대출 한도(만 원)", min_value=0, value=man_won(profile.mortgage_limit), step=100)
    emergency_cash = st.number_input("남겨둘 비상자금(만 원)", min_value=0, value=man_won(profile.emergency_cash), step=100)
    submitted = st.form_submit_button("저장", type="primary")

if submitted:
    new_profile = FinanceProfile(
        cash=int(cash) * 10_000,
        company_loan_limit=int(company_loan_limit) * 10_000,
        company_loan_balance=int(company_loan_balance) * 10_000,
        mortgage_limit=int(mortgage_limit) * 10_000,
        emergency_cash=int(emergency_cash) * 10_000,
    )
    FINANCE_PATH.write_text(json.dumps(new_profile.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")
    st.success("저장했습니다.")
    profile = new_profile

st.metric("예상 매수 가능 금액", f"{buying_power(profile) / 100_000_000:.2f}억 원")
st.caption("보유 현금 - 비상자금 + 사용 가능한 사내대출 + 주택담보대출 한도. 대출 심사·세금·중개보수를 반영하지 않은 단순 참고치입니다.")
