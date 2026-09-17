"""Zotero Web API client. Zotero is a read-only source; we never write back to it."""
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models import Paper, WorkflowStatus, AIOperationLog


ZOTERO_BASE = "https://api.zotero.org"


class ZoteroClient:
    def __init__(self):
        self.api_key = settings.zotero_api_key
        self.library_id = settings.zotero_library_id
        self.library_type = settings.zotero_library_type
        self._base = f"{ZOTERO_BASE}/{self.library_type}s/{self.library_id}"

    def _headers(self) -> dict:
        return {"Zotero-API-Key": self.api_key, "Zotero-API-Version": "3"}

    async def fetch_collections(self) -> list[dict]:
        """Return all collections in the library (key, name, parent)."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self._base}/collections",
                headers=self._headers(),
                params={"limit": 100, "format": "json"},
            )
            resp.raise_for_status()
            return [
                {
                    "key": c["key"],
                    "name": c["data"]["name"],
                    "parent": c["data"].get("parentCollection") or None,
                }
                for c in resp.json()
            ]

    def _items_url(self) -> str:
        key = settings.zotero_collection_key
        if key:
            return f"{self._base}/collections/{key}/items"
        return f"{self._base}/items"

    async def fetch_items(self, since_version: int = 0, limit: int = 100, start: int = 0) -> tuple[list[dict], int]:
        """Returns (items, library_version)."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                self._items_url(),
                headers=self._headers(),
                params={
                    "since": since_version,
                    "limit": limit,
                    "start": start,
                    "format": "json",
                },
            )
            resp.raise_for_status()
            library_version = int(resp.headers.get("Last-Modified-Version", 0))
            # Filter out attachments and notes in Python (avoids httpx encoding issues with Zotero's || syntax)
            items = [
                i for i in resp.json()
                if i.get("data", {}).get("itemType") not in ("attachment", "note")
            ]
            return items, library_version

    async def fetch_all_items(self, since_version: int = 0) -> tuple[list[dict], int]:
        items, version = [], 0
        start = 0
        while True:
            batch, version = await self.fetch_items(since_version=since_version, limit=100, start=start)
            items.extend(batch)
            if len(batch) < 100:
                break
            start += 100
        return items, version

    async def download_pdf(self, item_key: str) -> str | None:
        """Download PDF attachment for a Zotero item. Returns local path or None."""
        storage = Path(settings.pdf_storage_path)
        storage.mkdir(parents=True, exist_ok=True)
        pdf_path = storage / f"{item_key}.pdf"

        if pdf_path.exists():
            return str(pdf_path)

        async with httpx.AsyncClient(timeout=60) as client:
            # Get attachments
            resp = await client.get(
                f"{self._base}/items/{item_key}/children",
                headers=self._headers(),
                params={"itemType": "attachment"},
            )
            if resp.status_code != 200:
                return None
            children = resp.json()
            pdf_children = [
                c for c in children
                if c.get("data", {}).get("contentType") == "application/pdf"
            ]
            if not pdf_children:
                return None

            att_key = pdf_children[0]["key"]
            file_resp = await client.get(
                f"{self._base}/items/{att_key}/file",
                headers=self._headers(),
                follow_redirects=True,
            )
            if file_resp.status_code != 200:
                return None

            pdf_path.write_bytes(file_resp.content)
            return str(pdf_path)


def _parse_zotero_item(item: dict) -> dict:
    data = item.get("data", {})
    authors = [
        f"{c.get('lastName', '')}, {c.get('firstName', '')}".strip(", ")
        for c in data.get("creators", [])
        if c.get("creatorType") == "author"
    ]
    return {
        "zotero_key": item["key"],
        "title": data.get("title", "Untitled"),
        "authors": authors,
        "year": int(data["date"][:4]) if data.get("date") and data["date"][:4].isdigit() else None,
        "venue": data.get("publicationTitle") or data.get("conferenceName") or data.get("proceedingsTitle"),
        "doi": data.get("DOI"),
        "url": data.get("url"),
        "abstract": data.get("abstractNote"),
        "citation_key": data.get("citationKey"),
        "date_added": datetime.fromisoformat(data["dateAdded"].replace("Z", "+00:00")) if data.get("dateAdded") else None,
        "zotero_version": item.get("version"),
    }


async def sync_zotero(db: AsyncSession) -> dict:
    """Idempotent sync: import new papers, update metadata of existing ones.
    Never overwrites application metadata (reading intents, notes, claims, etc.)."""
    client = ZoteroClient()
    if not client.api_key or not client.library_id:
        return {"error": "Zotero not configured. Set ZOTERO_API_KEY and ZOTERO_LIBRARY_ID."}

    # Get last known version from most recent log
    last_log = (await db.execute(
        select(AIOperationLog)
        .where(AIOperationLog.operation_type == "zotero_sync")
        .order_by(AIOperationLog.created_at.desc())
        .limit(1)
    )).scalar_one_or_none()

    since_version = last_log.output.get("library_version", 0) if last_log and last_log.output else 0

    items, library_version = await client.fetch_all_items(since_version=since_version)

    imported, updated, skipped = 0, 0, 0
    for item in items:
        parsed = _parse_zotero_item(item)
        existing = (await db.execute(
            select(Paper).where(Paper.zotero_key == parsed["zotero_key"])
        )).scalar_one_or_none()

        if existing:
            if existing.zotero_version != parsed["zotero_version"]:
                # Update only bibliographic fields; never touch app metadata
                for field in ("title", "authors", "year", "venue", "doi", "url", "abstract", "citation_key", "date_added", "zotero_version"):
                    setattr(existing, field, parsed[field])
                db.add(existing)
                updated += 1
            else:
                skipped += 1
        else:
            paper = Paper(**parsed, workflow_status=WorkflowStatus.inbox)
            db.add(paper)
            imported += 1

    log = AIOperationLog(
        operation_type="zotero_sync",
        output={"library_version": library_version, "imported": imported, "updated": updated, "skipped": skipped},
    )
    db.add(log)
    await db.commit()

    return {"imported": imported, "updated": updated, "skipped": skipped, "library_version": library_version}
