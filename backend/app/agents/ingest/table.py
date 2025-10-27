import json
import csv
import io
from typing import List, Dict, Any
from .base import IngestAgent
from .types import IngestContext, TableData
from app.core.config import settings

try:
    from app.services.llm_client import get_llm_client
except ImportError:
    get_llm_client = None


class TableAgent(IngestAgent):
    """
    TableAgent - Parsira i strukturira tabele iz dokumenata.
    LLM mode: Koristi LLM za razumijevanje kompleksnih tabela
    Fallback mode: Heuristička analiza redova/kolona
    """
    
    def __init__(self, use_llm: bool = True):
        super().__init__("TableAgent", dependencies=["ExtractAgent"])
        self.use_llm = use_llm and bool(settings.OPENAI_API_KEY)
    
    async def process(self, context: IngestContext):
        """Procesuj sve tabele"""
        
        if not context.tables:
            # No tables extracted
            return
        
        processed_tables = []
        
        for idx, table in enumerate(context.tables):
            try:
                # Validate and clean table
                cleaned_table = await self._clean_table(table)
                
                # Enhance with LLM if available
                if self.use_llm and len(table.rows) > 2:
                    enhanced_table = await self._llm_enhance_table(cleaned_table, context)
                    if enhanced_table:
                        cleaned_table = enhanced_table
                
                # Convert to multiple formats
                cleaned_table.metadata["csv"] = self._table_to_csv(cleaned_table)
                cleaned_table.metadata["json"] = self._table_to_json(cleaned_table)
                
                processed_tables.append(cleaned_table)
                
            except Exception as e:
                context.add_error(f"Table {idx} processing greška: {str(e)}")
        
        # Update context with processed tables
        context.tables = processed_tables
        
        # Add table data to extracted metadata
        context.extracted_metadata["tables_count"] = len(processed_tables)
        context.extracted_metadata["tables_data"] = [
            {
                "headers": table.headers,
                "row_count": len(table.rows),
                "col_count": len(table.headers)
            }
            for table in processed_tables
        ]
        
        # Metrics
        context.set_metric("tables_processed", len(processed_tables))
    
    async def _clean_table(self, table: TableData) -> TableData:
        """Očisti tabelu od praznih redova/kolona"""
        # Remove empty rows
        cleaned_rows = [
            row for row in table.rows
            if any(cell.strip() for cell in row)
        ]
        
        # Remove empty columns
        if not table.headers or not cleaned_rows:
            return table
        
        col_count = len(table.headers)
        non_empty_cols = []
        
        for col_idx in range(col_count):
            has_data = False
            
            # Check header
            if col_idx < len(table.headers) and table.headers[col_idx].strip():
                has_data = True
            
            # Check rows
            for row in cleaned_rows:
                if col_idx < len(row) and row[col_idx].strip():
                    has_data = True
                    break
            
            if has_data:
                non_empty_cols.append(col_idx)
        
        # Rebuild table with non-empty columns
        new_headers = [table.headers[i] for i in non_empty_cols if i < len(table.headers)]
        new_rows = [
            [row[i] if i < len(row) else "" for i in non_empty_cols]
            for row in cleaned_rows
        ]
        
        return TableData(
            headers=new_headers,
            rows=new_rows,
            page=table.page,
            format=table.format,
            metadata=table.metadata.copy()
        )
    
    async def _llm_enhance_table(self, table: TableData, context: IngestContext) -> TableData:
        """LLM enhancement - provjerava header-e, tipove, značenje kolona"""
        llm = get_llm_client()
        
        # Create table preview
        preview_rows = table.rows[:5]
        table_text = self._table_to_text(table.headers, preview_rows)
        
        prompt = f"""Analiziraj sljedeću tabelu i poboljšaj nazive kolona:

{table_text}

Odgovori sa JSON:
{{
  "headers": ["Poboljšan Naziv 1", "Poboljšan Naziv 2", ...],
  "column_types": ["text|number|date|currency|boolean", ...],
  "description": "Šta ova tabela predstavlja"
}}

Pravila:
- Koristi jasne, deskriptivne nazive na bosanskom jeziku
- Detektuj tipove podataka
- Zadrži isti broj kolona"""
        
        try:
            response = await llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Clean JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            
            # Update headers if valid
            new_headers = data.get("headers", [])
            if len(new_headers) == len(table.headers):
                table.headers = new_headers
            
            # Store metadata
            table.metadata["column_types"] = data.get("column_types", [])
            table.metadata["description"] = data.get("description", "")
            table.metadata["enhanced"] = True
            
        except Exception as e:
            context.add_error(f"LLM table enhancement greška: {str(e)}")
        
        return table
    
    def _table_to_text(self, headers: List[str], rows: List[List[str]]) -> str:
        """Convert table to readable text"""
        lines = []
        
        # Headers
        lines.append(" | ".join(headers))
        lines.append("-" * 50)
        
        # Rows
        for row in rows:
            lines.append(" | ".join(str(cell) for cell in row))
        
        return "\n".join(lines)
    
    def _table_to_csv(self, table: TableData) -> str:
        """Convert table to CSV string"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(table.headers)
        
        # Write rows
        for row in table.rows:
            writer.writerow(row)
        
        return output.getvalue()
    
    def _table_to_json(self, table: TableData) -> str:
        """Convert table to JSON array"""
        records = []
        
        for row in table.rows:
            record = {}
            for idx, header in enumerate(table.headers):
                value = row[idx] if idx < len(row) else ""
                record[header] = value
            records.append(record)
        
        return json.dumps(records, ensure_ascii=False, indent=2)
