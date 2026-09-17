from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models import RQStatus


class RQCreate(BaseModel):
    project_id: int
    question: str
    motivation: Optional[str] = None
    status: RQStatus = RQStatus.active
    notes: Optional[str] = None


class RQUpdate(BaseModel):
    question: Optional[str] = None
    motivation: Optional[str] = None
    status: Optional[RQStatus] = None
    notes: Optional[str] = None


class RQOut(BaseModel):
    id: int
    project_id: int
    question: str
    motivation: Optional[str] = None
    status: RQStatus
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
