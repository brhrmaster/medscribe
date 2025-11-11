"""Unit tests for models."""
import pytest
from pydantic import ValidationError
from src.models import BoundingBox, DocumentField, MedicalReport


class TestBoundingBox:
    """Tests for BoundingBox model."""
    
    def test_bounding_box_should_have_required_fields(self):
        """Test that BoundingBox requires all fields."""
        # Arrange & Act
        bbox = BoundingBox(x=10.0, y=20.0, w=100.0, h=50.0)
        
        # Assert
        assert bbox.x == 10.0
        assert bbox.y == 20.0
        assert bbox.w == 100.0
        assert bbox.h == 50.0
    
    def test_bounding_box_should_reject_negative_x(self):
        """Test that BoundingBox rejects negative x."""
        # Act & Assert
        with pytest.raises(ValidationError):
            BoundingBox(x=-1.0, y=20.0, w=100.0, h=50.0)
    
    def test_bounding_box_should_reject_negative_y(self):
        """Test that BoundingBox rejects negative y."""
        # Act & Assert
        with pytest.raises(ValidationError):
            BoundingBox(x=10.0, y=-1.0, w=100.0, h=50.0)
    
    def test_bounding_box_should_reject_zero_width(self):
        """Test that BoundingBox rejects zero or negative width."""
        # Act & Assert
        with pytest.raises(ValidationError):
            BoundingBox(x=10.0, y=20.0, w=0.0, h=50.0)
    
    def test_bounding_box_should_reject_zero_height(self):
        """Test that BoundingBox rejects zero or negative height."""
        # Act & Assert
        with pytest.raises(ValidationError):
            BoundingBox(x=10.0, y=20.0, w=100.0, h=0.0)
    
    def test_bounding_box_should_accept_zero_coordinates(self):
        """Test that BoundingBox accepts zero x and y coordinates."""
        # Arrange & Act
        bbox = BoundingBox(x=0.0, y=0.0, w=100.0, h=50.0)
        
        # Assert
        assert bbox.x == 0.0
        assert bbox.y == 0.0


class TestDocumentField:
    """Tests for DocumentField model."""
    
    def test_document_field_should_have_required_field_name(self):
        """Test that DocumentField requires field_name."""
        # Arrange & Act
        field = DocumentField(field_name="patient_name")
        
        # Assert
        assert field.field_name == "patient_name"
        assert field.field_value is None
        assert field.confidence is None
        assert field.page is None
        assert field.bbox is None
    
    def test_document_field_should_accept_all_fields(self):
        """Test that DocumentField accepts all optional fields."""
        # Arrange
        bbox = BoundingBox(x=10.0, y=20.0, w=100.0, h=50.0)
        
        # Act
        field = DocumentField(
            field_name="patient_name",
            field_value="João Silva",
            confidence=0.95,
            page=1,
            bbox=bbox
        )
        
        # Assert
        assert field.field_name == "patient_name"
        assert field.field_value == "João Silva"
        assert field.confidence == 0.95
        assert field.page == 1
        assert field.bbox == bbox
    
    def test_document_field_should_reject_confidence_above_one(self):
        """Test that DocumentField rejects confidence > 1.0."""
        # Act & Assert
        with pytest.raises(ValidationError):
            DocumentField(field_name="test", confidence=1.5)
    
    def test_document_field_should_reject_confidence_below_zero(self):
        """Test that DocumentField rejects confidence < 0.0."""
        # Act & Assert
        with pytest.raises(ValidationError):
            DocumentField(field_name="test", confidence=-0.1)
    
    def test_document_field_should_reject_page_zero(self):
        """Test that DocumentField rejects page < 1."""
        # Act & Assert
        with pytest.raises(ValidationError):
            DocumentField(field_name="test", page=0)
    
    def test_document_field_should_accept_page_one(self):
        """Test that DocumentField accepts page = 1."""
        # Arrange & Act
        field = DocumentField(field_name="test", page=1)
        
        # Assert
        assert field.page == 1


class TestMedicalReport:
    """Tests for MedicalReport model."""
    
    def test_medical_report_should_have_required_fields(self):
        """Test that MedicalReport requires document_id, tenant, and model_version."""
        # Arrange & Act
        report = MedicalReport(
            document_id="123e4567-e89b-12d3-a456-426614174000",
            tenant="test-tenant",
            model_version="1.0.0"
        )
        
        # Assert
        assert report.document_id == "123e4567-e89b-12d3-a456-426614174000"
        assert report.tenant == "test-tenant"
        assert report.model_version == "1.0.0"
        assert report.fields == []
        assert report.pages == 0
        assert report.processing_time_seconds is None
    
    def test_medical_report_should_accept_all_fields(self):
        """Test that MedicalReport accepts all fields."""
        # Arrange
        field = DocumentField(field_name="patient_name", field_value="João Silva")
        
        # Act
        report = MedicalReport(
            document_id="123e4567-e89b-12d3-a456-426614174000",
            tenant="test-tenant",
            model_version="1.0.0",
            fields=[field],
            pages=2,
            processing_time_seconds=5.5
        )
        
        # Assert
        assert len(report.fields) == 1
        assert report.fields[0] == field
        assert report.pages == 2
        assert report.processing_time_seconds == 5.5
    
    def test_medical_report_should_reject_negative_pages(self):
        """Test that MedicalReport rejects negative pages."""
        # Act & Assert
        with pytest.raises(ValidationError):
            MedicalReport(
                document_id="123e4567-e89b-12d3-a456-426614174000",
                tenant="test-tenant",
                model_version="1.0.0",
                pages=-1
            )
    
    def test_medical_report_should_accept_zero_pages(self):
        """Test that MedicalReport accepts zero pages."""
        # Arrange & Act
        report = MedicalReport(
            document_id="123e4567-e89b-12d3-a456-426614174000",
            tenant="test-tenant",
            model_version="1.0.0",
            pages=0
        )
        
        # Assert
        assert report.pages == 0

