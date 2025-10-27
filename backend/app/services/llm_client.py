from typing import List, Optional
from app.core.config import settings

try:
    from openai import OpenAI
    _client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
except Exception:
    _client = None


def get_llm_client():
    """Vrati OpenAI client ili None ako nije dostupan"""
    return _client


def llm_complete(prompt: str, model: Optional[str] = None, n: int = 1) -> List[str]:
    """
    Vrati listu n završetaka. Ako OpenAI nije dostupan, vrati stub odgovore.
    
    Args:
        prompt: Prompt za LLM
        model: Model name (default: settings.CHAT_MODEL)
        n: Broj completion-a koji treba generisati
    
    Returns:
        Lista stringova sa odgovorima
    """
    model = model or settings.CHAT_MODEL
    if _client is None or not settings.OPENAI_API_KEY:
        # Fallback za razvoj
        return [f"[STUB:{model}] {prompt[:200]} ..."] * n

    resp = _client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        n=n,
        temperature=0.2,
    )
    outs = []
    for choice in resp.choices:
        outs.append(choice.message.content or "")
    return outs
