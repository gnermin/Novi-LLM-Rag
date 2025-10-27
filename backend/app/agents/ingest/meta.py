import re
from datetime import datetime
from typing import List, Dict, Any
from .base import IngestAgent
from .types import IngestContext, ExtractedEntity
from app.core.config import settings

try:
    from app.services.llm_client import get_llm_client
except ImportError:
    get_llm_client = None


class MetaAgent(IngestAgent):
    """
    MetaAgent - Ekstraktuje metapodatke iz dokumenta.
    LLM mode: Koristi LLM za tip dokumenta, NER, ekstrakciju entiteta
    Fallback mode: Regex-based heuristike za datume, brojeve, email-ove
    """
    
    def __init__(self):
        super().__init__("MetaAgent", dependencies=["ExtractAgent", "StructureAgent"])
        self.llm_available = bool(settings.OPENAI_API_KEY)
    
    async def process(self, context: IngestContext):
        """Ekstraktuj metapodatke"""
        
        if not context.raw_text:
            context.add_error("Nema teksta za ekstrakciju metapodataka")
            return
        
        # Step 1: Detect document type
        if self.llm_available:
            await self._llm_detect_doc_type(context)
            await self._llm_extract_entities(context)
        else:
            await self._heuristic_detect_doc_type(context)
            await self._heuristic_extract_entities(context)
        
        # Step 2: Extract specific patterns (always run)
        await self._extract_patterns(context)
        
        # Metrics
        context.set_metric("entities_extracted", len(context.entities))
        context.set_metric("metadata_fields", len(context.extracted_metadata))
    
    async def _llm_detect_doc_type(self, context: IngestContext):
        """LLM-bazirana detekcija tipa dokumenta"""
        llm = get_llm_client()
        
        # Sample text for classification
        sample = context.raw_text[:2000]
        
        prompt = f"""Analiziraj sljedeći dokument i klasifikuj ga:

{sample}

Odgovori sa JSON:
{{
  "doc_type": "invoice|contract|report|email|memo|letter|policy|manual|other",
  "confidence": 0.0-1.0,
  "language": "bos|eng|other",
  "keywords": ["ključna", "riječ", "..."]
}}"""
        
        try:
            response = await llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300
            )
            
            import json
            content = response.choices[0].message.content
            
            # Clean response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            
            context.doc_type = data.get("doc_type", "other")
            context.extracted_metadata["doc_type_confidence"] = data.get("confidence", 0.0)
            context.extracted_metadata["language"] = data.get("language", "unknown")
            context.extracted_metadata["keywords"] = data.get("keywords", [])
            
        except Exception as e:
            context.add_error(f"LLM doc type greška: {str(e)}")
            await self._heuristic_detect_doc_type(context)
    
    async def _heuristic_detect_doc_type(self, context: IngestContext):
        """Heuristička detekcija tipa dokumenta"""
        text_lower = context.raw_text.lower()
        
        # Pattern matching
        if any(keyword in text_lower for keyword in ['faktura', 'invoice', 'račun', 'iznos', 'pdv']):
            context.doc_type = "invoice"
        elif any(keyword in text_lower for keyword in ['ugovor', 'contract', 'sporazum', 'stranka']):
            context.doc_type = "contract"
        elif any(keyword in text_lower for keyword in ['izvještaj', 'report', 'analiza', 'rezultati']):
            context.doc_type = "report"
        elif any(keyword in text_lower for keyword in ['from:', 'to:', 'subject:', 'email']):
            context.doc_type = "email"
        elif any(keyword in text_lower for keyword in ['memo', 'memorandum', 'obavijest']):
            context.doc_type = "memo"
        else:
            context.doc_type = "other"
        
        context.extracted_metadata["detection_method"] = "heuristic"
    
    async def _llm_extract_entities(self, context: IngestContext):
        """LLM-bazirana NER"""
        llm = get_llm_client()
        
        # Sample for NER
        sample = context.raw_text[:2500]
        
        prompt = f"""Ekstraktuj sve važne entitete iz teksta:

{sample}

Odgovori sa JSON:
{{
  "entities": [
    {{"text": "...", "type": "PERSON|ORG|DATE|MONEY|LOCATION|ID|OTHER", "context": "..."}}
  ]
}}

Fokusiraj se na: imena, kompanije, datume, novčane iznose, lokacije, šifre/brojeve dokumenata."""
        
        try:
            response = await llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            import json
            content = response.choices[0].message.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            
            for ent_data in data.get("entities", []):
                entity = ExtractedEntity(
                    text=ent_data.get("text", ""),
                    entity_type=ent_data.get("type", "OTHER"),
                    start=0,  # LLM doesn't provide exact position
                    end=0,
                    confidence=0.8
                )
                context.entities.append(entity)
                
        except Exception as e:
            context.add_error(f"LLM NER greška: {str(e)}")
    
    async def _heuristic_extract_entities(self, context: IngestContext):
        """Heuristička NER sa regex-ima"""
        text = context.raw_text
        
        # Dates
        date_patterns = [
            r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}',
            r'\d{4}[./-]\d{1,2}[./-]\d{1,2}'
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text):
                entity = ExtractedEntity(
                    text=match.group(0),
                    entity_type="DATE",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9
                )
                context.entities.append(entity)
        
        # Money amounts
        money_pattern = r'\d+[.,]?\d*\s*(EUR|USD|BAM|KM|RSD|€|\$)'
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            entity = ExtractedEntity(
                text=match.group(0),
                entity_type="MONEY",
                start=match.start(),
                end=match.end(),
                confidence=0.85
            )
            context.entities.append(entity)
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entity = ExtractedEntity(
                text=match.group(0),
                entity_type="EMAIL",
                start=match.start(),
                end=match.end(),
                confidence=0.95
            )
            context.entities.append(entity)
        
        # Phone numbers
        phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        for match in re.finditer(phone_pattern, text):
            if len(match.group(0).replace(' ', '').replace('-', '').replace('.', '')) >= 8:
                entity = ExtractedEntity(
                    text=match.group(0),
                    entity_type="PHONE",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.7
                )
                context.entities.append(entity)
    
    async def _extract_patterns(self, context: IngestContext):
        """Ekstraktuj specifične pattern-e"""
        text = context.raw_text
        
        # JMBG (Bosnia ID number - 13 digits)
        jmbg_pattern = r'\b\d{13}\b'
        jmbg_matches = re.findall(jmbg_pattern, text)
        if jmbg_matches:
            context.extracted_metadata["jmbg_numbers"] = list(set(jmbg_matches[:5]))
        
        # Document IDs (patterns like: DOC-12345, INV-2024-001, etc.)
        doc_id_pattern = r'\b[A-Z]{2,4}[-/]?\d{3,8}\b'
        doc_ids = re.findall(doc_id_pattern, text)
        if doc_ids:
            context.extracted_metadata["document_ids"] = list(set(doc_ids[:10]))
        
        # URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        if urls:
            context.extracted_metadata["urls"] = list(set(urls[:10]))
        
        # Extract all unique dates for summary
        dates = [ent.text for ent in context.entities if ent.entity_type == "DATE"]
        if dates:
            context.extracted_metadata["dates"] = list(set(dates[:10]))
        
        # Extract all money amounts
        amounts = [ent.text for ent in context.entities if ent.entity_type == "MONEY"]
        if amounts:
            context.extracted_metadata["money_amounts"] = list(set(amounts[:10]))
