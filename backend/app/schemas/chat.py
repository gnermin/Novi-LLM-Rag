from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid


class Citation(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    threshold: Optional[float] = None


class SearchResponse(BaseModel):
    results: List[Citation]
    total: int


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    query: str
