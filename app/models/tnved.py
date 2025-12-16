from typing import Optional, List
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class TNVedCode(Base):
    __tablename__ = "tn_ved_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    full_code: Mapped[str] = mapped_column(String, nullable=True) 
    description: Mapped[str] = mapped_column(Text)
    level: Mapped[int] = mapped_column(Integer)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tn_ved_codes.id"), nullable=True)
    parent: Mapped[Optional["TNVedCode"]] = relationship("TNVedCode", remote_side=[id], back_populates="children")
    children: Mapped[List["TNVedCode"]] = relationship("TNVedCode", back_populates="parent")
    tariff_rate: Mapped[Optional["TariffRate"]] = relationship("TariffRate", uselist=False, back_populates="tnved_code")

    def __repr__(self):
        return f"<TNVedCode(code={self.code}, description={self.description[:30]})>"
