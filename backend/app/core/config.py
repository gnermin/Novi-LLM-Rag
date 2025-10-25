from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/multi_rag")
    SECRET_KEY: str = os.getenv("SESSION_SECRET", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    EMBEDDINGS_PROVIDER: str = os.getenv("EMBEDDINGS_PROVIDER", "openai")
    EMBEDDINGS_DIM: int = int(os.getenv("EMBEDDINGS_DIM", "1536"))
    EMBEDDINGS_MODEL: str = os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small")
    
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    AGENT_REWRITES: int = int(os.getenv("AGENT_REWRITES", "2"))
    JUDGE_STRICTNESS: str = os.getenv("JUDGE_STRICTNESS", "medium")
    
    OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "true").lower() == "true"
    PIPELINE_MODE: str = os.getenv("PIPELINE_MODE", "full")
    
    EXTERNAL_DB_URL: Optional[str] = os.getenv("EXTERNAL_DB_URL")
    SQL_INGEST_QUERY: Optional[str] = os.getenv("SQL_INGEST_QUERY")
    SQL_INGEST_BATCH_SIZE: int = int(os.getenv("SQL_INGEST_BATCH_SIZE", "500"))
    
    UPLOAD_MAX_SIZE: int = 50 * 1024 * 1024
    UPLOAD_DIR: str = "uploads"
    
    class Config:
        env_file = ".env"


settings = Settings()
