from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.zotero import sync_zotero, ZoteroClient

router = APIRouter(prefix="/zotero", tags=["zotero"])


@router.post("/sync")
async def trigger_sync(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Trigger a Zotero sync. Runs synchronously (may take a few seconds for large libraries)."""
    result = await sync_zotero(db)
    return result


@router.get("/collections")
async def list_collections():
    """List all Zotero collections so the user can find a collection key."""
    client = ZoteroClient()
    if not client.api_key or not client.library_id:
        return {"error": "Zotero not configured"}
    return await client.fetch_collections()


@router.get("/status")
async def sync_status(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models import AIOperationLog
    log = (await db.execute(
        select(AIOperationLog)
        .where(AIOperationLog.operation_type == "zotero_sync")
        .order_by(AIOperationLog.created_at.desc())
        .limit(1)
    )).scalar_one_or_none()
    if not log:
        return {"synced": False}
    return {"synced": True, "last_sync": log.created_at, **log.output}
