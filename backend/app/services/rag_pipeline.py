from sqlalchemy.orm import Session
from typing import List, Dict, Any
from openai import OpenAI
from app.services.search import SearchService
from app.models.document import Document
from app.core.config import settings


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
        top_k: int = 5
    ) -> Dict[str, Any]:
        if not self.client:
            raise Exception("OpenAI API key not configured")
        
        query_embedding = await self._get_embedding(query)
        
        search_results = await self.search_service.hybrid_search(
            query=query,
            query_embedding=query_embedding,
            top_k=top_k
        )
        
        if not search_results:
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "citations": [],
                "query": query
            }
        
        context_parts = []
        citations = []
        
        for chunk, score in search_results:
            context_parts.append(f"[Source: {chunk.document.filename}]\n{chunk.content}")
            
            citations.append({
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "filename": chunk.document.filename,
                "content": chunk.content,
                "score": score,
                "metadata": chunk.chunk_metadata
            })
        
        context = "\n\n---\n\n".join(context_parts)
        
        prompt = f"""Based on the following context, answer the user's question. 
If the context doesn't contain relevant information, say so clearly.

Context:
{context}

Question: {query}

Answer:"""
        
        system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
IMPORTANT: Always respond in the SAME LANGUAGE as the user's question. 
If the question is in Bosnian/Serbian/Croatian, answer in Bosnian. If in English, answer in English.
Always cite your sources and be accurate."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Failed to generate answer: {str(e)}")
        
        return {
            "answer": answer,
            "citations": citations,
            "query": query
        }
    
    async def _get_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to get embedding: {str(e)}")
