from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    molit_api_key: str = ""
    molit_apartment_trade_url: str = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
    database_url: str = "sqlite:///./data/real_estate.db"
    target_commute_min: int = 30
    default_emergency_cash: int = 20_000_000
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
