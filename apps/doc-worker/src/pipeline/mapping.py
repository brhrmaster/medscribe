"""Mapeamento de texto extraído para estruturas definidas."""
import re
import logging
from typing import List, Dict, Any
from ..models import DocumentField, BoundingBox
from .postprocess import normalize_date, normalize_cpf, normalize_crm, normalize_phone, clean_text

logger = logging.getLogger(__name__)


class FieldMapper:
    """Mapeia texto extraído para campos estruturados."""
    
    def __init__(self):
        """Inicializa o mapeador com padrões conhecidos."""
        # Padrões de regex para campos comuns
        self.patterns = {
            "patient_name": [
                r'(?:paciente|nome)[:\s]+([A-ZÁÉÍÓÚÇ][a-záéíóúç]+(?:\s+[A-ZÁÉÍÓÚÇ][a-záéíóúç]+)+)',
                r'nome[:\s]+([A-ZÁÉÍÓÚÇ][a-záéíóúç]+(?:\s+[A-ZÁÉÍÓÚÇ][a-záéíóúç]+)+)',
            ],
            "cpf": [
                r'CPF[:\s]*(\d{3}\.?\d{3}\.?\d{3}-?\d{2})',
                r'(\d{3}\.?\d{3}\.?\d{3}-?\d{2})',
            ],
            "crm": [
                r'CRM[:\s]*(\d+)[\s-]*([A-Z]{2})?',
            ],
            "date": [
                r'data[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})',
                r'(\d{2}[/-]\d{2}[/-]\d{4})',
            ],
            "phone": [
                r'telefone[:\s]+(\(?\d{2}\)?\s?\d{4,5}-?\d{4})',
                r'(\(?\d{2}\)?\s?\d{4,5}-?\d{4})',
            ],
        }
    
    def extract_fields(self, text: str, page: int = 1, confidence: float = 0.8) -> List[DocumentField]:
        """
        Extrai campos estruturados de um texto.
        
        Args:
            text: Texto extraído via OCR/HTR
            page: Número da página
            confidence: Confiança base do OCR
            
        Returns:
            Lista de campos extraídos
        """
        fields = []
        text_lower = text.lower()
        
        # Mapear cada padrão
        for field_name, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)
                    
                    # Normalizar valor conforme o tipo
                    normalized_value = self._normalize_field(field_name, value)
                    
                    if normalized_value:
                        fields.append(DocumentField(
                            field_name=field_name,
                            field_value=normalized_value,
                            confidence=confidence,
                            page=page
                        ))
                        logger.debug(f"Campo extraído: {field_name} = {normalized_value}")
                        break  # Usar apenas o primeiro match
        
        return fields
    
    def _normalize_field(self, field_name: str, value: str) -> str:
        """
        Normaliza um valor de campo conforme seu tipo.
        
        Args:
            field_name: Nome do campo
            value: Valor bruto
            
        Returns:
            Valor normalizado
        """
        normalizers = {
            "patient_name": clean_text,
            "cpf": normalize_cpf,
            "crm": normalize_crm,
            "date": normalize_date,
            "phone": normalize_phone,
        }
        
        normalizer = normalizers.get(field_name, clean_text)
        result = normalizer(value)
        return result if result else clean_text(value)


# Instância global
field_mapper = FieldMapper()

