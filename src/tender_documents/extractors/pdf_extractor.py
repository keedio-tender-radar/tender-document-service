"""Extracción de texto de PDF.

Estrategia: PyMuPDF (mejor que pypdf) → pypdf como respaldo → OCR (Tesseract) si el PDF
parece escaneado (muy poco texto por página). El OCR degrada de forma segura: si no hay
Tesseract instalado o falla, se devuelve el texto base sin romper.
"""

from __future__ import annotations

import io

_OCR_LANG = "spa+eng"
_OCR_MAX_PAGES = 30  # OCR es lento; se acota para no agotar el timeout del servicio
_OCR_DPI = 200


def _extract_pypdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text.strip())
    return "\n\n".join(parts)


def _extract_fitz(data: bytes) -> tuple[str, int]:
    import fitz  # PyMuPDF

    parts: list[str] = []
    with fitz.open(stream=data, filetype="pdf") as doc:
        n = doc.page_count
        for page in doc:
            text = page.get_text("text") or ""
            if text.strip():
                parts.append(text.strip())
    return "\n\n".join(parts), n


def _ocr(data: bytes) -> str:
    """OCR de las páginas (render con PyMuPDF + Tesseract). Vacío si no hay Tesseract."""
    try:
        import fitz
        import pytesseract
        from PIL import Image
    except Exception:  # noqa: BLE001 — librería ausente → sin OCR
        return ""
    parts: list[str] = []
    try:
        with fitz.open(stream=data, filetype="pdf") as doc:
            for i, page in enumerate(doc):
                if i >= _OCR_MAX_PAGES:
                    break
                pix = page.get_pixmap(dpi=_OCR_DPI)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(img, lang=_OCR_LANG)
                if text.strip():
                    parts.append(text.strip())
    except Exception:  # noqa: BLE001 — Tesseract ausente/fallo → devuelve lo obtenido
        pass
    return "\n\n".join(parts)


def extract(data: bytes) -> str:
    # 1) Texto embebido: PyMuPDF (mejor cobertura), con pypdf de respaldo.
    n_pages = 0
    try:
        text, n_pages = _extract_fitz(data)
    except Exception:  # noqa: BLE001
        text = ""
    if not text.strip():
        try:
            text = _extract_pypdf(data)
        except Exception:  # noqa: BLE001
            text = ""

    # 2) ¿Escaneado? Muy poco texto por página → intenta OCR y quédate con lo más largo.
    pages = n_pages or 1
    if len(text.strip()) < 40 * pages:
        ocr = _ocr(data)
        if len(ocr.strip()) > len(text.strip()):
            return ocr
    return text
