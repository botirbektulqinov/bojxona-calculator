from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class TariffRateBase(BaseModel):
    import_duty_percent: Optional[float] = None
    import_duty_specific: Optional[float] = None
    specific_unit: Optional[str] = None
    excise_percent: Optional[float] = None
    excise_specific: Optional[float] = None
    vat_percent: float = 12.0
    source_url: Optional[str] = None

class TariffRateCreate(TariffRateBase):
    tnved_id: int

class TariffRateUpdate(TariffRateBase):
    pass

class TariffRateInDBBase(TariffRateBase):
    id: int
    tnved_id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TariffRate(TariffRateInDBBase):
    pass
