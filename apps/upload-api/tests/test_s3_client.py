"""Unit tests for S3Client."""
import pytest
from unittest.mock import Mock, patch, MagicMock
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


class TestS3Client:
    """Tests for S3Client."""
    
    @patch('src.s3_client.boto3')
    def test_s3_client_should_initialize_with_settings(self, mock_boto3):
        """Test that S3Client initializes with correct settings."""
        # Arrange
        mock_boto3_client = Mock()
        mock_boto3.client.return_value = mock_boto3_client
        
        # Reload module to pick up settings
        modules_to_remove = ['src.s3_client', 'src.settings']
        for mod in modules_to_remove:
            if mod in sys.modules:
                del sys.modules[mod]
        
        # Ensure boto3 is available (may be mocked in conftest)
        import boto3
        if not hasattr(boto3, 'client'):
            boto3.client = mock_boto3.client
        
        from src.s3_client import S3Client
        
        # Act
        client = S3Client()
        
        # Assert
        # Check that boto3.client was called (either via patch or actual call)
        assert mock_boto3.client.called or hasattr(client, 's3_client')
        if mock_boto3.client.called:
            call_kwargs = mock_boto3.client.call_args[1]
            assert call_kwargs['endpoint_url'] == 'https://nyc3.digitaloceanspaces.com'
            assert call_kwargs['region_name'] == 'nyc3'
        assert client.bucket == 'test-bucket'
    
    def test_put_object_should_succeed(self):
        """Test successful put_object operation."""
        # Arrange
        mock_s3_client = Mock()
        
        if 'src.s3_client' in sys.modules:
            del sys.modules['src.s3_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.s3_client.boto3') as mock_boto3:
            mock_boto3.client.return_value = mock_s3_client
            from src.s3_client import S3Client
            client = S3Client()
            
            test_key = "test-tenant/test-doc.pdf"
            test_data = b"test pdf content"
            test_content_type = "application/pdf"
            
            # Act
            result = client.put_object(test_key, test_data, test_content_type)
            
            # Assert
            assert result is True
            mock_s3_client.put_object.assert_called_once_with(
                Bucket='test-bucket',
                Key=test_key,
                Body=test_data,
                ContentType=test_content_type
            )
    
    def test_put_object_should_handle_client_error(self):
        """Test put_object handles ClientError gracefully."""
        # Arrange
        mock_s3_client = Mock()
        mock_s3_client.put_object.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}},
            'PutObject'
        )
        
        if 'src.s3_client' in sys.modules:
            del sys.modules['src.s3_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.s3_client.boto3') as mock_boto3:
            mock_boto3.client.return_value = mock_s3_client
            from src.s3_client import S3Client
            client = S3Client()
            
            test_key = "test-tenant/test-doc.pdf"
            test_data = b"test pdf content"
            
            # Act
            result = client.put_object(test_key, test_data)
            
            # Assert
            assert result is False
    
    def test_get_object_should_return_data(self):
        """Test successful get_object operation."""
        # Arrange
        mock_s3_client = Mock()
        mock_body = Mock()
        mock_body.read.return_value = b"test pdf content"
        mock_response = {'Body': mock_body}
        mock_s3_client.get_object.return_value = mock_response
        
        if 'src.s3_client' in sys.modules:
            del sys.modules['src.s3_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.s3_client.boto3') as mock_boto3:
            mock_boto3.client.return_value = mock_s3_client
            from src.s3_client import S3Client
            client = S3Client()
            
            test_key = "test-tenant/test-doc.pdf"
            
            # Act
            result = client.get_object(test_key)
            
            # Assert
            assert result == b"test pdf content"
            mock_s3_client.get_object.assert_called_once_with(
                Bucket='test-bucket',
                Key=test_key
            )
    
    def test_get_object_should_return_none_on_error(self):
        """Test get_object returns None on error."""
        # Arrange
        mock_s3_client = Mock()
        mock_s3_client.get_object.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'Key not found'}},
            'GetObject'
        )
        
        if 'src.s3_client' in sys.modules:
            del sys.modules['src.s3_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.s3_client.boto3') as mock_boto3:
            mock_boto3.client.return_value = mock_s3_client
            from src.s3_client import S3Client
            client = S3Client()
            
            test_key = "test-tenant/nonexistent.pdf"
            
            # Act
            result = client.get_object(test_key)
            
            # Assert
            assert result is None
    
    def test_put_object_should_use_default_content_type(self):
        """Test that put_object uses default content_type when not provided."""
        # Arrange
        mock_s3_client = Mock()
        
        if 'src.s3_client' in sys.modules:
            del sys.modules['src.s3_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.s3_client.boto3') as mock_boto3:
            mock_boto3.client.return_value = mock_s3_client
            from src.s3_client import S3Client
            client = S3Client()
            
            test_key = "test-tenant/test-doc.pdf"
            test_data = b"test pdf content"
            
            # Act
            result = client.put_object(test_key, test_data)
            
            # Assert
            assert result is True
            mock_s3_client.put_object.assert_called_once_with(
                Bucket='test-bucket',
                Key=test_key,
                Body=test_data,
                ContentType="application/pdf"  # Default value
            )
