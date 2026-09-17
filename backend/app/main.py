from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import papers, projects, research_questions, zotero, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure pgvector extension exists before creating tables
    async with engine.begin() as conn:
        await conn.execute(__import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Paper Reading Tracker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(research_questions.router, prefix="/api")
app.include_router(zotero.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
