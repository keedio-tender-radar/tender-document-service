import pytest

from tender_documents.extractors import (
    dispatch,
    docx_extractor,
    html_extractor,
    xlsx_extractor,
)


def test_html_extract(html_bytes):
    text = html_extractor.extract(html_bytes)
    assert "Pliego" in text
    assert "plataforma de datos" in text
    assert "ignore()" not in text  # script descartado


def test_docx_extract(docx_bytes):
    text = docx_extractor.extract(docx_bytes)
    assert "Pliego de prescripciones" in text
    assert "integración de APIs" in text


def test_xlsx_extract(xlsx_bytes):
    text = xlsx_extractor.extract(xlsx_bytes)
    assert "Criterios" in text
    assert "Precio | 40" in text


def test_pdf_extract():
    fpdf = pytest.importorskip("fpdf")
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 8, "Objeto del contrato: plataforma de datos sanitarios.")
    data = bytes(pdf.output())

    from tender_documents.extractors import pdf_extractor

    text = pdf_extractor.extract(data)
    assert "plataforma de datos" in text.lower()


def test_pdf_scanned_degrades_safely():
    # PDF sin texto embebido (simula escaneo): sin Tesseract, el OCR degrada a "" sin romper.
    fitz = pytest.importorskip("fitz")
    from tender_documents.extractors import pdf_extractor

    doc = fitz.open()
    doc.new_page()
    data = doc.tobytes()
    doc.close()
    assert isinstance(pdf_extractor.extract(data), str)  # no lanza excepción


def test_dispatch_by_extension(html_bytes):
    assert dispatch.detect_kind("pliego.pdf", None) == "pdf"
    assert dispatch.detect_kind("a.docx", None) == "docx"
    text = dispatch.extract(html_bytes, filename="x.html")
    assert "plataforma de datos" in text


def test_dispatch_by_content_type(html_bytes):
    assert dispatch.detect_kind(None, "text/html; charset=utf-8") == "html"
    text = dispatch.extract(html_bytes, content_type="text/html")
    assert "plataforma de datos" in text


def test_dispatch_unsupported():
    with pytest.raises(dispatch.UnsupportedDocument):
        dispatch.extract(b"data", filename="x.zip", content_type="application/zip")
