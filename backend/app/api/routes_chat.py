from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, SearchRequest, SearchResponse, Citation, Verdict
from app.services.rag_pipeline import RAGPipeline
from app.services.search import SearchService

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        rag = RAGPipeline(db)
        result = await rag.generate_answer(
            query=request.query,
            top_k=request.top_k
        )
        
        citations = [Citation(**c) for c in result["citations"]]
        
        # Konvertuj verdict dict u Verdict model (ako postoji)
        verdict_data = result.get("verdict")
        verdict = Verdict(**verdict_data) if verdict_data else None
        
        return ChatResponse(
            answer=result["answer"],
            citations=citations,
            query=result["query"],
            verdict=verdict,
            summary=result.get("summary")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        search_service = SearchService(db)
        results = await search_service.hybrid_search(
            query=request.query,
            top_k=request.top_k
        )
        
        citations = []
        for chunk, score in results:
            citations.append(Citation(
                chunk_id=str(chunk.id),
                document_id=str(chunk.document_id),
                filename=chunk.document.filename,
                content=str(chunk.content),
                score=score,
                metadata=chunk.metadata or {}
            ))
        
        return SearchResponse(
            results=citations,
            total=len(citations)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
