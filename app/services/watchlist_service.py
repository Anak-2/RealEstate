import csv
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Apartment, Watchlist

WATCHLIST_PATH = Path(__file__).resolve().parents[2] / "data" / "watchlist.csv"


def sync_watchlist_from_csv(db: Session, csv_path: Path = WATCHLIST_PATH) -> int:
    """Upsert Apartment + Watchlist rows from the CSV into the database. Returns rows synced."""
    if not csv_path.exists():
        raise SystemExit("data/watchlist.csv가 없습니다.")
    count = 0
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for item in csv.DictReader(f):
            code = (item.get("legal_dong_code") or "").strip()
            name = (item.get("name") or "").strip()
            if not code or not name:
                continue
            apt = db.query(Apartment).filter_by(name=name, legal_dong_code=code).first()
            if not apt:
                apt = Apartment(name=name, legal_dong_code=code)
                db.add(apt)
                db.flush()
            apt.address = item.get("address") or None
            apt.district = item.get("district") or None
            apt.build_year = int(item["build_year"]) if item.get("build_year") else None
            apt.households = int(item["households"]) if item.get("households") else None
            apt.nearest_station = item.get("nearest_station") or None
            apt.station_distance_m = int(item["station_distance_m"]) if item.get("station_distance_m") else None
            apt.yeouido_commute_min = int(item["yeouido_commute_min"]) if item.get("yeouido_commute_min") else None
            apt.latitude = float(item["latitude"]) if item.get("latitude") else None
            apt.longitude = float(item["longitude"]) if item.get("longitude") else None
            watch = apt.watchlist
            if not watch:
                watch = Watchlist(apartment_id=apt.id)
                db.add(watch)
            watch.preferred_area_min = float(item["preferred_area_min"]) if item.get("preferred_area_min") else None
            watch.preferred_area_max = float(item["preferred_area_max"]) if item.get("preferred_area_max") else None
            watch.target_price = int(item["target_price"]) if item.get("target_price") else None
            watch.priority = int(item.get("priority") or 3)
            watch.memo = item.get("memo") or None
            count += 1
    db.commit()
    return count
