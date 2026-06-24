from tender_documents.chunking import chunker, section_detector

PLIEGO = """CLÁUSULA 1. OBJETO
El objeto del contrato es una plataforma de datos.
Incluye analítica e integración.

2. SOLVENCIA TÉCNICA
Se exige experiencia en proyectos de datos.

ANEXO I
Modelo de proposición económica.
"""


def test_is_heading():
    assert section_detector.is_heading("CLÁUSULA 1. OBJETO")
    assert section_detector.is_heading("2. SOLVENCIA TÉCNICA")
    assert section_detector.is_heading("ANEXO I")
    assert not section_detector.is_heading("El objeto del contrato es una plataforma de datos.")


def test_detect_sections():
    sections = section_detector.detect_sections(PLIEGO)
    titles = [s["title"] for s in sections]
    assert "CLÁUSULA 1. OBJETO" in titles
    assert "2. SOLVENCIA TÉCNICA" in titles
    assert "ANEXO I" in titles


def test_chunk_document_assigns_sections():
    chunks = chunker.chunk_document(PLIEGO, size=200, overlap=20)
    assert chunks
    assert chunks[0]["ordinal"] == 0
    # los fragmentos arrastran su sección
    assert any(c["section"] == "CLÁUSULA 1. OBJETO" for c in chunks)
    assert all("content" in c for c in chunks)


def test_chunk_empty():
    assert chunker.chunk_document("") == []
    assert chunker.chunk_document("   ") == []


def test_chunk_splits_large_text():
    big = "\n".join(f"Frase numero {i}." for i in range(400))
    chunks = chunker.chunk_document(big, size=500, overlap=50)
    assert len(chunks) > 1
    assert all(len(c["content"]) <= 700 for c in chunks)  # size + overlap holgura
