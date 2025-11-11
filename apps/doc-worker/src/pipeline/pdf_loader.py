"""Carregador de PDFs do S3."""
import hashlib
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Tuple
from ..settings import settings

logger = logging.getLogger(__name__)


class PDFLoader:
    """Carrega PDFs do DigitalOcean Spaces."""
    
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
    
    def download_pdf(self, object_key: str) -> Optional[bytes]:
        """
        Baixa um PDF do Spaces.
        
        Args:
            object_key: Chave do objeto no S3
            
        Returns:
            Dados binários do PDF ou None em caso de erro
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=object_key)
            data = response['Body'].read()
            logger.info(f"PDF baixado: {object_key} ({len(data)} bytes)")
            return data
        except ClientError as e:
            logger.error(f"Erro ao baixar PDF {object_key}: {e}")
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


# Instância global
pdf_loader = PDFLoader()

