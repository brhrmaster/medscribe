"""Unit tests for ocr_printed."""
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
import sys


class TestOCRPrinted:
    """Tests for ocr_printed function."""
    
    def test_ocr_printed_should_return_text_and_confidence(self, sample_image):
        """Test that ocr_printed returns text and confidence."""
        # Arrange
        if 'src.pipeline.ocr_printed' in sys.modules:
            del sys.modules['src.pipeline.ocr_printed']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.ocr_printed.pytesseract') as mock_pytesseract:
            mock_pytesseract.image_to_string.return_value = "Sample text"
            mock_pytesseract.image_to_data.return_value = {
                'conf': ['-1', '95', '90', '88']
            }
            mock_pytesseract.Output.DICT = MagicMock()
            
            with patch('src.pipeline.ocr_printed.settings') as mock_settings:
                mock_settings.ocr_langs = "por+eng"
                from src.pipeline.ocr_printed import ocr_printed
                
                # Act
                text, confidence = ocr_printed(sample_image)
                
                # Assert
                assert text == "Sample text"
                assert 0.0 <= confidence <= 1.0
                mock_pytesseract.image_to_string.assert_called_once()
                mock_pytesseract.image_to_data.assert_called_once()
    
    def test_ocr_printed_should_use_custom_lang(self, sample_image):
        """Test that ocr_printed uses custom language."""
        # Arrange
        if 'src.pipeline.ocr_printed' in sys.modules:
            del sys.modules['src.pipeline.ocr_printed']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.ocr_printed.pytesseract') as mock_pytesseract:
            mock_pytesseract.image_to_string.return_value = "Texto"
            mock_pytesseract.image_to_data.return_value = {'conf': ['95']}
            mock_pytesseract.Output.DICT = MagicMock()
            
            with patch('src.pipeline.ocr_printed.settings'):
                from src.pipeline.ocr_printed import ocr_printed
                
                # Act
                ocr_printed(sample_image, lang="por")
                
                # Assert
                call_kwargs = mock_pytesseract.image_to_string.call_args[1]
                assert call_kwargs['lang'] == "por"
    
    @patch('src.pipeline.ocr_printed.pytesseract')
    def test_ocr_printed_should_handle_empty_text(self, mock_pytesseract, sample_image):
        """Test that ocr_printed handles empty text."""
        # Arrange
        mock_pytesseract.image_to_string.return_value = ""
        mock_pytesseract.image_to_data.return_value = {'conf': []}
        mock_pytesseract.Output.DICT = MagicMock()
        
        if 'src.pipeline.ocr_printed' in sys.modules:
            del sys.modules['src.pipeline.ocr_printed']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.ocr_printed.settings'):
            from src.pipeline.ocr_printed import ocr_printed
            
            # Act
            text, confidence = ocr_printed(sample_image)
            
            # Assert
            assert text == ""
            assert confidence == 0.0
    
    @patch('src.pipeline.ocr_printed.pytesseract')
    def test_ocr_printed_should_handle_exception(self, mock_pytesseract, sample_image):
        """Test that ocr_printed handles exceptions gracefully."""
        # Arrange
        mock_pytesseract.image_to_string.side_effect = Exception("OCR error")
        
        if 'src.pipeline.ocr_printed' in sys.modules:
            del sys.modules['src.pipeline.ocr_printed']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.ocr_printed.settings'):
            from src.pipeline.ocr_printed import ocr_printed
            
            # Act
            text, confidence = ocr_printed(sample_image)
            
            # Assert
            assert text == ""
            assert confidence == 0.0
    
    def test_ocr_printed_should_calculate_average_confidence(self, sample_image):
        """Test that ocr_printed calculates average confidence correctly."""
        # Arrange
        if 'src.pipeline.ocr_printed' in sys.modules:
            del sys.modules['src.pipeline.ocr_printed']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.ocr_printed.pytesseract') as mock_pytesseract:
            mock_pytesseract.image_to_string.return_value = "Text"
            mock_pytesseract.image_to_data.return_value = {
                'conf': ['95', '90', '85', '80']  # Average should be ~0.875
            }
            mock_pytesseract.Output.DICT = MagicMock()
            
            with patch('src.pipeline.ocr_printed.settings'):
                from src.pipeline.ocr_printed import ocr_printed
                
                # Act
                text, confidence = ocr_printed(sample_image)
                
                # Assert
                assert confidence == pytest.approx(0.875, abs=0.01)

