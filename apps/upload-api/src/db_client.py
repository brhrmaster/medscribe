"""Cliente de banco de dados para Upload API."""
import asyncpg
import logging
from typing import Optional
from .settings import settings

logger = logging.getLogger(__name__)


class DbClient:
    """Cliente para operações no PostgreSQL."""
    
    def __init__(self):
        """Inicializa o cliente."""
        self.conn_pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Inicializa pool de conexões."""
        try:
            self.conn_pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=1,
                max_size=5
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
    
    async def create_document(self, document_id: str, tenant: str, object_key: str, sha256: str) -> bool:
        """
        Cria um documento na base com status RECEIVED.
        
        Args:
            document_id: ID do documento
            tenant: Tenant
            object_key: Chave do objeto no S3
            sha256: Hash SHA256
            
        Returns:
            True se criado ou já existe, False em caso de erro
        """
        async with self.conn_pool.acquire() as conn:
            try:
                result = await conn.execute("""
                    INSERT INTO documents (id, tenant, object_key, status, sha256)
                    VALUES ($1, $2, $3, 'RECEIVED', $4)
                    ON CONFLICT (id) DO NOTHING
                """, document_id, tenant, object_key, sha256)
                # INSERT retorna "INSERT 0 1" se inseriu, "INSERT 0 0" se já existia
                logger.info(f"Documento criado/verificado no banco: {document_id}")
                return True
            except Exception as e:
                logger.error(f"Erro ao criar documento {document_id}: {e}")
                return False


# Instância global
db_client = DbClient()

