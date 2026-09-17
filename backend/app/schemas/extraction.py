from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ExtractionOut(BaseModel):
    id: int
    paper_id: int
    problem: Optional[str] = None
    key_idea: Optional[str] = None
    approach: Optional[str] = None
    architecture: Optional[str] = None
    threat_model: Optional[str] = None
    assumptions: list[str] = []
    dataset: Optional[str] = None
    evaluation_methodology: Optional[str] = None
    baselines: list[str] = []
    metrics: list[str] = []
    main_results: Optional[str] = None
    limitations: list[str] = []
    future_work: list[str] = []
    relevant_sections: list[str] = []
    important_figures: list[str] = []
    claims_made: list[str] = []
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    confidence: Optional[float] = None
    generated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HumanNoteUpdate(BaseModel):
    why_i_care: Optional[str] = None
    what_surprised_me: Optional[str] = None
    what_i_dont_believe: Optional[str] = None
    relation_to_my_work: Optional[str] = None
    what_i_might_cite_this_for: Optional[str] = None
    methodological_ideas: Optional[str] = None
    unanswered_questions: Optional[str] = None
    freeform_notes: Optional[str] = None


class HumanNoteOut(BaseModel):
    id: int
    paper_id: int
    why_i_care: Optional[str] = None
    what_surprised_me: Optional[str] = None
    what_i_dont_believe: Optional[str] = None
    relation_to_my_work: Optional[str] = None
    what_i_might_cite_this_for: Optional[str] = None
    methodological_ideas: Optional[str] = None
    unanswered_questions: Optional[str] = None
    freeform_notes: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}
