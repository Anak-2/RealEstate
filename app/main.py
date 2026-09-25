from fastapi import FastAPI
from app.database import init_db

app = FastAPI(title="Real Estate Radar", version="0.1.0", description="실거래 기반 주택 매수 기회 탐지 도구")

@app.on_event("startup")
def startup() -> None:
    init_db()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
