from typing import List, Dict


def build_answer_prompt(user_query: str, chunks: List[Dict]) -> str:
    """
    Konstruiši prompt za generisanje odgovora baziranog na kontekstu.
    
    Args:
        user_query: Pitanje korisnika
        chunks: Lista chunk dict-ova sa 'content' poljem
    
    Returns:
        Formatirani prompt string
    """
    ctx_txt = "\n\n---\n".join(
        (c.get("content", "") or "")[:1200] for c in chunks
    )
    return (
        "Odgovori precizno na pitanje koristeći isključivo informacije iz KONTEKSTA. "
        "Ako nema dovoljno informacija, reci to eksplicitno i nemoj halucinirati.\n\n"
        f"PITANJE:\n{user_query}\n\nKONTEKST:\n{ctx_txt}\n\n"
        "Vrati jasan, sažet odgovor i ne uvodi nove činjenice van konteksta."
    )
