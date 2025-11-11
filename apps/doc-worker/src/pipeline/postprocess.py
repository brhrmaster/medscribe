"""Pós-processamento e normalização de dados extraídos."""
import re
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def normalize_date(text: str) -> Optional[str]:
    """
    Normaliza data para formato DD/MM/YYYY.
    
    Args:
        text: Texto contendo data
        
    Returns:
        Data normalizada ou None
    """
    # Padrões comuns de data
    patterns = [
        r'(\d{2})[/-](\d{2})[/-](\d{4})',  # DD/MM/YYYY ou DD-MM-YYYY
        r'(\d{2})[/-](\d{2})[/-](\d{2})',   # DD/MM/YY
        r'(\d{4})[/-](\d{2})[/-](\d{2})',   # YYYY/MM/DD
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                # Tentar normalizar para DD/MM/YYYY
                try:
                    if len(groups[2]) == 2:  # YY
                        year = "20" + groups[2] if int(groups[2]) < 50 else "19" + groups[2]
                    else:
                        year = groups[2]
                    
                    # Assumir formato DD/MM/YYYY
                    return f"{groups[0]}/{groups[1]}/{year}"
                except:
                    pass
    
    return None


def normalize_cpf(text: str) -> Optional[str]:
    """
    Normaliza CPF removendo caracteres não numéricos.
    
    Args:
        text: Texto contendo CPF
        
    Returns:
        CPF normalizado (11 dígitos) ou None
    """
    # Remover tudo exceto dígitos
    digits = re.sub(r'\D', '', text)
    
    if len(digits) == 11:
        # Formatar: XXX.XXX.XXX-XX
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    
    return None


def normalize_crm(text: str) -> Optional[str]:
    """
    Normaliza CRM (Conselho Regional de Medicina).
    
    Args:
        text: Texto contendo CRM
        
    Returns:
        CRM normalizado ou None
    """
    # Padrão: CRM seguido de números e estado
    match = re.search(r'CRM[:\s]*(\d+)[\s-]*([A-Z]{2})?', text, re.IGNORECASE)
    if match:
        number = match.group(1)
        state = match.group(2) or ""
        return f"CRM {number} {state}".strip()
    
    return None


def normalize_phone(text: str) -> Optional[str]:
    """
    Normaliza telefone para formato E.164 (simplificado).
    
    Args:
        text: Texto contendo telefone
        
    Returns:
        Telefone normalizado ou None
    """
    # Remover tudo exceto dígitos
    digits = re.sub(r'\D', '', text)
    
    # Telefone brasileiro: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
    if len(digits) == 10 or len(digits) == 11:
        if len(digits) == 10:
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        else:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    
    return None


def clean_text(text: str) -> str:
    """
    Limpa e normaliza texto genérico.
    
    Args:
        text: Texto a ser limpo
        
    Returns:
        Texto limpo
    """
    # Remover espaços múltiplos
    text = re.sub(r'\s+', ' ', text)
    # Remover espaços no início/fim
    text = text.strip()
    return text

