from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Tuple
from app.models.chunk import DocumentChunk
from app.models.document import Document
import uuid


class SearchService:
    def __init__(self, db: Session):
        self.db = db
    
    async def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        query_embedding: List[float] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        results = []
        
        if query_embedding:
            results = self._vector_search(query_embedding, top_k)
        else:
            results = self._text_search(query, top_k)
        
        return results
    
    def _vector_search(self, embedding: List[float], top_k: int) -> List[Tuple[DocumentChunk, float]]:
        embedding_str = f"[{','.join(map(str, embedding))}]"
        
        query = text("""
            SELECT dc.*, 
                   1 - (dc.embedding <=> :embedding::vector) as similarity
            FROM document_chunks dc
            WHERE dc.embedding IS NOT NULL
            ORDER BY dc.embedding <=> :embedding::vector
            LIMIT :limit
        """)
        
        result = self.db.execute(
            query,
            {"embedding": embedding_str, "limit": top_k}
        )
        
        chunks_with_scores = []
        for row in result:
            chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == row.id).first()
            if chunk:
                chunks_with_scores.append((chunk, float(row.similarity)))
        
        return chunks_with_scores
    
    def _text_search(self, query: str, top_k: int) -> List[Tuple[DocumentChunk, float]]:
        search_query = text("""
            SELECT dc.*, 
                   ts_rank(to_tsvector('simple', dc.content), plainto_tsquery('simple', :query)) as rank
            FROM document_chunks dc
            WHERE to_tsvector('simple', dc.content) @@ plainto_tsquery('simple', :query)
            ORDER BY rank DESC
            LIMIT :limit
        """)
        
        result = self.db.execute(
            search_query,
            {"query": query, "limit": top_k}
        )
        
        chunks_with_scores = []
        for row in result:
            chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == row.id).first()
            if chunk:
                chunks_with_scores.append((chunk, float(row.rank) if row.rank else 0.0))
        
        return chunks_with_scores
