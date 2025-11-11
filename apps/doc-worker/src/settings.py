"""Configurações da aplicação Doc Worker."""
from pydantic_settings import BaseSettings


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
    
    # Pipeline
    raster_dpi: int = 300
    ocr_langs: str = "por+eng"
    htr_onnx_enable: bool = False
    confidence_threshold: float = 0.8
    model_version: str = "1.0.0"
    
    # Worker
    worker_concurrency: int = 4
    task_acks_late: bool = True
    task_reject_on_worker_lost: bool = True
    task_max_retries: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instância global
settings = Settings()

