"""Unit tests for DbClient."""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys


class TestDbClient:
    """Tests for DbClient."""
    
    def test_db_client_should_initialize_with_none_pool(self):
        """Test that DbClient initializes with None connection pool."""
        # Arrange - reload module
        if 'src.db_client' in sys.modules:
            del sys.modules['src.db_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        from src.db_client import DbClient
        
        # Act
        client = DbClient()
        
        # Assert
        assert client.conn_pool is None
    
    @pytest.mark.asyncio
    async def test_initialize_should_create_connection_pool(self):
        """Test that initialize creates a connection pool."""
        # Arrange
        mock_pool = AsyncMock()
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        if 'src.db_client' in sys.modules:
            del sys.modules['src.db_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.db_client.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.db_client import DbClient
            client = DbClient()
            
            # Act
            await client.initialize()
            
            # Assert
            mock_create_pool.assert_called_once()
            call_args = mock_create_pool.call_args[0]
            assert call_args[0] == 'postgresql://test:test@localhost:5432/testdb'
            assert client.conn_pool == mock_pool
    
    @pytest.mark.asyncio
    async def test_initialize_should_raise_on_error(self):
        """Test that initialize raises exception on error."""
        # Arrange
        mock_create_pool = AsyncMock(side_effect=Exception("Connection failed"))
        
        if 'src.db_client' in sys.modules:
            del sys.modules['src.db_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.db_client.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.db_client import DbClient
            client = DbClient()
            
            # Act & Assert
            with pytest.raises(Exception, match="Connection failed"):
                await client.initialize()
    
    @pytest.mark.asyncio
    async def test_close_should_close_pool(self):
        """Test that close closes the connection pool."""
        # Arrange
        if 'src.db_client' in sys.modules:
            del sys.modules['src.db_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        from src.db_client import DbClient
        client = DbClient()
        mock_pool = AsyncMock()
        client.conn_pool = mock_pool
        
        # Act
        await client.close()
        
        # Assert
        mock_pool.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_should_handle_none_pool(self):
        """Test that close handles None pool gracefully."""
        # Arrange
        if 'src.db_client' in sys.modules:
            del sys.modules['src.db_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        from src.db_client import DbClient
        client = DbClient()
        client.conn_pool = None
        
        # Act & Assert (should not raise)
        await client.close()
    
    @pytest.mark.asyncio
    async def test_create_document_should_insert_successfully(self):
        """Test successful document creation."""
        # Arrange
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock(return_value="INSERT 0 1")
        # acquire() returns an async context manager, not a coroutine
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        if 'src.db_client' in sys.modules:
            del sys.modules['src.db_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.db_client.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.db_client import DbClient
            client = DbClient()
            await client.initialize()
            
            document_id = "123e4567-e89b-12d3-a456-426614174000"
            tenant = "test-tenant"
            object_key = "test-tenant/test-doc.pdf"
            sha256 = "abc123def456"
            
            # Act
            result = await client.create_document(document_id, tenant, object_key, sha256)
            
            # Assert
            assert result is True
            mock_conn.execute.assert_called_once()
            call_args = mock_conn.execute.call_args[0]
            assert "INSERT INTO documents" in call_args[0]
            assert call_args[1] == document_id
            assert call_args[2] == tenant
            assert call_args[3] == object_key
            assert call_args[4] == sha256
    
    @pytest.mark.asyncio
    async def test_create_document_should_handle_existing_document(self):
        """Test that create_document handles existing document (ON CONFLICT)."""
        # Arrange
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        # "INSERT 0 0" means no row was inserted (already exists)
        mock_conn.execute = AsyncMock(return_value="INSERT 0 0")
        # acquire() returns an async context manager, not a coroutine
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        if 'src.db_client' in sys.modules:
            del sys.modules['src.db_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.db_client.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.db_client import DbClient
            client = DbClient()
            await client.initialize()
            
            document_id = "existing-doc-id"
            tenant = "test-tenant"
            object_key = "test-tenant/existing-doc.pdf"
            sha256 = "abc123def456"
            
            # Act
            result = await client.create_document(document_id, tenant, object_key, sha256)
            
            # Assert
            assert result is True  # Should return True even if document already exists
    
    @pytest.mark.asyncio
    async def test_create_document_should_return_false_on_error(self):
        """Test that create_document returns False on error."""
        # Arrange
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock(side_effect=Exception("Database error"))
        # acquire() returns an async context manager, not a coroutine
        mock_pool.acquire = Mock(return_value=mock_conn)
        mock_create_pool = AsyncMock(return_value=mock_pool)
        
        if 'src.db_client' in sys.modules:
            del sys.modules['src.db_client']
        if 'src.settings' in sys.modules:
            del sys.modules['src.settings']
        
        with patch('src.db_client.asyncpg', create=True) as mock_asyncpg:
            mock_asyncpg.create_pool = mock_create_pool
            from src.db_client import DbClient
            client = DbClient()
            await client.initialize()
            
            document_id = "test-doc-id"
            tenant = "test-tenant"
            object_key = "test-tenant/test-doc.pdf"
            sha256 = "abc123def456"
            
            # Act
            result = await client.create_document(document_id, tenant, object_key, sha256)
            
            # Assert
            assert result is False
