"""
Tests for lastpass.blob module
"""

import pytest
import struct
from io import BytesIO
from lastpass.blob import BlobParser, parse_blob
from lastpass.models import Account, Share
from lastpass.cipher import aes_encrypt


class TestBlobParser:
    """Test BlobParser class"""
    
    @pytest.fixture
    def encryption_key(self):
        """Test encryption key"""
        return b"0123456789abcdef0123456789abcdef"
    
    def create_chunk(self, chunk_id: str, data: bytes) -> bytes:
        """Helper to create blob chunk"""
        chunk_id_bytes = chunk_id.encode('ascii')
        size = struct.pack(">I", len(data))
        return chunk_id_bytes + size + data
    
    def create_item(self, data: bytes) -> bytes:
        """Helper to create size-prefixed item"""
        size = struct.pack(">I", len(data))
        return size + data
    
    def test_blob_parser_creation(self, encryption_key):
        """Test creating BlobParser"""
        parser = BlobParser(b"test data", encryption_key)
        assert parser.key == encryption_key
        assert isinstance(parser.accounts, list)
        assert isinstance(parser.shares, list)
    
    def test_read_chunk(self, encryption_key):
        """Test reading chunk from blob"""
        chunk_data = self.create_chunk("TEST", b"chunk_content")
        parser = BlobParser(chunk_data, encryption_key)
        
        chunk_id, data = parser.read_chunk()
        assert chunk_id == "TEST"
        assert data == b"chunk_content"
    
    def test_read_chunk_empty(self, encryption_key):
        """Test reading from empty blob"""
        parser = BlobParser(b"", encryption_key)
        chunk_id, data = parser.read_chunk()
        assert chunk_id == ""
        assert data == b""
    
    def test_read_item(self, encryption_key):
        """Test reading size-prefixed item"""
        item_data = self.create_item(b"test_item")
        stream = BytesIO(item_data)
        
        parser = BlobParser(b"", encryption_key)
        item = parser.read_item(stream)
        assert item == b"test_item"
    
    def test_read_item_empty(self, encryption_key):
        """Test reading item from empty stream"""
        stream = BytesIO(b"")
        parser = BlobParser(b"", encryption_key)
        item = parser.read_item(stream)
        assert item == b""
    
    def test_decrypt_item(self, encryption_key):
        """Test decrypting blob item"""
        plaintext = "secret data"
        encrypted = aes_encrypt(plaintext, encryption_key)
        
        parser = BlobParser(b"", encryption_key)
        decrypted = parser.decrypt_item(encrypted)
        assert decrypted == plaintext
    
    def test_decrypt_item_empty(self, encryption_key):
        """Test decrypting empty item"""
        parser = BlobParser(b"", encryption_key)
        decrypted = parser.decrypt_item(b"")
        assert decrypted == ""
    
    def test_decrypt_item_custom_key(self, encryption_key):
        """Test decrypting with custom key"""
        custom_key = b"fedcba9876543210fedcba9876543210"
        plaintext = "custom encrypted"
        encrypted = aes_encrypt(plaintext, custom_key)
        
        parser = BlobParser(b"", encryption_key)
        decrypted = parser.decrypt_item(encrypted, custom_key)
        assert decrypted == plaintext


class TestParseBlobFunction:
    """Test parse_blob function"""
    
    def test_parse_empty_blob(self):
        """Test parsing empty blob"""
        key = b"0123456789abcdef0123456789abcdef"
        accounts, shares = parse_blob(b"", key)
        
        assert isinstance(accounts, list)
        assert isinstance(shares, list)
        assert len(accounts) == 0
        assert len(shares) == 0
    
    def test_parse_blob_returns_correct_types(self):
        """Test parse_blob returns correct types"""
        key = b"0123456789abcdef0123456789abcdef"
        
        # Create minimal valid blob with ACCT chunk
        chunk_id = b"ACCT"
        size = struct.pack(">I", 100)
        data = b"\x00" * 100  # Dummy data
        blob_data = chunk_id + size + data
        
        accounts, shares = parse_blob(blob_data, key)
        
        assert isinstance(accounts, list)
        assert isinstance(shares, list)


class TestBlobEdgeCases:
    """Test edge cases for blob parsing"""
    
    def test_blob_with_corrupted_data(self):
        """Test parsing corrupted blob data"""
        key = b"0123456789abcdef0123456789abcdef"
        corrupted = b"corrupted_blob_data"
        
        # Should not crash, may return empty lists
        accounts, shares = parse_blob(corrupted, key)
        assert isinstance(accounts, list)
        assert isinstance(shares, list)
    
    def test_blob_with_partial_chunk(self):
        """Test parsing blob with incomplete chunk"""
        key = b"0123456789abcdef0123456789abcdef"
        
        # Create incomplete chunk (missing data)
        chunk_id = b"ACCT"
        size = struct.pack(">I", 1000)  # Says 1000 bytes
        data = b"\x00" * 10  # But only 10 bytes
        partial_blob = chunk_id + size + data
        
        accounts, shares = parse_blob(partial_blob, key)
        assert isinstance(accounts, list)
        assert isinstance(shares, list)
    
    def test_blob_with_unknown_chunks(self):
        """Test parsing blob with unknown chunk types"""
        key = b"0123456789abcdef0123456789abcdef"
        
        # Create chunk with unknown ID
        chunk_id = b"UNKN"
        size = struct.pack(">I", 10)
        data = b"x" * 10
        unknown_blob = chunk_id + size + data
        
        # Should handle gracefully
        accounts, shares = parse_blob(unknown_blob, key)
        assert isinstance(accounts, list)
        assert isinstance(shares, list)
    
    def test_blob_parser_multiple_chunks(self):
        """Test parsing blob with multiple chunks"""
        key = b"0123456789abcdef0123456789abcdef"
        
        def create_chunk(chunk_id: str, data: bytes) -> bytes:
            chunk_id_bytes = chunk_id.encode('ascii')
            size = struct.pack(">I", len(data))
            return chunk_id_bytes + size + data
        
        # Create multiple chunks
        chunk1 = create_chunk("TST1", b"data1")
        chunk2 = create_chunk("TST2", b"data2")
        blob_data = chunk1 + chunk2
        
        parser = BlobParser(blob_data, key)
        
        # Read both chunks
        id1, data1 = parser.read_chunk()
        id2, data2 = parser.read_chunk()
        
        assert id1 == "TST1"
        assert data1 == b"data1"
        assert id2 == "TST2"
        assert data2 == b"data2"


class TestBlobIntegration:
    """Integration tests for blob parsing"""
    
    def test_parse_blob_function(self):
        """Test the main parse_blob function"""
        key = b"0123456789abcdef0123456789abcdef"
        blob_data = b""  # Empty blob for now
        
        accounts, shares = parse_blob(blob_data, key)
        
        assert isinstance(accounts, list)
        assert isinstance(shares, list)
        # All accounts should be Account objects
        for account in accounts:
            assert isinstance(account, Account)
        # All shares should be Share objects
        for share in shares:
            assert isinstance(share, Share)
