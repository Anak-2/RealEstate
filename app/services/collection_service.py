from collections.abc import Iterator
from datetime import date
from dateutil.relativedelta import relativedelta
from app.database import SessionLocal, init_db
from app.models import Apartment, Transaction
from app.services.molit_service import MolitApartmentTradeClient
from app.services.watchlist_service import sync_watchlist_from_csv


def collect_all(months: int = 24) -> Iterator[tuple[float, str]]:
    """Sync the watchlist and pull MOLIT transactions. Yields (progress 0~1, message) pairs."""
    init_db()
    with SessionLocal() as db:
        synced = sync_watchlist_from_csv(db)
        yield 0.0, f"관심 단지 {synced}개 동기화 완료"
        apartments = db.query(Apartment).join(Apartment.watchlist).all()
        if not apartments:
            yield 1.0, "관심 단지가 없습니다. Watchlist 페이지에서 먼저 등록하세요."
            return
        client = MolitApartmentTradeClient()
        start = date.today().replace(day=1) - relativedelta(months=months - 1)
        total_steps = len(apartments) * months
        step = 0
        for apt in apartments:
            for offset in range(months):
                month = start + relativedelta(months=offset)
                step += 1
                try:
                    trades = client.get_transactions(apt.legal_dong_code, month.strftime("%Y%m"))
                except Exception as exc:  # noqa: BLE001 - surface any API/network error to the UI log
                    yield step / total_steps, f"{apt.name} {month:%Y-%m}: 오류 - {exc}"
                    continue
                new_count = 0
                for trade in trades:
                    if trade.apt_name.replace(" ", "") != apt.name.replace(" ", ""):
                        continue
                    existing = db.query(Transaction).filter_by(
                        apartment_id=apt.id,
                        contract_date=trade.contract_date,
                        area_m2=trade.area_m2,
                        floor=trade.floor,
                        price=trade.price,
                    ).first()
                    if existing:
                        existing.cancellation_date = trade.cancellation_date
                        existing.status = "CANCELLED" if trade.cancellation_date else "ACTIVE"
                    else:
                        db.add(Transaction(
                            apartment_id=apt.id,
                            contract_date=trade.contract_date,
                            area_m2=trade.area_m2,
                            floor=trade.floor,
                            price=trade.price,
                            status="CANCELLED" if trade.cancellation_date else "ACTIVE",
                            cancellation_date=trade.cancellation_date,
                        ))
                        new_count += 1
                db.commit()
                yield step / total_steps, f"{apt.name} {month:%Y-%m}: 신규 {new_count}건"
        yield 1.0, "수집 완료"
