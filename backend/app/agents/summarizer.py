from typing import Any, Dict
from app.services.llm_client import llm_complete


class SummarizerAgent:
    """
    Kreira sažetak generisanog odgovora.
    """
    name = "summarizer"
    
    def run(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generiše kratak sažetak odgovora.
        
        Args:
            ctx: Kontekst sa 'answer' stringom
        
        Returns:
            Ažurirani kontekst sa 'summary' stringom
        """
        ans = ctx.get("answer", "")
        if not ans:
            ctx["summary"] = ""
            return ctx
            
        prompt = f"Sažmi sljedeći odgovor u dvije rečenice, jasno i precizno:\n\n{ans}"
        ctx["summary"] = llm_complete(prompt, n=1)[0]
        return ctx
