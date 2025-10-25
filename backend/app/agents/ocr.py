from PIL import Image
import pytesseract
from pathlib import Path
from app.agents.base import BaseAgent
from app.agents.types import ProcessingContext, DocumentType


class OCRAgent(BaseAgent):
    def __init__(self, enabled: bool = True):
        super().__init__("OCRAgent", enabled=enabled)
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        if context.document_type != DocumentType.IMAGE:
            return context
        
        file_path = Path(context.file_path)
        
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            context.text_content = text.strip()
            context.metadata['ocr_confidence'] = 'completed'
        except Exception as e:
            context.metadata['ocr_error'] = str(e)
            context.text_content = ""
        
        return context
