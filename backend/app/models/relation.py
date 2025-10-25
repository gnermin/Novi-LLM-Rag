from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.app.core.db import Base


class DocumentRelation(Base):
    __tablename__ = "document_relations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    source_ref = Column(String(255), nullable=True)
    target_ref = Column(String(255), nullable=True)
    relation_type = Column(String(100), nullable=True)
    score = Column(Float, nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="relations")
