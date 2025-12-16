from typing import Optional
from pydantic import BaseModel, ConfigDict


class CountryBase(BaseModel):
    code: str
    name_uz: str
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    is_active: bool = True


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    is_active: Optional[bool] = None


class Country(CountryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class FreeTradeCountryBase(BaseModel):
    country_code: str
    country_name: str
    agreement_name: Optional[str] = None
    requires_certificate: bool = True
    is_active: bool = True


class FreeTradeCountryCreate(FreeTradeCountryBase):
    pass


class FreeTradeCountry(FreeTradeCountryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
