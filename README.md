# Multi-RAG - Multi-Agent Retrieval-Augmented Generation System

A comprehensive RAG system featuring multi-agent document processing, SQL data ingestion, and intelligent chat with citations.

## Features

- **Multi-Agent Document Processing**: Automated pipeline for PDF, DOCX, Excel, CSV, and image processing
- **SQL Data Ingestion**: Connect to external databases and ingest data via SQL queries
- **Hybrid Search**: BM25 + pgvector similarity search for optimal retrieval
- **RAG Chat**: OpenAI-powered chat with source citations
- **Modern UI**: React + TypeScript + Tailwind CSS frontend

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL + pgvector** - Vector database for embeddings
- **SQLAlchemy** - ORM for database operations
- **OpenAI** - Embeddings and chat completions
- **PyPDF2, python-docx, openpyxl** - Document processing
- **Pytesseract** - OCR for images

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS 3** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client

## Quick Start

The application is pre-configured and ready to run in Replit:

1. **Environment Variables**: Already configured
   - `DATABASE_URL` - PostgreSQL connection
   - `OPENAI_API_KEY` - OpenAI API key
   - `SESSION_SECRET` - JWT secret

2. **Development Server**: Single unified server
   - Dev Server: http://localhost:5000 (API + Frontend)

3. **Access the App**: Click the webview to open the application

## Deployment

The application is **ready to deploy** with Replit Autoscale! See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

**Quick Deploy:**
1. Click "Deploy" in Replit
2. Choose "Autoscale" deployment
3. Select machine size and max instances
4. Click "Deploy" - that's it!

The deployment automatically:
- Builds the React frontend
- Starts FastAPI server on port 5000
- Serves both API and frontend from single origin

## Usage

### 1. Create an Account
- Navigate to the login page
- Click "Need an account? Sign up"
- Enter email and password

### 2. Upload Documents
- Go to the Documents page
- Drag and drop or click to upload files
- Supported formats: PDF, DOCX, XLSX, CSV, JPG, PNG
- Watch the multi-agent pipeline process your document

### 3. Chat with RAG
- Navigate to the Chat page
- Ask questions about your uploaded documents
- Get AI-powered answers with source citations

### 4. Ingest SQL Data
- Go to Settings
- Enter a source name and SQL SELECT query
- Optionally provide a connection string
- Click "Ingest Data" to process and index

## Multi-Agent Pipeline

Documents are processed through these agents:

1. **MimeDetectAgent** - Detects file type
2. **TextExtractAgent** - Extracts text from documents
3. **OCRAgent** - Processes scanned images/PDFs
4. **ChunkingAgent** - Splits text into chunks (1000 chars, 200 overlap)
5. **EmbeddingAgent** - Generates OpenAI embeddings
6. **IndexingAgent** - Stores in pgvector database

## API Endpoints

### Authentication
- `POST /auth/signup` - Create account
- `POST /auth/login` - Login

### Documents
- `POST /documents/upload` - Upload file
- `GET /documents` - List documents
- `GET /documents/{id}` - Get document details

### Chat & Search
- `POST /chat` - RAG chat with citations
- `POST /search` - Hybrid search

### SQL Ingestion
- `POST /ingest/sql` - Ingest SQL data

### Health
- `GET /health` - Health check
- `GET /` - API info

## Architecture

```
┌─────────────────┐
│  React Frontend │ :5000
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Backend│ :8000
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────────┐
│OpenAI  │ │PostgreSQL    │
│API     │ │+ pgvector    │
└────────┘ └──────────────┘
```

## Security

- JWT-based authentication with bcrypt password hashing
- SQL injection prevention (SELECT-only queries)
- CORS configuration for API access
- Environment-based secret management
- File upload size limits (50MB)

## Database Schema

- **users** - User accounts
- **documents** - Uploaded documents
- **document_chunks** - Text chunks with embeddings
- **document_relations** - Document relationships
- **external_sources** - SQL data sources
- **ingest_jobs** - Processing job logs

## Environment Configuration

All required environment variables are pre-configured:
- `DATABASE_URL` - PostgreSQL with pgvector
- `OPENAI_API_KEY` - For embeddings and chat
- `SESSION_SECRET` - JWT signing key

Optional SQL ingestion variables:
- `EXTERNAL_DB_URL` - External database connection
- `SQL_INGEST_QUERY` - Default SQL query
- `SQL_INGEST_BATCH_SIZE` - Batch size (default: 500)

## Development

### Backend Development
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Build Frontend
```bash
cd frontend
npm run build
```

## Troubleshooting

**Backend won't start**
- Verify `DATABASE_URL` is set
- Check `OPENAI_API_KEY` is configured
- Review backend logs in the console

**Document processing fails**
- Check file format is supported
- Verify file size is under 50MB
- Review agent logs in the UI

**Chat returns no results**
- Ensure documents are processed (status: ready)
- Verify OpenAI API key is valid
- Check embeddings were generated

**SQL ingestion fails**
- Verify database connection string
- Ensure query is SELECT only
- Check database permissions

## License

ISC

## Author

Nermin Goran - AI/IoT Systems Architect
