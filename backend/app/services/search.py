from sqlalchemy.orm import Session
from sqlalchemy import text, func, select, desc
from typing import List, Tuple, Dict, Any
from app.models.chunk import DocumentChunk
from app.models.document import Document
from pgvector.sqlalchemy import Vector
import uuid


def rrf_merge(result_sets: List[List[Dict]], k: int = 60) -> List[Dict]:
    """
    Reciprocal Rank Fusion - spaja više result setova u jedan rangiran rezultat.
    
    Args:
        result_sets: Lista listi hitova; svaki hit treba da ima unique "chunk_id" ili "id"
        k: RRF parametar (default 60)
    
    Returns:
        Ujedinjena lista dict-ova sortirana po RRF score-u
    """
    scores: dict[str, float] = {}
    keep: dict[str, Dict] = {}
    
    for results in result_sets:
        for rank, item in enumerate(results, start=1):
            cid = item.get("chunk_id") or item.get("id")
            if not cid:
                continue
            keep[cid] = item
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    
    # Sort po zbirnim score
    merged_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return [keep[cid] for cid in merged_ids]


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
        from pgvector.sqlalchemy import Vector
        
        embedding_str = str(embedding)
        
        query_sql = text("""
            SELECT dc.id, dc.document_id, dc.content, dc.chunk_index, dc.metadata, dc.created_at,
                   1 - (dc.embedding <=> CAST(:embedding AS vector)) as similarity
            FROM document_chunks dc
            WHERE dc.embedding IS NOT NULL
            ORDER BY dc.embedding <=> CAST(:embedding AS vector)
            LIMIT :top_k
        """)
        
        result = self.db.execute(query_sql, {"embedding": embedding_str, "top_k": top_k})
        
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
