from typing import Optional
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Country(Base):
    """Mamlakatlar ro'yxati"""
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, index=True)  # ISO 3166-1 alpha-2 (UZ, RU, CN...)
    name_uz: Mapped[str] = mapped_column(String(255))
    name_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<Country(code={self.code}, name={self.name_uz})>"


class FreeTradeCountry(Base):
    """
    Erkin savdo mamlakatlar ro'yxati
    Agar tovar shu mamlakatdan kelsa va sertifikat bo'lsa - poshina 0%
    Manba: https://lex.uz/docs/4911947
    """
    __tablename__ = "free_trade_countries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    country_code: Mapped[str] = mapped_column(String(3), unique=True, index=True)
    country_name: Mapped[str] = mapped_column(String(255))
    agreement_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Shartnoma nomi
    requires_certificate: Mapped[bool] = mapped_column(Boolean, default=True)  # ST-1 talab qilinadimi
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<FreeTradeCountry(code={self.country_code})>"
