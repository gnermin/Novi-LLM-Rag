from typing import List
from app.agents.base import BaseAgent
from app.agents.types import ProcessingContext


class ChunkingAgent(BaseAgent):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        super().__init__("ChunkingAgent")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        if not context.text_content:
            context.chunks = []
            return context
        
        text = context.text_content
        chunks = []
        
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start += self.chunk_size - self.chunk_overlap
        
        context.chunks = chunks
        context.metadata['chunk_count'] = len(chunks)
        context.metadata['chunk_size'] = self.chunk_size
        context.metadata['chunk_overlap'] = self.chunk_overlap
        
        return context
