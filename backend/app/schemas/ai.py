from typing import Literal, Optional
from pydantic import BaseModel


# ── Triage ─────────────────────────────────────────────────────────────────────

class TriageRequest(BaseModel):
    paper_ids: list[int]
    project_id: Optional[int] = None


class TriageResult(BaseModel):
    paper_id: int
    relevance_score: float
    recommended_action: Literal["deep_read", "skim", "citation_only", "ignore"]
    reason: str
    related_question_ids: list[int] = []
    suggested_reading_intent: str
    sections_to_inspect: list[str] = []
    confidence: float


class TriageApply(BaseModel):
    """User-approved triage to actually apply."""
    paper_id: int
    workflow_status: str
    relevance_score: float
    reading_intent: Optional[str] = None
    research_question_ids: list[int] = []


# ── Extraction ─────────────────────────────────────────────────────────────────

class ExtractionResult(BaseModel):
    problem: str
    key_idea: str
    approach: str
    architecture: Optional[str] = None
    threat_model: Optional[str] = None
    assumptions: list[str] = []
    dataset: Optional[str] = None
    evaluation_methodology: str
    baselines: list[str] = []
    metrics: list[str] = []
    main_results: str
    limitations: list[str] = []
    future_work: list[str] = []
    relevant_sections: list[str] = []
    important_figures: list[str] = []
    claims_made: list[str] = []
    confidence: float


# ── Reading contract ───────────────────────────────────────────────────────────

class ReadingContractRequest(BaseModel):
    paper_id: int
    project_id: Optional[int] = None
    research_question_id: Optional[int] = None
    reading_intent_id: Optional[int] = None


class ReadingContract(BaseModel):
    why_relevant: str
    priority_sections: list[str]
    claims_to_verify: list[str]
    important_figures: list[str]
    assumptions_to_examine: list[str]
    comparisons_to_own_work: list[str]
    sections_to_skip: list[str]


# ── Claim suggestions ──────────────────────────────────────────────────────────

class ClaimSuggestion(BaseModel):
    claim_id: Optional[int] = None      # existing claim; None = new claim
    claim_text: str
    relation: Literal["supports", "contradicts", "qualifies", "background", "methodological"]
    evidence_text: str
    source_location: str
    confidence: float


# ── Open question suggestions ──────────────────────────────────────────────────

class OQSuggestion(BaseModel):
    question: str
    origin: str
    importance: int     # 1-5
    rationale: str
