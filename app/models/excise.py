"""Aksiz stavkalari modeli - Soliq kodeksi 289-moddalar asosida"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Float, String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ExciseRate(Base):
    """
    Aksiz soliq stavkalari - Soliq kodeksi 289-moddalariga asosan:
    - 289-1 modda: Tamaki mahsulotlari
    - 289-2 modda: Spirtli ichimliklar
    - 289-3 modda: Neft mahsulotlari va boshqalar (shakar, shirin ichimliklar)
    """
    __tablename__ = "excise_rates"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Mahsulot kategoriyasi
    category: Mapped[str] = mapped_column(String(100), index=True)  # tobacco, alcohol, petroleum, sugar, beverages
    
    # Mahsulot nomlari
    product_name_ru: Mapped[str] = mapped_column(String(500))  # Ruscha - qonundagi kabi
    product_name_uz: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # O'zbekcha
    
    # TN VED kodlar (vergul bilan ajratilgan)
    tnved_codes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # "2402201000,2402209000"
    
    # Import uchun stavkalar
    import_rate_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Foiz
    import_rate_specific: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Absolyut summa
    import_rate_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # sum/1000pcs, sum/liter
    import_rate_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Minimal stavka
    
    # Mahalliy ishlab chiqarish uchun stavkalar
    local_rate_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    local_rate_specific: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    local_rate_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Izoh
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Holat
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Meta
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ExciseRate {self.category}: {self.product_name_ru[:50]}>"
