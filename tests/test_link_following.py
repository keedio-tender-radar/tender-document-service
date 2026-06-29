from tender_documents.extractors import html_extractor


def test_find_document_links():
    html = b"""
    <html><body>
      <a href="/docs/PCAP.pdf">Pliego de clausulas administrativas</a>
      <a href="https://x.org/ppt.docx">Prescripciones tecnicas</a>
      <a href="#seccion">Ir a seccion</a>
      <a href="/style.css">estilo</a>
      <a href="https://x.org/anexo-1.pdf">Anexo I</a>
    </body></html>
    """
    links = html_extractor.find_document_links(html, "https://ted.europa.eu/notice/1/html")
    assert "https://ted.europa.eu/docs/PCAP.pdf" in links
    assert "https://x.org/ppt.docx" in links
    assert "https://x.org/anexo-1.pdf" in links
    assert all("style.css" not in u and "#seccion" not in u for u in links)


def test_extract_still_returns_text():
    html = b"<html><body><p>Hola mundo</p><a href='x.pdf'>pliego</a></body></html>"
    assert "Hola mundo" in html_extractor.extract(html)
