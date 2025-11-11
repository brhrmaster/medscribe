"""Unit tests for rasterizer."""
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
import sys


class TestRasterizer:
    """Tests for Rasterizer."""
    
    def test_rasterizer_should_initialize_with_default_dpi(self):
        """Test that Rasterizer initializes with default DPI."""
        # Arrange
        if 'src.pipeline.rasterizer' in sys.modules:
            del sys.modules['src.pipeline.rasterizer']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.rasterizer.settings') as mock_settings:
            mock_settings.raster_dpi = 300
            from src.pipeline.rasterizer import Rasterizer
            
            # Act
            rasterizer = Rasterizer()
            
            # Assert
            assert rasterizer.dpi == 300
            assert rasterizer.scale == pytest.approx(300.0 / 72.0)
    
    def test_rasterizer_should_initialize_with_custom_dpi(self):
        """Test that Rasterizer initializes with custom DPI."""
        # Arrange
        if 'src.pipeline.rasterizer' in sys.modules:
            del sys.modules['src.pipeline.rasterizer']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.rasterizer.settings'):
            from src.pipeline.rasterizer import Rasterizer
            
            # Act
            rasterizer = Rasterizer(dpi=400)
            
            # Assert
            assert rasterizer.dpi == 400
            assert rasterizer.scale == pytest.approx(400.0 / 72.0)
    
    def test_pdf_to_images_should_return_list_of_images(self, sample_pdf_content):
        """Test that pdf_to_images returns list of PIL Images."""
        # Arrange
        if 'src.pipeline.rasterizer' in sys.modules:
            del sys.modules['src.pipeline.rasterizer']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.rasterizer.fitz') as mock_fitz:
            mock_doc = MagicMock()
            mock_page = MagicMock()
            mock_pix = MagicMock()
            mock_pix.width = 100
            mock_pix.height = 100
            mock_pix.samples = b'\x00' * (100 * 100 * 3)  # RGB bytes
            mock_page.get_pixmap.return_value = mock_pix
            mock_doc.__len__.return_value = 1
            mock_doc.__getitem__.return_value = mock_page
            mock_fitz.open.return_value = mock_doc
            mock_fitz.Matrix = MagicMock()
            
            with patch('src.pipeline.rasterizer.settings') as mock_settings:
                mock_settings.raster_dpi = 300
                from src.pipeline.rasterizer import Rasterizer
                rasterizer = Rasterizer()
                
                # Act
                images = rasterizer.pdf_to_images(sample_pdf_content)
                
                # Assert
                assert isinstance(images, list)
                assert len(images) == 1
                assert isinstance(images[0], Image.Image)
                mock_fitz.open.assert_called_once()
                mock_doc.close.assert_called_once()
    
    def test_pdf_to_images_should_handle_multiple_pages(self, sample_pdf_content):
        """Test that pdf_to_images handles multiple pages."""
        # Arrange
        if 'src.pipeline.rasterizer' in sys.modules:
            del sys.modules['src.pipeline.rasterizer']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.rasterizer.fitz') as mock_fitz:
            mock_doc = MagicMock()
            mock_page = MagicMock()
            mock_pix = MagicMock()
            mock_pix.width = 100
            mock_pix.height = 100
            mock_pix.samples = b'\x00' * (100 * 100 * 3)
            mock_page.get_pixmap.return_value = mock_pix
            mock_doc.__len__.return_value = 3
            mock_doc.__getitem__.return_value = mock_page
            mock_fitz.open.return_value = mock_doc
            mock_fitz.Matrix = MagicMock()
            
            with patch('src.pipeline.rasterizer.settings') as mock_settings:
                mock_settings.raster_dpi = 300
                from src.pipeline.rasterizer import Rasterizer
                rasterizer = Rasterizer()
                
                # Act
                images = rasterizer.pdf_to_images(sample_pdf_content)
                
                # Assert
                assert len(images) == 3
                assert all(isinstance(img, Image.Image) for img in images)
    
    def test_pdf_to_images_should_raise_on_error(self, sample_pdf_content):
        """Test that pdf_to_images raises exception on error."""
        # Arrange
        if 'src.pipeline.rasterizer' in sys.modules:
            del sys.modules['src.pipeline.rasterizer']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.rasterizer.fitz') as mock_fitz:
            mock_fitz.open.side_effect = Exception("PDF error")
            
            with patch('src.pipeline.rasterizer.settings') as mock_settings:
                mock_settings.raster_dpi = 300
                from src.pipeline.rasterizer import Rasterizer
                rasterizer = Rasterizer()
                
                # Act & Assert
                with pytest.raises(Exception, match="PDF error"):
                    rasterizer.pdf_to_images(sample_pdf_content)

