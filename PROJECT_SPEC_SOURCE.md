# Real Estate Radar — 프로젝트 명세서

> 여의도 출퇴근권 주택 매수 기회를 장기 추적하기 위한 개인용 부동산 분석 시스템  
> 문서 버전: v0.1  
> 기준일: 2026-09-25

---

## 1. 프로젝트 개요

### 1.1 프로젝트명

**Real Estate Radar**

### 1.2 목적

향후 약 2년 이내 서울 서남권에서 실거주 목적의 주택을 매수하기 위해 다음 정보를 지속적으로 수집·분석한다.

- 아파트 실거래가 변화
- 거래량 변화
- 전세가 및 전세가율
- 사용자의 실제 매수 가능 금액
- 여의도 출퇴근 접근성
- 주변 정비사업 및 재개발/재건축 진행 상황
- 관심 단지의 가격 하락 및 거래 회복 신호
- 대출 정책 변화에 따른 매수 가능 금액 변화

이 시스템의 목표는 **집값을 예측하는 것**이 아니라,

> "내 조건에서 관심 있게 검토할 만한 매수 기회가 발생했는가?"

를 빠르게 탐지하는 것이다.

---

# 2. 사용자 시나리오

현재 기준 사용자의 주요 조건은 다음과 같다.

| 항목 | 값 |
|---|---:|
| 근무지 | 여의도 |
| 세전 연봉 | 약 1억 원 |
| 현재 현금 | 약 8,000만 원 |
| 사내대출 가능액 | 최대 1억 5,000만 원 |
| 주택 보유 | 무주택 |
| 생애최초 주택구입 | 미사용 |
| 희망 매수 시점 | 약 2년 이내 |
| 희망 주거 형태 | 최소 침실 1개 이상 분리 |
| 중요 요소 | 환금성, 거래량, 입지, 향후 정비사업 |
| 우선 관심지역 | 당산, 양평/선유도, 신길, 노량진/대방 |

> 자금 및 대출 조건은 변할 수 있으므로 코드에서는 고정값으로 두지 않고 사용자 프로필 데이터로 관리한다.

---

# 3. 핵심 원칙

## 3.1 "예측"보다 "탐지"

시스템은 다음과 같은 기능을 제공한다.

잘못된 방향:

```text
AI가 이 아파트는 2년 뒤 20% 오른다고 예측
```

지향하는 방향:

```text
12개월 평균보다 현재 실거래가가 10% 낮다.
최근 거래량은 회복 중이다.
현재 최저 호가와 최근 실거래의 차이가 작다.
여의도 출근 시간이 25분 이내다.
주변 정비사업이 사업시행인가 단계로 진행됐다.

→ 관심도 상승
```

즉, **의사결정 지원 시스템**으로 만든다.

---

## 3.2 실거래가 우선

가격 판단 우선순위:

1. 국토교통부 실거래가
2. 동일 전용면적 최근 거래
3. 현재 매도 호가
4. 전세 실거래
5. 주변 유사 단지 가격

호가만으로 시세를 판단하지 않는다.

---

## 3.3 아파트 우선

장기적인 환금성을 중요하게 보기 때문에 기본적으로 다음 순서를 사용한다.

```text
대단지 아파트
    ↓
중소규모 아파트
    ↓
정비사업 대상 아파트
    ↓
도시형생활주택
    ↓
연립/다세대
```

단, 재개발/재건축 물건은 별도의 분석 모델을 사용한다.

---

# 4. MVP 범위

## 4.1 MVP에서 지원할 기능

### A. 관심 단지 관리

사용자가 관심 단지를 등록한다.

예:

```text
당산동1가 코오롱
양평동1가 삼환
신길 삼성래미안
신길우성1차
노량진 신동아리버파크
```

각 단지에 다음 정보를 저장한다.

- 단지명
- 법정동
- 주소
- 준공연도
- 세대수
- 지하철역
- 역까지 거리
- 여의도 예상 출퇴근 시간
- 관심 평형

---

### B. 실거래 데이터 수집

국토교통부 실거래가 OpenAPI를 이용한다.

MVP에서는 먼저 **아파트 매매 실거래가**만 지원한다.

이후 확장:

- 아파트 전월세
- 연립·다세대
- 오피스텔
- 분양권
- 토지

---

### C. 가격 지표 계산

단지 + 전용면적별로 다음 값을 계산한다.

```text
최근 실거래가
최근 3개월 평균
최근 6개월 평균
최근 12개월 평균
최근 24개월 평균
최근 12개월 최고가
최근 12개월 최저가
최근 3개월 거래량
직전 3개월 거래량
12개월 거래량
고점 대비 하락률
```

---

### D. 개인 매수 가능 금액

사용자 금융정보를 기반으로 별도 계산한다.

```text
현금
사내대출
예상 주담대
취득 관련 비용
비상자금
```

예시:

```text
현금                  80,000,000
비상자금              20,000,000
사용 가능한 현금       60,000,000

사내대출             150,000,000
예상 주담대           380,000,000

---------------------------------
예상 매수 가능 금액    590,000,000
```

실제 대출 가능 여부는 금융기관 심사를 대체하지 않는다.

---

### E. Opportunity 탐지

다음 조건에 해당하는 단지를 자동으로 표시한다.

예:

```text
현재 실거래가 <= 12개월 평균 × 0.90

AND

최근 3개월 거래량 >= 직전 3개월 거래량

AND

여의도 출퇴근 <= 30분

AND

현재 가격 <= 개인 매수가능액 × 1.05
```

출력:

```text
🔥 Opportunity
👀 Watch
⚪ Normal
```

이는 투자 등급이나 향후 수익률 예측이 아니라 **사용자 정의 관심 조건 충족 여부**를 나타낸다.

---

# 5. 향후 확장 기능

## Phase 2

### 전세 분석

추가 데이터:

- 최근 전세 실거래
- 전세가율
- 전세 거래량

계산:

```text
전세가율 = 최근 전세가 / 최근 매매가
```

활용:

```text
매수 6.5억
전세 4.1억
전세가율 63%
```

---

### 매수 vs 전세 비교

예:

```text
[당산 XX아파트 59㎡]

매매      6.5억
전세      4.1억

매수 시 필요 자기자본  2.1억
월 예상 원리금          210만원

전세 시 필요 자기자본  0.8억
전세대출                3.3억

5년 보유 비용 비교
```

---

## Phase 3

### 정비사업 추적

정비사업 진행단계:

```text
후보지
→ 정비구역 지정
→ 추진위원회
→ 조합설립인가
→ 사업시행인가
→ 관리처분인가
→ 이주/철거
→ 착공
→ 준공
```

관심지역별 프로젝트를 저장한다.

예:

```text
양평신동아 재건축
신길 XX구역 재개발
노량진 1구역
노량진 3구역
```

변경사항을 히스토리로 저장한다.

---

## Phase 4

### 매물 호가 추적

주의:

부동산 플랫폼 페이지를 무단 크롤링하지 않는다.

가능한 경우:

- 공식 API
- 사용자가 직접 입력
- 허용된 데이터 공급자
- CSV import

로 호가 데이터를 추가한다.

---

## Phase 5

### 알림

예:

```text
당산 코오롱 59㎡ 실거래가가
최근 12개월 평균보다 12% 낮아졌습니다.

최근 3개월 거래량
2건 → 6건

현재 사용자 매수 가능 금액 범위 안입니다.
```

알림 수단 후보:

- Telegram
- Discord
- Email
- Web Push

---

# 6. 기술 스택

## 6.1 MVP 권장 구성

### Backend

```text
Python 3.12+
FastAPI
SQLAlchemy
Pydantic
APScheduler
```

Python을 추천하는 이유:

- 데이터 분석 라이브러리 활용
- 공공 API 연동 용이
- pandas 기반 통계 계산 편리
- 빠른 MVP 개발

---

### Database

초기:

```text
SQLite
```

향후:

```text
PostgreSQL
```

초기에는 SQLite로 충분하다.

---

### Frontend

MVP:

```text
Streamlit
```

또는

```text
FastAPI
+
React
```

개발 속도를 우선하면 Streamlit을 먼저 사용한다.

---

### Chart

```text
Plotly
```

화면:

- 가격 추이
- 거래량
- 전세가율
- 매수가능액 비교

---

# 7. 프로젝트 디렉터리 구조

권장 프로젝트 폴더:

```text
RealEstateRadar/
│
├─ README.md
├─ PROJECT_SPEC.md
├─ requirements.txt
├─ .env.example
├─ .gitignore
│
├─ app/
│  ├─ __init__.py
│  │
│  ├─ main.py
│  │
│  ├─ config.py
│  │
│  ├─ database.py
│  │
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ apartment.py
│  │  ├─ transaction.py
│  │  ├─ redevelopment.py
│  │  ├─ user_finance.py
│  │  └─ opportunity.py
│  │
│  ├─ schemas/
│  │  ├─ apartment.py
│  │  ├─ transaction.py
│  │  └─ finance.py
│  │
│  ├─ repositories/
│  │  ├─ apartment_repository.py
│  │  ├─ transaction_repository.py
│  │  └─ redevelopment_repository.py
│  │
│  ├─ services/
│  │  ├─ molit_service.py
│  │  ├─ price_analysis_service.py
│  │  ├─ finance_service.py
│  │  ├─ opportunity_service.py
│  │  └─ redevelopment_service.py
│  │
│  ├─ collectors/
│  │  ├─ apartment_trade_collector.py
│  │  └─ redevelopment_collector.py
│  │
│  └─ api/
│     ├─ apartments.py
│     ├─ transactions.py
│     └─ dashboard.py
│
├─ dashboard/
│  ├─ Home.py
│  └─ pages/
│     ├─ 1_Opportunity.py
│     ├─ 2_Watchlist.py
│     ├─ 3_Apartment.py
│     ├─ 4_Redevelopment.py
│     └─ 5_My_Finance.py
│
├─ scripts/
│  ├─ init_db.py
│  ├─ seed_watchlist.py
│  └─ collect_transactions.py
│
├─ tests/
│  ├─ test_price_analysis.py
│  ├─ test_finance.py
│  └─ test_opportunity.py
│
├─ data/
│  └─ .gitkeep
│
└─ docs/
   ├─ api.md
   ├─ database.md
   └─ scoring.md
```

---

# 8. DB 설계

## 8.1 apartments

```sql
CREATE TABLE apartments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    legal_dong_code TEXT,
    address TEXT,
    district TEXT,
    build_year INTEGER,
    households INTEGER,
    nearest_station TEXT,
    station_distance_m INTEGER,
    yeouido_commute_min INTEGER,
    latitude REAL,
    longitude REAL,
    created_at DATETIME,
    updated_at DATETIME
);
```

---

## 8.2 transactions

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    apartment_id INTEGER NOT NULL,

    contract_date DATE NOT NULL,

    area_m2 REAL NOT NULL,
    floor INTEGER,
    price INTEGER NOT NULL,

    transaction_type TEXT,
    cancellation_date DATE,

    created_at DATETIME,

    FOREIGN KEY(apartment_id)
        REFERENCES apartments(id)
);
```

price 단위는 원을 권장한다.

---

## 8.3 user_finance

```sql
CREATE TABLE user_finance (
    id INTEGER PRIMARY KEY,

    annual_income INTEGER,
    cash INTEGER,

    company_loan_limit INTEGER,
    company_loan_balance INTEGER,

    mortgage_limit INTEGER,

    emergency_cash INTEGER,

    updated_at DATETIME
);
```

---

## 8.4 redevelopment_projects

```sql
CREATE TABLE redevelopment_projects (
    id INTEGER PRIMARY KEY,

    name TEXT NOT NULL,
    district TEXT,

    project_type TEXT,
    stage TEXT,

    address TEXT,

    source_url TEXT,

    last_checked_at DATETIME,
    updated_at DATETIME
);
```

---

## 8.5 redevelopment_history

```sql
CREATE TABLE redevelopment_history (
    id INTEGER PRIMARY KEY,

    project_id INTEGER NOT NULL,

    stage TEXT,
    event_date DATE,
    description TEXT,

    source_url TEXT,

    FOREIGN KEY(project_id)
        REFERENCES redevelopment_projects(id)
);
```

---

## 8.6 watchlist

```sql
CREATE TABLE watchlist (
    id INTEGER PRIMARY KEY,

    apartment_id INTEGER NOT NULL,

    preferred_area_min REAL,
    preferred_area_max REAL,

    target_price INTEGER,

    priority INTEGER,

    memo TEXT,

    created_at DATETIME,

    FOREIGN KEY(apartment_id)
        REFERENCES apartments(id)
);
```

---

# 9. 분석 로직

## 9.1 동일 면적 그룹

부동산 가격 비교 시 단지 전체 평균을 사용하지 않는다.

예:

```text
59.62㎡
59.76㎡
59.89㎡
```

같은 평형군으로 묶는다.

예:

```python
area_group = round(area_m2 / 5) * 5
```

실제 구현에서는 단지별 평형 매핑 테이블을 두는 것이 더 정확하다.

---

## 9.2 가격 변화

```text
discount_from_12m_avg
=
(latest_price - avg_12m)
/
avg_12m
```

예:

```text
12개월 평균   7.5억
최근 거래     6.8억

→ -9.3%
```

---

## 9.3 고점 대비

```text
drawdown
=
(latest_price - max_price_24m)
/
max_price_24m
```

---

## 9.4 거래량 Momentum

```text
volume_ratio
=
최근 3개월 거래량
/
직전 3개월 거래량
```

예:

```text
이전 3개월  2건
최근 3개월  6건

volume_ratio = 3.0
```

---

# 10. Opportunity Rule v1

처음부터 복잡한 AI 모델을 사용하지 않는다.

명확한 Rule Engine으로 시작한다.

예:

```python
def is_opportunity(stats, finance, apartment):

    affordable = (
        stats.latest_price
        <= finance.buying_power * 1.05
    )

    discounted = (
        stats.latest_price
        <= stats.avg_12m * 0.92
    )

    volume_recovery = (
        stats.volume_3m
        >= stats.previous_volume_3m
    )

    good_commute = (
        apartment.yeouido_commute_min <= 30
    )

    return (
        affordable
        and discounted
        and volume_recovery
        and good_commute
    )
```

---

# 11. Opportunity Score v2

향후 화면 정렬을 위해 내부적으로 점수를 사용할 수 있다.

다만 이 점수는 **향후 가격 상승 확률**이 아니다.

사용자의 조건에 얼마나 잘 맞는지를 나타낸다.

예:

```text
Affordability       30
Transaction         20
Price Discount      20
Commute             15
Redevelopment       10
Liquidity            5
-----------------------
Total              100
```

예시:

```text
당산 XX

Affordability       25 / 30
Transaction         18 / 20
Price Discount      12 / 20
Commute             15 / 15
Redevelopment        6 / 10
Liquidity            5 / 5

Match Score         81 / 100
```

---

# 12. 대시보드

## Home

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        REAL ESTATE RADAR

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cash                80M

Company Loan       150M

Mortgage           360M

Available Cash      60M

--------------------------------

Estimated
Buying Power       570M

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 OPPORTUNITY

당산 XX 59㎡

최근 거래       5.6억
12M 평균        6.2억
고점 대비      -14%

3M 거래량       6건
이전 3M         3건

여의도          19분

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Watchlist

| 단지 | 면적 | 최근가 | 12M 평균 | 거래량 | 여의도 | 상태 |
|---|---:|---:|---:|---:|---:|---|
| 당산 A | 59㎡ | 6.4억 | 6.8억 | ↑ | 18m | 👀 |
| 양평 B | 59㎡ | 6.7억 | 7.2억 | ↑ | 22m | 🔥 |
| 신길 C | 59㎡ | 8.2억 | 8.1억 | → | 15m | ⚪ |

---

## Apartment Detail

```text
당산 A 59㎡

[가격 그래프]

8억 ┤
    │       ●
7억 ┤   ●       ●
    │              ●
6억 ┤                  ●
    └──────────────────
       2025       2026
```

추가 표시:

```text
최근 실거래
3개월 평균
12개월 평균
전세가
전세가율
거래량
준공연도
세대수
역거리
여의도 이동시간
주변 정비사업
```

---

# 13. 초기 Watchlist

MVP에서는 너무 많은 단지를 넣지 않는다.

지역별 약 5개씩 선정한다.

## 당산

```text
5개 내외
```

## 양평 / 선유도

```text
5개 내외
```

## 신길

```text
5개 내외
```

## 노량진 / 대방

```text
5개 내외
```

총:

```text
약 20개
```

---

# 14. 데이터 수집 주기

## 실거래

```text
매일 1회
06:00
```

실거래 데이터는 신고 지연이나 정정/취소가 발생할 수 있으므로 과거 최근 몇 개월 데이터를 반복 조회해 업데이트한다.

예:

```text
현재월
1개월 전
2개월 전
```

---

## 정비사업

```text
주 1회
```

예:

```text
토요일 08:00
```

---

## 금융정보

자동 수집보다는 사용자가 직접 업데이트한다.

```text
3개월마다
```

---

# 15. 배치 구조

```text
Scheduler
   │
   ├── collect apartment transactions
   │
   ├── normalize transactions
   │
   ├── remove duplicates
   │
   ├── update cancellations
   │
   ├── calculate statistics
   │
   ├── update opportunity flags
   │
   └── send alerts
```

---

# 16. 중복 거래 처리

실거래 데이터는 중복 수집될 수 있으므로 Unique Key를 만든다.

예:

```text
법정동코드
+
아파트명
+
전용면적
+
계약년월일
+
층
+
거래금액
```

가능하면 API에서 제공하는 거래 식별 필드를 우선 사용한다.

---

# 17. 취소 거래 처리

실거래 신고 후 취소될 수 있으므로 삭제하지 않고 상태를 관리한다.

```text
ACTIVE
CANCELLED
```

분석에서는:

```text
ACTIVE 거래만 사용
```

---

# 18. 설정 파일

`.env`

```text
MOLIT_API_KEY=

DATABASE_URL=sqlite:///./data/real_estate.db

TARGET_COMMUTE_MIN=30

DEFAULT_EMERGENCY_CASH=20000000
```

`.env`는 Git에 올리지 않는다.

---

# 19. 테스트

최소 단위 테스트:

## price_analysis

```text
12개월 평균 계산
24개월 최고가 계산
거래량 계산
취소 거래 제외
```

## finance

```text
매수 가능액 계산
비상자금 제외
사내대출 포함/제외
```

## opportunity

```text
가격 조건
거래량 조건
출퇴근 조건
매수가능금액 조건
```

---

# 20. 개발 순서

## Sprint 1 — Skeleton

- 프로젝트 생성
- FastAPI 구성
- SQLite 연결
- SQLAlchemy 모델 생성
- `.env` 구성
- pytest 구성

완료 기준:

```text
API 서버 실행
DB 생성
테스트 실행
```

---

## Sprint 2 — 실거래 API

- 국토부 API client
- XML parsing
- 법정동 코드 입력
- 거래 DB 저장
- duplicate 방지

완료 기준:

```text
영등포구 특정 월 데이터를 가져와 DB 저장
```

---

## Sprint 3 — Watchlist

- 아파트 등록
- 관심 평형 등록
- 최근 거래 조회

완료 기준:

```text
당산/양평/신길 관심단지 조회 가능
```

---

## Sprint 4 — Analytics

- 3M/6M/12M 평균
- 거래량
- 고점 대비 하락률
- Opportunity rule

완료 기준:

```text
관심단지별 Opportunity 상태 계산
```

---

## Sprint 5 — Dashboard

Streamlit 화면:

```text
Home
Watchlist
Apartment Detail
My Finance
```

완료 기준:

```text
브라우저에서 현재 후보 단지 비교 가능
```

---

## Sprint 6 — Scheduler

- 매일 자동 수집
- 분석 업데이트

완료 기준:

```text
사용자가 수동 실행하지 않아도 DB 최신화
```

---

# 21. 향후 기술 확장

## 지도

후보:

```text
Kakao Map API
Naver Map API
OpenStreetMap
```

지도에서는 다음을 표시한다.

```text
아파트
지하철역
재개발구역
직장
```

---

## 출퇴근

초기:

```text
수동 입력
```

향후:

```text
지도/대중교통 API 연동
```

---

## AI Layer

충분한 데이터가 쌓인 후 추가한다.

용도:

- 단지 변화 요약
- 최근 거래 이상점 설명
- 정비사업 변경 요약
- 관심단지 주간 리포트

AI가 매수 여부를 결정하지 않는다.

---

# 22. 하지 않을 것

초기 버전에서는 다음은 하지 않는다.

```text
X 부동산 가격 ML 예측
X 네이버 부동산 무단 크롤링
X 자동 매매
X 과도한 지역 확장
X 전국 데이터 수집
X 수십 개 외부 API 연동
```

**여의도 출퇴근권 20개 단지에 집중한다.**

---

# 23. 최종 사용 흐름

```text
              ┌───────────────┐
              │ 국토부 실거래 │
              └───────┬───────┘
                      │
                      ▼
             ┌─────────────────┐
             │   Collector     │
             └────────┬────────┘
                      │
                      ▼
               ┌────────────┐
               │ PostgreSQL │
               │ / SQLite   │
               └─────┬──────┘
                     │
             ┌───────┴────────┐
             ▼                ▼
      Price Analyzer     Finance Engine
             │                │
             └───────┬────────┘
                     ▼
              Opportunity
                 Engine
                     │
             ┌───────┴────────┐
             ▼                ▼
        Dashboard           Alert
```

---

# 24. 프로젝트 성공 기준

2년 뒤 다음 질문에 1분 안에 답할 수 있으면 성공이다.

> 지금 내가 얼마짜리 집까지 살 수 있는가?

> 당산/양평/신길/노량진 중 현재 상대적으로 가격이 내려온 곳은 어디인가?

> 거래량이 다시 증가하는 단지는 어디인가?

> 최근 1년 평균보다 싸게 거래된 단지는 어디인가?

> 주변 정비사업 단계가 최근 바뀐 곳은 어디인가?

> 실제 매수 후보 5개는 무엇인가?

즉,

```text
정보 수집
     ↓
비교
     ↓
기회 탐지
     ↓
임장
     ↓
대출 확인
     ↓
매수 판단
```

까지 이어지는 개인용 **Home Buying Decision Support System**을 만드는 것이 최종 목표다.

---

# 25. 권장 첫 번째 구현 목표

첫 번째 버전은 아래 하나만 제대로 만든다.

> **당산·양평·신길·노량진 관심단지의 최근 24개월 실거래를 자동 수집하고, 최근 가격·12개월 평균·거래량·고점 대비 하락률을 한 화면에서 보여준다.**

이 기능이 완성되기 전까지 추가 기능을 늘리지 않는다.

첫 번째 화면 예:

```text
단지             최근가   12M평균   고점대비   3M거래   상태

당산 A            6.4      6.9      -11%       5      👀
양평 B            6.7      7.4      -14%       7      🔥
신길 C            8.2      8.0       -3%       4      ⚪
노량진 D          9.1      9.5       -8%       2      ⚪
```

여기에 사용자의 현재 매수가능금액을 표시한다.

```text
현재 예상 매수 가능 금액

██████████████░░░░

5.9억
```

이 정도만 되어도 실제 집을 찾는 데 상당히 유용한 도구가 된다.

---

# 26. 공식 데이터 출처

프로젝트에서 우선 사용할 데이터는 공식 소스를 기준으로 한다.

### 국토교통부 아파트 매매 실거래가 상세 자료

- 제공기관: 국토교통부
- 형태: REST OpenAPI
- 데이터 포맷: XML
- 주요 조회 조건: 법정동 코드 앞 5자리 + 계약년월
- 공공데이터포털:
  - https://www.data.go.kr/data/15126468/openapi.do

### 국토교통부 실거래가 공개시스템

- https://rt.molit.go.kr/

### 서울시 정비사업 정보몽땅

- 재개발·재건축 사업 단계 및 사업장 정보 확인
- https://cleanup.seoul.go.kr/

> 외부 서비스의 이용약관 및 API 정책을 준수한다.  
> 공식 API가 있는 데이터는 HTML 크롤링보다 공식 API를 우선 사용한다.

---

# 27. 다음 개발 작업

다음 단계에서는 실제 프로젝트를 생성하고 아래 파일부터 구현한다.

```text
RealEstateRadar/
├─ PROJECT_SPEC.md
├─ README.md
├─ requirements.txt
├─ .env.example
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ database.py
│  ├─ models/
│  └─ services/
└─ tests/
```

첫 구현 대상:

```text
MOLIT Apartment Trade API Client
```

인터페이스 초안:

```python
class MolitApartmentTradeClient:

    def get_transactions(
        self,
        legal_dong_code: str,
        year_month: str,
    ) -> list[ApartmentTransaction]:
        ...
```

그 다음:

```text
API
 ↓
Parser
 ↓
SQLite
 ↓
Price Analysis
 ↓
Dashboard
```

순서로 진행한다.
