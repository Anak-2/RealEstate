from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Apartment(Base):
    __tablename__ = "apartments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    legal_dong_code: Mapped[str | None] = mapped_column(String(5), index=True)
    address: Mapped[str | None] = mapped_column(String(300))
    district: Mapped[str | None] = mapped_column(String(100))
    build_year: Mapped[int | None] = mapped_column(Integer)
    households: Mapped[int | None] = mapped_column(Integer)
    nearest_station: Mapped[str | None] = mapped_column(String(100))
    station_distance_m: Mapped[int | None] = mapped_column(Integer)
    yeouido_commute_min: Mapped[int | None] = mapped_column(Integer)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    transactions = relationship("Transaction", back_populates="apartment", cascade="all, delete-orphan")
    watchlist = relationship("Watchlist", back_populates="apartment", uselist=False, cascade="all, delete-orphan")
