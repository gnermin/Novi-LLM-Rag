from typing import List
from openai import OpenAI
from app.agents.base import BaseAgent
from app.agents.types import ProcessingContext
from app.core.config import settings


class EmbeddingAgent(BaseAgent):
    def __init__(self):
        super().__init__("EmbeddingAgent")
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        if not self.client:
            raise Exception("OpenAI API key not configured")
        
        if not context.chunks:
            context.metadata['embeddings'] = []
            return context
        
        embeddings = []
        
        for chunk in context.chunks:
            try:
                response = self.client.embeddings.create(
                    input=chunk,
                    model="text-embedding-ada-002"
                )
                embedding = response.data[0].embedding
                embeddings.append(embedding)
            except Exception as e:
                raise Exception(f"Embedding generation failed: {str(e)}")
        
        context.metadata['embeddings'] = embeddings
        context.metadata['embedding_count'] = len(embeddings)
        context.metadata['embedding_model'] = "text-embedding-ada-002"
        
        return context
