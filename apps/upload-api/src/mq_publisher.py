"""Publicador de mensagens para RabbitMQ."""
import pika
import json
import logging
from typing import Dict, Any
from .settings import settings

logger = logging.getLogger(__name__)


class MQPublisher:
    """Publicador de mensagens para fila RabbitMQ."""
    
    def __init__(self):
        """Inicializa a conexão com RabbitMQ."""
        self.connection = None
        self.channel = None
        self.queue_name = "process_document"
        self._connect()
    
    def _connect(self):
        """Estabelece conexão com RabbitMQ."""
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(settings.rabbitmq_uri)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            logger.info(f"Conectado ao RabbitMQ, fila: {self.queue_name}")
        except Exception as e:
            logger.error(f"Erro ao conectar ao RabbitMQ: {e}")
            raise
    
    def publish_message(self, message: Dict[str, Any]) -> bool:
        """
        Publica uma mensagem na fila.
        
        Args:
            message: Dicionário com dados da mensagem
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()
            
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Torna a mensagem persistente
                )
            )
            logger.info(f"Mensagem publicada: {message.get('document_id')}")
            return True
        except Exception as e:
            logger.error(f"Erro ao publicar mensagem: {e}")
            return False
    
    def close(self):
        """Fecha a conexão."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()


# Instância global
mq_publisher = MQPublisher()

