import re

class PreEmbedCleanerAgent:
    """Heurističko čišćenje teksta prije chunkanja (bez LLM poziva)."""

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        t = text
        t = re.sub(r'\s+', ' ', t)                         # višak whitespace
        t = re.sub(r'(\.\s*\.){1,}', '.', t)               # ... → .
        t = t.replace("•", "-").replace("", "-")          # bullet normalizacija
        t = re.sub(r'(?<=\d)\s+(?=\d)', '', t)             # 1 000 → 1000 (ako ti ne treba razmak)
        t = t.strip()
        return t
