from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "tender-document-service"
    version: str = "0.1.0"

    api_url: str = "http://localhost:8000"

    # Chunking
    chunk_size: int = 1200
    chunk_overlap: int = 150
    max_download_bytes: int = 25 * 1024 * 1024  # 25 MB

    # Almacenamiento de objetos (opcional, S3-compatible / InsForge Storage).
    storage_endpoint: str = ""
    storage_bucket: str = ""
    storage_access_key: str = ""
    storage_secret_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
