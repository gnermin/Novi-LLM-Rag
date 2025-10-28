from sqlalchemy.orm import Session
from app.agents.mime_detect import MimeDetectAgent
from app.agents.text_extract import TextExtractAgent
from app.agents.ocr import OCRAgent
from app.agents.chunking import ChunkingAgent
from app.agents.llm_dense_prep import LLMDensePrepAgent
from app.agents.embedding import EmbeddingAgent
from app.agents.indexing import IndexingAgent
from app.agents.types import ProcessingContext
from app.core.config import settings


class DocumentPipeline:
    """
    Klasični document processing pipeline sa provjerenim agentima.
    Pipeline flow:
    1. MimeDetectAgent - Detektuje tip fajla
    2. TextExtractAgent - Ekstraktuje tekst (PDF, DOCX, CSV, Excel)
    3. OCRAgent - OCR za slike i scanned PDF-ove
    4. ChunkingAgent - Deli tekst u chunk-ove (1000 chars, 200 overlap)
    5. LLMDensePrepAgent - Priprema chunk-ove za LLM dense retrieval (NOVO)
    6. EmbeddingAgent - Generiše OpenAI embeddings
    7. IndexingAgent - Upisuje chunk-ove u bazu sa embeddings
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Initialize agents
        self.mime_detect_agent = MimeDetectAgent()
        self.text_extract_agent = TextExtractAgent()
        self.ocr_agent = OCRAgent(enabled=settings.OCR_ENABLED)
        self.chunking_agent = ChunkingAgent(chunk_size=1000, chunk_overlap=200)
        self.llm_dense_prep_agent = LLMDensePrepAgent(enabled=True)  # NOVO
        self.embedding_agent = EmbeddingAgent()
        self.indexing_agent = IndexingAgent(db=self.db)
    
    async def process_document(
        self,
        document_id: str,
        file_path: str,
        filename: str,
        user_id: int
    ) -> ProcessingContext:
        """
        Procesira dokument kroz pipeline.
        Vraća ProcessingContext sa svim rezultatima i logovima.
        """
        
        # Create context
        context = ProcessingContext(
            document_id=document_id,
            file_path=file_path,
            filename=filename
        )
        
        # Execute pipeline (sequential)
        context = await self.mime_detect_agent.execute(context)
        context = await self.text_extract_agent.execute(context)
        context = await self.ocr_agent.execute(context)
        context = await self.chunking_agent.execute(context)
        context = await self.llm_dense_prep_agent.execute(context)   # NOVO
        context = await self.embedding_agent.execute(context)
        context = await self.indexing_agent.execute(context)
        
        return context
