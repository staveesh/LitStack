import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer,
    String, Text, JSON, Enum as SAEnum, Table, UniqueConstraint, func
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from app.database import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class WorkflowStatus(str, enum.Enum):
    inbox = "inbox"
    triaged = "triaged"
    skim = "skim"
    deep_read = "deep_read"
    read = "read"
    citation_only = "citation_only"
    archived = "archived"


class RQStatus(str, enum.Enum):
    active = "active"
    partially_answered = "partially_answered"
    answered = "answered"
    abandoned = "abandoned"


class ClaimStatus(str, enum.Enum):
    hypothesis = "hypothesis"
    weak_evidence = "weak_evidence"
    supported = "supported"
    contested = "contested"
    rejected = "rejected"


class EvidenceType(str, enum.Enum):
    supports = "supports"
    contradicts = "contradicts"
    qualifies = "qualifies"
    background = "background"
    methodological = "methodological"


class OQStatus(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    answered = "answered"
    converted_to_experiment = "converted_to_experiment"
    abandoned = "abandoned"


# ── Junction tables ────────────────────────────────────────────────────────────

paper_projects = Table(
    "paper_projects", Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
)

paper_research_questions = Table(
    "paper_research_questions", Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("research_question_id", Integer, ForeignKey("research_questions.id", ondelete="CASCADE"), primary_key=True),
)

paper_open_questions = Table(
    "paper_open_questions", Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("open_question_id", Integer, ForeignKey("open_questions.id", ondelete="CASCADE"), primary_key=True),
)

paper_synthesis_notes = Table(
    "paper_synthesis_notes", Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("synthesis_note_id", Integer, ForeignKey("synthesis_notes.id", ondelete="CASCADE"), primary_key=True),
)


# ── Core entities ──────────────────────────────────────────────────────────────

class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(primary_key=True)
    zotero_key: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list] = mapped_column(JSON, default=list)  # list of strings
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    citation_key: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    date_added: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    workflow_status: Mapped[WorkflowStatus] = mapped_column(
        SAEnum(WorkflowStatus), default=WorkflowStatus.inbox, nullable=False
    )
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reading_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    zotero_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    projects = relationship("Project", secondary=paper_projects, back_populates="papers")
    research_questions = relationship("ResearchQuestion", secondary=paper_research_questions, back_populates="papers")
    open_questions = relationship("OpenQuestion", secondary=paper_open_questions, back_populates="papers")
    synthesis_notes = relationship("SynthesisNote", secondary=paper_synthesis_notes, back_populates="papers")
    reading_intents = relationship("ReadingIntent", back_populates="paper", cascade="all, delete-orphan")
    extraction = relationship("PaperExtraction", back_populates="paper", uselist=False, cascade="all, delete-orphan")
    notes = relationship("HumanPaperNote", back_populates="paper", uselist=False, cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="paper", cascade="all, delete-orphan")
    chunks = relationship("PaperChunk", back_populates="paper", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    papers = relationship("Paper", secondary=paper_projects, back_populates="projects")
    research_questions = relationship("ResearchQuestion", back_populates="project", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="project", cascade="all, delete-orphan")
    open_questions = relationship("OpenQuestion", back_populates="project", cascade="all, delete-orphan")
    synthesis_notes = relationship("SynthesisNote", back_populates="project", cascade="all, delete-orphan")


class ResearchQuestion(Base):
    __tablename__ = "research_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    motivation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[RQStatus] = mapped_column(SAEnum(RQStatus), default=RQStatus.active)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="research_questions")
    papers = relationship("Paper", secondary=paper_research_questions, back_populates="research_questions")
    reading_intents = relationship("ReadingIntent", back_populates="research_question")


class ReadingIntent(Base):
    __tablename__ = "reading_intents"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"))
    research_question_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("research_questions.id", ondelete="SET NULL"), nullable=True
    )
    intent: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    paper = relationship("Paper", back_populates="reading_intents")
    research_question = relationship("ResearchQuestion", back_populates="reading_intents")


class PaperExtraction(Base):
    __tablename__ = "paper_extractions"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), unique=True)
    problem: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key_idea: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approach: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    architecture: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    threat_model: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assumptions: Mapped[list] = mapped_column(JSON, default=list)
    dataset: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evaluation_methodology: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    baselines: Mapped[list] = mapped_column(JSON, default=list)
    metrics: Mapped[list] = mapped_column(JSON, default=list)
    main_results: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    limitations: Mapped[list] = mapped_column(JSON, default=list)
    future_work: Mapped[list] = mapped_column(JSON, default=list)
    relevant_sections: Mapped[list] = mapped_column(JSON, default=list)
    important_figures: Mapped[list] = mapped_column(JSON, default=list)
    claims_made: Mapped[list] = mapped_column(JSON, default=list)
    model_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    paper = relationship("Paper", back_populates="extraction")


class HumanPaperNote(Base):
    __tablename__ = "human_paper_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), unique=True)
    why_i_care: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    what_surprised_me: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    what_i_dont_believe: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    relation_to_my_work: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    what_i_might_cite_this_for: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    methodological_ideas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unanswered_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    freeform_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    paper = relationship("Paper", back_populates="notes")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ClaimStatus] = mapped_column(SAEnum(ClaimStatus), default=ClaimStatus.hypothesis)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project = relationship("Project", back_populates="claims")
    evidence = relationship("Evidence", back_populates="claim", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id", ondelete="CASCADE"))
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"))
    evidence_type: Mapped[EvidenceType] = mapped_column(SAEnum(EvidenceType))
    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_location: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    strength: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    claim = relationship("Claim", back_populates="evidence")
    paper = relationship("Paper", back_populates="evidence")


class OpenQuestion(Base):
    __tablename__ = "open_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    origin: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[OQStatus] = mapped_column(SAEnum(OQStatus), default=OQStatus.open)
    importance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="open_questions")
    papers = relationship("Paper", secondary=paper_open_questions, back_populates="open_questions")


class SynthesisNote(Base):
    __tablename__ = "synthesis_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    synthesis_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project = relationship("Project", back_populates="synthesis_notes")
    papers = relationship("Paper", secondary=paper_synthesis_notes, back_populates="synthesis_notes")


class PaperChunk(Base):
    """Structural chunks for semantic search (post-MVP: embedding filled later)."""
    __tablename__ = "paper_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    page_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    page_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)  # ponytail: deferred until semantic search milestone

    paper = relationship("Paper", back_populates="chunks")

    __table_args__ = (
        UniqueConstraint("paper_id", "chunk_index"),
    )


class AIOperationLog(Base):
    __tablename__ = "ai_operation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    operation_type: Mapped[str] = mapped_column(String(128), nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    input_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    output = Column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
