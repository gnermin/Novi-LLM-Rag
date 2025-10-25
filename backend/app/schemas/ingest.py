from pydantic import BaseModel
from typing import Optional
import uuid


class SQLIngestRequest(BaseModel):
    source_name: str
    query: str
    connection_string: Optional[str] = None


class SQLIngestResponse(BaseModel):
    document_id: uuid.UUID
    job_id: uuid.UUID
    status: str
    message: str
