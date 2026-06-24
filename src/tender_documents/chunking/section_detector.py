"""Detección heurística de secciones en pliegos.

Reconoce cabeceras típicas (numeración "1.", "1.2.", CLÁUSULA/ANEXO/APARTADO, líneas cortas en
mayúsculas) y parte el texto en secciones {title, content}.
"""

from __future__ import annotations

import re

_HEADING_KEYWORDS = re.compile(
    r"^(CL[ÁA]USULA|ANEXO|AP[ÁA]RTADO|SECCI[ÓO]N|T[ÍI]TULO|CAP[ÍI]TULO)\b",
    re.IGNORECASE,
)
_NUMBERED = re.compile(r"^\d+(\.\d+)*\.?\s+\S")


def is_heading(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > 120:
        return False
    if _HEADING_KEYWORDS.match(s):
        return True
    if _NUMBERED.match(s):
        return True
    # línea corta en mayúsculas (con letras)
    letters = [c for c in s if c.isalpha()]
    if letters and len(s) <= 80 and s == s.upper() and len(letters) >= 3:
        return True
    return False


def detect_sections(text: str) -> list[dict]:
    """Devuelve [{title, content}]. Si no hay cabeceras, una sola sección sin título."""
    lines = text.splitlines()
    sections: list[dict] = []
    current = {"title": None, "lines": []}
    for line in lines:
        if is_heading(line):
            if current["lines"]:
                sections.append(current)
            current = {"title": line.strip(), "lines": []}
        else:
            current["lines"].append(line)
    if current["lines"] or current["title"]:
        sections.append(current)

    return [
        {"title": s["title"], "content": "\n".join(s["lines"]).strip()}
        for s in sections
        if "\n".join(s["lines"]).strip() or s["title"]
    ]
