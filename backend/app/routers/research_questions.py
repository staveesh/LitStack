from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ResearchQuestion, Claim, Evidence, OpenQuestion
from app.schemas.research_question import RQUpdate, RQOut
from app.schemas.claim import ClaimUpdate, ClaimOut, EvidenceCreate, EvidenceOut, OpenQuestionUpdate, OpenQuestionOut

router = APIRouter(tags=["knowledge"])


@router.put("/research-questions/{rq_id}", response_model=RQOut)
async def update_rq(rq_id: int, body: RQUpdate, db: AsyncSession = Depends(get_db)):
    rq = await db.get(ResearchQuestion, rq_id)
    if not rq:
        raise HTTPException(404, "Research question not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(rq, k, v)
    db.add(rq)
    await db.commit()
    await db.refresh(rq)
    return rq


@router.get("/research-questions", response_model=list[RQOut])
async def list_all_rqs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ResearchQuestion).order_by(ResearchQuestion.created_at))
    return result.scalars().all()


@router.put("/claims/{claim_id}", response_model=ClaimOut)
async def update_claim(claim_id: int, body: ClaimUpdate, db: AsyncSession = Depends(get_db)):
    claim = await db.get(Claim, claim_id)
    if not claim:
        raise HTTPException(404, "Claim not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(claim, k, v)
    db.add(claim)
    await db.commit()
    await db.refresh(claim)
    return claim


@router.get("/claims/{claim_id}/evidence", response_model=list[EvidenceOut])
async def list_evidence(claim_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evidence).where(Evidence.claim_id == claim_id))
    return result.scalars().all()


@router.post("/claims/{claim_id}/evidence", response_model=EvidenceOut, status_code=201)
async def add_evidence(claim_id: int, body: EvidenceCreate, db: AsyncSession = Depends(get_db)):
    claim = await db.get(Claim, claim_id)
    if not claim:
        raise HTTPException(404, "Claim not found")
    body.claim_id = claim_id
    ev = Evidence(**body.model_dump())
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    return ev


@router.delete("/evidence/{evidence_id}", status_code=204)
async def delete_evidence(evidence_id: int, db: AsyncSession = Depends(get_db)):
    ev = await db.get(Evidence, evidence_id)
    if not ev:
        raise HTTPException(404, "Evidence not found")
    await db.delete(ev)
    await db.commit()


@router.put("/open-questions/{oq_id}", response_model=OpenQuestionOut)
async def update_oq(oq_id: int, body: OpenQuestionUpdate, db: AsyncSession = Depends(get_db)):
    oq = await db.get(OpenQuestion, oq_id)
    if not oq:
        raise HTTPException(404, "Open question not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(oq, k, v)
    db.add(oq)
    await db.commit()
    await db.refresh(oq)
    return oq
