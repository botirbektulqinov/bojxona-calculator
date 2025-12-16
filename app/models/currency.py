from datetime import date
from typing import Optional
from sqlalchemy import String, Numeric, Date, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(10), index=True)  # USD, EUR...
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # AQSH dollari
    name_ru: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Доллар США
    name_en: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # US Dollar
    nominal: Mapped[int] = mapped_column(Integer, default=1)  # 1, 10, 100...
    rate_uzs: Mapped[float] = mapped_column(Numeric(15, 2))  # Rate per nominal
    diff: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)  # Change from previous day
    date: Mapped[date] = mapped_column(Date, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cbu_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # CBU API id

    __table_args__ = (
        {"schema": None},  # Default schema
    )

    def __repr__(self):
        return f"<Currency(code={self.code}, rate={self.rate_uzs}, date={self.date})>"
