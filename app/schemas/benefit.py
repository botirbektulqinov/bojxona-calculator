from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TariffBenefitBase(BaseModel):
    tnved_code: Optional[str] = None
    tnved_code_start: Optional[str] = None
    tnved_code_end: Optional[str] = None
    benefit_type: str  # 'duty_exempt', 'duty_reduction', 'vat_exempt', 'excise_exempt'
    reduction_percent: Optional[float] = None
    condition_description: Optional[str] = None
    requires_certificate: bool = False
    certificate_type: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    legal_basis: Optional[str] = None
    source_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class TariffBenefitCreate(TariffBenefitBase):
    pass


class TariffBenefit(TariffBenefitBase):
    id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CustomsFeeRateBase(BaseModel):
    min_customs_value: Optional[float] = None
    max_customs_value: Optional[float] = None
    fee_type: str  # 'fixed', 'percent', 'brv'
    fee_value: float
    min_fee: Optional[float] = None
    max_fee: Optional[float] = None
    description: Optional[str] = None
    is_active: bool = True


class CustomsFeeRateCreate(CustomsFeeRateBase):
    pass


class CustomsFeeRate(CustomsFeeRateBase):
    id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BRVRateBase(BaseModel):
    year: int
    amount: float
    valid_from: date
    valid_until: Optional[date] = None
    is_active: bool = True


class BRVRateCreate(BRVRateBase):
    pass


class BRVRate(BRVRateBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
