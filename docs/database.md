# Database

SQLite is the initial store. `apartments`, `transactions`, `user_finance`, and `watchlist` tables are created by `python scripts/init_db.py`. Transaction identity uses apartment, contract date, area, floor, and price; cancellations are retained via status and cancellation date.
