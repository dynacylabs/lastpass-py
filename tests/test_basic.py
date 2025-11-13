"""
Basic tests for LastPass Python implementation
"""

import pytest
from lastpass.kdf import kdf_login_key, kdf_decryption_key, derive_keys
from lastpass.cipher import aes_encrypt, aes_decrypt_base64, sha256_hex
from lastpass.models import Account, Field, Share
from lastpass.exceptions import LastPassException, DecryptionException


class TestKDF:
    """Test key derivation functions"""
    
    def test_kdf_login_key(self):
        """Test login key generation"""
        login_key = kdf_login_key("user@example.com", "password", 5000)
        assert isinstance(login_key, str)
        assert len(login_key) == 64  # 32 bytes in hex
    
    def test_kdf_decryption_key(self):
        """Test decryption key generation"""
        dec_key = kdf_decryption_key("user@example.com", "password", 5000)
        assert isinstance(dec_key, bytes)
        assert len(dec_key) == 32  # 256 bits
    
    def test_derive_keys(self):
        """Test deriving both keys at once"""
        login_key, dec_key = derive_keys("user@example.com", "password", 5000)
        assert isinstance(login_key, str)
        assert isinstance(dec_key, bytes)
        assert len(login_key) == 64
        assert len(dec_key) == 32


class TestCipher:
    """Test encryption/decryption"""
    
    def test_aes_encrypt_decrypt(self):
        """Test AES encryption and decryption"""
        key = b"0" * 32  # 256-bit key
        plaintext = "Hello, World!"
        
        # Encrypt
        ciphertext = aes_encrypt(plaintext, key)
        assert ciphertext.startswith(b"!")
        
        # Decrypt
        decrypted = aes_decrypt_base64(ciphertext.decode('ascii'), key)
        assert decrypted == plaintext
    
    def test_sha256(self):
        """Test SHA256 hashing"""
        data = b"test data"
        hash_hex = sha256_hex(data)
        assert isinstance(hash_hex, str)
        assert len(hash_hex) == 64


class TestModels:
    """Test data models"""
    
    def test_account_creation(self):
        """Test creating an account"""
        account = Account(
            id="123",
            name="Test Account",
            username="user",
            password="pass",
            url="https://example.com",
            group="Work",
        )
        
        assert account.id == "123"
        assert account.name == "Test Account"
        assert account.username == "user"
        assert account.password == "pass"
        assert account.fullname == ""  # Not set
    
    def test_account_to_dict(self):
        """Test converting account to dict"""
        account = Account(
            id="123",
            name="Test",
            username="user",
            password="pass",
        )
        
        data = account.to_dict()
        assert data["id"] == "123"
        assert data["name"] == "Test"
        assert data["username"] == "user"
    
    def test_field_creation(self):
        """Test creating a field"""
        field = Field(name="API Key", value="abc123", type="text")
        assert field.name == "API Key"
        assert field.value == "abc123"
    
    def test_account_get_field(self):
        """Test getting field from account"""
        account = Account(id="1", name="Test")
        account.fields = [
            Field(name="Field 1", value="value1"),
            Field(name="Field 2", value="value2"),
        ]
        
        field = account.get_field("Field 1")
        assert field is not None
        assert field.value == "value1"
        
        field = account.get_field("Nonexistent")
        assert field is None
    
    def test_is_secure_note(self):
        """Test secure note detection"""
        account = Account(id="1", name="Note", url="http://sn")
        assert account.is_secure_note()
        
        account2 = Account(id="2", name="Site", url="https://example.com")
        assert not account2.is_secure_note()


class TestExceptions:
    """Test exception handling"""
    
    def test_lastpass_exception(self):
        """Test base exception"""
        with pytest.raises(LastPassException):
            raise LastPassException("Test error")
    
    def test_decryption_exception(self):
        """Test decryption exception"""
        with pytest.raises(DecryptionException):
            raise DecryptionException("Decryption failed")


def test_password_generation():
    """Test password generation"""
    from lastpass.client import LastPassClient
    
    client = LastPassClient()
    
    # Generate password
    password = client.generate_password(length=20, symbols=True)
    assert len(password) == 20
    
    # Generate without symbols
    password2 = client.generate_password(length=16, symbols=False)
    assert len(password2) == 16


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
