from dataclasses import dataclass
from datetime import date
from statistics import mean
from app.models.transaction import Transaction

@dataclass(frozen=True)
class PriceStats:
    latest_price: int | None
    avg_3m: float | None
    avg_6m: float | None
    avg_12m: float | None
    avg_24m: float | None
    max_24m: int | None
    volume_3m: int
    previous_volume_3m: int
    volume_12m: int
    discount_from_12m_avg: float | None
    drawdown_from_24m_high: float | None

def area_group(area_m2: float) -> int:
    return round(area_m2 / 5) * 5

def analyze_transactions(transactions: list[Transaction], area_m2: float, as_of: date | None = None) -> PriceStats:
    as_of = as_of or date.today()
    rows = [t for t in transactions if t.status == "ACTIVE" and area_group(t.area_m2) == area_group(area_m2) and (t.contract_date.year, t.contract_date.month) <= (as_of.year, as_of.month)]
    rows.sort(key=lambda t: t.contract_date)
    def months_ago(n: int) -> tuple[int, int]:
        idx = as_of.year * 12 + as_of.month - 1 - n
        return idx // 12, idx % 12 + 1
    def within(t: Transaction, n: int) -> bool:
        return (t.contract_date.year, t.contract_date.month) >= months_ago(n)
    active = [t for t in rows if t.cancellation_date is None]
    recent_3 = [t for t in active if within(t, 3)]
    prev_3 = [t for t in active if months_ago(6) <= (t.contract_date.year, t.contract_date.month) < months_ago(3)]
    recent_6 = [t for t in active if within(t, 6)]
    recent_12 = [t for t in active if within(t, 12)]
    recent_24 = [t for t in active if within(t, 24)]
    latest = max(active, key=lambda t: t.contract_date).price if active else None
    avg12 = mean(t.price for t in recent_12) if recent_12 else None
    high24 = max((t.price for t in recent_24), default=None)
    return PriceStats(latest, mean(t.price for t in recent_3) if recent_3 else None, mean(t.price for t in recent_6) if recent_6 else None, avg12, mean(t.price for t in recent_24) if recent_24 else None, high24, len(recent_3), len(prev_3), len(recent_12), (latest - avg12) / avg12 if latest is not None and avg12 else None, (latest - high24) / high24 if latest is not None and high24 else None)
