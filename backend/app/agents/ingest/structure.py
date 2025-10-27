from typing import List
import re
from .base import IngestAgent
from .types import IngestContext, DocumentSegment, ProcessedChunk
from app.core.config import settings

try:
    from app.services.llm_client import get_llm_client
except ImportError:
    get_llm_client = None


class StructureAgent(IngestAgent):
    """
    StructureAgent - Strukturira dokument u segmente i pravi pametne chunk-ove.
    LLM mode: Koristi LLM za detekciju strukture, naslova, sekcija
    Fallback mode: Heuristička segmentacija na osnovu formatiranja
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        super().__init__("StructureAgent", dependencies=["ExtractAgent"])
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.llm_available = bool(settings.OPENAI_API_KEY)
    
    async def process(self, context: IngestContext):
        """Strukturiraj dokument i kreiraj chunk-ove"""
        
        if not context.blocks:
            context.add_error("Nema ekstraktovanih blokova za strukturiranje")
            return
        
        # Step 1: Segmentacija
        if self.llm_available:
            await self._llm_segmentation(context)
        else:
            await self._heuristic_segmentation(context)
        
        # Step 2: Pametni chunking
        await self._create_chunks(context)
        
        # Metrics
        context.set_metric("segments", len(context.segments))
        context.set_metric("chunks_created", len(context.chunks))
    
    async def _llm_segmentation(self, context: IngestContext):
        """LLM-bazirana segmentacija sa strukturom"""
        llm = get_llm_client()
        
        # Combine first few blocks for structure detection
        sample_text = "\n\n".join([block.text for block in context.blocks[:10]])[:3000]
        
        prompt = f"""Analiziraj sljedeći tekst dokumenta i identifikuj strukturu:

{sample_text}

Odgovori sa JSON:
{{
  "segments": [
    {{"type": "heading|section|paragraph", "level": 0-3, "text": "...", "summary": "..."}}
  ]
}}

Pravila:
- Detektuj naslove (heading) i njihov nivo hijerarhije (1=glavni, 2=podnaslov, 3=sekcija)
- Grupiši paragrafe u sekcije
- Sažmi svaki segment u 1-2 rečenice"""
        
        try:
            response = await llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse LLM response (basic JSON extraction)
            import json
            content = response.choices[0].message.content
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            
            # Create segments from LLM response
            for seg_data in data.get("segments", []):
                segment = DocumentSegment(
                    text=seg_data.get("text", ""),
                    segment_type=seg_data.get("type", "paragraph"),
                    level=seg_data.get("level", 0),
                    metadata={"summary": seg_data.get("summary", ""), "source": "llm"}
                )
                context.segments.append(segment)
                
        except Exception as e:
            context.add_error(f"LLM segmentacija greška: {str(e)}, prebacujem na heuristike")
            await self._heuristic_segmentation(context)
    
    async def _heuristic_segmentation(self, context: IngestContext):
        """Heuristička segmentacija bez LLM-a"""
        
        for block in context.blocks:
            # Detect heading based on block type or text patterns
            level = 0
            segment_type = "paragraph"
            
            if block.block_type == "heading":
                segment_type = "heading"
                level = 1
            elif self._is_heading(block.text):
                segment_type = "heading"
                level = self._detect_heading_level(block.text)
            elif block.block_type == "table":
                segment_type = "table"
            elif len(block.text) < 50 and block.text.isupper():
                # Short all-caps text is likely a heading
                segment_type = "heading"
                level = 2
            
            segment = DocumentSegment(
                text=block.text,
                segment_type=segment_type,
                level=level,
                metadata={"source": "heuristic", "block_type": block.block_type}
            )
            context.segments.append(segment)
    
    def _is_heading(self, text: str) -> bool:
        """Heuristika da li je tekst naslov"""
        # Short text (< 100 chars)
        if len(text) > 100:
            return False
        
        # Ends without period
        if text.strip().endswith('.'):
            return False
        
        # Starts with number or bullet
        if re.match(r'^(\d+\.|\d+\)|\*|\-|\•)', text.strip()):
            return True
        
        # Title case
        if text.strip().istitle():
            return True
        
        return False
    
    def _detect_heading_level(self, text: str) -> int:
        """Detektuj nivo naslova"""
        # Check for numeric prefix (1., 1.1., 1.1.1.)
        match = re.match(r'^(\d+)(\.\d+)*', text.strip())
        if match:
            dots = match.group(0).count('.')
            return min(dots + 1, 3)
        
        # Default
        return 1
    
    async def _create_chunks(self, context: IngestContext):
        """Kreiraj chunk-ove sa pametnim granama"""
        
        # Combine segments into full text
        full_text = "\n\n".join([seg.text for seg in context.segments])
        
        if not full_text.strip():
            context.add_error("Nema teksta za chunking")
            return
        
        # Smart chunking - poštuje granice rečenica
        sentences = self._split_into_sentences(full_text)
        
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            # Check if adding this sentence exceeds chunk_size
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # Save current chunk
                chunk = ProcessedChunk(
                    text=current_chunk.strip(),
                    chunk_index=chunk_index,
                    metadata={"char_count": len(current_chunk), "source": "structure"}
                )
                context.chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = overlap_text + " " + sentence
                chunk_index += 1
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add last chunk
        if current_chunk.strip():
            chunk = ProcessedChunk(
                text=current_chunk.strip(),
                chunk_index=chunk_index,
                metadata={"char_count": len(current_chunk), "source": "structure"}
            )
            context.chunks.append(chunk)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split tekst u rečenice"""
        # Simple sentence splitting (can be improved with NLTK)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap(self, text: str) -> str:
        """Uzmi overlap sa kraja chunk-a"""
        if len(text) <= self.chunk_overlap:
            return text
        
        # Take last chunk_overlap chars, but try to start at sentence boundary
        overlap_text = text[-self.chunk_overlap:]
        
        # Find first sentence boundary
        match = re.search(r'[.!?]\s+', overlap_text)
        if match:
            return overlap_text[match.end():]
        
        return overlap_text
