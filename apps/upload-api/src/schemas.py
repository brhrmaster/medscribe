"""Schemas Pydantic para respostas da API."""
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class UploadResponse(BaseModel):
    """Resposta do endpoint de upload."""
    document_id: str = Field(..., description="UUID do documento")
    status: Literal["ACCEPTED"] = Field(..., description="Status do documento")
    tenant: str = Field(..., description="Tenant do documento")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criação")


class HealthResponse(BaseModel):
    """Resposta do health check."""
    ok: bool = Field(..., description="Status do serviço")
    service: str = Field(..., description="Nome do serviço")
    version: str = Field(..., description="Versão do serviço")

