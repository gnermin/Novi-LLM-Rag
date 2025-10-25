from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_auth, routes_documents, routes_chat, routes_ingest

app = FastAPI(
    title="Multi-RAG API",
    description="Multi-Agent Retrieval-Augmented Generation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router)
app.include_router(routes_documents.router)
app.include_router(routes_chat.router)
app.include_router(routes_ingest.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Multi-RAG API"}


@app.get("/")
async def root():
    return {
        "message": "Multi-RAG API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "documents": "/documents",
            "chat": "/chat",
            "search": "/search",
            "ingest": "/ingest"
        }
    }
