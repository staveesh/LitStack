from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReadingIntentCreate(BaseModel):
    paper_id: int
    research_question_id: Optional[int] = None
    intent: str


class ReadingIntentResolve(BaseModel):
    resolution_notes: Optional[str] = None


class ReadingIntentOut(BaseModel):
    id: int
    paper_id: int
    research_question_id: Optional[int] = None
    intent: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    model_config = {"from_attributes": True}
