from datetime import datetime
from typing import Optional
from sqlalchemy import Float, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.tnved import TNVedCode

class TariffRate(Base):
    __tablename__ = "tariff_rates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tnved_id: Mapped[int] = mapped_column(ForeignKey("tn_ved_codes.id", ondelete="CASCADE"), unique=True)    
    # RNB mamlakatlari uchun (MDH + erkin savdo)
    import_duty_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # Boshqa mamlakatlar uchun (2x stavka)
    import_duty_percent_non_rnb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    import_duty_specific: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # e.g. amount in USD
    import_duty_specific_non_rnb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    specific_unit: Mapped[Optional[str]] = mapped_column(String, nullable=True) # e.g. "kg", "pcs"
    excise_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    excise_specific: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vat_percent: Mapped[float] = mapped_column(Float, default=12.0)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    tnved_code: Mapped["TNVedCode"] = relationship("TNVedCode", back_populates="tariff_rate")

    def __repr__(self):
        return f"<TariffRate(tnved_id={self.tnved_id}, duty={self.import_duty_percent}%)>"
