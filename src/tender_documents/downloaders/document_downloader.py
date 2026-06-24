"""Descarga de documentos por URL."""

from __future__ import annotations

import httpx

from tender_documents.config import settings


class DownloadError(RuntimeError):
    pass


class DocumentDownloader:
    def __init__(self, *, timeout: float = 60.0, max_bytes: int | None = None) -> None:
        self.timeout = timeout
        self.max_bytes = max_bytes or settings.max_download_bytes

    def _client(self) -> httpx.Client:
        """Cliente httpx. Monkeypatcheable en tests."""
        return httpx.Client(timeout=self.timeout, follow_redirects=True)

    def download(self, url: str) -> tuple[bytes, str | None]:
        """Devuelve (bytes, content_type). Lanza DownloadError si falla o excede el tamaño."""
        try:
            with self._client() as client:
                resp = client.get(url)
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise DownloadError(f"No se pudo descargar {url}: {exc}") from exc
        data = resp.content
        if len(data) > self.max_bytes:
            raise DownloadError(f"Documento demasiado grande ({len(data)} bytes).")
        return data, resp.headers.get("content-type")
