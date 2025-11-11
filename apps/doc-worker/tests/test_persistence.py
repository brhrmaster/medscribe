"""Unit tests for persistence."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
import json
from src.models import DocumentField, BoundingBox


class TestPersistence:
    """Tests for Persistence."""
    
    def test_persistence_should_initialize_with_none_pool(self):
        """Test that Persistence initializes with None connection pool."""
        # Arrange
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        from src.pipeline.persistence import Persistence
        
        # Act
        persistence = Persistence()
        
        # Assert
        assert persistence.conn_pool is None
    
    @pytest.mark.asyncio
    async def test_initialize_should_create_connection_pool(self):
        """Test that initialize creates a connection pool."""
        # Arrange
        mock_pool = AsyncMock()
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.persistence.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.pipeline.persistence import Persistence
            persistence = Persistence()
            
            # Act
            await persistence.initialize()
            
            # Assert
            mock_create_pool.assert_called_once()
            assert persistence.conn_pool == mock_pool
    
    @pytest.mark.asyncio
    async def test_close_should_close_pool(self):
        """Test that close closes the connection pool."""
        # Arrange
        mock_pool = AsyncMock()
        
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.persistence.asyncpg', create=True):
            from src.pipeline.persistence import Persistence
            persistence = Persistence()
            persistence.conn_pool = mock_pool
            
            # Act
            await persistence.close()
            
            # Assert
            mock_pool.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_document_status_should_update_status(self):
        """Test that update_document_status updates document status."""
        # Arrange
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.persistence.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.pipeline.persistence import Persistence
            persistence = Persistence()
            await persistence.initialize()
            
            # Act
            await persistence.update_document_status(
                "doc-id", "PROCESSING", pages=2, processing_time=5.5
            )
            
            # Assert
            mock_conn.execute.assert_called_once()
            call_args = mock_conn.execute.call_args[0]
            assert "UPDATE documents" in call_args[0]
            assert call_args[1] == "PROCESSING"
            assert call_args[3] == 2
            assert call_args[4] == 5.5
    
    @pytest.mark.asyncio
    async def test_save_document_fields_should_insert_fields(self):
        """Test that save_document_fields inserts fields."""
        # Arrange
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_transaction = Mock()
        mock_transaction.__aenter__ = AsyncMock(return_value=None)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)
        mock_conn.transaction = Mock(return_value=mock_transaction)
        mock_conn.execute = AsyncMock()
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        field = DocumentField(
            field_name="patient_name",
            field_value="João Silva",
            confidence=0.95,
            page=1
        )
        
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.persistence.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.pipeline.persistence import Persistence
            persistence = Persistence()
            await persistence.initialize()
            
            # Act
            await persistence.save_document_fields("doc-id", [field])
            
            # Assert
            mock_conn.execute.assert_called_once()
            call_args = mock_conn.execute.call_args[0]
            assert "INSERT INTO document_fields" in call_args[0]
            assert call_args[1] == "doc-id"
            assert call_args[2] == "patient_name"
            assert call_args[3] == "João Silva"
    
    @pytest.mark.asyncio
    async def test_save_document_fields_should_handle_bbox(self):
        """Test that save_document_fields handles bbox."""
        # Arrange
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_transaction = Mock()
        mock_transaction.__aenter__ = AsyncMock(return_value=None)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)
        mock_conn.transaction = Mock(return_value=mock_transaction)
        mock_conn.execute = AsyncMock()
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        bbox = BoundingBox(x=10.0, y=20.0, w=100.0, h=50.0)
        field = DocumentField(
            field_name="patient_name",
            field_value="João Silva",
            confidence=0.95,
            page=1,
            bbox=bbox
        )
        
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.persistence.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.pipeline.persistence import Persistence
            persistence = Persistence()
            await persistence.initialize()
            
            # Act
            await persistence.save_document_fields("doc-id", [field])
            
            # Assert
            call_args = mock_conn.execute.call_args[0]
            # Check that bbox JSON is passed
            assert call_args[6] is not None  # bbox_json parameter
    
    @pytest.mark.asyncio
    async def test_save_document_fields_should_skip_empty_list(self):
        """Test that save_document_fields skips empty list."""
        # Arrange
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.persistence.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.pipeline.persistence import Persistence
            persistence = Persistence()
            await persistence.initialize()
            
            # Act
            await persistence.save_document_fields("doc-id", [])
            
            # Assert
            mock_conn.execute.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_document_exists_should_return_true_when_exists(self):
        """Test that document_exists returns True when document exists."""
        # Arrange
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.fetchrow = AsyncMock(return_value={"exists": True})
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.persistence.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.pipeline.persistence import Persistence
            persistence = Persistence()
            await persistence.initialize()
            
            # Act
            result = await persistence.document_exists("doc-id")
            
            # Assert
            assert result is True
            mock_conn.fetchrow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_document_should_insert_document(self):
        """Test that create_document inserts document."""
        # Arrange
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        if 'src.pipeline.persistence' in sys.modules:
            del sys.modules['src.pipeline.persistence']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.pipeline.persistence.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.pipeline.persistence import Persistence
            persistence = Persistence()
            await persistence.initialize()
            
            # Act
            result = await persistence.create_document(
                "doc-id", "tenant", "object-key", "sha256"
            )
            
            # Assert
            assert result is True
            mock_conn.execute.assert_called_once()
            call_args = mock_conn.execute.call_args[0]
            assert "INSERT INTO documents" in call_args[0]

