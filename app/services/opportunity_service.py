from dataclasses import dataclass
from app.services.price_analysis_service import PriceStats

@dataclass(frozen=True)
class OpportunityResult:
    status: str
    reasons: tuple[str, ...]

def classify_opportunity(stats: PriceStats, buying_power_krw: int, commute_min: int | None, target_commute_min: int = 30) -> OpportunityResult:
    reasons: list[str] = []
    eligible = True
    if stats.latest_price is None:
        return OpportunityResult("NORMAL", ("최근 유효 실거래 없음",))
    if stats.avg_12m is None or stats.latest_price > stats.avg_12m * 0.92:
        eligible = False
    else:
        reasons.append("최근 거래가 12개월 평균보다 8% 이상 낮음")
    if stats.volume_3m < stats.previous_volume_3m:
        eligible = False
    else:
        reasons.append("최근 3개월 거래량이 직전 3개월 이상")
    if commute_min is None or commute_min > target_commute_min:
        eligible = False
    else:
        reasons.append("여의도 출퇴근 시간 조건 충족")
    if stats.latest_price > buying_power_krw * 1.05:
        eligible = False
    else:
        reasons.append("입력된 매수 가능 금액 범위")
    return OpportunityResult("OPPORTUNITY" if eligible else "WATCH" if reasons else "NORMAL", tuple(reasons))
