from sqlalchemy.orm import Session
from app.agents.base import BaseAgent
from app.agents.types import ProcessingContext
from app.models.chunk import DocumentChunk
import uuid


class IndexingAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__("IndexingAgent")
        self.db = db
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        if not context.chunks:
            return context
        
        embeddings = context.metadata.get('embeddings', [])
        
        if len(embeddings) != len(context.chunks):
            raise Exception("Mismatch between chunks and embeddings count")
        
        indexed_count = 0
        
        for idx, (chunk_text, embedding) in enumerate(zip(context.chunks, embeddings)):
            chunk = DocumentChunk(
                document_id=uuid.UUID(context.document_id),
                chunk_index=idx,
                content=chunk_text,
                embedding=embedding,
                chunk_metadata={}
            )
            self.db.add(chunk)
            indexed_count += 1
        
        self.db.commit()
        
        context.metadata['indexed_chunks'] = indexed_count
        
        return context
