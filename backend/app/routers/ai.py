from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.ai.provider import get_provider
from app.ai.operations import (
    triage_papers, generate_reading_contract,
    suggest_claims, suggest_open_questions,
)
from app.schemas.ai import (
    TriageRequest, TriageResult, TriageApply,
    ReadingContractRequest, ReadingContract,
    ClaimSuggestion, OQSuggestion,
)
from app.models import Paper, WorkflowStatus, ReadingIntent

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/triage", response_model=list[TriageResult])
async def ai_triage(body: TriageRequest, db: AsyncSession = Depends(get_db)):
    """Returns AI triage suggestions. Does NOT apply them — user must call /ai/triage/apply."""
    try:
        provider = get_provider()
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    return await triage_papers(body.paper_ids, db, provider, body.project_id)


@router.post("/triage/apply", status_code=204)
async def apply_triage(body: TriageApply, db: AsyncSession = Depends(get_db)):
    """Apply user-approved triage results to a paper."""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    result = await db.execute(
        select(Paper).options(selectinload(Paper.research_questions)).where(Paper.id == body.paper_id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")

    paper.workflow_status = WorkflowStatus(body.workflow_status)
    paper.relevance_score = body.relevance_score

    if body.reading_intent:
        intent = ReadingIntent(paper_id=body.paper_id, intent=body.reading_intent)
        db.add(intent)

    if body.research_question_ids:
        from app.models import ResearchQuestion
        for rq_id in body.research_question_ids:
            rq = await db.get(ResearchQuestion, rq_id)
            if rq and rq not in paper.research_questions:
                paper.research_questions.append(rq)

    db.add(paper)
    await db.commit()


@router.post("/reading-contract/{paper_id}", response_model=ReadingContract)
async def reading_contract(paper_id: int, body: ReadingContractRequest, db: AsyncSession = Depends(get_db)):
    try:
        provider = get_provider()
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    try:
        return await generate_reading_contract(
            paper_id, db, provider,
            project_id=body.project_id,
            research_question_id=body.research_question_id,
            reading_intent_id=body.reading_intent_id,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/claim-suggestions/{paper_id}", response_model=list[ClaimSuggestion])
async def claim_suggestions(paper_id: int, project_id: int, db: AsyncSession = Depends(get_db)):
    try:
        provider = get_provider()
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    return await suggest_claims(paper_id, db, provider, project_id)


@router.post("/open-question-suggestions/{paper_id}", response_model=list[OQSuggestion])
async def oq_suggestions(paper_id: int, project_id: int, db: AsyncSession = Depends(get_db)):
    try:
        provider = get_provider()
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    return await suggest_open_questions(paper_id, db, provider, project_id)
