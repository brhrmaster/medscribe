"""HTR para texto manuscrito usando TrOCR (ONNX)."""
import logging
from PIL import Image
from typing import Optional
from ..settings import settings

logger = logging.getLogger(__name__)


def htr_handwritten(img: Image.Image) -> tuple[str, float]:
    """
    Extrai texto manuscrito de uma imagem usando TrOCR via ONNX.
    
    Nota: Implementação placeholder. Requer exportação prévia do modelo TrOCR para ONNX.
    
    Args:
        img: Imagem PIL
        
    Returns:
        Tupla (texto_extraído, confiança)
    """
    if not settings.htr_onnx_enable:
        logger.debug("HTR ONNX desabilitado")
        return "", 0.0
    
    try:
        # TODO: Implementar carregamento do modelo ONNX
        # TODO: Preprocessar imagem para o formato esperado pelo modelo
        # TODO: Executar inferência ONNX
        # TODO: Decodificar tokens para texto
        # TODO: Calcular confiança
        
        logger.warning("HTR ONNX não implementado ainda - retornando placeholder")
        return "", 0.0
        
    except Exception as e:
        logger.error(f"Erro no HTR manuscrito: {e}")
        return "", 0.0


def load_onnx_model(model_path: str):
    """
    Carrega modelo TrOCR ONNX.
    
    Args:
        model_path: Caminho para o arquivo .onnx
    """
    # TODO: Implementar carregamento do modelo
    pass

