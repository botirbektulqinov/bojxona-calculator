from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Float, Text, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base


class TariffBenefit(Base):
    """
    Bojxona imtiyozlari (lgoty)
    Manba: Google Drive fayl - https://drive.google.com/file/d/1zt48lIq9nIaIqzZttvXRq-PerbJzghuZ/view
    """
    __tablename__ = "tariff_benefits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # TN VED kod yoki kod diapazoni
    tnved_code: Mapped[Optional[str]] = mapped_column(String(10), index=True, nullable=True)
    tnved_code_start: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    tnved_code_end: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Imtiyoz turi
    benefit_type: Mapped[str] = mapped_column(String(50))  # 'duty_exempt', 'duty_reduction', 'vat_exempt', 'excise_exempt'
    
    # Chegirma/Imtiyoz qiymati
    reduction_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Chegirma foizi (100 = to'liq ozod)
    
    # Qo'llash shartlari
    condition_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Qo'llash sharti ta'rifi
    requires_certificate: Mapped[bool] = mapped_column(Boolean, default=False)  # Sertifikat talab qiladimi
    certificate_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Sertifikat turi
    
    # Amal qilish muddati
    valid_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Qonuniy asos
    legal_basis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Qaror raqami/sanasi
    source_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<TariffBenefit(code={self.tnved_code}, type={self.benefit_type})>"


class CustomsFeeRate(Base):
    """
    Bojxona rasmiylash yig'imi stavkalari
    Odatda BRV asosida hisoblanadi
    """
    __tablename__ = "customs_fee_rates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Stavka parametrlari
    min_customs_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Minimal bojxona qiymati (UZS)
    max_customs_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Maksimal bojxona qiymati (UZS)
    
    # Yig'im qiymati
    fee_type: Mapped[str] = mapped_column(String(20))  # 'fixed', 'percent', 'brv'
    fee_value: Mapped[float] = mapped_column(Float)  # Qiymat (raqam, foiz yoki BRV soni)
    min_fee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Minimal yig'im
    max_fee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Maksimal yig'im
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<CustomsFeeRate(type={self.fee_type}, value={self.fee_value})>"


class BRVRate(Base):
    """
    BRV (Bazaviy Hisoblash Razmer) qiymatlari
    Har yili o'zgaradi
    """
    __tablename__ = "brv_rates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    year: Mapped[int] = mapped_column(unique=True, index=True)  # Yil
    amount: Mapped[float] = mapped_column(Float)  # BRV qiymati UZS da
    
    valid_from: Mapped[date] = mapped_column(Date)
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<BRVRate(year={self.year}, amount={self.amount})>"
