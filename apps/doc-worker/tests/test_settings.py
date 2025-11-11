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
        monkeypatch.delenv('S3_REGION', raising=False)
        monkeypatch.delenv('RASTER_DPI', raising=False)
        monkeypatch.delenv('OCR_LANGS', raising=False)
        monkeypatch.delenv('HTR_ONNX_ENABLE', raising=False)
        monkeypatch.delenv('CONFIDENCE_THRESHOLD', raising=False)
        monkeypatch.delenv('MODEL_VERSION', raising=False)
        monkeypatch.delenv('WORKER_CONCURRENCY', raising=False)
        monkeypatch.delenv('TASK_ACKS_LATE', raising=False)
        monkeypatch.delenv('TASK_REJECT_ON_WORKER_LOST', raising=False)
        monkeypatch.delenv('TASK_MAX_RETRIES', raising=False)
        
        # Act
        settings = Settings()
        
        # Assert
        assert settings.s3_region == "nyc3"
        assert settings.raster_dpi == 300
        assert settings.ocr_langs == "por+eng"
        assert settings.htr_onnx_enable is False
        assert settings.confidence_threshold == 0.8
        assert settings.model_version == "1.0.0"
        assert settings.worker_concurrency == 4
        assert settings.task_acks_late is True
        assert settings.task_reject_on_worker_lost is True
        assert settings.task_max_retries == 3
    
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
    
    def test_settings_should_accept_custom_raster_dpi(self, monkeypatch):
        """Test that raster_dpi can be customized."""
        # Arrange
        env_vars = {
            'S3_ENDPOINT': 'https://test.endpoint.com',
            'S3_BUCKET': 'test-bucket',
            'S3_ACCESS_KEY': 'test-key',
            'S3_SECRET_KEY': 'test-secret',
            'RABBITMQ_URI': 'amqp://test:test@localhost:5672//',
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
            'RASTER_DPI': '400'
        }
        
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        
        # Act
        settings = Settings()
        
        # Assert
        assert settings.raster_dpi == 400
    
    def test_settings_should_accept_custom_htr_onnx_enable(self, monkeypatch):
        """Test that htr_onnx_enable can be customized."""
        # Arrange
        env_vars = {
            'S3_ENDPOINT': 'https://test.endpoint.com',
            'S3_BUCKET': 'test-bucket',
            'S3_ACCESS_KEY': 'test-key',
            'S3_SECRET_KEY': 'test-secret',
            'RABBITMQ_URI': 'amqp://test:test@localhost:5672//',
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
            'HTR_ONNX_ENABLE': 'true'
        }
        
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        
        # Act
        settings = Settings()
        
        # Assert
        assert settings.htr_onnx_enable is True

