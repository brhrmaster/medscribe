"""Cliente S3 para DigitalOcean Spaces."""
import boto3
from botocore.exceptions import ClientError
from typing import Optional
import logging
from .settings import settings

logger = logging.getLogger(__name__)


class S3Client:
    """Cliente para operações no DigitalOcean Spaces (S3-compatible)."""
    
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
    
    def put_object(self, key: str, data: bytes, content_type: str = "application/pdf") -> bool:
        """
        Armazena um objeto no Spaces.
        
        Args:
            key: Chave do objeto (caminho)
            data: Dados binários do arquivo
            content_type: Tipo MIME do conteúdo
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type
            )
            logger.info(f"Arquivo armazenado com sucesso: {key}")
            return True
        except ClientError as e:
            logger.error(f"Erro ao armazenar arquivo {key}: {e}")
            return False
    
    def get_object(self, key: str) -> Optional[bytes]:
        """
        Recupera um objeto do Spaces.
        
        Args:
            key: Chave do objeto
            
        Returns:
            Dados binários ou None em caso de erro
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Erro ao recuperar arquivo {key}: {e}")
            return None


# Instância global
s3_client = S3Client()

