from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class TNVedBase(BaseModel):
    code: str
    full_code: Optional[str] = None
    description: str
    level: int
    parent_id: Optional[int] = None

class TNVedCreate(TNVedBase):
    pass

class TNVedUpdate(TNVedBase):
    pass

class TNVedInDBBase(TNVedBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TNVed(TNVedInDBBase):
    pass

class TNVedWithChildren(TNVed):
    children: List[TNVed] = []
