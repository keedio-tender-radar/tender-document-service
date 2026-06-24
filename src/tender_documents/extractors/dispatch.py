"""Selección del extractor según extensión o content-type."""

from __future__ import annotations

from tender_documents.extractors import (
    docx_extractor,
    html_extractor,
    pdf_extractor,
    xlsx_extractor,
)


class UnsupportedDocument(ValueError):
    """Tipo de documento no soportado."""


_DOCX_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_XLSX_CT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

_BY_EXT = {
    "pdf": pdf_extractor.extract,
    "docx": docx_extractor.extract,
    "xlsx": xlsx_extractor.extract,
    "html": html_extractor.extract,
    "htm": html_extractor.extract,
}

_CT_TO_KIND = {
    "application/pdf": "pdf",
    _DOCX_CT: "docx",
    _XLSX_CT: "xlsx",
    "text/html": "html",
}


def detect_kind(filename: str | None, content_type: str | None) -> str | None:
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext in _BY_EXT:
            return ext
    if content_type:
        ct = content_type.split(";", 1)[0].strip().lower()
        if ct in _CT_TO_KIND:
            return _CT_TO_KIND[ct]
    return None


def extract(data: bytes, *, filename: str | None = None, content_type: str | None = None) -> str:
    kind = detect_kind(filename, content_type)
    if kind is None:
        raise UnsupportedDocument(
            f"No soportado (filename={filename!r}, content_type={content_type!r})."
        )
    return _BY_EXT[kind](data)
