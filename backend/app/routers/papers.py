from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import (
    Paper, WorkflowStatus, HumanPaperNote, PaperExtraction,
    ReadingIntent, ResearchQuestion, paper_research_questions, paper_projects
)
from app.schemas.paper import PaperCreate, PaperUpdate, PaperOut, PaperDetail
from app.schemas.extraction import HumanNoteUpdate, HumanNoteOut, ExtractionOut
from app.schemas.reading_intent import ReadingIntentCreate, ReadingIntentResolve, ReadingIntentOut

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("", response_model=list[PaperOut])
async def list_papers(
    status: Optional[WorkflowStatus] = None,
    project_id: Optional[int] = None,
    research_question_id: Optional[int] = None,
    q: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Paper)
    if status:
        stmt = stmt.where(Paper.workflow_status == status)
    if project_id:
        stmt = stmt.where(Paper.projects.any(id=project_id))
    if research_question_id:
        stmt = stmt.where(Paper.research_questions.any(id=research_question_id))
    if q:
        stmt = stmt.where(
            or_(
                Paper.title.ilike(f"%{q}%"),
                Paper.abstract.ilike(f"%{q}%"),
                Paper.citation_key.ilike(f"%{q}%"),
            )
        )
    stmt = stmt.order_by(Paper.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=PaperOut, status_code=201)
async def create_paper(body: PaperCreate, db: AsyncSession = Depends(get_db)):
    paper = Paper(**body.model_dump())
    db.add(paper)
    await db.commit()
    await db.refresh(paper)
    return paper


@router.get("/{paper_id}", response_model=PaperDetail)
async def get_paper(paper_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Paper)
        .options(selectinload(Paper.projects), selectinload(Paper.research_questions))
        .where(Paper.id == paper_id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    out = PaperDetail.model_validate(paper)
    out.project_ids = [p.id for p in paper.projects]
    out.research_question_ids = [r.id for r in paper.research_questions]
    return out


@router.put("/{paper_id}", response_model=PaperOut)
async def update_paper(paper_id: int, body: PaperUpdate, db: AsyncSession = Depends(get_db)):
    paper = await db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(404, "Paper not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(paper, k, v)
    db.add(paper)
    await db.commit()
    await db.refresh(paper)
    return paper


@router.delete("/{paper_id}", status_code=204)
async def delete_paper(
    paper_id: int,
    zotero: bool = False,
    db: AsyncSession = Depends(get_db),
):
    paper = await db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(404, "Paper not found")
    if zotero and paper.zotero_key and paper.zotero_version is not None:
        from app.services.zotero import ZoteroClient
        try:
            await ZoteroClient().delete_item(paper.zotero_key, paper.zotero_version)
        except Exception as e:
            raise HTTPException(502, f"Zotero delete failed: {e}")
    await db.delete(paper)
    await db.commit()


# ── Research question links ────────────────────────────────────────────────────

@router.post("/{paper_id}/research-questions/{rq_id}", status_code=204)
async def link_rq(paper_id: int, rq_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Paper).options(selectinload(Paper.research_questions)).where(Paper.id == paper_id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    rq = await db.get(ResearchQuestion, rq_id)
    if not rq:
        raise HTTPException(404, "Research question not found")
    if rq not in paper.research_questions:
        paper.research_questions.append(rq)
        db.add(paper)
        await db.commit()


@router.delete("/{paper_id}/research-questions/{rq_id}", status_code=204)
async def unlink_rq(paper_id: int, rq_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Paper).options(selectinload(Paper.research_questions)).where(Paper.id == paper_id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    rq = await db.get(ResearchQuestion, rq_id)
    if rq and rq in paper.research_questions:
        paper.research_questions.remove(rq)
        db.add(paper)
        await db.commit()


# ── Project links ──────────────────────────────────────────────────────────────

@router.post("/{paper_id}/projects/{project_id}", status_code=204)
async def link_project(paper_id: int, project_id: int, db: AsyncSession = Depends(get_db)):
    from app.models import Project
    result = await db.execute(
        select(Paper).options(selectinload(Paper.projects)).where(Paper.id == paper_id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    proj = await db.get(Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    if proj not in paper.projects:
        paper.projects.append(proj)
        db.add(paper)
        await db.commit()


@router.delete("/{paper_id}/projects/{project_id}", status_code=204)
async def unlink_project(paper_id: int, project_id: int, db: AsyncSession = Depends(get_db)):
    from app.models import Project
    result = await db.execute(
        select(Paper).options(selectinload(Paper.projects)).where(Paper.id == paper_id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    proj = await db.get(Project, project_id)
    if proj and proj in paper.projects:
        paper.projects.remove(proj)
        db.add(paper)
        await db.commit()


# ── Reading intents ────────────────────────────────────────────────────────────

@router.get("/{paper_id}/reading-intents", response_model=list[ReadingIntentOut])
async def list_intents(paper_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ReadingIntent).where(ReadingIntent.paper_id == paper_id)
        .order_by(ReadingIntent.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{paper_id}/reading-intents", response_model=ReadingIntentOut, status_code=201)
async def create_intent(paper_id: int, body: ReadingIntentCreate, db: AsyncSession = Depends(get_db)):
    paper = await db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(404, "Paper not found")
    intent = ReadingIntent(**body.model_dump())
    db.add(intent)
    await db.commit()
    await db.refresh(intent)
    return intent


@router.post("/{paper_id}/reading-intents/{intent_id}/resolve", response_model=ReadingIntentOut)
async def resolve_intent(
    paper_id: int, intent_id: int, body: ReadingIntentResolve, db: AsyncSession = Depends(get_db)
):
    intent = await db.get(ReadingIntent, intent_id)
    if not intent or intent.paper_id != paper_id:
        raise HTTPException(404, "Reading intent not found")
    intent.resolved_at = datetime.now(timezone.utc)
    intent.resolution_notes = body.resolution_notes
    db.add(intent)
    await db.commit()
    await db.refresh(intent)
    return intent


# ── Human notes ────────────────────────────────────────────────────────────────

@router.get("/{paper_id}/notes", response_model=HumanNoteOut)
async def get_notes(paper_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(HumanPaperNote).where(HumanPaperNote.paper_id == paper_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(404, "No notes yet")
    return note


@router.put("/{paper_id}/notes", response_model=HumanNoteOut)
async def upsert_notes(paper_id: int, body: HumanNoteUpdate, db: AsyncSession = Depends(get_db)):
    paper = await db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(404, "Paper not found")
    result = await db.execute(
        select(HumanPaperNote).where(HumanPaperNote.paper_id == paper_id)
    )
    note = result.scalar_one_or_none()
    updates = body.model_dump(exclude_none=True)
    if note:
        for k, v in updates.items():
            setattr(note, k, v)
        db.add(note)
    else:
        note = HumanPaperNote(paper_id=paper_id, **updates)
        db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


# ── AI extraction ──────────────────────────────────────────────────────────────

@router.get("/{paper_id}/extraction", response_model=ExtractionOut)
async def get_extraction(paper_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PaperExtraction).where(PaperExtraction.paper_id == paper_id)
    )
    ext = result.scalar_one_or_none()
    if not ext:
        raise HTTPException(404, "No extraction yet")
    return ext


@router.post("/{paper_id}/extraction", response_model=ExtractionOut)
async def trigger_extraction(paper_id: int, db: AsyncSession = Depends(get_db)):
    from app.ai.provider import get_provider
    from app.ai.operations import extract_paper
    from app.services.pdf import get_full_text

    paper = await db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(404, "Paper not found")
    if not paper.pdf_path:
        raise HTTPException(422, "No PDF available for extraction")

    try:
        text = get_full_text(paper.pdf_path)
    except Exception as e:
        raise HTTPException(422, f"PDF extraction failed: {e}")

    provider = get_provider()
    extraction = await extract_paper(paper_id, db, provider, text)
    return extraction
