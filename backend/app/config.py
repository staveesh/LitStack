from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://papertracker:papertracker@localhost/papertracker"
    zotero_api_key: str = ""
    zotero_library_id: str = ""
    zotero_library_type: Literal["user", "group"] = "user"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    local_llm_base_url: str = ""
    local_llm_model: str = ""
    default_ai_provider: Literal["anthropic", "openai", "local"] = "anthropic"
    pdf_storage_path: str = "/data/pdfs"
    zotero_collection_key: str = ""   # if set, sync only this collection
    zotero_sync_interval_minutes: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
