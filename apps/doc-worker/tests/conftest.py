"""Pytest configuration and fixtures."""
import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Generator
import os
import sys
from PIL import Image
import numpy as np


# Define test environment variables before any imports
# This runs during pytest collection, before Settings() is instantiated
def pytest_configure(config):
    """Configure pytest - runs before test collection."""
    test_settings = {
        'S3_ENDPOINT': 'https://nyc3.digitaloceanspaces.com',
        'S3_REGION': 'nyc3',
        'S3_BUCKET': 'test-bucket',
        'S3_ACCESS_KEY': 'test-access-key',
        'S3_SECRET_KEY': 'test-secret-key',
        'RABBITMQ_URI': 'amqp://test:test@localhost:5672//',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/testdb',
        'RASTER_DPI': '300',
        'OCR_LANGS': 'por+eng',
        'HTR_ONNX_ENABLE': 'false',
        'CONFIDENCE_THRESHOLD': '0.8',
        'MODEL_VERSION': '1.0.0',
        'WORKER_CONCURRENCY': '4',
        'TASK_ACKS_LATE': 'true',
        'TASK_REJECT_ON_WORKER_LOST': 'true',
        'TASK_MAX_RETRIES': '3'
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
        'RASTER_DPI': '300',
        'OCR_LANGS': 'por+eng',
        'HTR_ONNX_ENABLE': 'false',
        'CONFIDENCE_THRESHOLD': '0.8',
        'MODEL_VERSION': '1.0.0',
        'WORKER_CONCURRENCY': '4',
        'TASK_ACKS_LATE': 'true',
        'TASK_REJECT_ON_WORKER_LOST': 'true',
        'TASK_MAX_RETRIES': '3'
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
def sample_image():
    """Sample PIL Image for testing."""
    # Create a simple test image (100x100 RGB)
    img = Image.new('RGB', (100, 100), color='white')
    return img


@pytest.fixture
def sample_grayscale_image():
    """Sample grayscale PIL Image for testing."""
    # Create a simple test grayscale image (100x100)
    img = Image.new('L', (100, 100), color=255)
    return img


@pytest.fixture
def sample_numpy_array():
    """Sample numpy array for testing."""
    return np.array([[255, 255, 255], [0, 0, 0], [128, 128, 128]], dtype=np.uint8)

