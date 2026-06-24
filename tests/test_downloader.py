import httpx
import pytest

from tender_documents.downloaders.document_downloader import DocumentDownloader, DownloadError


def _patch(monkeypatch, handler):
    dl = DocumentDownloader()
    monkeypatch.setattr(
        dl, "_client", lambda: httpx.Client(transport=httpx.MockTransport(handler))
    )
    return dl


def test_download_ok(monkeypatch):
    def handler(req):
        return httpx.Response(200, content=b"hola", headers={"content-type": "text/html"})

    dl = _patch(monkeypatch, handler)
    data, ct = dl.download("http://x/doc.html")
    assert data == b"hola"
    assert ct == "text/html"


def test_download_http_error(monkeypatch):
    def handler(req):
        return httpx.Response(404)

    dl = _patch(monkeypatch, handler)
    with pytest.raises(DownloadError):
        dl.download("http://x/missing")


def test_download_too_big(monkeypatch):
    def handler(req):
        return httpx.Response(200, content=b"x" * 100)

    dl = _patch(monkeypatch, handler)
    dl.max_bytes = 10
    with pytest.raises(DownloadError):
        dl.download("http://x/big")
