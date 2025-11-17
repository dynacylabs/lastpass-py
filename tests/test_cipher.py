"""
Tests for lastpass.cipher module
"""

import pytest
import base64
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA as CryptoRSA
from lastpass.cipher import (
    aes_decrypt,
    aes_decrypt_base64,
    aes_encrypt,
    encrypt_and_base64,
    rsa_decrypt,
    rsa_encrypt,
    decrypt_private_key,
    sha256_hex,
    sha256_base64,
    hex_to_bytes,
)
from lastpass.exceptions import DecryptionException


class TestAESCrypto:
    """Test AES encryption/decryption"""
    
    @pytest.fixture
    def aes_key(self):
        """32-byte AES-256 key"""
        return b"0123456789abcdef0123456789abcdef"
    
    def test_aes_encrypt_decrypt(self, aes_key):
        """Test AES encryption and decryption round trip"""
        plaintext = "Hello, LastPass!"
        encrypted = aes_encrypt(plaintext, aes_key)
        
        # Verify format: '!' + base64(iv) + '|' + base64(ciphertext)
        assert encrypted.startswith(b'!')
        assert b'|' in encrypted
        
        # Decrypt
        decrypted = aes_decrypt(encrypted, aes_key)
        assert decrypted.decode('utf-8') == plaintext
    
    def test_aes_encrypt_empty_string(self, aes_key):
        """Test encrypting empty string"""
        encrypted = aes_encrypt("", aes_key)
        assert encrypted == b''
    
    def test_aes_decrypt_empty_data(self, aes_key):
        """Test decrypting empty data"""
        decrypted = aes_decrypt(b'', aes_key)
        assert decrypted == b''
    
    def test_aes_decrypt_base64(self, aes_key):
        """Test base64 AES decryption"""
        plaintext = "Secret message"
        encrypted = aes_encrypt(plaintext, aes_key)
        encrypted_b64 = base64.b64encode(encrypted).decode('ascii')
        
        decrypted = aes_decrypt_base64(encrypted_b64, aes_key)
        assert decrypted == plaintext
    
    def test_aes_decrypt_base64_empty(self, aes_key):
        """Test base64 decryption with empty string"""
        result = aes_decrypt_base64("", aes_key)
        assert result == ""
    
    def test_encrypt_and_base64(self, aes_key):
        """Test encrypt_and_base64 helper"""
        plaintext = "Test data"
        result = encrypt_and_base64(plaintext, aes_key)
        
        # Should be base64 encoded
        assert isinstance(result, str)
        base64.b64decode(result)  # Should not raise
    
    def test_aes_decrypt_invalid_format(self, aes_key):
        """Test decryption with invalid format"""
        with pytest.raises(DecryptionException):
            aes_decrypt(b'!invalid_data', aes_key)
    
    def test_aes_decrypt_legacy_ecb_mode(self, aes_key):
        """Test decryption of legacy ECB mode data"""
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
        
        # Create ECB encrypted data
        plaintext = b"Legacy data"
        cipher = AES.new(aes_key, AES.MODE_ECB)
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
        
        # Decrypt
        decrypted = aes_decrypt(ciphertext, aes_key)
        assert decrypted == plaintext
    
    def test_aes_unicode_support(self, aes_key):
        """Test AES with unicode characters"""
        plaintext = "Hello 世界 🔒"
        encrypted = aes_encrypt(plaintext, aes_key)
        decrypted = aes_decrypt(encrypted, aes_key)
        assert decrypted.decode('utf-8') == plaintext


class TestRSACrypto:
    """Test RSA encryption/decryption"""
    
    @pytest.fixture
    def rsa_keypair(self):
        """Generate RSA key pair for testing"""
        key = CryptoRSA.generate(2048)
        private_pem = key.export_key().decode('ascii')
        public_pem = key.publickey().export_key().decode('ascii')
        return private_pem, public_pem
    
    def test_rsa_encrypt_decrypt(self, rsa_keypair):
        """Test RSA encryption and decryption"""
        private_key, public_key = rsa_keypair
        plaintext = "Secret message"
        
        # Encrypt with public key
        ciphertext = rsa_encrypt(plaintext, public_key)
        assert isinstance(ciphertext, bytes)
        assert ciphertext != plaintext.encode('utf-8')
        
        # Decrypt with private key
        decrypted = rsa_decrypt(ciphertext, private_key)
        assert decrypted == plaintext
    
    def test_rsa_decrypt_invalid_key(self):
        """Test RSA decryption with invalid key"""
        with pytest.raises(DecryptionException):
            rsa_decrypt(b"encrypted_data", "invalid_key")
    
    def test_rsa_encrypt_invalid_key(self):
        """Test RSA encryption with invalid key"""
        with pytest.raises(DecryptionException):
            rsa_encrypt("plaintext", "invalid_key")


class TestPrivateKeyDecryption:
    """Test private key decryption"""
    
    def test_decrypt_private_key(self):
        """Test decrypting an encrypted private key"""
        decryption_key = b"0123456789abcdef0123456789abcdef"
        plaintext_key = "-----BEGIN RSA PRIVATE KEY-----\nMIICXAIB..."
        
        # Encrypt the key
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
        cipher = AES.new(decryption_key, AES.MODE_ECB)
        encrypted_key = cipher.encrypt(pad(plaintext_key.encode('utf-8'), AES.block_size))
        key_hex = encrypted_key.hex()
        
        # Decrypt
        decrypted = decrypt_private_key(key_hex, decryption_key)
        assert decrypted == plaintext_key
    
    def test_decrypt_private_key_invalid_hex(self):
        """Test decrypting with invalid hex string"""
        decryption_key = b"0123456789abcdef0123456789abcdef"
        with pytest.raises(DecryptionException):
            decrypt_private_key("invalid_hex_zzz", decryption_key)


class TestHashFunctions:
    """Test hash functions"""
    
    def test_sha256_hex(self):
        """Test SHA256 hex output"""
        data = b"test data"
        hash_result = sha256_hex(data)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA256 hex is 64 characters
        # Verify it's valid hex
        int(hash_result, 16)
    
    def test_sha256_hex_consistent(self):
        """Test SHA256 produces consistent results"""
        data = b"consistent data"
        hash1 = sha256_hex(data)
        hash2 = sha256_hex(data)
        assert hash1 == hash2
    
    def test_sha256_base64(self):
        """Test SHA256 base64 output"""
        data = b"test data"
        hash_result = sha256_base64(data)
        
        assert isinstance(hash_result, str)
        # Should be valid base64
        base64.b64decode(hash_result)
    
    def test_sha256_base64_length(self):
        """Test SHA256 base64 length"""
        data = b"any data"
        hash_result = sha256_base64(data)
        # SHA256 is 32 bytes, base64 encoded is 44 characters
        assert len(hash_result) == 44


class TestHexConversion:
    """Test hex conversion utilities"""
    
    def test_hex_to_bytes(self):
        """Test hex string to bytes conversion"""
        hex_str = "48656c6c6f"  # "Hello"
        result = hex_to_bytes(hex_str)
        assert result == b"Hello"
    
    def test_hex_to_bytes_uppercase(self):
        """Test hex conversion with uppercase"""
        hex_str = "48656C6C6F"
        result = hex_to_bytes(hex_str)
        assert result == b"Hello"
    
    def test_hex_to_bytes_invalid(self):
        """Test hex conversion with invalid input"""
        with pytest.raises(DecryptionException):
            hex_to_bytes("invalid_hex_zzz")
    
    def test_hex_to_bytes_empty(self):
        """Test hex conversion with empty string"""
        result = hex_to_bytes("")
        assert result == b""
    
    def test_hex_to_bytes_round_trip(self):
        """Test hex encoding and decoding round trip"""
        original = b"test data 123"
        hex_str = original.hex()
        result = hex_to_bytes(hex_str)
        assert result == original


class TestCryptoEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_aes_wrong_key_length(self):
        """Test AES with wrong key length"""
        # AES-256 requires 32-byte key
        short_key = b"short"
        with pytest.raises(Exception):
            aes_encrypt("test", short_key)
    
    def test_aes_decrypt_corrupted_data(self):
        """Test decrypting corrupted data"""
        key = b"0123456789abcdef0123456789abcdef"
        corrupted = b"!corrupted|data"
        with pytest.raises(DecryptionException):
            aes_decrypt(corrupted, key)
    
    def test_aes_decrypt_wrong_key(self):
        """Test decrypting with wrong key"""
        key1 = b"0123456789abcdef0123456789abcdef"
        key2 = b"fedcba9876543210fedcba9876543210"
        
        plaintext = "secret"
        encrypted = aes_encrypt(plaintext, key1)
        
        # Decrypting with wrong key should not return original plaintext
        decrypted = aes_decrypt(encrypted, key2)
        assert decrypted.decode('utf-8', errors='replace') != plaintext
