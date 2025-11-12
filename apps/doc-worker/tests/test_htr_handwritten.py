"""Unit tests for htr_handwritten."""
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
import sys


class TestHTRHandwritten:
    """Tests for htr_handwritten function."""
    
    def test_htr_handwritten_should_return_empty_when_disabled(self, sample_image):
        """Test that htr_handwritten returns empty when ONNX is disabled."""
        # Arrange
        if 'src.pipeline.htr_handwritten' in sys.modules:
            del sys.modules['src.pipeline.htr_handwritten']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        # Mock onnxruntime before import
        with patch.dict('sys.modules', {
            'onnxruntime': MagicMock(),
            'transformers': MagicMock()
        }):
            with patch('src.pipeline.htr_handwritten.settings') as mock_settings:
                mock_settings.htr_onnx_enable = False
                from src.pipeline.htr_handwritten import htr_handwritten
                
                # Act
                text, confidence = htr_handwritten(sample_image)
                
                # Assert
                assert text == ""
                assert confidence == 0.0
    
    def test_htr_handwritten_should_return_empty_when_enabled_but_not_implemented(self, sample_image):
        """Test that htr_handwritten returns empty when enabled but not implemented."""
        # Arrange
        if 'src.pipeline.htr_handwritten' in sys.modules:
            del sys.modules['src.pipeline.htr_handwritten']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        # Mock onnxruntime before import
        with patch.dict('sys.modules', {
            'onnxruntime': MagicMock(),
            'transformers': MagicMock()
        }):
            with patch('src.pipeline.htr_handwritten.settings') as mock_settings:
                mock_settings.htr_onnx_enable = True
                from src.pipeline.htr_handwritten import htr_handwritten
                
                # Mock file not found to simulate models not available
                with patch('src.pipeline.htr_handwritten.os.path.exists', return_value=False):
                    # Act
                    text, confidence = htr_handwritten(sample_image)
                    
                    # Assert
                    # Returns empty when models not found
                    assert text == ""
                    assert confidence == 0.0
    
    def test_htr_handwritten_should_handle_exception(self, sample_image):
        """Test that htr_handwritten handles exceptions gracefully."""
        # Arrange
        if 'src.pipeline.htr_handwritten' in sys.modules:
            del sys.modules['src.pipeline.htr_handwritten']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        # Mock onnxruntime before import
        with patch.dict('sys.modules', {
            'onnxruntime': MagicMock(),
            'transformers': MagicMock()
        }):
            with patch('src.pipeline.htr_handwritten.settings') as mock_settings:
                mock_settings.htr_onnx_enable = True
                # Simulate an exception during processing
                with patch('src.pipeline.htr_handwritten.logger') as mock_logger:
                    from src.pipeline.htr_handwritten import htr_handwritten
                    
                    # Mock file not found to trigger exception handling
                    with patch('src.pipeline.htr_handwritten.os.path.exists', return_value=False):
                        # Act
                        text, confidence = htr_handwritten(sample_image)
                        
                        # Assert
                        assert text == ""
                        assert confidence == 0.0

