"""Unit tests for MQPublisher."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys


class TestMQPublisher:
    """Tests for MQPublisher."""
    
    def test_mq_publisher_should_initialize_celery(self):
        """Test that MQPublisher initializes Celery with correct settings."""
        # Arrange
        mock_celery_app = Mock()
        
        if 'src.mq_publisher' in sys.modules:
            del sys.modules['src.mq_publisher']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.mq_publisher.Celery', create=True) as mock_celery:
            mock_celery.return_value = mock_celery_app
            from src.mq_publisher import MQPublisher
            
            # Act
            publisher = MQPublisher()
            
            # Assert
            mock_celery.assert_called_once()
            call_kwargs = mock_celery.call_args[1]
            assert call_kwargs['broker'] == 'amqp://test:test@localhost:5672//'
            assert call_kwargs['backend'] == 'rpc://'
            assert publisher.celery_app == mock_celery_app
            mock_celery_app.conf.update.assert_called_once()
    
    def test_publish_message_should_send_task(self):
        """Test successful message publishing."""
        # Arrange
        mock_celery_app = Mock()
        
        if 'src.mq_publisher' in sys.modules:
            del sys.modules['src.mq_publisher']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.mq_publisher.Celery', create=True) as mock_celery:
            mock_celery.return_value = mock_celery_app
            from src.mq_publisher import MQPublisher
            publisher = MQPublisher()
            
            message = {
                "document_id": "123e4567-e89b-12d3-a456-426614174000",
                "tenant": "test-tenant",
                "object_key": "test-tenant/test-doc.pdf",
                "sha256": "abc123def456",
                "file_size": 1024,
                "content_type": "application/pdf"
            }
            
            # Act
            result = publisher.publish_message(message)
            
            # Assert
            assert result is True
            mock_celery_app.send_task.assert_called_once_with(
                'process_document',
                args=[message],
                queue='process_document',
            )
    
    def test_publish_message_should_return_false_on_error(self):
        """Test that publish_message returns False on error."""
        # Arrange
        mock_celery_app = Mock()
        mock_celery_app.send_task.side_effect = Exception("Connection error")
        
        if 'src.mq_publisher' in sys.modules:
            del sys.modules['src.mq_publisher']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.mq_publisher.Celery', create=True) as mock_celery:
            mock_celery.return_value = mock_celery_app
            from src.mq_publisher import MQPublisher
            publisher = MQPublisher()
            
            message = {
                "document_id": "test-id",
                "tenant": "test-tenant",
                "object_key": "test-tenant/test-doc.pdf",
                "sha256": "abc123def456"
            }
            
            # Act
            result = publisher.publish_message(message)
            
            # Assert
            assert result is False
    
    def test_close_should_not_raise(self):
        """Test that close method does not raise exceptions."""
        # Arrange
        mock_celery_app = Mock()
        
        if 'src.mq_publisher' in sys.modules:
            del sys.modules['src.mq_publisher']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.mq_publisher.Celery', create=True) as mock_celery:
            mock_celery.return_value = mock_celery_app
            from src.mq_publisher import MQPublisher
            publisher = MQPublisher()
            
            # Act & Assert (should not raise)
            publisher.close()
