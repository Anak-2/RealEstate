from datetime import datetime
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class UserFinance(Base):
    __tablename__ = "user_finance"
    id: Mapped[int] = mapped_column(primary_key=True)
    annual_income: Mapped[int] = mapped_column(Integer, default=0)
    cash: Mapped[int] = mapped_column(Integer, default=0)
    company_loan_limit: Mapped[int] = mapped_column(Integer, default=0)
    company_loan_balance: Mapped[int] = mapped_column(Integer, default=0)
    mortgage_limit: Mapped[int] = mapped_column(Integer, default=0)
    emergency_cash: Mapped[int] = mapped_column(Integer, default=20_000_000)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
