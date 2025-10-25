from typing import Any, Dict
from app.core.config import settings
from app.services.prompting import build_answer_prompt
from app.services.llm_client import llm_complete


class GenerationAgent:
    """
    Generiše finalni odgovor baziran na retrieved kontekstu.
    """
    name = "generation"
    
    def run(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generiše odgovor koristeći retrieved chunks i LLM.
        
        Args:
            ctx: Kontekst sa 'query' i 'retrieval' dict-om
        
        Returns:
            Ažurirani kontekst sa 'answer' stringom
        """
        chunks = ctx.get("retrieval", {}).get("hits", [])
        prompt = build_answer_prompt(user_query=ctx["query"], chunks=chunks)
        out = llm_complete(prompt, model=settings.CHAT_MODEL, n=1)[0]
        ctx["answer"] = (out or "").strip()
        return ctx
