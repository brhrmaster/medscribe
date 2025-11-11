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
                r'(?:paciente|nome|patient)[:\s\[\]]+([A-ZÁÉÍÓÚÇ][a-záéíóúç]+(?:\s+[A-ZÁÉÍÓÚÇ][a-záéíóúç]+)+)',
                r'nome[:\s\[\]]+([A-ZÁÉÍÓÚÇ][a-záéíóúç]+(?:\s+[A-ZÁÉÍÓÚÇ][a-záéíóúç]+)+)',
            ],
            "cpf": [
                r'CPF[:\s\[\]]*(\d{3}\.?\d{3}\.?\d{3}-?\d{2})',
                r'(\d{3}\.?\d{3}\.?\d{3}-?\d{2})',
            ],
            "crm": [
                r'CRM[:\s\[\]]*(\d+)[\s-]*([A-Z]{2})?',
            ],
            "date": [
                r'data[:\s\[\]]+(\d{2}[/-]\d{2}[/-]\d{4})',
                r'(\d{2}[/-]\d{2}[/-]\d{4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # Formato mais flexível
            ],
            "phone": [
                r'telefone[:\s\[\]]+(\(?\d{2}\)?\s?\d{4,5}-?\d{4})',
                r'(\(?\d{2}\)?\s?\d{4,5}-?\d{4})',
            ],
            "document_type": [
                r'(?:tipo|tipo\s+de\s+documento|documento)[:\s\[\]]+([A-ZÁÉÍÓÚÇ][a-záéíóúç\s]{2,50})',
                r'(ATESTADO[^-\n]{0,50}|LAUDO[^-\n]{0,50}|RECEITA[^-\n]{0,50}|EXAME[^-\n]{0,50}|RELAT[OÓ]RIO[^-\n]{0,50})',
            ],
            "institution": [
                r'(?:institui[çc][aã]o|hospital|cl[íi]nica|unidade)[:\s\[\]]+([A-ZÁÉÍÓÚÇ][a-záéíóúç\s]+)',
                r'(SECRETARIA[^-\n]+)',
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
        
        if not text or not text.strip():
            logger.warning(f"Texto vazio na página {page}, nenhum campo será extraído")
            return fields
        
        # Limpar texto: remover caracteres especiais problemáticos mas manter estrutura
        cleaned_text = re.sub(r'[^\w\s:\[\]()\-/.,]', ' ', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalizar espaços
        
        text_lower = cleaned_text.lower()
        logger.debug(f"Extraindo campos de texto com {len(cleaned_text)} caracteres na página {page}")
        
        # Mapear cada padrão
        for field_name, patterns in self.patterns.items():
            for pattern in patterns:
                try:
                    # Tentar primeiro no texto limpo, depois no original
                    match = re.search(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE)
                    if not match:
                        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                    
                    if match:
                        value = match.group(1) if match.groups() else match.group(0)
                        # Limpar valor extraído
                        value = re.sub(r'\s+', ' ', value).strip()
                        
                        # Normalizar valor conforme o tipo
                        normalized_value = self._normalize_field(field_name, value)
                        
                        if normalized_value and len(normalized_value) > 2:  # Ignorar valores muito curtos
                            fields.append(DocumentField(
                                field_name=field_name,
                                field_value=normalized_value,
                                confidence=confidence,
                                page=page
                            ))
                            logger.info(f"Campo extraído: {field_name} = {normalized_value} (página {page})")
                            break  # Usar apenas o primeiro match
                except Exception as e:
                    logger.warning(f"Erro ao processar padrão {pattern} para {field_name}: {e}")
                    continue
        
        if not fields:
            logger.warning(f"Nenhum campo encontrado na página {page}. Texto (primeiros 500 chars): {text[:500]}")
        
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
            "document_type": clean_text,
            "institution": clean_text,
        }
        
        normalizer = normalizers.get(field_name, clean_text)
        result = normalizer(value)
        return result if result else clean_text(value)


# Instância global
field_mapper = FieldMapper()

