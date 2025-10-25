from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pathlib import Path
import aiofiles
import uuid
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.external_source import IngestJob
from app.schemas.document import DocumentResponse, DocumentListResponse, AgentLog
from app.services.pipeline import DocumentPipeline
from app.agents.types import ProcessingContext
from app.core.config import settings
import os

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.size and file.size > settings.UPLOAD_MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large"
        )
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    file_path = Path(settings.UPLOAD_DIR) / f"{file_id}{file_ext}"
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    document = Document(
        filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        mime_type=file.content_type,
        status="pending",
        created_by=current_user.id
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    job = IngestJob(
        document_id=document.id,
        status="processing"
    )
    db.add(job)
    db.commit()
    
    try:
        pipeline = DocumentPipeline(db)
        context = ProcessingContext(
            document_id=str(document.id),
            file_path=str(file_path),
            filename=file.filename,
            mime_type=file.content_type
        )
        
        context = await pipeline.process_document(context)
        
        document.status = "ready"
        document.doc_metadata = {
            "chunks": len(context.chunks),
            "text_length": len(context.text_content) if context.text_content else 0,
            "indexed_chunks": context.metadata.get('indexed_chunks', 0)
        }
        
        job.status = "completed"
        job.logs = [result.to_dict() for result in context.agent_results]
        job.completed_at = db.execute(text("SELECT NOW()")).scalar()
        
        db.commit()
        db.refresh(document)
        db.refresh(job)
        
    except Exception as e:
        document.status = "error"
        job.status = "failed"
        job.error = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )
    
    agent_logs = [AgentLog(**log) for log in job.logs] if job.logs else []
    
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
        mime_type=document.mime_type,
        file_size=document.file_size,
        metadata=document.doc_metadata or {},
        created_at=document.created_at,
        agent_logs=agent_logs
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = db.query(Document).filter(
        Document.created_by == current_user.id
    ).order_by(Document.created_at.desc()).all()
    
    doc_responses = []
    for doc in documents:
        job = db.query(IngestJob).filter(IngestJob.document_id == doc.id).first()
        agent_logs = []
        if job and job.logs:
            agent_logs = [AgentLog(**log) for log in job.logs]
        
        doc_responses.append(DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            status=doc.status,
            mime_type=doc.mime_type,
            file_size=doc.file_size,
            metadata=doc.doc_metadata or {},
            created_at=doc.created_at,
            agent_logs=agent_logs
        ))
    
    return DocumentListResponse(
        documents=doc_responses,
        total=len(doc_responses)
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.created_by == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    job = db.query(IngestJob).filter(IngestJob.document_id == document.id).first()
    agent_logs = []
    if job and job.logs:
        agent_logs = [AgentLog(**log) for log in job.logs]
    
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
        mime_type=document.mime_type,
        file_size=document.file_size,
        metadata=document.doc_metadata or {},
        created_at=document.created_at,
        agent_logs=agent_logs
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.created_by == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Brisanje fizičkog fajla sa diska
    if document.file_path and Path(document.file_path).exists():
        try:
            Path(document.file_path).unlink()
        except Exception as e:
            print(f"Failed to delete file {document.file_path}: {e}")
    
    # CASCADE brisanje će automatski obrisati:
    # - document_chunks (svi chunk-ovi)
    # - document_relations (sve relacije)
    # - ingest_jobs (sve job-ove)
    db.delete(document)
    db.commit()
    
    return {
        "success": True,
        "message": f"Dokument '{document.filename}' i svi povezani podaci uspješno obrisani",
        "deleted_id": document_id
    }


@router.delete("")
async def delete_all_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = db.query(Document).filter(
        Document.created_by == current_user.id
    ).all()
    
    if not documents:
        return {
            "success": True,
            "message": "Nema dokumenata za brisanje",
            "deleted_count": 0
        }
    
    deleted_count = 0
    deleted_files = []
    
    for document in documents:
        # Brisanje fizičkog fajla
        if document.file_path and Path(document.file_path).exists():
            try:
                Path(document.file_path).unlink()
            except Exception as e:
                print(f"Failed to delete file {document.file_path}: {e}")
        
        deleted_files.append(document.filename)
        db.delete(document)
        deleted_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Svi dokumenti ({deleted_count}) i povezani podaci uspješno obrisani",
        "deleted_count": deleted_count,
        "deleted_files": deleted_files
    }
