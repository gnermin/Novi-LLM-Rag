import mimetypes
from pathlib import Path
from app.agents.base import BaseAgent
from app.agents.types import ProcessingContext, DocumentType


class MimeDetectAgent(BaseAgent):
    def __init__(self):
        super().__init__("MimeDetectAgent")
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        mime_type, _ = mimetypes.guess_type(context.filename)
        
        if mime_type:
            context.mime_type = mime_type
        
        file_ext = Path(context.filename).suffix.lower()
        
        doc_type_map = {
            '.pdf': DocumentType.PDF,
            '.docx': DocumentType.DOCX,
            '.doc': DocumentType.DOCX,
            '.xlsx': DocumentType.XLSX,
            '.xls': DocumentType.XLSX,
            '.csv': DocumentType.CSV,
            '.jpg': DocumentType.IMAGE,
            '.jpeg': DocumentType.IMAGE,
            '.png': DocumentType.IMAGE,
            '.txt': DocumentType.TEXT,
        }
        
        context.document_type = doc_type_map.get(file_ext, DocumentType.UNKNOWN)
        context.metadata['detected_mime_type'] = mime_type
        context.metadata['detected_document_type'] = context.document_type.value
        
        return context
