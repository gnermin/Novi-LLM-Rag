from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
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


@app.get("/api")
async def api_root():
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


frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(
                file_path,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )
        return FileResponse(
            frontend_dist / "index.html",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
