from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Watchlist(Base):
    __tablename__ = "watchlist"
    id: Mapped[int] = mapped_column(primary_key=True)
    apartment_id: Mapped[int] = mapped_column(ForeignKey("apartments.id"), unique=True)
    preferred_area_min: Mapped[float | None] = mapped_column(Float)
    preferred_area_max: Mapped[float | None] = mapped_column(Float)
    target_price: Mapped[int | None] = mapped_column(Integer)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    memo: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    apartment = relationship("Apartment", back_populates="watchlist")
