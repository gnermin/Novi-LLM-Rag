# Multi-RAG Usage Guide

## Getting Started

### 1. Sign Up / Login

1. Navigate to the application (it will show the login page)
2. Click "Need an account? Sign up"
3. Enter your email and create a password
4. You'll be automatically logged in

### 2. Upload Documents

1. Click on **Documents** in the navigation
2. Drag and drop a file or click the upload area
3. Supported formats:
   - **PDF** - Research papers, reports, ebooks
   - **DOCX** - Word documents
   - **XLSX** - Excel spreadsheets
   - **CSV** - Data files
   - **JPG/PNG** - Images (with OCR)

4. Watch the multi-agent pipeline process your document:
   - **MimeDetectAgent**: Detects file type
   - **TextExtractAgent**: Extracts text
   - **OCRAgent**: Processes images if enabled
   - **ChunkingAgent**: Splits into searchable chunks
   - **EmbeddingAgent**: Generates OpenAI embeddings
   - **IndexingAgent**: Stores in vector database

5. Document status will change from "pending" → "processing" → "ready"

### 3. Chat with Your Documents

1. Go to **Chat** page
2. Ask natural language questions about your uploaded content
3. Example questions:
   - "What are the main topics in my documents?"
   - "Summarize the key findings from the research paper"
   - "What data is available about customers?"
   
4. Get AI-powered answers with source citations
5. Each answer shows:
   - The generated response
   - Source documents with similarity scores
   - Relevant text chunks from your content

### 4. Ingest SQL Data (Optional)

1. Navigate to **Settings**
2. Configure SQL data ingestion:
   - **Source Name**: Friendly name for your data source
   - **SQL Query**: SELECT statement to fetch data
   - **Connection String** (optional): PostgreSQL connection URL

3. Example SQL queries:
   ```sql
   SELECT * FROM customers LIMIT 100
   SELECT name, email, created_at FROM users WHERE active = true
   SELECT product_name, price, category FROM products
   ```

4. The system will:
   - Fetch rows from your database
   - Convert them into searchable text chunks
   - Generate embeddings
   - Index for RAG search

5. Once ingested, you can chat with your SQL data just like documents!

## Features Explained

### Hybrid Search

The system uses two search methods combined:
- **BM25**: Traditional keyword-based search
- **Vector Similarity**: Semantic search using embeddings
- Results are merged and ranked for optimal retrieval

### Agent Pipeline

Each document goes through specialized agents:
1. **MIME Detection**: Identifies file type
2. **Text Extraction**: Pulls text from documents
3. **OCR**: Scans images if needed
4. **Chunking**: Breaks text into 1000-char pieces with 200-char overlap
5. **Embedding**: Creates vector representations (1536 dimensions)
6. **Indexing**: Stores in PostgreSQL with pgvector

### Citations

Every chat answer includes citations showing:
- Which document the information came from
- The specific text chunk matched
- Similarity score (0-1, higher is better match)

## Tips for Best Results

### Document Upload
- Keep files under 50MB
- Use clear, well-formatted documents
- PDFs work best when they contain text (not just scanned images)
- For scanned documents, enable OCR in settings

### Chat Queries
- Be specific in your questions
- Ask about topics covered in your documents
- Use natural language
- For better results, upload multiple related documents

### SQL Ingestion
- Use SELECT queries only (security restriction)
- Limit large result sets (e.g., LIMIT 1000)
- Include meaningful column names
- Consider joining related tables for richer context

## Security Notes

- All data is associated with your user account
- JWT authentication protects all API calls
- SQL queries are validated (only SELECT allowed)
- Passwords are hashed with bcrypt
- File uploads are validated for size and type

## Troubleshooting

**Document stuck in "pending" status**
- Check the agent logs on the Documents page
- Verify the file format is supported
- Ensure the file isn't corrupted

**Chat returns no results**
- Make sure you have documents in "ready" status
- Check that embeddings were generated (see agent logs)
- Try rephrasing your question

**SQL ingestion fails**
- Verify connection string format: `postgresql://user:pass@host:port/db`
- Ensure query is a SELECT statement
- Check database permissions
- Review error message in UI

## Advanced Usage

### Environment Variables

You can customize behavior via environment variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
EMBEDDINGS_PROVIDER=openai
EMBEDDINGS_DIM=1536

# Pipeline Settings  
OCR_ENABLED=true
PIPELINE_MODE=full

# SQL Ingestion Defaults
EXTERNAL_DB_URL=postgresql://...
SQL_INGEST_QUERY=SELECT * FROM table LIMIT 100
SQL_INGEST_BATCH_SIZE=500

# Upload Limits
UPLOAD_MAX_SIZE=52428800  # 50MB in bytes
```

### Database Schema

Documents are stored with:
- Original file metadata
- Processing status
- Agent execution logs
- Chunk count and text length

Chunks include:
- Text content
- 1536-dimensional embedding vector
- Document reference
- Chunk index

### API Integration

You can integrate with the API directly:

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}'

# Upload Document
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is in my documents?","top_k":5}'
```

## Next Steps

1. **Upload your first document** to see the pipeline in action
2. **Try the chat interface** to ask questions
3. **Explore SQL ingestion** to connect external data
4. **Review agent logs** to understand how processing works
5. **Experiment with different document types** to see versatility

Enjoy your Multi-RAG system! 🚀
