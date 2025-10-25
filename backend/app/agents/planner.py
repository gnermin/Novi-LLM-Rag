from typing import Any, Dict


class PlannerAgent:
    """
    Planira strategiju pretrage i odgovaranja.
    Trenutno uvijek koristi RAG pretragu sa konfigurabilnim brojem rewrites-a.
    """
    name = "planner"
    
    def run(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kreira plan za query processing.
        
        Args:
            ctx: Kontekst sa 'rewrites_count' i ostalim parametrima
        
        Returns:
            Ažurirani kontekst sa 'plan' dict-om
        """
        # Minimalni plan: koristi RAG; broj rewrites je iz ctx-a ili 0
        rewrites = int(ctx.get("rewrites_count", 0))
        ctx["plan"] = {
            "use_rag": True,
            "use_sql": False,
            "use_web": False,
            "rewrites": rewrites,
        }
        return ctx
