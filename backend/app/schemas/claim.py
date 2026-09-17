from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models import ClaimStatus, EvidenceType


class ClaimCreate(BaseModel):
    project_id: int
    claim: str
    status: ClaimStatus = ClaimStatus.hypothesis
    confidence: Optional[float] = None
    notes: Optional[str] = None


class ClaimUpdate(BaseModel):
    claim: Optional[str] = None
    status: Optional[ClaimStatus] = None
    confidence: Optional[float] = None
    notes: Optional[str] = None


class ClaimOut(BaseModel):
    id: int
    project_id: int
    claim: str
    status: ClaimStatus
    confidence: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EvidenceCreate(BaseModel):
    claim_id: int
    paper_id: int
    evidence_type: EvidenceType
    evidence_text: str
    source_location: Optional[str] = None
    strength: Optional[float] = None
    notes: Optional[str] = None


class EvidenceOut(BaseModel):
    id: int
    claim_id: int
    paper_id: int
    evidence_type: EvidenceType
    evidence_text: str
    source_location: Optional[str] = None
    strength: Optional[float] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class OpenQuestionCreate(BaseModel):
    project_id: int
    question: str
    origin: Optional[str] = None
    importance: Optional[int] = None
    notes: Optional[str] = None


class OpenQuestionUpdate(BaseModel):
    question: Optional[str] = None
    origin: Optional[str] = None
    status: Optional[str] = None
    importance: Optional[int] = None
    notes: Optional[str] = None


class OpenQuestionOut(BaseModel):
    id: int
    project_id: int
    question: str
    origin: Optional[str] = None
    status: str
    importance: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
