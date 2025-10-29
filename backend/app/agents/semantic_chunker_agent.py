import json
from typing import List, Dict

# Pretpostavka: imaš helper u app.services.llm_client: llm_complete(prompt, n=1) -> list[str]
from app.services.llm_client import llm_complete

CHUNK_PROMPT = """Podijeli donji tekst na tematske cjeline.
Za svaku cjelinu vrati JSON objekt sa poljima:
- "title": kratak naslov (<= 8 riječi)
- "content": glavni tekst te cjeline
- "summary": 1-2 rečenice sažetka

Vrati isključivo JSON listu ovih objekata, bez dodatnog teksta.

TEKST:
\"\"\"{text}\"\"\""""

class SemanticChunkerAgent:
    """LLM agent: semantičko chunkanje u blokove {title, content, summary}."""

    def __init__(self, max_chars: int = 8000):
        self.max_chars = max_chars

    async def process(self, clean_text: str) -> List[Dict]:
        if not clean_text:
            return []
        prompt = CHUNK_PROMPT.format(text=clean_text[: self.max_chars])
        out = llm_complete(prompt, n=1)[0]
        try:
            data = json.loads(out)
            if isinstance(data, list):
                # normalizacija zapisa
                chunks: List[Dict] = []
                for it in data:
                    chunks.append({
                        "title": (it.get("title") or "").strip(),
                        "content": (it.get("content") or "").strip(),
                        "summary": (it.get("summary") or "").strip(),
                    })
                return [c for c in chunks if c["content"]]
        except Exception:
            pass
        # fallback: jedan blok ako LLM vrati nešto neočekivano
        return [{"title": "", "content": clean_text[: self.max_chars].strip(), "summary": ""}]
