from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UtilizationFeeBase(BaseModel):
    tnved_code_start: str
    tnved_code_end: Optional[str] = None
    fee_type: str  # 'fixed', 'percent', 'brv_multiplier'
    fee_amount: Optional[float] = None
    fee_percent: Optional[float] = None
    brv_multiplier: Optional[float] = None
    engine_volume_min: Optional[int] = None
    engine_volume_max: Optional[int] = None
    vehicle_age_min: Optional[int] = None
    vehicle_age_max: Optional[int] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    is_active: bool = True


class UtilizationFeeCreate(UtilizationFeeBase):
    pass


class UtilizationFeeUpdate(BaseModel):
    fee_type: Optional[str] = None
    fee_amount: Optional[float] = None
    fee_percent: Optional[float] = None
    brv_multiplier: Optional[float] = None
    is_active: Optional[bool] = None


class UtilizationFee(UtilizationFeeBase):
    id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
