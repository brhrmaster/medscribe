"""Rasterizador de PDF para imagens."""
import logging
from typing import List
from PIL import Image
import fitz  # PyMuPDF
from ..settings import settings

logger = logging.getLogger(__name__)


class Rasterizer:
    """Converte páginas de PDF em imagens."""
    
    def __init__(self, dpi: int = None):
        """
        Inicializa o rasterizador.
        
        Args:
            dpi: Resolução DPI (padrão das settings)
        """
        self.dpi = dpi or settings.raster_dpi
        self.scale = self.dpi / 72.0  # PDF padrão é 72 DPI
    
    def pdf_to_images(self, pdf_data: bytes) -> List[Image.Image]:
        """
        Converte um PDF em lista de imagens PIL.
        
        Args:
            pdf_data: Dados binários do PDF
            
        Returns:
            Lista de imagens PIL (uma por página)
        """
        images = []
        try:
            # Abrir PDF com PyMuPDF
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Renderizar página como imagem
                mat = fitz.Matrix(self.scale, self.scale)
                pix = page.get_pixmap(matrix=mat)
                # Converter para PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
                logger.debug(f"Página {page_num + 1} rasterizada: {img.size}")
            
            doc.close()
            logger.info(f"PDF convertido em {len(images)} páginas")
            return images
            
        except Exception as e:
            logger.error(f"Erro ao rasterizar PDF: {e}")
            raise


# Instância global
rasterizer = Rasterizer()

