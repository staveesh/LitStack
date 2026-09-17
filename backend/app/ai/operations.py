"""AI operation implementations. All LLM calls go through here, never in routers."""
import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ai.provider import LLMProvider
from app.ai import prompts
from app.models import Paper, ResearchQuestion, PaperExtraction, Claim, OpenQuestion, AIOperationLog
from app.schemas.ai import (
    TriageResult, ExtractionResult, ReadingContract,
    ClaimSuggestion, OQSuggestion,
)


async def _log_operation(
    db: AsyncSession,
    operation_type: str,
    model_name: str,
    prompt_version: str,
    input_data: dict,
    output: dict,
) -> None:
    input_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:16]
    log = AIOperationLog(
        operation_type=operation_type,
        model_name=model_name,
        prompt_version=prompt_version,
        input_hash=input_hash,
        output=output,
    )
    db.add(log)
    await db.flush()


async def triage_papers(
    paper_ids: list[int],
    db: AsyncSession,
    provider: LLMProvider,
    project_id: int | None = None,
) -> list[TriageResult]:
    papers = (await db.execute(select(Paper).where(Paper.id.in_(paper_ids)))).scalars().all()
    rqs: list[ResearchQuestion] = []
    project_name = "General"

    if project_id:
        from app.models import Project
        proj = await db.get(Project, project_id)
        if proj:
            project_name = proj.name
            rqs_result = await db.execute(
                select(ResearchQuestion).where(
                    ResearchQuestion.project_id == project_id,
                    ResearchQuestion.status == "active",
                )
            )
            rqs = rqs_result.scalars().all()

    rq_texts = [r.question for r in rqs]
    results = []

    for paper in papers:
        if not paper.abstract:
            results.append(TriageResult(
                paper_id=paper.id,
                relevance_score=0.0,
                recommended_action="ignore",
                reason="No abstract available for triage.",
                suggested_reading_intent="Review abstract manually.",
                confidence=0.0,
            ))
            continue

        class _TriageOut(TriageResult):
            pass

        user_msg = prompts.triage_user(
            title=paper.title,
            abstract=paper.abstract or "",
            project_name=project_name,
            research_questions=rq_texts,
        )

        # Build a triage-specific schema with rq text (we map IDs separately)
        from pydantic import BaseModel
        from typing import Literal

        class _TResult(BaseModel):
            relevance_score: float
            recommended_action: Literal["deep_read", "skim", "citation_only", "ignore"]
            reason: str
            related_questions: list[str] = []  # matched by text
            suggested_reading_intent: str
            sections_to_inspect: list[str] = []
            confidence: float

        result = await provider.complete_structured(
            system=prompts.TRIAGE_SYSTEM,
            user=user_msg,
            schema=_TResult,
        )

        # Match related question texts back to IDs
        related_ids = [
            rq.id for rq in rqs
            if any(q.lower() in rq.question.lower() or rq.question.lower() in q.lower()
                   for q in result.related_questions)
        ]

        triage = TriageResult(
            paper_id=paper.id,
            relevance_score=result.relevance_score,
            recommended_action=result.recommended_action,
            reason=result.reason,
            related_question_ids=related_ids,
            suggested_reading_intent=result.suggested_reading_intent,
            sections_to_inspect=result.sections_to_inspect,
            confidence=result.confidence,
        )

        await _log_operation(
            db, "triage", provider.model_name, prompts.TRIAGE_VERSION,
            {"paper_id": paper.id, "project_id": project_id},
            triage.model_dump(),
        )
        results.append(triage)

    await db.commit()
    return results


async def extract_paper(
    paper_id: int,
    db: AsyncSession,
    provider: LLMProvider,
    text_excerpt: str,
) -> PaperExtraction:
    paper = await db.get(Paper, paper_id)
    if not paper:
        raise ValueError(f"Paper {paper_id} not found")

    class _ExtOut(ExtractionResult):
        pass

    result: ExtractionResult = await provider.complete_structured(
        system=prompts.EXTRACTION_SYSTEM,
        user=prompts.extraction_user(text_excerpt, paper.title),
        schema=ExtractionResult,
    )

    extraction = await db.get(PaperExtraction, paper_id)  # won't work by paper_id; use query
    existing = (await db.execute(
        select(PaperExtraction).where(PaperExtraction.paper_id == paper_id)
    )).scalar_one_or_none()

    data = result.model_dump()
    if existing:
        for k, v in data.items():
            setattr(existing, k, v)
        existing.model_name = provider.model_name
        existing.prompt_version = prompts.EXTRACTION_VERSION
        existing.confidence = result.confidence
        existing.generated_at = datetime.now(timezone.utc)
        db.add(existing)
    else:
        existing = PaperExtraction(
            paper_id=paper_id,
            model_name=provider.model_name,
            prompt_version=prompts.EXTRACTION_VERSION,
            confidence=result.confidence,
            generated_at=datetime.now(timezone.utc),
            **{k: v for k, v in data.items() if k != "confidence"},
        )
        db.add(existing)

    await _log_operation(
        db, "extraction", provider.model_name, prompts.EXTRACTION_VERSION,
        {"paper_id": paper_id},
        data,
    )
    await db.commit()
    await db.refresh(existing)
    return existing


async def generate_reading_contract(
    paper_id: int,
    db: AsyncSession,
    provider: LLMProvider,
    project_id: int | None = None,
    research_question_id: int | None = None,
    reading_intent_id: int | None = None,
) -> ReadingContract:
    paper = await db.get(Paper, paper_id)
    if not paper:
        raise ValueError(f"Paper {paper_id} not found")

    intent_text = paper.reading_reason or ""
    if reading_intent_id:
        from app.models import ReadingIntent
        ri = await db.get(ReadingIntent, reading_intent_id)
        if ri:
            intent_text = ri.intent

    question_text = ""
    if research_question_id:
        rq = await db.get(ResearchQuestion, research_question_id)
        if rq:
            question_text = rq.question

    project_name = "General"
    if project_id:
        from app.models import Project
        proj = await db.get(Project, project_id)
        if proj:
            project_name = proj.name

    result: ReadingContract = await provider.complete_structured(
        system=prompts.READING_CONTRACT_SYSTEM,
        user=prompts.reading_contract_user(
            title=paper.title,
            abstract=paper.abstract or "",
            intent=intent_text,
            question=question_text,
            project=project_name,
        ),
        schema=ReadingContract,
    )

    await _log_operation(
        db, "reading_contract", provider.model_name, prompts.READING_CONTRACT_VERSION,
        {"paper_id": paper_id},
        result.model_dump(),
    )
    await db.commit()
    return result


async def suggest_claims(
    paper_id: int,
    db: AsyncSession,
    provider: LLMProvider,
    project_id: int,
) -> list[ClaimSuggestion]:
    paper = await db.get(Paper, paper_id)
    if not paper:
        raise ValueError(f"Paper {paper_id} not found")

    claims = (await db.execute(
        select(Claim).where(Claim.project_id == project_id)
    )).scalars().all()

    from pydantic import BaseModel

    class _SuggestionsOut(BaseModel):
        suggestions: list[ClaimSuggestion]

    result: _SuggestionsOut = await provider.complete_structured(
        system=prompts.CLAIM_SUGGESTION_SYSTEM,
        user=prompts.claim_suggestion_user(
            title=paper.title,
            abstract=paper.abstract or "",
            existing_claims=[{"id": c.id, "claim": c.claim} for c in claims],
        ),
        schema=_SuggestionsOut,
    )

    await _log_operation(
        db, "claim_suggestions", provider.model_name, prompts.CLAIM_SUGGESTION_VERSION,
        {"paper_id": paper_id, "project_id": project_id},
        result.model_dump(),
    )
    await db.commit()
    return result.suggestions


async def suggest_open_questions(
    paper_id: int,
    db: AsyncSession,
    provider: LLMProvider,
    project_id: int,
) -> list[OQSuggestion]:
    paper = await db.get(Paper, paper_id)
    if not paper:
        raise ValueError(f"Paper {paper_id} not found")

    oqs = (await db.execute(
        select(OpenQuestion).where(OpenQuestion.project_id == project_id)
    )).scalars().all()

    from pydantic import BaseModel

    class _OQOut(BaseModel):
        suggestions: list[OQSuggestion]

    result: _OQOut = await provider.complete_structured(
        system=prompts.OQ_SUGGESTION_SYSTEM,
        user=prompts.oq_suggestion_user(
            title=paper.title,
            abstract=paper.abstract or "",
            existing_questions=[q.question for q in oqs],
        ),
        schema=_OQOut,
    )

    await _log_operation(
        db, "oq_suggestions", provider.model_name, prompts.OQ_SUGGESTION_VERSION,
        {"paper_id": paper_id, "project_id": project_id},
        result.model_dump(),
    )
    await db.commit()
    return result.suggestions
