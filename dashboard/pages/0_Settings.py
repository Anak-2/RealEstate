from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import streamlit as st
from app import config
from app.services.env_service import get_env_value, set_env_value
from app.services.collection_service import collect_all
from app.services.molit_service import MolitApartmentTradeClient

st.set_page_config(page_title="설정 - Real Estate Radar", page_icon="⚙️")
st.title("⚙️ 설정")
st.caption("맨 처음 한 번만 하면 되는 설정입니다.")

st.header("1. 국토교통부 API 키")
st.markdown(
    "국토교통부 실거래가 데이터를 받아오려면 공공데이터포털의 서비스키가 필요합니다.\n\n"
    "1. [공공데이터포털](https://www.data.go.kr) 접속 후 회원가입/로그인\n"
    "2. \"아파트매매 실거래 상세자료\" 검색 후 활용신청 (승인까지 보통 몇 분~몇 시간)\n"
    "3. 마이페이지 > 개발계정에서 발급된 **일반 인증키(Decoding)** 를 복사\n"
    "4. 아래에 붙여넣고 저장"
)
current_key = get_env_value("MOLIT_API_KEY")
with st.form("api_key_form"):
    new_key = st.text_input("서비스키", value=current_key, type="password")
    submitted = st.form_submit_button("저장")
if submitted:
    set_env_value("MOLIT_API_KEY", new_key.strip())
    config.settings.molit_api_key = new_key.strip()
    st.success("저장했습니다.")
    current_key = new_key.strip()

if current_key:
    st.success("API 키가 설정되어 있습니다.")
else:
    st.warning("API 키가 아직 없습니다. 저장 후 아래 연결 테스트를 눌러보세요.")

if st.button("연결 테스트"):
    with st.spinner("국토교통부 API에 연결하는 중..."):
        try:
            from datetime import date
            client = MolitApartmentTradeClient(api_key=current_key)
            client.get_transactions("11560", date.today().strftime("%Y%m"))
            st.success("연결에 성공했습니다.")
        except Exception as exc:  # noqa: BLE001
            st.error(f"연결 실패: {exc}")

st.divider()
st.header("2. 실거래 데이터 수집")
st.markdown("Watchlist 페이지에서 관심 단지를 등록한 뒤 실행하세요. 등록된 단지 수와 개월 수에 따라 시간이 걸릴 수 있습니다.")
months = st.slider("수집할 개월 수", min_value=1, max_value=24, value=24)
if st.button("데이터 수집 시작", type="primary"):
    if not get_env_value("MOLIT_API_KEY"):
        st.error("먼저 API 키를 저장하세요.")
    else:
        progress = st.progress(0.0)
        log = st.empty()
        lines: list[str] = []
        for ratio, message in collect_all(months):
            progress.progress(min(ratio, 1.0))
            lines.append(message)
            log.text("\n".join(lines[-15:]))
        st.success("수집이 끝났습니다. Home 화면에서 결과를 확인하세요.")
