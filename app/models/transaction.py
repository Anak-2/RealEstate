from datetime import date, datetime
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("apartment_id", "contract_date", "area_m2", "floor", "price", name="uq_transaction_identity"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    apartment_id: Mapped[int] = mapped_column(ForeignKey("apartments.id"), index=True)
    contract_date: Mapped[date] = mapped_column(Date, index=True)
    area_m2: Mapped[float] = mapped_column(Float)
    floor: Mapped[int | None] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)  # KRW
    transaction_type: Mapped[str] = mapped_column(String(20), default="매매")
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", index=True)
    cancellation_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    apartment = relationship("Apartment", back_populates="transactions")
