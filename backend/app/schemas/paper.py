from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models import WorkflowStatus


class PaperBase(BaseModel):
    title: str
    authors: list[str] = []
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    citation_key: Optional[str] = None
    reading_reason: Optional[str] = None
    priority: Optional[int] = None


class PaperCreate(PaperBase):
    zotero_key: Optional[str] = None
    workflow_status: WorkflowStatus = WorkflowStatus.inbox


class PaperUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[list[str]] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    citation_key: Optional[str] = None
    reading_reason: Optional[str] = None
    priority: Optional[int] = None
    workflow_status: Optional[WorkflowStatus] = None
    relevance_score: Optional[float] = None


class PaperOut(PaperBase):
    id: int
    zotero_key: Optional[str] = None
    pdf_path: Optional[str] = None
    workflow_status: WorkflowStatus
    relevance_score: Optional[float] = None
    date_added: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaperDetail(PaperOut):
    """Full paper detail including linked entities."""
    project_ids: list[int] = []
    research_question_ids: list[int] = []

    model_config = {"from_attributes": True}
