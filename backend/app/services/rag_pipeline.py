from sqlalchemy.orm import Session
from typing import List, Dict, Any
from openai import OpenAI
from app.models.document import Document
from app.core.config import settings
from app.services.search import SearchService, rrf_merge
from app.agents.planner import PlannerAgent
from app.agents.rewriter import RewriterAgent
from app.agents.generation import GenerationAgent
from app.agents.judge import JudgeAgent
from app.agents.summarizer import SummarizerAgent

# Inicijalizacija agenata
planner = PlannerAgent()
rewriter = RewriterAgent()
generator = GenerationAgent()
judge = JudgeAgent()
summarizer = SummarizerAgent()


class RAGPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.search_service = SearchService(db)
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_answer(
        self,
        query: str,
        top_k: int | None = None
    ) -> Dict[str, Any]:
        """
        Multi-agent RAG pipeline za generisanje odgovora.
        Backward compatible sa starim API-jem.
        
        Args:
            query: Korisnikov upit
            top_k: Broj rezultata za pretragu (default: settings.RAG_TOP_K)
        
        Returns:
            Dict sa answer, citations (sources), verdict, i summary
        """
        if not self.client:
            raise Exception("OpenAI API key not configured")
        
        top_k = top_k or settings.RAG_TOP_K
        
        # Inicijalizuj kontekst za agente
        ctx: Dict[str, Any] = {
            "query": query,
            "rewrites_count": settings.AGENT_REWRITES
        }

        # 1) PLAN - Planner odlučuje strategiju
        ctx = planner.run(ctx)

        # 2) REWRITES - Generiši dodatne query varijante
        ctx = rewriter.run(ctx)

        # 3) RETRIEVAL - Federated search sa RRF
        queries = [ctx["query"]] + ctx.get("rewrites", [])
        result_sets: List[List[Dict[str, Any]]] = []
        
        for q in queries:
            q_vec = await self._get_embedding(q)
            hits = await self._search_and_convert(q_vec, top_k)
            result_sets.append(hits)

        # RRF merge svih rezultata
        merged = rrf_merge(result_sets)
        ctx["retrieval"] = {"hits": merged[:top_k], "top_k": top_k}

        # 4) GENERATE - Generiši odgovor
        ctx = generator.run(ctx)

        # 5) JUDGE - Evaluacija kvaliteta + eventualna iteracija
        ctx = judge.run(ctx)

        # Opciona iteracija ako judge kaže da treba više konteksta
        iteration = 0
        while ctx.get("verdict", {}).get("needs_more") and iteration < 2:
            iteration += 1
            more_k = min(ctx["retrieval"]["top_k"] + 5, 20)
            extra_sets = []
            for q in queries:
                q_vec = await self._get_embedding(q)
                hits = await self._search_and_convert(q_vec, more_k)
                extra_sets.append(hits)
            
            merged = rrf_merge(result_sets + extra_sets)
            ctx["retrieval"] = {"hits": merged[:more_k], "top_k": more_k}
            ctx = generator.run(ctx)
            ctx = judge.run(ctx)

        # 6) SUMMARIZE - Opcioni sažetak (možeš aktivirati po potrebi)
        # ctx = summarizer.run(ctx)

        # Konvertuj hits u citations format (backward compatibility)
        citations = self._convert_hits_to_citations(ctx["retrieval"]["hits"])

        return {
            "answer": ctx.get("answer", ""),
            "citations": citations,  # Backward compatible
            "sources": citations,    # Novi alias
            "query": query,
            "verdict": ctx.get("verdict", {"ok": True, "needs_more": False}),
            # "summary": ctx.get("summary")  # Odkomentiraj ako koristiš summarizer
        }
    
    async def _search_and_convert(self, embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """
        Izvuči rezultate pretrage i konvertuj u dict format za RRF.
        """
        search_results = await self.search_service.hybrid_search(
            query="",
            query_embedding=embedding,
            top_k=top_k
        )
        
        hits = []
        for chunk, score in search_results:
            # Konvertuj metadata u dict ako je potrebno
            meta = chunk.chunk_metadata
            if meta is None:
                meta = {}
            elif not isinstance(meta, dict):
                meta = dict(meta) if hasattr(meta, '__iter__') else {}
            
            hits.append({
                "id": str(chunk.id),
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "filename": chunk.document.filename if chunk.document else "Unknown",
                "content": chunk.content,
                "score": float(score),
                "metadata": meta
            })
        return hits
    
    def _convert_hits_to_citations(self, hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Konvertuj hits u citations format (backward compatibility).
        """
        return [
            {
                "chunk_id": hit.get("chunk_id"),
                "document_id": hit.get("document_id"),
                "filename": hit.get("filename"),
                "content": hit.get("content"),
                "score": hit.get("score"),
                "metadata": hit.get("metadata", {})
            }
            for hit in hits
        ]
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Generiši embedding vektor za tekst sa fallback-om."""
        if not self.client:
            # Fallback: Jednostavan deterministički vektor za dev bez API ključa
            # U produkciji OPENAI_API_KEY mora biti setovan
            import hashlib
            hash_digest = hashlib.sha256(text.encode()).digest()
            # Generiši 1536-dimenzionalni vektor iz hash-a (repeating pattern)
            base = [float(b) / 255.0 - 0.5 for b in hash_digest]  # 32 floata
            return (base * 48)[:1536]  # Repeat do 1536 dim
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model=settings.EMBEDDINGS_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to get embedding: {str(e)}")
