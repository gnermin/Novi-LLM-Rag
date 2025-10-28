from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_auth, routes_documents, routes_chat, routes_ingest
from app.core.config import settings

app = FastAPI(
    title="Multi-RAG API",
    description="Multi-Agent Retrieval-Augmented Generation System",
    version="1.0.0",
)

# CORS (uzima iz settings; fallback na localhost ako helper ne postoji)
try:
    origins = settings.get_cors_origins()
except Exception:
    origins = getattr(settings, "CORS_ORIGINS", ["http://localhost", "http://127.0.0.1"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if isinstance(origins, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"

# VAŽNO: tvoji routeri već imaju interna imena (/auth, /documents, /chat, /ingest),
# ovdje im samo dodajemo globalni prefiks /api
app.include_router(routes_auth.router,      prefix=API_PREFIX)
app.include_router(routes_documents.router, prefix=API_PREFIX)
app.include_router(routes_chat.router,      prefix=API_PREFIX)
app.include_router(routes_ingest.router,    prefix=API_PREFIX)

@app.get(f"{API_PREFIX}/health")
async def health_check():
    return {"status": "ok", "service": "Multi-RAG API"}

@app.get(API_PREFIX)
async def api_root():
    return {
        "message": "Multi-RAG API",
        "version": "1.0.0",
        "endpoints": {
            "auth": f"{API_PREFIX}/auth",
            "documents": f"{API_PREFIX}/documents",
            "chat": f"{API_PREFIX}/chat",
            "search": f"{API_PREFIX}/search",
            "ingest": f"{API_PREFIX}/ingest",
        },
    }
