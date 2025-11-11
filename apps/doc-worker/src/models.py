"""Modelos Pydantic para validação de dados extraídos."""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime


class BoundingBox(BaseModel):
    """Caixa delimitadora de um campo."""
    x: float = Field(..., ge=0, description="Coordenada X")
    y: float = Field(..., ge=0, description="Coordenada Y")
    w: float = Field(..., gt=0, description="Largura")
    h: float = Field(..., gt=0, description="Altura")


class DocumentField(BaseModel):
    """Campo extraído de um documento."""
    field_name: str = Field(..., description="Nome do campo")
    field_value: Optional[str] = Field(None, description="Valor extraído")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confiança (0-1)")
    page: Optional[int] = Field(None, ge=1, description="Número da página")
    bbox: Optional[BoundingBox] = Field(None, description="Caixa delimitadora")


class MedicalReport(BaseModel):
    """Estrutura de um laudo médico processado."""
    document_id: str = Field(..., description="ID do documento")
    tenant: str = Field(..., description="Tenant")
    fields: list[DocumentField] = Field(default_factory=list, description="Campos extraídos")
    pages: int = Field(0, ge=0, description="Número de páginas")
    model_version: str = Field(..., description="Versão do modelo usado")
    processing_time_seconds: Optional[float] = Field(None, description="Tempo de processamento")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "123e4567-e89b-12d3-a456-426614174000",
                "tenant": "default",
                "fields": [
                    {
                        "field_name": "patient_name",
                        "field_value": "João Silva",
                        "confidence": 0.95,
                        "page": 1,
                        "bbox": {"x": 100, "y": 200, "w": 150, "h": 20}
                    }
                ],
                "pages": 1,
                "model_version": "1.0.0"
            }
        }

