import json
from typing import List, Dict
from app.services.llm_client import llm_complete

TAG_PROMPT = """Analiziraj tekst i vrati JSON sa poljima:
{{
  "summary": "sažetak u 2-3 rečenice",
  "keywords": ["ključne", "riječi", "bez interpunkcije"],
  "topic_label": "kratak naziv teme"
}}
Vrati ISKLJUČIVO JSON.

TEKST:
\"\"\"{text}\"\"\""""

class TaggingAgent:
    """LLM agent: dodaje summary/keywords/topic_label u metapodatke chunkova."""

    def __init__(self, per_batch: int = 1):
        # ostavljamo per_chunk za najjednostavniju implementaciju; batchanje može kasnije
        self.per_batch = per_batch

    async def process(self, chunks: List[Dict]) -> List[Dict]:
        enriched: List[Dict] = []
        for ch in chunks:
            txt = ch.get("content", "")
            meta = {"summary": ch.get("summary", ""), "keywords": [], "topic_label": ""}
            if txt:
                out = llm_complete(TAG_PROMPT.format(text=txt[:1200]), n=1)[0]
                try:
                    j = json.loads(out)
                    if isinstance(j, dict):
                        meta["summary"] = (j.get("summary") or meta["summary"] or "").strip()
                        kw = j.get("keywords") or []
                        if isinstance(kw, list):
                            meta["keywords"] = [str(k).strip().strip(",.;") for k in kw if str(k).strip()]
                        meta["topic_label"] = (j.get("topic_label") or "").strip()
                except Exception:
                    pass
            enriched.append({**ch, **meta})
        return enriched
