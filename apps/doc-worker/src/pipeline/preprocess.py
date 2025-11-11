"""Pré-processamento de imagens."""
import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def preprocess_image(img: Image.Image) -> Image.Image:
    """
    Pré-processa uma imagem: deskew, denoise, binarização.
    
    Args:
        img: Imagem PIL
        
    Returns:
        Imagem PIL processada
    """
    # Converter PIL para OpenCV (BGR)
    arr = np.array(img)
    if len(arr.shape) == 3:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    
    # Converter para escala de cinza
    if len(arr.shape) == 3:
        gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    else:
        gray = arr
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, h=15, templateWindowSize=7, searchWindowSize=21)
    
    # Binarização adaptativa (OTSU)
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Deskew (opcional - pode ser custoso)
    # binary = deskew_image(binary)
    
    # Converter de volta para PIL
    return Image.fromarray(binary)


def deskew_image(img: np.ndarray) -> np.ndarray:
    """
    Corrige inclinação (skew) da imagem.
    
    Args:
        img: Imagem em escala de cinza (numpy array)
        
    Returns:
        Imagem corrigida
    """
    # Detectar linhas usando Hough Transform
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    
    if lines is None or len(lines) == 0:
        return img
    
    # Calcular ângulo médio
    angles = []
    for rho, theta in lines[:20]:  # Limitar a 20 linhas
        angle = (theta * 180 / np.pi) - 90
        if abs(angle) < 45:  # Ignorar ângulos muito grandes
            angles.append(angle)
    
    if not angles:
        return img
    
    angle = np.median(angles)
    
    # Rotacionar imagem
    if abs(angle) > 0.5:  # Só rotacionar se necessário
        center = (img.shape[1] // 2, img.shape[0] // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        img = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), 
                            flags=cv2.INTER_CUBIC, 
                            borderMode=cv2.BORDER_REPLICATE)
        logger.debug(f"Imagem rotacionada em {angle:.2f} graus")
    
    return img

