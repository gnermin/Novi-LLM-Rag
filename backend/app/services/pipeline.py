from sqlalchemy.orm import Session
from app.agents.ingest import (
    IngestDAG,
    ExtractAgent,
    StructureAgent,
    MetaAgent,
    TableAgent,
    DedupAgent,
    PolicyAgent,
    IndexAgent
)
from app.agents.ingest.types import IngestContext
from app.core.config import settings


class DocumentPipeline:
    """
    Refaktorizovan DocumentPipeline sa DAG arhitekturom.
    Koristi 7 specijalizovanih mini-agenata:
    1. ExtractAgent - PDF/Docx/OCR extraction
    2. StructureAgent - Segmentacija i chunking
    3. MetaAgent - Metadata i NER
    4. TableAgent - Table parsing
    5. DedupAgent - MinHash/LSH deduplication
    6. PolicyAgent - PII masking
    7. IndexAgent - Embeddings i indexing
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.dag = IngestDAG()
        
        # Initialize all agents
        self._setup_dag()
    
    def _setup_dag(self):
        """Postavi DAG sa svim agentima i dependency order-om"""
        
        # Agent 1: Extract (no dependencies)
        extract_agent = ExtractAgent(ocr_enabled=settings.OCR_ENABLED)
        self.dag.add_agent(extract_agent)
        
        # Agent 2: Structure (depends on Extract)
        structure_agent = StructureAgent(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.dag.add_agent(structure_agent)
        
        # Agent 3: Meta (depends on Extract, Structure)
        meta_agent = MetaAgent()
        self.dag.add_agent(meta_agent)
        
        # Agent 4: Table (depends on Extract)
        table_agent = TableAgent(use_llm=bool(settings.OPENAI_API_KEY))
        self.dag.add_agent(table_agent)
        
        # Agent 5: Dedup (depends on Structure)
        dedup_agent = DedupAgent(
            similarity_threshold=0.85,
            shingle_size=3
        )
        self.dag.add_agent(dedup_agent)
        
        # Agent 6: Policy (depends on Dedup)
        policy_agent = PolicyAgent(
            mask_emails=True,
            mask_phones=True,
            mask_ids=True,
            mask_cards=True
        )
        self.dag.add_agent(policy_agent)
        
        # Agent 7: Index (depends on all previous)
        index_agent = IndexAgent(db=self.db, batch_size=50)
        self.dag.add_agent(index_agent)
    
    async def process_document(
        self,
        document_id: str,
        file_path: str,
        filename: str,
        user_id: int
    ) -> IngestContext:
        """
        Procesira dokument kroz DAG pipeline.
        Vraća IngestContext sa svim rezultatima i logovima.
        """
        
        # Create context
        context = IngestContext(
            document_id=document_id,
            file_path=file_path,
            filename=filename,
            user_id=user_id
        )
        
        # Execute DAG
        context = await self.dag.execute(context)
        
        return context
