from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class ExtractRequest(BaseModel):
    """Extrae de una URL o de bytes en base64. Indica uno de los dos."""

    url: str | None = None
    content_base64: str | None = None
    filename: str | None = None
    content_type: str | None = None

    @model_validator(mode="after")
    def _one_source(self):
        if not self.url and not self.content_base64:
            raise ValueError("Indica 'url' o 'content_base64'.")
        return self


class Chunk(BaseModel):
    ordinal: int
    section: str | None = None
    content: str


class ExtractResponse(BaseModel):
    kind: str
    char_count: int
    chunk_count: int
    chunks: list[Chunk] = Field(default_factory=list)


class DocRef(BaseModel):
    url: str
    filename: str | None = None
    content_type: str | None = None


class ProcessRequest(BaseModel):
    tender_id: str | None = None
    documents: list[DocRef]


class ProcessResultItem(BaseModel):
    url: str
    ok: bool
    kind: str | None = None
    chunk_count: int = 0
    error: str | None = None


class ProcessResponse(BaseModel):
    tender_id: str | None = None
    processed: int
    results: list[ProcessResultItem]
