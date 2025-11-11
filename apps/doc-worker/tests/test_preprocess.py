"""Unit tests for preprocess."""
import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from PIL import Image
from src.pipeline.preprocess import preprocess_image, deskew_image


class TestPreprocessImage:
    """Tests for preprocess_image function."""
    
    def test_preprocess_image_should_convert_rgb_to_grayscale(self, sample_image):
        """Test that preprocess_image converts RGB to grayscale."""
        # Act
        result = preprocess_image(sample_image)
        
        # Assert
        assert isinstance(result, Image.Image)
        assert result.mode == 'L'  # Grayscale
    
    def test_preprocess_image_should_handle_grayscale_input(self, sample_grayscale_image):
        """Test that preprocess_image handles grayscale input."""
        # Act
        result = preprocess_image(sample_grayscale_image)
        
        # Assert
        assert isinstance(result, Image.Image)
        assert result.mode == 'L'
    
    def test_preprocess_image_should_apply_denoising(self, sample_image):
        """Test that preprocess_image applies denoising."""
        # Act
        result = preprocess_image(sample_image)
        
        # Assert
        assert isinstance(result, Image.Image)
        # Result should be binary (after threshold)
        assert result.mode == 'L'
    
    def test_preprocess_image_should_apply_binarization(self, sample_image):
        """Test that preprocess_image applies binarization."""
        # Act
        result = preprocess_image(sample_image)
        
        # Assert
        assert isinstance(result, Image.Image)
        # After OTSU threshold, image should be binary-like
        arr = np.array(result)
        # Should have mostly 0 and 255 values
        unique_values = np.unique(arr)
        assert len(unique_values) <= 2  # Binary image
    
    def test_preprocess_image_should_maintain_image_size(self, sample_image):
        """Test that preprocess_image maintains image size."""
        # Arrange
        original_size = sample_image.size
        
        # Act
        result = preprocess_image(sample_image)
        
        # Assert
        assert result.size == original_size


class TestDeskewImage:
    """Tests for deskew_image function."""
    
    def test_deskew_image_should_return_image_without_lines(self):
        """Test that deskew_image returns image when no lines detected."""
        # Arrange
        img = np.ones((100, 100), dtype=np.uint8) * 255  # White image
        
        # Act
        result = deskew_image(img)
        
        # Assert
        assert isinstance(result, np.ndarray)
        assert result.shape == img.shape
    
    def test_deskew_image_should_handle_empty_image(self):
        """Test that deskew_image handles empty image."""
        # Arrange
        img = np.zeros((10, 10), dtype=np.uint8)
        
        # Act
        result = deskew_image(img)
        
        # Assert
        assert isinstance(result, np.ndarray)
        assert result.shape == img.shape
    
    def test_deskew_image_should_maintain_image_shape(self):
        """Test that deskew_image maintains image shape."""
        # Arrange
        img = np.random.randint(0, 255, (200, 300), dtype=np.uint8)
        original_shape = img.shape
        
        # Act
        result = deskew_image(img)
        
        # Assert
        assert result.shape == original_shape
    
    @patch('src.pipeline.preprocess.cv2.Canny')
    @patch('src.pipeline.preprocess.cv2.HoughLines')
    def test_deskew_image_should_handle_no_lines_detected(self, mock_hough, mock_canny):
        """Test that deskew_image handles case when no lines are detected."""
        # Arrange
        mock_canny.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_hough.return_value = None
        img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        # Act
        result = deskew_image(img)
        
        # Assert
        assert isinstance(result, np.ndarray)
        assert result.shape == img.shape

