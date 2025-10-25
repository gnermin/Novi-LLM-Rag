from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class DocumentCreate(BaseModel):
    filename: str
    file_path: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class AgentLog(BaseModel):
    agent: str
    status: str
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    agent_logs: Optional[List[AgentLog]] = []

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
