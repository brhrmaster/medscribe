"""Configurações da aplicação Upload API."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""
    
    # S3 / DigitalOcean Spaces
    s3_endpoint: str
    s3_region: str = "nyc3"
    s3_bucket: str
    s3_access_key: str
    s3_secret_key: str
    
    # RabbitMQ
    rabbitmq_uri: str
    
    # PostgreSQL
    database_url: str
    
    # App
    tenant_default: str = "default"
    app_name: str = "medscribe-upload-api"
    app_version: str = "1.0.0"
    
    # Upload limits
    max_file_size_mb: int = 50
    allowed_content_types: list[str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instância global
settings = Settings()

