from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class AgentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    CSV = "csv"
    IMAGE = "image"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class AgentResult:
    agent_name: str
    status: AgentStatus
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "status": self.status.value,
            "message": self.message,
            "metadata": self.metadata,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ProcessingContext:
    document_id: str
    file_path: str
    filename: str
    mime_type: Optional[str] = None
    document_type: DocumentType = DocumentType.UNKNOWN
    
    text_content: str = ""
    chunks: List[str] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    agent_results: List[AgentResult] = field(default_factory=list)
    
    def add_result(self, result: AgentResult):
        self.agent_results.append(result)
    
    def get_latest_result(self) -> Optional[AgentResult]:
        return self.agent_results[-1] if self.agent_results else None
