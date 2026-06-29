"""Extracción de texto de HTML (stdlib, sin dependencias) + descubrimiento de enlaces a pliegos."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.parse import urljoin

_SKIP = {"script", "style", "head", "noscript"}

# Extensiones de documento del expediente.
_DOC_EXT = (".pdf", ".doc", ".docx", ".odt", ".rtf")
# Palabras que delatan un documento de pliego en el texto/href del enlace.
_DOC_HINTS = (
    "pliego", "pcap", "ppt", "prescripciones", "clausulas", "cláusulas", "anexo",
    "memoria", "documento", "bases", "caracteristicas", "características",
)
# Pistas de página intermedia (perfil del contratante / plataforma) a la que saltar (HTML→PDF).
_PROFILE_HINTS = (
    "perfil", "contratante", "contractant", "licitaci", "expedient", "perfils-contractant",
    "contrataciondelestado", "contractaciopublica", "plataforma",
)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip_depth = 0
        self.links: list[tuple[str, str]] = []  # (href, texto del enlace)
        self._href: str | None = None
        self._a_text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in _SKIP:
            self._skip_depth += 1
        elif tag == "a":
            self._href = dict(attrs).get("href")
            self._a_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag == "a" and self._href:
            self.links.append((self._href, " ".join(self._a_text).strip()))
            self._href = None

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._chunks.append(data.strip())
            if self._href is not None:
                self._a_text.append(data.strip())

    @property
    def text(self) -> str:
        return "\n".join(self._chunks)


def _parse(data: bytes) -> _TextExtractor:
    parser = _TextExtractor()
    parser.feed(data.decode("utf-8", errors="replace"))
    return parser


def extract(data: bytes) -> str:
    text = _parse(data).text
    return re.sub(r"\n{3,}", "\n\n", text)


def find_document_links(data: bytes, base_url: str) -> list[str]:
    """Enlaces a documentos del expediente (PDF/DOCX/…) descubiertos en el HTML del anuncio.

    Heurística: href con extensión de documento, o cuyo href/texto contiene pistas de pliego.
    Devuelve URLs absolutas, sin duplicados, preservando el orden de aparición.
    """
    out: list[str] = []
    seen: set[str] = set()
    for href, label in _parse(data).links:
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        low = f"{href} {label}".lower()
        is_doc = href.lower().split("?", 1)[0].endswith(_DOC_EXT)
        is_hint = any(h in low for h in _DOC_HINTS)
        if not (is_doc or is_hint):
            continue
        absu = urljoin(base_url, href)
        if absu not in seen:
            seen.add(absu)
            out.append(absu)
    return out


def find_profile_links(data: bytes, base_url: str) -> list[str]:
    """Enlaces a páginas intermedias (perfil del contratante/plataforma) para saltar HTML→PDF.

    Útil en TED: el anuncio no enlaza el PDF directamente, sino el perfil del comprador donde
    están los documentos. Devuelve URLs absolutas, sin duplicados.
    """
    out: list[str] = []
    seen: set[str] = set()
    for href, label in _parse(data).links:
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        if href.lower().split("?", 1)[0].endswith(_DOC_EXT):
            continue  # eso es un documento directo, no una página intermedia
        low = f"{href} {label}".lower()
        if not any(h in low for h in _PROFILE_HINTS):
            continue
        absu = urljoin(base_url, href)
        if absu not in seen:
            seen.add(absu)
            out.append(absu)
    return out
