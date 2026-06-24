"""Almacenamiento de objetos S3-compatible (MinIO / InsForge Storage), opcional.

Si no está configurado (o falta boto3), `store` devuelve None y el servicio sigue funcionando:
la extracción de texto no requiere almacenar el original.
"""

from __future__ import annotations

from tender_documents.config import settings


def is_configured() -> bool:
    return bool(
        settings.storage_endpoint and settings.storage_bucket and settings.storage_access_key
    )


def store(key: str, data: bytes, content_type: str | None = None) -> str | None:
    """Sube el objeto y devuelve su clave, o None si el almacenamiento no está disponible."""
    if not is_configured():
        return None
    try:
        import boto3  # import perezoso: dependencia opcional
    except ImportError:
        return None

    client = boto3.client(
        "s3",
        endpoint_url=settings.storage_endpoint,
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key,
    )
    extra = {"ContentType": content_type} if content_type else {}
    client.put_object(Bucket=settings.storage_bucket, Key=key, Body=data, **extra)
    return key
