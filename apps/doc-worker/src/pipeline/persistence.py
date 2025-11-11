"""Persistência de dados no PostgreSQL."""
import asyncpg
import logging
import json
from typing import List, Optional
from datetime import datetime
from ..models import MedicalReport, DocumentField
from ..settings import settings

logger = logging.getLogger(__name__)


class Persistence:
    """Gerencia persistência no PostgreSQL."""
    
    def __init__(self):
        """Inicializa conexão com banco."""
        self.conn_pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Inicializa pool de conexões."""
        try:
            self.conn_pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=2,
                max_size=10
            )
            logger.info("Pool de conexões PostgreSQL inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar pool: {e}")
            raise
    
    async def close(self):
        """Fecha pool de conexões."""
        if self.conn_pool:
            await self.conn_pool.close()
            logger.info("Pool de conexões fechado")
    
    async def update_document_status(self, document_id: str, status: str, 
                                    error_message: Optional[str] = None,
                                    pages: int = 0,
                                    processing_time: Optional[float] = None):
        """
        Atualiza status de um documento.
        
        Args:
            document_id: ID do documento
            status: Novo status
            error_message: Mensagem de erro (se houver)
            pages: Número de páginas
            processing_time: Tempo de processamento em segundos
        """
        async with self.conn_pool.acquire() as conn:
            await conn.execute("""
                UPDATE documents
                SET status = $1,
                    error_message = $2,
                    pages = $3,
                    processing_time_seconds = $4,
                    updated_at = now()
                WHERE id = $5
            """, status, error_message, pages, processing_time, document_id)
            logger.info(f"Status atualizado: {document_id} -> {status}")
    
    async def save_document_fields(self, document_id: str, fields: List[DocumentField]):
        """
        Salva campos extraídos de um documento.
        
        Args:
            document_id: ID do documento
            fields: Lista de campos extraídos
        """
        if not fields:
            return
        
        async with self.conn_pool.acquire() as conn:
            async with conn.transaction():
                for field in fields:
                    bbox_json = None
                    if field.bbox:
                        bbox_json = json.dumps({
                            "x": field.bbox.x,
                            "y": field.bbox.y,
                            "w": field.bbox.w,
                            "h": field.bbox.h
                        })
                    
                    await conn.execute("""
                        INSERT INTO document_fields 
                        (document_id, field_name, field_value, confidence, page, bbox)
                        VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                    """, document_id, field.field_name, field.field_value,
                        field.confidence, field.page, bbox_json)
        
        logger.info(f"{len(fields)} campos salvos para documento {document_id}")
    
    async def document_exists(self, document_id: str) -> bool:
        """
        Verifica se um documento existe.
        
        Args:
            document_id: ID do documento
            
        Returns:
            True se existe, False caso contrário
        """
        async with self.conn_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT 1 FROM documents WHERE id = $1",
                document_id
            )
            return row is not None
    
    async def create_document(self, document_id: str, tenant: str, object_key: str, sha256: str) -> bool:
        """
        Cria um documento na base com status RECEIVED.
        
        Args:
            document_id: ID do documento
            tenant: Tenant
            object_key: Chave do objeto no S3
            sha256: Hash SHA256
            
        Returns:
            True se criado com sucesso, False se já existe
        """
        async with self.conn_pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO documents (id, tenant, object_key, status, sha256)
                    VALUES ($1, $2, $3, 'RECEIVED', $4)
                    ON CONFLICT (id) DO NOTHING
                """, document_id, tenant, object_key, sha256)
                return True
            except Exception as e:
                logger.error(f"Erro ao criar documento {document_id}: {e}")
                return False


# Instância global
persistence = Persistence()

