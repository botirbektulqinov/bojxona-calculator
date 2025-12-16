from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class CurrencyBase(BaseModel):
    code: str = Field(min_length=2, max_length=10)
    name: Optional[str] = None
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    nominal: int = 1
    rate_uzs: float
    diff: Optional[float] = None
    date: date
    is_active: bool = True
    cbu_id: Optional[int] = None

class CurrencyCreate(CurrencyBase):
    pass

class CurrencyUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    nominal: Optional[int] = None
    rate_uzs: Optional[float] = None
    diff: Optional[float] = None
    date: Optional[date] = None
    is_active: Optional[bool] = None
    cbu_id: Optional[int] = None

class CurrencyInDBBase(CurrencyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Currency(CurrencyInDBBase):
    pass
