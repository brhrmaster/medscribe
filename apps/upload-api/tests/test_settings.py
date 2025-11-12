"""Unit tests for settings."""
import pytest
from unittest.mock import patch
from pydantic import ValidationError
from src.settings import Settings


class TestSettings:
    """Tests for Settings configuration."""
    
    def test_settings_should_load_from_environment(self, mock_settings):
        """Test that Settings loads values from environment variables."""
        # Arrange - mock_settings fixture sets environment variables
        
        # Act
        with patch.dict('os.environ', {
            'S3_ENDPOINT': 'https://test.endpoint.com',
            'S3_BUCKET': 'test-bucket',
            'S3_ACCESS_KEY': 'test-key',
            'S3_SECRET_KEY': 'test-secret',
            'RABBITMQ_URI': 'amqp://test:test@localhost:5672//',
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test'
        }):
            settings = Settings()
        
        # Assert
        assert settings.s3_endpoint == 'https://test.endpoint.com'
        assert settings.s3_bucket == 'test-bucket'
        assert settings.s3_access_key == 'test-key'
        assert settings.s3_secret_key == 'test-secret'
        assert settings.rabbitmq_uri == 'amqp://test:test@localhost:5672//'
        assert settings.database_url == 'postgresql://test:test@localhost:5432/test'
    
    def test_settings_should_have_default_values(self, monkeypatch):
        """Test that Settings has correct default values."""
        # Arrange
        env_vars = {
            'S3_ENDPOINT': 'https://test.endpoint.com',
            'S3_BUCKET': 'test-bucket',
            'S3_ACCESS_KEY': 'test-key',
            'S3_SECRET_KEY': 'test-secret',
            'RABBITMQ_URI': 'amqp://test:test@localhost:5672//',
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test'
        }
        
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        
        # Remove variables that have defaults to test default values
        monkeypatch.delenv('TENANT_DEFAULT', raising=False)
        monkeypatch.delenv('APP_NAME', raising=False)
        monkeypatch.delenv('APP_VERSION', raising=False)
        monkeypatch.delenv('MAX_FILE_SIZE_MB', raising=False)
        monkeypatch.delenv('ALLOWED_CONTENT_TYPES', raising=False)
        
        # Act
        settings = Settings()
        
        # Assert
        assert settings.s3_region == "nyc3"
        assert settings.tenant_default == "default"
        assert settings.app_name == "medscribe-upload-api"
        assert settings.app_version == "1.0.0"
        assert settings.max_file_size_mb == 50
        assert settings.allowed_content_types == [
            "application/pdf",
            "image/png",
            "image/jpeg",
            "image/jpg",
        ]
    
    def test_settings_should_require_required_fields(self, monkeypatch):
        """Test that Settings requires all mandatory fields."""
        # Arrange - Clear all environment variables
        required_vars = ['S3_ENDPOINT', 'S3_BUCKET', 'S3_ACCESS_KEY', 'S3_SECRET_KEY', 
                         'RABBITMQ_URI', 'DATABASE_URL']
        for var in required_vars:
            monkeypatch.delenv(var, raising=False)
        
        # Act & Assert
        with pytest.raises(ValidationError):
            Settings()  # Missing required fields
    
    def test_settings_should_accept_custom_max_file_size(self, monkeypatch):
        """Test that max_file_size_mb can be customized."""
        # Arrange
        env_vars = {
            'S3_ENDPOINT': 'https://test.endpoint.com',
            'S3_BUCKET': 'test-bucket',
            'S3_ACCESS_KEY': 'test-key',
            'S3_SECRET_KEY': 'test-secret',
            'RABBITMQ_URI': 'amqp://test:test@localhost:5672//',
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
            'MAX_FILE_SIZE_MB': '100'
        }
        
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        
        # Act
        settings = Settings()
        
        # Assert
        assert settings.max_file_size_mb == 100
    
    def test_settings_should_have_pdf_in_allowed_content_types(self, monkeypatch):
        """Test that allowed_content_types includes PDF by default."""
        # Arrange
        env_vars = {
            'S3_ENDPOINT': 'https://test.endpoint.com',
            'S3_BUCKET': 'test-bucket',
            'S3_ACCESS_KEY': 'test-key',
            'S3_SECRET_KEY': 'test-secret',
            'RABBITMQ_URI': 'amqp://test:test@localhost:5672//',
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test'
        }
        
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        
        # Act
        settings = Settings()
        
        # Assert - default behavior
        assert "application/pdf" in settings.allowed_content_types

