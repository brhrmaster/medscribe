"""Pytest configuration and fixtures."""
import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Generator
import os
import sys


# Mock external dependencies before any imports
# This prevents import errors when dependencies are not installed
def _mock_external_dependencies():
    """Mock external dependencies that may not be installed."""
    # Mock boto3
    if 'boto3' not in sys.modules:
        mock_boto3 = MagicMock()
        sys.modules['boto3'] = mock_boto3
    
    # Mock asyncpg
    if 'asyncpg' not in sys.modules:
        mock_asyncpg = MagicMock()
        sys.modules['asyncpg'] = mock_asyncpg
    
    # Mock celery
    if 'celery' not in sys.modules:
        mock_celery = MagicMock()
        sys.modules['celery'] = mock_celery


# Define test environment variables before any imports
# This runs during pytest collection, before Settings() is instantiated
def pytest_configure(config):
    """Configure pytest - runs before test collection."""
    # Mock external dependencies first
    _mock_external_dependencies()
    
    test_settings = {
        'S3_ENDPOINT': 'https://nyc3.digitaloceanspaces.com',
        'S3_REGION': 'nyc3',
        'S3_BUCKET': 'test-bucket',
        'S3_ACCESS_KEY': 'test-access-key',
        'S3_SECRET_KEY': 'test-secret-key',
        'RABBITMQ_URI': 'amqp://test:test@localhost:5672//',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/testdb',
        'TENANT_DEFAULT': 'test-tenant',
        'APP_NAME': 'medscribe-upload-api',
        'APP_VERSION': '1.0.0',
        'MAX_FILE_SIZE_MB': '50',
        'ALLOWED_CONTENT_TYPES': '["application/pdf"]'
    }
    
    # Set environment variables before any module imports
    for key, value in test_settings.items():
        os.environ[key] = str(value)


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Mock settings for testing - auto-use to ensure settings are available."""
    test_settings = {
        'S3_ENDPOINT': 'https://nyc3.digitaloceanspaces.com',
        'S3_REGION': 'nyc3',
        'S3_BUCKET': 'test-bucket',
        'S3_ACCESS_KEY': 'test-access-key',
        'S3_SECRET_KEY': 'test-secret-key',
        'RABBITMQ_URI': 'amqp://test:test@localhost:5672//',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/testdb',
        'TENANT_DEFAULT': 'test-tenant',
        'APP_NAME': 'medscribe-upload-api',
        'APP_VERSION': '1.0.0',
        'MAX_FILE_SIZE_MB': '50',
        'ALLOWED_CONTENT_TYPES': '["application/pdf"]'
    }
    
    for key, value in test_settings.items():
        monkeypatch.setenv(key, str(value))
    
    return test_settings


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    # Minimal valid PDF header
    return b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 0\ntrailer\n<< /Root 1 0 R >>\n%%EOF'


@pytest.fixture
def sample_upload_file(sample_pdf_content):
    """Mock UploadFile for testing."""
    mock_file = Mock()
    mock_file.filename = "test.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.read = AsyncMock(return_value=sample_pdf_content)
    mock_file.size = len(sample_pdf_content)
    return mock_file

