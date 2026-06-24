"""Troceado de texto en fragmentos para RAG, respetando secciones y párrafos."""

from __future__ import annotations

from tender_documents.chunking import section_detector


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n") if p.strip()]


def _chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Acumula párrafos hasta `size`; arrastra `overlap` caracteres entre chunks."""
    paragraphs = _split_paragraphs(text)
    chunks: list[str] = []
    buf = ""
    for para in paragraphs:
        if buf and len(buf) + len(para) + 1 > size:
            chunks.append(buf.strip())
            buf = (buf[-overlap:] if overlap else "") + "\n" + para
        else:
            buf = f"{buf}\n{para}" if buf else para
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


def chunk_document(text: str, *, size: int = 1200, overlap: int = 150) -> list[dict]:
    """Devuelve [{ordinal, section, content}] troceando por secciones y tamaño."""
    if not text or not text.strip():
        return []
    sections = section_detector.detect_sections(text)
    if not sections:
        sections = [{"title": None, "content": text}]

    out: list[dict] = []
    ordinal = 0
    for section in sections:
        body = section["content"]
        pieces = _chunk_text(body, size, overlap) if body else []
        # una sección con solo título (sin cuerpo) también aporta un fragmento mínimo
        if not pieces and section["title"]:
            pieces = [section["title"]]
        for piece in pieces:
            out.append({"ordinal": ordinal, "section": section["title"], "content": piece})
            ordinal += 1
    return out
