from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base


class UtilizationFee(Base):
    """
    Utilizatsiya yig'imi stavkalari
    Manba: https://lex.uz/docs/4848953
    Asosan avtomobillar va elektronika uchun
    """
    __tablename__ = "utilization_fees"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # TN VED kod yoki kod diapazoni
    tnved_code_start: Mapped[str] = mapped_column(String(10), index=True)  # Boshlang'ich kod
    tnved_code_end: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # Tugash kod (diapazon uchun)
    
    # Stavka turi
    fee_type: Mapped[str] = mapped_column(String(20))  # 'fixed' yoki 'percent' yoki 'brv_multiplier'
    
    # Qiymatlar
    fee_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Raqamli qiymat
    fee_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Foiz stavka
    brv_multiplier: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # BRV koeffitsienti
    
    # Qo'shimcha shartlar
    engine_volume_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Dvigatel hajmi (sm³) min
    engine_volume_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Dvigatel hajmi (sm³) max
    vehicle_age_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Avtomobil yoshi (yil) min
    vehicle_age_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Avtomobil yoshi (yil) max
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<UtilizationFee(code={self.tnved_code_start}, type={self.fee_type})>"
