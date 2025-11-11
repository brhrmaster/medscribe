"""Unit tests for schemas."""
import pytest
from datetime import datetime
from src.schemas import UploadResponse, HealthResponse


class TestUploadResponse:
    """Tests for UploadResponse schema."""
    
    def test_upload_response_should_have_required_fields(self):
        """Test that UploadResponse has all required fields."""
        # Arrange
        document_id = "123e4567-e89b-12d3-a456-426614174000"
        tenant = "test-tenant"
        
        # Act
        response = UploadResponse(
            document_id=document_id,
            status="ACCEPTED",
            tenant=tenant
        )
        
        # Assert
        assert response.document_id == document_id
        assert response.status == "ACCEPTED"
        assert response.tenant == tenant
        assert isinstance(response.created_at, datetime)
    
    def test_upload_response_should_auto_generate_created_at(self):
        """Test that created_at is automatically generated."""
        # Arrange & Act
        response1 = UploadResponse(
            document_id="id1",
            status="ACCEPTED",
            tenant="tenant1"
        )
        
        import time
        time.sleep(0.01)  # Small delay to ensure different timestamps
        
        response2 = UploadResponse(
            document_id="id2",
            status="ACCEPTED",
            tenant="tenant2"
        )
        
        # Assert
        assert response1.created_at < response2.created_at
    
    def test_upload_response_should_accept_custom_created_at(self):
        """Test that created_at can be explicitly set."""
        # Arrange
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        
        # Act
        response = UploadResponse(
            document_id="test-id",
            status="ACCEPTED",
            tenant="test-tenant",
            created_at=custom_time
        )
        
        # Assert
        assert response.created_at == custom_time
    
    def test_upload_response_status_must_be_accepted(self):
        """Test that status must be 'ACCEPTED'."""
        # Arrange & Act
        response = UploadResponse(
            document_id="test-id",
            status="ACCEPTED",
            tenant="test-tenant"
        )
        
        # Assert
        assert response.status == "ACCEPTED"
        
        # Test that other values are not allowed (Pydantic validation)
        with pytest.raises(Exception):  # Pydantic validation error
            UploadResponse(
                document_id="test-id",
                status="INVALID",
                tenant="test-tenant"
            )


class TestHealthResponse:
    """Tests for HealthResponse schema."""
    
    def test_health_response_should_have_required_fields(self):
        """Test that HealthResponse has all required fields."""
        # Arrange
        service = "medscribe-upload-api"
        version = "1.0.0"
        
        # Act
        response = HealthResponse(
            ok=True,
            service=service,
            version=version
        )
        
        # Assert
        assert response.ok is True
        assert response.service == service
        assert response.version == version
    
    def test_health_response_should_accept_false_ok(self):
        """Test that ok can be False."""
        # Arrange & Act
        response = HealthResponse(
            ok=False,
            service="test-service",
            version="1.0.0"
        )
        
        # Assert
        assert response.ok is False
    
    def test_health_response_should_validate_field_types(self):
        """Test that HealthResponse validates field types."""
        # Test with invalid types should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            HealthResponse(
                ok="not-a-boolean",
                service="test",
                version="1.0.0"
            )


