"""Procesa una lista de documentos: descarga → extrae → trocea.

Función pura sobre el downloader: testeable con un doble sin red.
"""

from __future__ import annotations

from tender_documents.chunking import chunker
from tender_documents.config import settings
from tender_documents.extractors import dispatch


def process_documents(documents: list[dict], downloader) -> list[dict]:
    """Cada doc: {url, filename?, content_type?} → {url, ok, kind, chunk_count, error}."""
    results: list[dict] = []
    for doc in documents:
        url = doc.get("url")
        try:
            data, header_ct = downloader.download(url)
            content_type = doc.get("content_type") or header_ct
            kind = dispatch.detect_kind(doc.get("filename"), content_type)
            text = dispatch.extract(
                data, filename=doc.get("filename"), content_type=content_type
            )
            chunks = chunker.chunk_document(
                text, size=settings.chunk_size, overlap=settings.chunk_overlap
            )
            results.append(
                {"url": url, "ok": True, "kind": kind, "chunk_count": len(chunks), "error": None}
            )
        except Exception as exc:  # noqa: BLE001 — un documento con error no tumba el lote
            results.append(
                {"url": url, "ok": False, "kind": None, "chunk_count": 0, "error": str(exc)}
            )
    return results
