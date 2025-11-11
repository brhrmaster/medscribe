"""Publicador de mensagens para RabbitMQ usando Celery."""
from celery import Celery
import logging
from typing import Dict, Any
from .settings import settings

logger = logging.getLogger(__name__)


class MQPublisher:
    """Publicador de mensagens para fila RabbitMQ via Celery."""
    
    def __init__(self):
        """Inicializa o cliente Celery."""
        self.celery_app = Celery(
            'upload_api',
            broker=settings.rabbitmq_uri,
            backend='rpc://',
        )
        self.celery_app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            task_default_queue='process_document',
            task_routes={
                'process_document': {'queue': 'process_document'},
            },
        )
        logger.info("Cliente Celery inicializado")
    
    def publish_message(self, message: Dict[str, Any]) -> bool:
        """
        Publica uma mensagem na fila via Celery.
        
        Args:
            message: Dicionário com dados da mensagem
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Chamar a task do worker
            self.celery_app.send_task(
                'process_document',
                args=[message],
                queue='process_document',
            )
            logger.info(f"Task enfileirada: {message.get('document_id')}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enfileirar task: {e}")
            return False
    
    def close(self):
        """Cleanup (não necessário para Celery client)."""
        pass


# Instância global
mq_publisher = MQPublisher()

