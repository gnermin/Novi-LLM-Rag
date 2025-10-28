from typing import List
from openai import OpenAI
from app.agents.base import BaseAgent
from app.agents.types import ProcessingContext
from app.core.config import settings

# Model i batch parametri
EMBED_MODEL = "text-embedding-3-small"  # 1536 dimenzija, idealno za tvoju bazu
BATCH_SIZE = 64

class EmbeddingAgent(BaseAgent):
    def __init__(self):
        super().__init__("EmbeddingAgent")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def process(self, context: ProcessingContext) -> ProcessingContext:
        if not context.chunks:
            context.metadata["embeddings"] = []
            return context

        # Koristi obogaćene tekstove iz DensePrep agenta ako postoje
        texts = context.metadata.get("embed_texts") or context.chunks
        # Dodaj "instruct" prefiks radi stabilnijeg embeddinga
        texts = [f"search_document: {t}" for t in texts]

        embeddings: List[List[float]] = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i + BATCH_SIZE]
            try:
                resp = self.client.embeddings.create(
                    model=EMBED_MODEL,
                    input=batch
                )
                embeddings.extend([d.embedding for d in resp.data])
            except Exception as e:
                raise Exception(f"Embedding batch failed at {i}: {e}")

        if len(embeddings) != len(texts):
            raise Exception(f"Embedding count mismatch: {len(embeddings)} vs {len(texts)}")

        context.metadata["embeddings"] = embeddings
        context.metadata["embedding_count"] = len(embeddings)
        context.metadata["embedding_model"] = EMBED_MODEL
        return context
