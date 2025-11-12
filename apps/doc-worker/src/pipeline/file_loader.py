"""Carregador de arquivos (PDFs e imagens) do S3."""
import hashlib
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Tuple
from PIL import Image
import io
from ..settings import settings

logger = logging.getLogger(__name__)


class FileLoader:
    """Carrega arquivos (PDFs e imagens) do DigitalOcean Spaces."""
    
    def __init__(self):
        """Inicializa o cliente S3."""
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.s3_endpoint,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key
        )
        self.bucket = settings.s3_bucket
    
    def download_file(self, object_key: str) -> Optional[bytes]:
        """
        Baixa um arquivo do Spaces.
        
        Args:
            object_key: Chave do objeto no S3
            
        Returns:
            Dados binários do arquivo ou None em caso de erro
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=object_key)
            data = response['Body'].read()
            logger.info(f"Arquivo baixado: {object_key} ({len(data)} bytes)")
            return data
        except ClientError as e:
            logger.error(f"Erro ao baixar arquivo {object_key}: {e}")
            return None
    
    def download_pdf(self, object_key: str) -> Optional[bytes]:
        """
        Baixa um PDF do Spaces (método de compatibilidade).
        
        Args:
            object_key: Chave do objeto no S3
            
        Returns:
            Dados binários do PDF ou None em caso de erro
        """
        return self.download_file(object_key)
    
    def download_image(self, object_key: str) -> Optional[Image.Image]:
        """
        Baixa uma imagem do Spaces e retorna como PIL Image.
        
        Args:
            object_key: Chave do objeto no S3
            
        Returns:
            Imagem PIL ou None em caso de erro
        """
        data = self.download_file(object_key)
        if not data:
            return None
        
        try:
            img = Image.open(io.BytesIO(data))
            # Converter para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')
            logger.info(f"Imagem carregada: {object_key} ({img.size})")
            return img
        except Exception as e:
            logger.error(f"Erro ao carregar imagem {object_key}: {e}")
            return None
    
    def calculate_sha256(self, data: bytes) -> str:
        """
        Calcula o hash SHA256 dos dados.
        
        Args:
            data: Dados binários
            
        Returns:
            Hash SHA256 em hexadecimal
        """
        return hashlib.sha256(data).hexdigest()
    
    def is_pdf(self, data: bytes) -> bool:
        """
        Verifica se os dados são um PDF.
        
        Args:
            data: Dados binários
            
        Returns:
            True se for PDF, False caso contrário
        """
        if len(data) < 4:
            return False
        return data[:4].startswith(b'%PDF')
    
    def is_image(self, data: bytes) -> bool:
        """
        Verifica se os dados são uma imagem (PNG, JPEG).
        
        Args:
            data: Dados binários
            
        Returns:
            True se for imagem, False caso contrário
        """
        if len(data) < 8:
            return False
        
        # PNG signature: 89 50 4E 47 0D 0A 1A 0A
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return True
        
        # JPEG signature: FF D8 FF
        if data[:3] == b'\xff\xd8\xff':
            return True
        
        return False
    
    def validate_pdf(self, data: bytes) -> Tuple[bool, Optional[str]]:
        """
        Valida se os dados são um PDF válido.
        
        Args:
            data: Dados binários
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if len(data) < 4:
            return False, "Arquivo muito pequeno"
        
        # Verificar assinatura PDF (%PDF)
        if not data[:4].startswith(b'%PDF'):
            return False, "Arquivo não é um PDF válido"
        
        return True, None
    
    def validate_image(self, data: bytes) -> Tuple[bool, Optional[str]]:
        """
        Valida se os dados são uma imagem válida (PNG ou JPEG).
        
        Args:
            data: Dados binários
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if len(data) < 8:
            return False, "Arquivo muito pequeno"
        
        # Verificar PNG
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return True, None
        
        # Verificar JPEG
        if data[:3] == b'\xff\xd8\xff':
            return True, None
        
        return False, "Arquivo não é uma imagem válida (PNG ou JPEG)"
    
    def get_file_type(self, object_key: str) -> Optional[str]:
        """
        Determina o tipo de arquivo baseado na extensão.
        
        Args:
            object_key: Chave do objeto no S3
            
        Returns:
            'pdf', 'image' ou None se não reconhecido
        """
        ext = object_key.lower().split('.')[-1]
        if ext == 'pdf':
            return 'pdf'
        elif ext in ['png', 'jpg', 'jpeg']:
            return 'image'
        return None


# Instância global
file_loader = FileLoader()

# Alias para compatibilidade
pdf_loader = file_loader

