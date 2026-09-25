from dataclasses import dataclass
from datetime import date
import requests
import xml.etree.ElementTree as ET
from app.config import settings

@dataclass(frozen=True)
class ApartmentTrade:
    apt_name: str
    contract_date: date
    area_m2: float
    floor: int | None
    price: int
    cancellation_date: date | None = None

class MolitApartmentTradeClient:
    """Client for the MOLIT apartment sale transaction OpenAPI (XML)."""
    def __init__(self, api_key: str | None = None, endpoint: str | None = None, timeout: int = 30):
        self.api_key = api_key if api_key is not None else settings.molit_api_key
        self.endpoint = endpoint or settings.molit_apartment_trade_url
        self.timeout = timeout

    def get_transactions(self, legal_dong_code: str, year_month: str) -> list[ApartmentTrade]:
        if not self.api_key:
            raise RuntimeError("MOLIT_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        if len(legal_dong_code) != 5 or not legal_dong_code.isdigit():
            raise ValueError("legal_dong_code는 숫자 5자리여야 합니다.")
        if len(year_month) != 6 or not year_month.isdigit():
            raise ValueError("year_month는 YYYYMM 형식이어야 합니다.")
        response = requests.get(self.endpoint, params={"serviceKey": self.api_key, "LAWD_CD": legal_dong_code, "DEAL_YMD": year_month, "pageNo": 1, "numOfRows": 1000}, timeout=self.timeout)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        code = root.findtext("./header/resultCode")
        if code not in (None, "00", "000"):
            message = root.findtext("./header/resultMsg", "알 수 없는 API 오류")
            raise RuntimeError(f"MOLIT API 오류 {code}: {message}")
        result: list[ApartmentTrade] = []
        for item in root.findall(".//item"):
            try:
                y, m, d = (int(item.findtext(k, "0").strip()) for k in ("dealYear", "dealMonth", "dealDay"))
                price = int(item.findtext("dealAmount", "0").replace(",", "").strip()) * 10_000
                cancel = item.findtext("cdealDay", "").strip()
                cancel_date = (date(int(cancel[:4]), int(cancel[4:6]), int(cancel[6:8])) if len(cancel) == 8 else date(y, int(cancel[:2]), int(cancel[2:])) if len(cancel) == 4 else date(y, m, int(cancel)) if cancel.isdigit() else None)
                result.append(ApartmentTrade(apt_name=item.findtext("아파트", "").strip(), contract_date=date(y, m, d), area_m2=float(item.findtext("전용면적", "0").strip()), floor=int(item.findtext("층", "0").strip() or 0) or None, price=price, cancellation_date=cancel_date))
            except (ValueError, TypeError):
                continue
        return result
