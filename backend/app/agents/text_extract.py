from pathlib import Path
import PyPDF2
from docx import Document as DocxDocument
import pandas as pd
from app.agents.base import BaseAgent
from app.agents.types import ProcessingContext, DocumentType


class TextExtractAgent(BaseAgent):
    def __init__(self):
        super().__init__("TextExtractAgent")
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        file_path = Path(context.file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {context.file_path}")
        
        if context.document_type == DocumentType.PDF:
            context.text_content = self._extract_from_pdf(file_path)
        
        elif context.document_type == DocumentType.DOCX:
            context.text_content = self._extract_from_docx(file_path)
        
        elif context.document_type in [DocumentType.CSV, DocumentType.XLSX]:
            context.text_content = self._extract_from_table(file_path)
        
        elif context.document_type == DocumentType.TEXT:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                context.text_content = f.read()
        
        context.metadata['extracted_text_length'] = len(context.text_content)
        
        return context
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        text = ""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"PDF extraction error: {str(e)}")
        return text.strip()
    
    def _extract_from_docx(self, file_path: Path) -> str:
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX extraction error: {str(e)}")
    
    def _extract_from_table(self, file_path: Path) -> str:
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            text = df.to_string(index=False)
            
            context_metadata = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist()
            }
            
            return text
        except Exception as e:
            raise Exception(f"Table extraction error: {str(e)}")
