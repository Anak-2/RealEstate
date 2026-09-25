# API / Data Collection

Set `MOLIT_API_KEY` in `.env`, then run `python scripts/collect_transactions.py --months 24`. The collector requests one 법정동 code and month at a time from the MOLIT apartment sale API. Amounts are converted from 만원 to KRW. API access, service-key encoding and quota depend on the issued data.go.kr key.
