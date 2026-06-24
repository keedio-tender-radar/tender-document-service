# tender-document-service

> 📄 Descarga y extracción de pliegos (PDF/DOCX/XLSX/HTML) de **Keedio Tender Radar** (MVP-2).
> Convierte documentos en **texto + fragmentos por sección** listos para el análisis y el RAG.

## Pipeline

```
URL / bytes  ─►  download  ─►  extract (PDF/DOCX/XLSX/HTML)  ─►  detectar secciones  ─►  chunking
```

- **Extractores** (`extractors/`): `pypdf`, `python-docx`, `openpyxl`, HTML con stdlib. `dispatch`
  elige por extensión o content-type.
- **Chunking** (`chunking/`): `section_detector` reconoce cabeceras de pliego (CLÁUSULA, ANEXO,
  numeración, mayúsculas); `chunker` trocea por sección y tamaño con solape (para RAG por
  expediente, ADR 004).
- **Descarga** (`downloaders/`): httpx con límite de tamaño; mockeable.
- **Almacenamiento** (`storage/`): subida opcional del original a S3/InsForge Storage (no-op si no
  está configurado).

## API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado + formatos soportados |
| POST | `/extract` | Extrae de `url` **o** `content_base64` → `{kind, char_count, chunks}` |
| POST | `/process` | Lista de documentos → resultado por documento (ok/kind/chunk_count/error) |

```jsonc
// POST /extract
{ "content_base64": "...", "filename": "pliego.pdf" }
// o
{ "url": "https://.../PCAP.pdf" }
```

## Ejecutar

```bash
python -m venv .venv && . .venv/Scripts/activate    # Linux/mac: source .venv/bin/activate
pip install -r requirements.txt -e ../tender-shared-contracts
pip install pytest ruff fpdf2   # fpdf2 solo para generar un PDF en los tests

uvicorn tender_documents.main:app --app-dir src --reload
pytest -q          # 20 tests (extractores + chunking + downloader + API/job)
ruff check src tests
```

## Notas

- Pure-Python (sin binarios de sistema) → imagen Docker slim.
- El test de PDF sintetiza un PDF con `fpdf2` (se omite si no está instalado).
- Persistir documentos/chunks en `tender-api` requiere endpoints de documentos (siguiente
  incremento; hoy el servicio devuelve los fragmentos y, opcionalmente, guarda el original).
