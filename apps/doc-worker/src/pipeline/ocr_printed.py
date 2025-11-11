"""OCR para texto impresso usando Tesseract."""
import pytesseract
from PIL import Image
import logging
from ..settings import settings

logger = logging.getLogger(__name__)


def ocr_printed(img: Image.Image, lang: str = None) -> tuple[str, float]:
    """
    Extrai texto impresso de uma imagem usando Tesseract.
    
    Args:
        img: Imagem PIL
        lang: Idioma(s) para OCR (padrão das settings)
        
    Returns:
        Tupla (texto_extraído, confiança_média)
    """
    lang = lang or settings.ocr_langs
    
    try:
        # Configurações otimizadas para CPU
        config = "--oem 1 --psm 6"
        
        # Extrair texto
        text = pytesseract.image_to_string(img, lang=lang, config=config)
        
        # Extrair dados com confiança
        data = pytesseract.image_to_data(img, lang=lang, config=config, output_type=pytesseract.Output.DICT)
        
        # Calcular confiança média (ignorar valores -1)
        confidences = [float(conf) for conf in data['conf'] if float(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
        
        logger.debug(f"OCR impresso: {len(text)} caracteres, confiança média: {avg_confidence:.2f}")
        return text.strip(), avg_confidence
        
    except Exception as e:
        logger.error(f"Erro no OCR impresso: {e}")
        return "", 0.0

