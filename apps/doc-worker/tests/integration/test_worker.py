"""Integration tests for worker."""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
from PIL import Image


class TestProcessDocument:
    """Tests for process_document Celery task."""
    
    @patch('src.worker.persistence')
    @patch('src.worker.field_mapper')
    @patch('src.worker.htr_handwritten')
    @patch('src.worker.ocr_printed')
    @patch('src.worker.preprocess_image')
    @patch('src.worker.rasterizer')
    @patch('src.worker.file_loader')
    @patch('src.worker.Celery')
    def test_process_document_should_process_successfully(
        self, mock_celery, mock_file_loader, mock_rasterizer, mock_preprocess,
        mock_ocr, mock_htr, mock_field_mapper, mock_persistence, sample_pdf_content
    ):
        """Test successful document processing."""
        # Arrange
        mock_celery_app = Mock()
        mock_celery.return_value = mock_celery_app
        
        # Mock file loader - need to patch the instance, not the class
        mock_file_loader_instance = Mock()
        mock_file_loader_instance.download_pdf.return_value = sample_pdf_content
        mock_file_loader_instance.validate_pdf.return_value = (True, None)
        mock_file_loader_instance.calculate_sha256.return_value = "test-sha256"
        mock_file_loader_instance.get_file_type.return_value = 'pdf'
        # Patch the module-level instance
        mock_file_loader.file_loader = mock_file_loader_instance
        
        # Mock rasterizer - need to patch the instance
        mock_rasterizer_instance = Mock()
        test_image = Image.new('RGB', (100, 100), color='white')
        mock_rasterizer_instance.pdf_to_images.return_value = [test_image]
        mock_rasterizer.rasterizer = mock_rasterizer_instance
        
        # Mock preprocess
        mock_preprocess.return_value = test_image
        
        # Mock OCR
        mock_ocr.return_value = ("Sample text", 0.9)
        
        # Mock HTR
        mock_htr.return_value = ("", 0.0)
        
        # Mock field mapper - need to patch the instance
        mock_field_mapper_instance = Mock()
        from src.models import DocumentField
        mock_field_mapper_instance.extract_fields.return_value = [
            DocumentField(field_name="patient_name", field_value="João Silva", confidence=0.9, page=1)
        ]
        mock_field_mapper.field_mapper = mock_field_mapper_instance
        
        # Mock persistence - need to patch the instance
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        mock_pool = Mock()
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_persistence_instance = Mock()
        mock_persistence_instance.conn_pool = mock_pool
        mock_persistence_instance.create_document = AsyncMock(return_value=True)
        mock_persistence_instance.document_exists = AsyncMock(return_value=False)
        mock_persistence_instance.update_document_status = AsyncMock()
        mock_persistence_instance.save_document_fields = AsyncMock()
        mock_persistence_instance.initialize = AsyncMock()
        mock_persistence.persistence = mock_persistence_instance
        
        # Clean up modules
        modules_to_remove = [
            'src.worker',
            'src.settings',
            'src.pipeline.file_loader',
            'src.pipeline.pdf_loader',
            'src.pipeline.rasterizer',
            'src.pipeline.persistence',
            'src.pipeline.htr_handwritten',
            'src.pipeline.ocr_printed',
            'src.pipeline.preprocess',
            'src.pipeline.mapping'
        ]
        for mod in modules_to_remove:
            if mod in sys.modules:
                del sys.modules[mod]
        
        # Mock onnxruntime before importing worker
        with patch.dict('sys.modules', {
            'onnxruntime': MagicMock(),
            'transformers': MagicMock()
        }):
            with patch('src.worker.settings') as mock_settings:
                mock_settings.rabbitmq_uri = 'amqp://test:test@localhost:5672//'
                mock_settings.task_acks_late = True
                mock_settings.task_reject_on_worker_lost = True
                
                # Import after all mocks are set up
                import src.worker as worker_module
                # Replace the imported instances with our mocks
                worker_module.file_loader = mock_file_loader_instance
                worker_module.rasterizer = mock_rasterizer_instance
                worker_module.field_mapper = mock_field_mapper_instance
                worker_module.persistence = mock_persistence_instance
                # Set persistence.conn_pool with proper async context manager support
                worker_module.persistence.conn_pool = mock_pool
                # Mock ensure_persistence_initialized to prevent real DB connection
                worker_module.ensure_persistence_initialized = Mock()
            
                message = {
                    'document_id': 'test-doc-id',
                    'tenant': 'test-tenant',
                    'object_key': 'test-tenant/test-doc.pdf',
                    'sha256': 'test-sha256',
                    'content_type': 'application/pdf'
                }
                
                # Create a mock task instance - process_document is bound, so self is the task
                mock_task = Mock()
                mock_request = Mock()
                mock_request.retries = 0
                mock_task.request = mock_request
                mock_task.max_retries = 3
                mock_task.retry = Mock(side_effect=Exception("Should not retry"))
                
                # Act - Call .run() with just the message; Celery provides self automatically
                # We need to set the task instance on the task object
                worker_module.process_document._get_current_object = Mock(return_value=mock_task)
                result = worker_module.process_document.run(message)
                
                # Assert
                assert result['status'] == 'success'
                assert result['document_id'] == 'test-doc-id'
                assert result['pages'] == 1
                assert result['fields_count'] == 1
                assert 'processing_time' in result
    
    @patch('src.worker.persistence')
    @patch('src.worker.file_loader')
    @patch('src.worker.Celery')
    def test_process_document_should_handle_pdf_download_error(
        self, mock_celery, mock_file_loader, mock_persistence
    ):
        """Test that process_document handles PDF download error."""
        # Arrange
        mock_celery_app = Mock()
        mock_celery.return_value = mock_celery_app
        
        mock_file_loader_instance = Mock()
        mock_file_loader_instance.download_pdf.return_value = None
        mock_file_loader_instance.get_file_type.return_value = 'pdf'
        mock_file_loader.file_loader = mock_file_loader_instance
        
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        mock_pool = Mock()
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_persistence_instance = Mock()
        mock_persistence_instance.conn_pool = mock_pool
        mock_persistence_instance.create_document = AsyncMock(return_value=True)
        mock_persistence_instance.document_exists = AsyncMock(return_value=False)
        mock_persistence_instance.update_document_status = AsyncMock()
        mock_persistence.persistence = mock_persistence_instance
        
        if 'src.worker' in sys.modules:
            del sys.modules['src.worker']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        if 'src.pipeline.file_loader' in sys.modules:
            del sys.modules['src.pipeline.file_loader']
        if 'src.pipeline.pdf_loader' in sys.modules:
            del sys.modules['src.pipeline.pdf_loader']
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        
        with patch('src.worker.settings') as mock_settings:
            mock_settings.rabbitmq_uri = 'amqp://test:test@localhost:5672//'
            mock_settings.task_acks_late = True
            mock_settings.task_reject_on_worker_lost = True
            import src.worker as worker_module
            # Replace the imported instances with our mocks
            worker_module.file_loader = mock_file_loader_instance
            worker_module.persistence = mock_persistence_instance
            worker_module.persistence.conn_pool = mock_pool
            worker_module.ensure_persistence_initialized = Mock()
            
            message = {
                'document_id': 'test-doc-id',
                'tenant': 'test-tenant',
                'object_key': 'test-tenant/test-doc.pdf',
                'sha256': 'test-sha256',
                'content_type': 'application/pdf'
            }
            
            mock_task = Mock()
            mock_request = Mock()
            mock_request.retries = 0
            mock_task.request = mock_request
            mock_task.max_retries = 3
            mock_task.retry = Mock(side_effect=Exception("Retry called"))
            
            # Act & Assert
            worker_module.process_document._get_current_object = Mock(return_value=mock_task)
            # The function will raise "Erro ao baixar PDF do S3" which triggers retry
            with pytest.raises(Exception):
                worker_module.process_document.run(message)
    
    @patch('src.worker.persistence')
    @patch('src.worker.file_loader')
    @patch('src.worker.Celery')
    def test_process_document_should_handle_invalid_pdf(
        self, mock_celery, mock_file_loader, mock_persistence, sample_pdf_content
    ):
        """Test that process_document handles invalid PDF."""
        # Arrange
        mock_celery_app = Mock()
        mock_celery.return_value = mock_celery_app
        
        mock_file_loader_instance = Mock()
        mock_file_loader_instance.download_pdf.return_value = sample_pdf_content
        mock_file_loader_instance.validate_pdf.return_value = (False, "Invalid PDF")
        mock_file_loader_instance.get_file_type.return_value = 'pdf'
        mock_file_loader.file_loader = mock_file_loader_instance
        
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        mock_pool = Mock()
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_persistence_instance = Mock()
        mock_persistence_instance.conn_pool = mock_pool
        mock_persistence_instance.create_document = AsyncMock(return_value=True)
        mock_persistence_instance.document_exists = AsyncMock(return_value=False)
        mock_persistence_instance.update_document_status = AsyncMock()
        mock_persistence.persistence = mock_persistence_instance
        
        if 'src.worker' in sys.modules:
            del sys.modules['src.worker']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        if 'src.pipeline.file_loader' in sys.modules:
            del sys.modules['src.pipeline.file_loader']
        if 'src.pipeline.pdf_loader' in sys.modules:
            del sys.modules['src.pipeline.pdf_loader']
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        
        with patch('src.worker.settings') as mock_settings:
            mock_settings.rabbitmq_uri = 'amqp://test:test@localhost:5672//'
            mock_settings.task_acks_late = True
            mock_settings.task_reject_on_worker_lost = True
            import src.worker as worker_module
            # Replace the imported instances with our mocks
            worker_module.file_loader = mock_file_loader_instance
            worker_module.persistence = mock_persistence_instance
            worker_module.persistence.conn_pool = mock_pool
            worker_module.ensure_persistence_initialized = Mock()
            
            message = {
                'document_id': 'test-doc-id',
                'tenant': 'test-tenant',
                'object_key': 'test-tenant/test-doc.pdf',
                'sha256': 'test-sha256',
                'content_type': 'application/pdf'
            }
            
            mock_task = Mock()
            mock_request = Mock()
            mock_request.retries = 0
            mock_task.request = mock_request
            mock_task.max_retries = 3
            mock_task.retry = Mock(side_effect=Exception("Retry called"))
            
            # Act & Assert
            worker_module.process_document._get_current_object = Mock(return_value=mock_task)
            # The function will raise "Erro ao baixar PDF do S3" which triggers retry
            with pytest.raises(Exception):
                worker_module.process_document.run(message)

