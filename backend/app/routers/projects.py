from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Project, ResearchQuestion, Claim, Evidence, OpenQuestion
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.schemas.research_question import RQCreate, RQUpdate, RQOut
from app.schemas.claim import ClaimCreate, ClaimUpdate, ClaimOut, EvidenceCreate, EvidenceOut, OpenQuestionCreate, OpenQuestionUpdate, OpenQuestionOut

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)):
    proj = Project(**body.model_dump())
    db.add(proj)
    await db.commit()
    await db.refresh(proj)
    return proj


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    proj = await db.get(Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    return proj


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(project_id: int, body: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    proj = await db.get(Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(proj, k, v)
    db.add(proj)
    await db.commit()
    await db.refresh(proj)
    return proj


# ── Research questions ─────────────────────────────────────────────────────────

@router.get("/{project_id}/research-questions", response_model=list[RQOut])
async def list_rqs(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ResearchQuestion).where(ResearchQuestion.project_id == project_id)
        .order_by(ResearchQuestion.created_at)
    )
    return result.scalars().all()


@router.post("/{project_id}/research-questions", response_model=RQOut, status_code=201)
async def create_rq(project_id: int, body: RQCreate, db: AsyncSession = Depends(get_db)):
    proj = await db.get(Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    body.project_id = project_id
    rq = ResearchQuestion(**body.model_dump())
    db.add(rq)
    await db.commit()
    await db.refresh(rq)
    return rq


# ── Claims ─────────────────────────────────────────────────────────────────────

@router.get("/{project_id}/claims", response_model=list[ClaimOut])
async def list_claims(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Claim).where(Claim.project_id == project_id).order_by(Claim.created_at)
    )
    return result.scalars().all()


@router.post("/{project_id}/claims", response_model=ClaimOut, status_code=201)
async def create_claim(project_id: int, body: ClaimCreate, db: AsyncSession = Depends(get_db)):
    proj = await db.get(Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    body.project_id = project_id
    claim = Claim(**body.model_dump())
    db.add(claim)
    await db.commit()
    await db.refresh(claim)
    return claim


@router.get("/{project_id}/claims/bibtex", response_class=PlainTextResponse)
async def export_claims_bibtex(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Claim)
        .where(Claim.project_id == project_id)
        .options(selectinload(Claim.evidence).selectinload(Evidence.paper))
    )
    claims = result.scalars().all()

    papers = {}
    for claim in claims:
        for ev in claim.evidence:
            if ev.paper_id not in papers:
                papers[ev.paper_id] = ev.paper

    entries = []
    for paper in papers.values():
        key = paper.citation_key or f"paper{paper.id}"
        authors = " and ".join(paper.authors) if paper.authors else "Unknown"
        lines = [f"@article{{{key},"]
        lines.append(f"  title = {{{paper.title}}},")
        lines.append(f"  author = {{{authors}}},")
        if paper.year:
            lines.append(f"  year = {{{paper.year}}},")
        if paper.venue:
            lines.append(f"  journal = {{{paper.venue}}},")
        if paper.doi:
            lines.append(f"  doi = {{{paper.doi}}},")
        if paper.url:
            lines.append(f"  url = {{{paper.url}}},")
        lines.append("}")
        entries.append("\n".join(lines))

    return PlainTextResponse(
        "\n\n".join(entries) if entries else "% No cited papers found",
        headers={"Content-Disposition": 'attachment; filename="references.bib"'},
    )


# ── Open questions ─────────────────────────────────────────────────────────────

@router.get("/{project_id}/open-questions", response_model=list[OpenQuestionOut])
async def list_oqs(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OpenQuestion).where(OpenQuestion.project_id == project_id).order_by(OpenQuestion.created_at)
    )
    return result.scalars().all()


@router.post("/{project_id}/open-questions", response_model=OpenQuestionOut, status_code=201)
async def create_oq(project_id: int, body: OpenQuestionCreate, db: AsyncSession = Depends(get_db)):
    proj = await db.get(Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    body.project_id = project_id
    oq = OpenQuestion(**body.model_dump())
    db.add(oq)
    await db.commit()
    await db.refresh(oq)
    return oq
