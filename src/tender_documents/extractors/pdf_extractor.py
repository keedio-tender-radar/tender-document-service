"""Extracción de texto de PDF (pypdf, pure-python)."""

from __future__ import annotations

import io

from pypdf import PdfReader


def extract(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text.strip())
    return "\n\n".join(parts)
