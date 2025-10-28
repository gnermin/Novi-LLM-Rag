from app.agents.base import BaseAgent
from app.agents.types import ProcessingContext
from app.services.llm_client import llm_complete
from app.core.config import settings

PROMPT_TMPL = """Pretvori sljedeći odlomak u 'embedding-ready' tekst za semantičku pretragu.
- U jednoj rečenici sažmi suštinu (maks. 25 riječi).
- Dodaj 3–6 ključnih pojmova (bez znakova).
- Vrati 1–3 kratka reda koji nose glavni smisao teksta, bez uvoda i zaključka.
- Ne dodaj oznake ili meta-tekst; vrati samo čisti tekst.

Tekst:
\"\"\"{chunk}\"\"\""""

class LLMDensePrepAgent(BaseAgent):
    def __init__(self, enabled: bool = True):
        super().__init__("LLMDensePrepAgent")
        self.enabled = enabled and bool(settings.OPENAI_API_KEY)

    async def process(self, context: ProcessingContext) -> ProcessingContext:
        if not self.enabled or not context.chunks:
            return context

        embed_texts = []
        for ch in context.chunks:
            try:
                out = llm_complete(PROMPT_TMPL.format(chunk=ch), n=1)[0]
                cleaned = (out or "").strip()
                if not cleaned:
                    cleaned = ch
                embed_texts.append(cleaned)
            except Exception:
                embed_texts.append(ch)  # fallback ako LLM padne

        context.metadata["embed_texts"] = embed_texts
        return context
