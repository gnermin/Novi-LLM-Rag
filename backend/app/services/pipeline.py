from typing import List
from sqlalchemy.orm import Session
from app.agents.base import BaseAgent
from app.agents.types import ProcessingContext
from app.agents.mime_detect import MimeDetectAgent
from app.agents.text_extract import TextExtractAgent
from app.agents.ocr import OCRAgent
from app.agents.chunking import ChunkingAgent
from app.agents.embedding import EmbeddingAgent
from app.agents.indexing import IndexingAgent
from app.core.config import settings


class DocumentPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.agents: List[BaseAgent] = [
            MimeDetectAgent(),
            TextExtractAgent(),
            OCRAgent(enabled=settings.OCR_ENABLED),
            ChunkingAgent(chunk_size=1000, chunk_overlap=200),
            EmbeddingAgent(),
            IndexingAgent(db=db)
        ]
    
    async def process_document(self, context: ProcessingContext) -> ProcessingContext:
        for agent in self.agents:
            try:
                context = await agent.execute(context)
            except Exception as e:
                print(f"Error in {agent.name}: {str(e)}")
                raise
        
        return context
