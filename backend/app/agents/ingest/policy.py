import re
from typing import List, Dict, Tuple
from .base import IngestAgent
from .types import IngestContext


class PolicyAgent(IngestAgent):
    """
    PolicyAgent - Primjenjuje sigurnosne politike i maskira PII.
    Detektuje i maskira: email, telefon, JMBG, kartice, pasosi, etc.
    """
    
    def __init__(
        self,
        mask_emails: bool = True,
        mask_phones: bool = True,
        mask_ids: bool = True,
        mask_cards: bool = True
    ):
        super().__init__("PolicyAgent", dependencies=["DedupAgent"])
        self.mask_emails = mask_emails
        self.mask_phones = mask_phones
        self.mask_ids = mask_ids
        self.mask_cards = mask_cards
    
    async def process(self, context: IngestContext):
        """Primijeni sigurnosne politike na chunk-ove"""
        
        if not context.chunks:
            return
        
        masked_count = 0
        pii_stats = {
            "emails": 0,
            "phones": 0,
            "jmbg": 0,
            "credit_cards": 0,
            "iban": 0
        }
        
        # Apply masking to each chunk
        for chunk in context.chunks:
            if chunk.is_duplicate:
                # Skip duplicates
                continue
            
            original_text = chunk.text
            masked_text = original_text
            
            # Mask emails
            if self.mask_emails:
                masked_text, count = self._mask_emails(masked_text)
                pii_stats["emails"] += count
            
            # Mask phones
            if self.mask_phones:
                masked_text, count = self._mask_phones(masked_text)
                pii_stats["phones"] += count
            
            # Mask JMBG (Bosnian ID)
            if self.mask_ids:
                masked_text, count = self._mask_jmbg(masked_text)
                pii_stats["jmbg"] += count
            
            # Mask credit cards
            if self.mask_cards:
                masked_text, count = self._mask_credit_cards(masked_text)
                pii_stats["credit_cards"] += count
                
                masked_text, count = self._mask_iban(masked_text)
                pii_stats["iban"] += count
            
            # Update chunk if anything was masked
            if masked_text != original_text:
                chunk.text = masked_text
                chunk.metadata["pii_masked"] = True
                masked_count += 1
        
        # Store PII stats in metadata
        context.extracted_metadata["pii_masked"] = pii_stats
        
        # Metrics
        context.set_metric("chunks_with_pii", masked_count)
        context.set_metric("total_pii_masked", sum(pii_stats.values()))
    
    def _mask_emails(self, text: str) -> Tuple[str, int]:
        """Maskira email adrese"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        count = 0
        def replacer(match):
            nonlocal count
            count += 1
            email = match.group(0)
            # Keep first char and domain
            parts = email.split('@')
            if len(parts) == 2:
                return f"{parts[0][0]}***@{parts[1]}"
            return "[EMAIL_MASKED]"
        
        masked_text = re.sub(email_pattern, replacer, text)
        return masked_text, count
    
    def _mask_phones(self, text: str) -> Tuple[str, int]:
        """Maskira telefonske brojeve"""
        # Bosnian phones: +387 XX XXX XXX, 06X XXX XXX
        phone_patterns = [
            r'\+387\s?\d{2}\s?\d{3}\s?\d{3,4}',
            r'\b06[0-9]\s?\d{3}\s?\d{3,4}\b',
            r'\+\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        ]
        
        count = 0
        masked_text = text
        
        for pattern in phone_patterns:
            def replacer(match):
                nonlocal count
                phone = match.group(0)
                # Keep only last 3 digits
                if len(phone.replace(' ', '').replace('-', '').replace('.', '')) >= 8:
                    count += 1
                    return "[PHONE_XXX" + phone[-3:] + "]"
                return phone
            
            masked_text = re.sub(pattern, replacer, masked_text)
        
        return masked_text, count
    
    def _mask_jmbg(self, text: str) -> Tuple[str, int]:
        """Maskira JMBG (13-cifreni ID broj)"""
        jmbg_pattern = r'\b\d{13}\b'
        
        count = 0
        def replacer(match):
            nonlocal count
            jmbg = match.group(0)
            # Validate JMBG (basic check: first 7 digits should be valid date)
            try:
                day = int(jmbg[0:2])
                month = int(jmbg[2:4])
                if 1 <= day <= 31 and 1 <= month <= 12:
                    count += 1
                    # Keep first 2 digits (day), mask rest
                    return f"{jmbg[0:2]}***********"
            except:
                pass
            return jmbg
        
        masked_text = re.sub(jmbg_pattern, replacer, text)
        return masked_text, count
    
    def _mask_credit_cards(self, text: str) -> Tuple[str, int]:
        """Maskira brojeve kreditnih kartica"""
        # 16-digit cards (Visa, MasterCard, etc.) with optional spaces/dashes
        card_pattern = r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'
        
        count = 0
        def replacer(match):
            nonlocal count
            card = match.group(0)
            # Basic Luhn check
            digits = re.sub(r'[\s\-]', '', card)
            if len(digits) == 16 and self._luhn_check(digits):
                count += 1
                # Show only last 4 digits
                return "****-****-****-" + digits[-4:]
            return card
        
        masked_text = re.sub(card_pattern, replacer, text)
        return masked_text, count
    
    def _mask_iban(self, text: str) -> Tuple[str, int]:
        """Maskira IBAN brojeve"""
        # IBAN: BA39 1234 5678 9012 3456
        iban_pattern = r'\b[A-Z]{2}\d{2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'
        
        count = 0
        def replacer(match):
            nonlocal count
            iban = match.group(0)
            count += 1
            # Keep country code, mask rest except last 4
            country = iban[0:2]
            digits = re.sub(r'[\s\-]', '', iban)[2:]
            return f"{country}** **** **** **** {digits[-4:]}"
        
        masked_text = re.sub(iban_pattern, replacer, text, flags=re.IGNORECASE)
        return masked_text, count
    
    def _luhn_check(self, card_number: str) -> bool:
        """Luhn algorithm za validaciju broja kartice"""
        try:
            digits = [int(d) for d in card_number]
            checksum = 0
            
            # Double every second digit from right
            for i in range(len(digits) - 2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            
            checksum = sum(digits)
            return checksum % 10 == 0
        except:
            return False
