from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from .base import IngestAgent
from .types import IngestContext
from app.models.chunk import DocumentChunk

try:
    from app.services.llm_client import get_llm_client
except ImportError:
    get_llm_client = None


class IndexAgent(IngestAgent):
    """
    IndexAgent - Kreira embeddings i indeksira chunk-ove u bazi.
    - Batch embeddings za performanse
    - Skip duplicates
    - ANALYZE hint za optimizaciju indeksa
    """
    
    def __init__(self, db: Session, batch_size: int = 50):
        super().__init__("IndexAgent", dependencies=[
            "ExtractAgent",
            "StructureAgent",
            "MetaAgent",
            "TableAgent",
            "DedupAgent",
            "PolicyAgent"
        ])
        self.db = db
        self.batch_size = batch_size
    
    async def process(self, context: IngestContext):
        """Indeksiraj chunk-ove sa embeddingima"""
        
        if not context.chunks:
            context.add_error("Nema chunk-ova za indeksiranje")
            return
        
        # Filter out duplicates - indeksiramo samo unique chunk-ove
        unique_chunks = [chunk for chunk in context.chunks if not chunk.is_duplicate]
        
        if not unique_chunks:
            context.add_error("Svi chunk-ovi su duplikati")
            return
        
        # Step 1: Generate embeddings in batches
        await self._generate_embeddings(unique_chunks, context)
        
        # Step 2: Insert into database
        await self._insert_chunks(unique_chunks, context)
        
        # Step 3: Optimize indexes with ANALYZE
        await self._analyze_indexes()
        
        # Metrics
        context.set_metric("indexed_chunks", len(unique_chunks))
        context.set_metric("duplicate_chunks_skipped", len(context.chunks) - len(unique_chunks))
    
    async def _generate_embeddings(self, chunks: List, context: IngestContext):
        """Generiši embeddings u batch-evima"""
        llm = get_llm_client()
        
        total_batches = (len(chunks) + self.batch_size - 1) // self.batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(chunks))
            batch = chunks[start_idx:end_idx]
            
            try:
                # Get texts from batch
                texts = [chunk.text for chunk in batch]
                
                # Batch embedding request
                embeddings = await llm.create_embeddings(texts)
                
                # Assign embeddings to chunks
                for chunk, embedding in zip(batch, embeddings):
                    chunk.embedding = embedding
                
                context.add_log(
                    "IndexAgent",
                    "info",
                    f"Batch {batch_idx + 1}/{total_batches}: {len(batch)} embeddings generisano"
                )
                
            except Exception as e:
                context.add_error(f"Embedding batch {batch_idx} greška: {str(e)}")
                # Continue with next batch
    
    async def _insert_chunks(self, chunks: List, context: IngestContext):
        """Upiši chunk-ove u bazu"""
        
        inserted_count = 0
        
        for chunk in chunks:
            if not chunk.embedding:
                continue
            
            try:
                # Create chunk record
                db_chunk = DocumentChunk(
                    document_id=int(context.document_id),
                    chunk_index=chunk.chunk_index,
                    text_content=chunk.text,
                    embedding=chunk.embedding,
                    metadata_={
                        "char_count": len(chunk.text),
                        **chunk.metadata
                    }
                )
                
                self.db.add(db_chunk)
                inserted_count += 1
                
            except Exception as e:
                context.add_error(f"Insert chunk {chunk.chunk_index} greška: {str(e)}")
        
        # Commit all chunks
        try:
            self.db.commit()
            context.add_log(
                "IndexAgent",
                "success",
                f"{inserted_count} chunk-ova upisano u bazu"
            )
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Database commit greška: {str(e)}")
    
    async def _analyze_indexes(self):
        """Pokreni ANALYZE za optimizaciju indeksa"""
        try:
            # ANALYZE document_chunks table for query planner
            self.db.execute(text("ANALYZE document_chunks"))
            self.db.commit()
        except Exception as e:
            # Not critical if ANALYZE fails
            pass
