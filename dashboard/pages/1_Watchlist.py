from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import streamlit as st
from app.database import SessionLocal, init_db
from app.services.watchlist_service import sync_watchlist_from_csv, WATCHLIST_PATH

st.set_page_config(page_title="관심 단지 - Real Estate Radar", page_icon="🏢", layout="wide")
st.title("🏢 관심 단지 (Watchlist)")
st.caption("표를 엑셀처럼 편집한 뒤 저장하세요. 행 끝의 빈 줄을 채우면 단지가 추가됩니다.")

with st.expander("법정동코드는 어디서 찾나요?"):
    st.markdown(
        "[행정표준코드관리시스템](https://www.code.go.kr/stdcode/regCodeL.do) 에서 "
        "구 이름으로 검색하면 앞 5자리 숫자 코드를 확인할 수 있습니다. "
        "예: 영등포구 = 11560, 강서구 = 11500"
    )

COLUMNS = ["name", "legal_dong_code", "address", "district", "build_year", "households", "nearest_station", "station_distance_m", "yeouido_commute_min", "latitude", "longitude", "preferred_area_min", "preferred_area_max", "target_price", "priority", "memo"]
INT_COLUMNS = ["build_year", "households", "station_distance_m", "yeouido_commute_min", "target_price", "priority"]
FLOAT_COLUMNS = ["latitude", "longitude", "preferred_area_min", "preferred_area_max"]

COLUMN_CONFIG = {
    "name": st.column_config.TextColumn("단지명", required=True),
    "legal_dong_code": st.column_config.TextColumn("법정동코드(5자리)", required=True, help="숫자 5자리, 예: 11560"),
    "address": st.column_config.TextColumn("주소"),
    "district": st.column_config.TextColumn("구"),
    "build_year": st.column_config.NumberColumn("준공년도", format="%d"),
    "households": st.column_config.NumberColumn("세대수", format="%d"),
    "nearest_station": st.column_config.TextColumn("인근역"),
    "station_distance_m": st.column_config.NumberColumn("역까지 거리(m)", format="%d"),
    "yeouido_commute_min": st.column_config.NumberColumn("여의도 출근(분)", format="%d"),
    "latitude": st.column_config.NumberColumn("위도", format="%.6f"),
    "longitude": st.column_config.NumberColumn("경도", format="%.6f"),
    "preferred_area_min": st.column_config.NumberColumn("관심 평형 최소(㎡)", format="%.1f"),
    "preferred_area_max": st.column_config.NumberColumn("관심 평형 최대(㎡)", format="%.1f"),
    "target_price": st.column_config.NumberColumn("목표가(원)", format="%d", help="예: 15억 = 1500000000"),
    "priority": st.column_config.NumberColumn("우선순위(1~5)", format="%d"),
    "memo": st.column_config.TextColumn("메모"),
}


def load_df() -> pd.DataFrame:
    if WATCHLIST_PATH.exists() and WATCHLIST_PATH.stat().st_size:
        df = pd.read_csv(WATCHLIST_PATH, dtype=str, keep_default_na=False)
    else:
        df = pd.DataFrame(columns=COLUMNS)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNS]
    for col in INT_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in FLOAT_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


edited = st.data_editor(
    load_df(),
    column_config=COLUMN_CONFIG,
    num_rows="dynamic",
    width='stretch',
    hide_index=True,
    key="watchlist_editor",
)

if st.button("저장", type="primary"):
    clean = edited.dropna(how="all")
    clean = clean[clean["name"].fillna("").astype(str).str.strip() != ""]
    errors = []
    for i, row in clean.iterrows():
        code = str(row["legal_dong_code"]).strip()
        if not (len(code) == 5 and code.isdigit()):
            errors.append(f"{row['name']}: 법정동코드는 숫자 5자리여야 합니다 (입력값: '{code}')")
    if errors:
        for e in errors:
            st.error(e)
    else:
        for col in INT_COLUMNS:
            clean[col] = clean[col].astype("Int64")
        clean.to_csv(WATCHLIST_PATH, index=False, encoding="utf-8-sig")
        init_db()
        with SessionLocal() as db:
            synced = sync_watchlist_from_csv(db, WATCHLIST_PATH)
        st.success(f"저장했습니다. {synced}개 단지가 반영되었습니다.")
        st.rerun()
