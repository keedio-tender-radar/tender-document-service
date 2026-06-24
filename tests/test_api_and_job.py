import base64

from fastapi.testclient import TestClient

from tender_documents.jobs.process_documents import process_documents
from tender_documents.main import app

client = TestClient(app)


def test_health():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert "pdf" in body["formats"]


def test_extract_base64_html(html_bytes):
    b64 = base64.b64encode(html_bytes).decode()
    resp = client.post("/extract", json={"content_base64": b64, "filename": "p.html"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["kind"] == "html"
    assert body["chunk_count"] >= 1
    assert any("plataforma de datos" in c["content"] for c in body["chunks"])


def test_extract_unsupported(html_bytes):
    b64 = base64.b64encode(html_bytes).decode()
    resp = client.post("/extract", json={"content_base64": b64, "filename": "p.zip"})
    assert resp.status_code == 415


def test_extract_requires_source():
    assert client.post("/extract", json={}).status_code == 422


class FakeDownloader:
    def __init__(self, payloads):
        self._payloads = payloads  # url -> (bytes, content_type)

    def download(self, url):
        if url not in self._payloads:
            raise RuntimeError("404")
        return self._payloads[url]


def test_process_documents_mixed(html_bytes):
    dl = FakeDownloader({"http://x/p.html": (html_bytes, "text/html")})
    docs = [
        {"url": "http://x/p.html", "filename": "p.html"},
        {"url": "http://x/missing", "filename": "m.pdf"},
    ]
    results = process_documents(docs, dl)
    assert results[0]["ok"] is True
    assert results[0]["kind"] == "html"
    assert results[0]["chunk_count"] >= 1
    assert results[1]["ok"] is False
    assert results[1]["error"]
