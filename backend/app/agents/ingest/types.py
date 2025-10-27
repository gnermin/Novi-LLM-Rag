from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TextBlock:
    """Blok teksta sa pozicijom i metapodacima"""
    text: str
    page: Optional[int] = None
    position: Optional[Dict[str, float]] = None  # {x, y, width, height}
    block_type: str = "paragraph"  # paragraph, heading, list, table, etc.
    confidence: float = 1.0


@dataclass
class DocumentSegment:
    """Strukturirani segment dokumenta"""
    text: str
    segment_type: str  # heading, section, paragraph, list, table
    level: int = 0  # hierarchy level (0=root, 1=h1, 2=h2, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedEntity:
    """NER ekstraktovana entiteta"""
    text: str
    entity_type: str  # DATE, PERSON, ORG, MONEY, CARDINAL, etc.
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class TableData:
    """Parsirana tabela"""
    headers: List[str]
    rows: List[List[str]]
    page: Optional[int] = None
    format: str = "csv"  # csv, json
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedChunk:
    """Procesovani chunk sa embeddingom"""
    text: str
    chunk_index: int
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_duplicate: bool = False
    deduplicated_with: Optional[str] = None  # hashOriginating chunk-a


@dataclass
class IngestContext:
    """Kontekst za cio ingest pipeline"""
    document_id: str
    file_path: str
    filename: str
    user_id: int
    
    # Extracted data
    raw_text: str = ""
    blocks: List[TextBlock] = field(default_factory=list)
    
    # Structured data
    segments: List[DocumentSegment] = field(default_factory=list)
    
    # Metadata
    doc_type: Optional[str] = None  # invoice, contract, report, email, etc.
    entities: List[ExtractedEntity] = field(default_factory=list)
    extracted_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Tables
    tables: List[TableData] = field(default_factory=list)
    
    # Chunks (after dedup and policy)
    chunks: List[ProcessedChunk] = field(default_factory=list)
    
    # Agent execution logs
    agent_logs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Errors
    errors: List[str] = field(default_factory=list)
    
    # Performance metrics
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def add_log(self, agent_name: str, status: str, message: str, **kwargs):
        """Dodaj log unos za agenta"""
        log_entry = {
            "agent": agent_name,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        self.agent_logs.append(log_entry)
    
    def add_error(self, error: str):
        """Dodaj error"""
        self.errors.append(error)
        
    def set_metric(self, key: str, value: Any):
        """Postavi performance metriku"""
        self.metrics[key] = value


@dataclass
class AgentResult:
    """Rezultat izvršavanja agenta"""
    agent_name: str
    status: str  # success, failed, skipped
    message: str
    duration_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "status": self.status,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata
        }
