import re
from sqlalchemy import create_engine, text
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.agents.types import ProcessingContext
from app.core.config import settings


class SQLIngestAgent(BaseAgent):
    def __init__(self, connection_string: str = None, query: str = None, batch_size: int = None):
        super().__init__("SQLIngestAgent")
        self.connection_string = connection_string or settings.EXTERNAL_DB_URL
        self.query = query or settings.SQL_INGEST_QUERY
        self.batch_size = batch_size or settings.SQL_INGEST_BATCH_SIZE
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        if not self.connection_string:
            raise Exception("External database connection string not configured")
        
        if not self.query:
            raise Exception("SQL query not provided")
        
        if not self._is_safe_query(self.query):
            raise Exception("Only SELECT queries are allowed for security reasons")
        
        engine = create_engine(self.connection_string)
        
        try:
            with engine.connect() as conn:
                result = conn.execute(text(self.query))
                rows = result.fetchall()
                columns = result.keys()
                
                text_content = []
                text_content.append(f"SQL Query Results from: {context.filename}")
                text_content.append(f"Columns: {', '.join(columns)}")
                text_content.append("")
                
                for row in rows[:self.batch_size]:
                    row_dict = dict(zip(columns, row))
                    row_text = " | ".join([f"{k}: {v}" for k, v in row_dict.items()])
                    text_content.append(row_text)
                
                context.text_content = "\n".join(text_content)
                context.metadata['sql_rows_fetched'] = len(rows)
                context.metadata['sql_columns'] = list(columns)
                context.metadata['sql_query'] = self.query
                
        except Exception as e:
            raise Exception(f"SQL ingestion failed: {str(e)}")
        finally:
            engine.dispose()
        
        return context
    
    def _is_safe_query(self, query: str) -> bool:
        query_upper = query.strip().upper()
        
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER', 'TRUNCATE', 'EXEC', 'EXECUTE']
        
        for keyword in dangerous_keywords:
            if re.search(rf'\b{keyword}\b', query_upper):
                return False
        
        if not query_upper.startswith('SELECT'):
            return False
        
        return True
