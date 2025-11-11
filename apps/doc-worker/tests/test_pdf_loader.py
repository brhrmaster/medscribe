"""Unit tests for PDFLoader."""
import pytest
from unittest.mock import Mock, patch
import sys

# Mock ClientError if botocore is not available
try:
    from botocore.exceptions import ClientError
except ImportError:
    class ClientError(Exception):
        def __init__(self, error_response, operation_name):
            self.error_response = error_response
            self.operation_name = operation_name
            super().__init__(f"{operation_name}: {error_response}")


class TestPDFLoader:
    """Tests for PDFLoader."""
    
    def test_pdf_loader_should_initialize_with_settings(self):
        """Test that PDFLoader initializes with correct settings."""
        # Arrange
        mock_s3_client = Mock()
        
        if 'src.pipeline.pdf_loader' in sys.modules:
            del sys.modules['src.pipeline.pdf_loader']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.pdf_loader.boto3') as mock_boto3:
            mock_boto3.client.return_value = mock_s3_client
            from src.pipeline.pdf_loader import PDFLoader
            
            # Act
            loader = PDFLoader()
            
            # Assert
            assert loader.s3_client == mock_s3_client
            assert loader.bucket == 'test-bucket'
            mock_boto3.client.assert_called_once()
    
    def test_download_pdf_should_return_pdf_data(self, sample_pdf_content):
        """Test successful PDF download."""
        # Arrange
        mock_s3_client = Mock()
        mock_body = Mock()
        mock_body.read.return_value = sample_pdf_content
        mock_response = {'Body': mock_body}
        mock_s3_client.get_object.return_value = mock_response
        
        if 'src.pipeline.pdf_loader' in sys.modules:
            del sys.modules['src.pipeline.pdf_loader']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.pdf_loader.boto3') as mock_boto3:
            mock_boto3.client.return_value = mock_s3_client
            from src.pipeline.pdf_loader import PDFLoader
            loader = PDFLoader()
            
            # Act
            result = loader.download_pdf("test-tenant/test-doc.pdf")
            
            # Assert
            assert result == sample_pdf_content
            mock_s3_client.get_object.assert_called_once_with(
                Bucket='test-bucket',
                Key="test-tenant/test-doc.pdf"
            )
    
    def test_download_pdf_should_return_none_on_error(self):
        """Test that download_pdf returns None on error."""
        # Arrange
        mock_s3_client = Mock()
        mock_s3_client.get_object.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'Key not found'}},
            'GetObject'
        )
        
        if 'src.pipeline.pdf_loader' in sys.modules:
            del sys.modules['src.pipeline.pdf_loader']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.pdf_loader.boto3') as mock_boto3:
            mock_boto3.client.return_value = mock_s3_client
            from src.pipeline.pdf_loader import PDFLoader
            loader = PDFLoader()
            
            # Act
            result = loader.download_pdf("test-tenant/nonexistent.pdf")
            
            # Assert
            assert result is None
    
    def test_calculate_sha256_should_return_hex_digest(self, sample_pdf_content):
        """Test that calculate_sha256 returns correct hash."""
        # Arrange
        if 'src.pipeline.pdf_loader' in sys.modules:
            del sys.modules['src.pipeline.pdf_loader']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.pdf_loader.boto3'):
            from src.pipeline.pdf_loader import PDFLoader
            loader = PDFLoader()
            
            # Act
            result = loader.calculate_sha256(sample_pdf_content)
            
            # Assert
            assert isinstance(result, str)
            assert len(result) == 64  # SHA256 hex digest is 64 chars
            # Verify it's the same for same input
            result2 = loader.calculate_sha256(sample_pdf_content)
            assert result == result2
    
    def test_validate_pdf_should_return_true_for_valid_pdf(self, sample_pdf_content):
        """Test that validate_pdf returns True for valid PDF."""
        # Arrange
        if 'src.pipeline.pdf_loader' in sys.modules:
            del sys.modules['src.pipeline.pdf_loader']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.pdf_loader.boto3'):
            from src.pipeline.pdf_loader import PDFLoader
            loader = PDFLoader()
            
            # Act
            is_valid, error_msg = loader.validate_pdf(sample_pdf_content)
            
            # Assert
            assert is_valid is True
            assert error_msg is None
    
    def test_validate_pdf_should_return_false_for_too_small(self):
        """Test that validate_pdf returns False for too small file."""
        # Arrange
        small_data = b'PDF'
        
        if 'src.pipeline.pdf_loader' in sys.modules:
            del sys.modules['src.pipeline.pdf_loader']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.pdf_loader.boto3'):
            from src.pipeline.pdf_loader import PDFLoader
            loader = PDFLoader()
            
            # Act
            is_valid, error_msg = loader.validate_pdf(small_data)
            
            # Assert
            assert is_valid is False
            assert error_msg == "Arquivo muito pequeno"
    
    def test_validate_pdf_should_return_false_for_invalid_header(self):
        """Test that validate_pdf returns False for invalid PDF header."""
        # Arrange
        invalid_data = b'NOTAPDF1234567890'
        
        if 'src.pipeline.pdf_loader' in sys.modules:
            del sys.modules['src.pipeline.pdf_loader']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.pdf_loader.boto3'):
            from src.pipeline.pdf_loader import PDFLoader
            loader = PDFLoader()
            
            # Act
            is_valid, error_msg = loader.validate_pdf(invalid_data)
            
            # Assert
            assert is_valid is False
            assert error_msg == "Arquivo não é um PDF válido"

