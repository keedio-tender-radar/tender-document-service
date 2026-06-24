"""tender-document-service — extracción y troceado de pliegos (PDF/DOCX/XLSX/HTML)."""

from __future__ import annotations

import base64

from fastapi import FastAPI, HTTPException

from tender_documents.chunking import chunker
from tender_documents.config import settings
from tender_documents.downloaders.document_downloader import DocumentDownloader, DownloadError
from tender_documents.extractors import dispatch
from tender_documents.jobs.process_documents import process_documents
from tender_documents.schemas import (
    Chunk,
    ExtractRequest,
    ExtractResponse,
    ProcessRequest,
    ProcessResponse,
    ProcessResultItem,
)

app = FastAPI(title=settings.app_name, version=settings.version)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.version,
        "formats": ["pdf", "docx", "xlsx", "html"],
    }


@app.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> ExtractResponse:
    content_type = payload.content_type
    if payload.url:
        try:
            data, header_ct = DocumentDownloader().download(payload.url)
        except DownloadError as exc:
            raise HTTPException(502, str(exc)) from exc
        content_type = content_type or header_ct
        filename = payload.filename or payload.url.rsplit("/", 1)[-1]
    else:
        try:
            data = base64.b64decode(payload.content_base64, validate=True)
        except (ValueError, TypeError) as exc:
            raise HTTPException(422, f"base64 inválido: {exc}") from exc
        filename = payload.filename

    kind = dispatch.detect_kind(filename, content_type)
    if kind is None:
        raise HTTPException(415, "Tipo de documento no soportado (usa pdf/docx/xlsx/html).")

    text = dispatch.extract(data, filename=filename, content_type=content_type)
    chunks = chunker.chunk_document(text, size=settings.chunk_size, overlap=settings.chunk_overlap)
    return ExtractResponse(
        kind=kind,
        char_count=len(text),
        chunk_count=len(chunks),
        chunks=[Chunk(**c) for c in chunks],
    )


@app.post("/process", response_model=ProcessResponse)
def process(payload: ProcessRequest) -> ProcessResponse:
    docs = [d.model_dump() for d in payload.documents]
    results = process_documents(docs, DocumentDownloader())
    return ProcessResponse(
        tender_id=payload.tender_id,
        processed=len(results),
        results=[ProcessResultItem(**r) for r in results],
    )
