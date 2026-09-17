from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
