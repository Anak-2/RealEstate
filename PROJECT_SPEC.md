# Real Estate Radar — 프로젝트 명세

원본 요구사항은 사용자가 제공한 `RealEstateRadar_PROJECT_SPEC.md`를 바탕으로 합니다. 이 프로젝트는 서울 서남권에서 실거주 매수 후보를 장기 추적하는 개인용 의사결정 지원 시스템입니다.

## MVP 우선순위

1. 관심 단지와 프로필을 로컬 CSV/JSON으로 관리
2. 국토교통부 아파트 매매 OpenAPI에서 거래 수집
3. SQLite에 중복 없이 저장하고 취소 여부 보존
4. 동일 단지·평형군의 최근 거래, 3/6/12/24개월 평균, 24개월 최고가, 거래량 및 하락률 계산
5. Streamlit 화면에서 목록 및 상세 지표 표시

## 기준 원칙

- 실거래가를 우선하고 호가만으로 시세를 판단하지 않습니다.
- 단지 전체 평균 대신 전용면적 평형군으로 비교합니다.
- Opportunity 상태는 사용자 조건의 일치 정도를 표시하며 수익률 예측이 아닙니다.
- API 키·개인 금융정보는 저장소에 커밋하지 않습니다.
- Phase 2 전월세, 정비사업 자동 수집, 알림은 제외합니다.

## 설정 파일

`data/watchlist.csv`의 필드: `name,legal_dong_code,address,district,build_year,households,nearest_station,station_distance_m,yeouido_commute_min,latitude,longitude,preferred_area_min,preferred_area_max,target_price,priority,memo`

`data/user_finance.json`은 연봉, 현금, 사내대출 한도/잔액, 예상 주담대 한도, 비상자금을 원 단위로 저장합니다.
