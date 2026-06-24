"""Extracción de texto de HTML (stdlib, sin dependencias)."""

from __future__ import annotations

import re
from html.parser import HTMLParser

_SKIP = {"script", "style", "head", "noscript"}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in _SKIP:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._chunks.append(data.strip())

    @property
    def text(self) -> str:
        return "\n".join(self._chunks)


def extract(data: bytes) -> str:
    html = data.decode("utf-8", errors="replace")
    parser = _TextExtractor()
    parser.feed(html)
    text = parser.text
    return re.sub(r"\n{3,}", "\n\n", text)
