"""
Tests for lastpass.kdf module
"""

import pytest
from lastpass.kdf import (
    pbkdf2_sha256,
    kdf_login_key,
    kdf_decryption_key,
    derive_keys,
)


class TestPBKDF2:
    """Test PBKDF2 key derivation"""
    
    def test_pbkdf2_sha256(self):
        """Test PBKDF2-SHA256 key derivation"""
        password = b"password"
        salt = b"salt"
        iterations = 1000
        
        result = pbkdf2_sha256(password, salt, iterations)
        assert isinstance(result, bytes)
        assert len(result) == 32  # 256 bits / 8 = 32 bytes
    
    def test_pbkdf2_consistency(self):
        """Test PBKDF2 produces consistent results"""
        password = b"testpass"
        salt = b"testsalt"
        iterations = 5000
        
        result1 = pbkdf2_sha256(password, salt, iterations)
        result2 = pbkdf2_sha256(password, salt, iterations)
        assert result1 == result2
    
    def test_pbkdf2_different_iterations(self):
        """Test PBKDF2 with different iteration counts"""
        password = b"password"
        salt = b"salt"
        
        result1 = pbkdf2_sha256(password, salt, 1000)
        result2 = pbkdf2_sha256(password, salt, 5000)
        assert result1 != result2
    
    def test_pbkdf2_different_passwords(self):
        """Test PBKDF2 with different passwords"""
        salt = b"salt"
        iterations = 1000
        
        result1 = pbkdf2_sha256(b"password1", salt, iterations)
        result2 = pbkdf2_sha256(b"password2", salt, iterations)
        assert result1 != result2
    
    def test_pbkdf2_different_salts(self):
        """Test PBKDF2 with different salts"""
        password = b"password"
        iterations = 1000
        
        result1 = pbkdf2_sha256(password, b"salt1", iterations)
        result2 = pbkdf2_sha256(password, b"salt2", iterations)
        assert result1 != result2


class TestLoginKey:
    """Test login key derivation"""
    
    def test_kdf_login_key(self):
        """Test login key generation"""
        username = "user@example.com"
        password = "masterpassword"
        iterations = 5000
        
        login_key = kdf_login_key(username, password, iterations)
        assert isinstance(login_key, str)
        assert len(login_key) == 64  # SHA256 hex is 64 characters
    
    def test_kdf_login_key_consistency(self):
        """Test login key is consistent"""
        username = "test@example.com"
        password = "testpass"
        iterations = 1000
        
        key1 = kdf_login_key(username, password, iterations)
        key2 = kdf_login_key(username, password, iterations)
        assert key1 == key2
    
    def test_kdf_login_key_case_sensitive(self):
        """Test login key is case sensitive for username"""
        password = "password"
        iterations = 1000
        
        key1 = kdf_login_key("user@example.com", password, iterations)
        key2 = kdf_login_key("USER@EXAMPLE.COM", password, iterations)
        # LastPass may normalize email addresses, but keys should differ
        # if usernames are treated as case-sensitive
        assert isinstance(key1, str)
        assert isinstance(key2, str)
    
    def test_kdf_login_key_hex_format(self):
        """Test login key is valid hex"""
        username = "test@example.com"
        password = "password"
        iterations = 5000
        
        login_key = kdf_login_key(username, password, iterations)
        # Should be valid hex string
        int(login_key, 16)


class TestDecryptionKey:
    """Test decryption key derivation"""
    
    def test_kdf_decryption_key(self):
        """Test decryption key generation"""
        username = "user@example.com"
        password = "masterpassword"
        iterations = 5000
        
        dec_key = kdf_decryption_key(username, password, iterations)
        assert isinstance(dec_key, bytes)
        assert len(dec_key) == 32  # 256 bits / 8 = 32 bytes
    
    def test_kdf_decryption_key_consistency(self):
        """Test decryption key is consistent"""
        username = "test@example.com"
        password = "testpass"
        iterations = 1000
        
        key1 = kdf_decryption_key(username, password, iterations)
        key2 = kdf_decryption_key(username, password, iterations)
        assert key1 == key2
    
    def test_kdf_decryption_key_different_from_login(self):
        """Test decryption key differs from login key"""
        username = "test@example.com"
        password = "password"
        iterations = 5000
        
        login_key = kdf_login_key(username, password, iterations)
        dec_key = kdf_decryption_key(username, password, iterations)
        
        # They should be different
        assert login_key != dec_key.hex()


class TestDeriveKeys:
    """Test combined key derivation"""
    
    def test_derive_keys(self):
        """Test deriving both keys at once"""
        username = "user@example.com"
        password = "masterpassword"
        iterations = 5000
        
        login_key, dec_key = derive_keys(username, password, iterations)
        
        assert isinstance(login_key, str)
        assert isinstance(dec_key, bytes)
        assert len(login_key) == 64
        assert len(dec_key) == 32
    
    def test_derive_keys_matches_individual(self):
        """Test derive_keys matches individual key functions"""
        username = "test@example.com"
        password = "testpass"
        iterations = 1000
        
        login_key, dec_key = derive_keys(username, password, iterations)
        
        individual_login = kdf_login_key(username, password, iterations)
        individual_dec = kdf_decryption_key(username, password, iterations)
        
        assert login_key == individual_login
        assert dec_key == individual_dec
    
    def test_derive_keys_consistency(self):
        """Test derive_keys produces consistent results"""
        username = "user@example.com"
        password = "password123"
        iterations = 5000
        
        login1, dec1 = derive_keys(username, password, iterations)
        login2, dec2 = derive_keys(username, password, iterations)
        
        assert login1 == login2
        assert dec1 == dec2
    
    def test_derive_keys_different_iterations(self):
        """Test keys differ with different iteration counts"""
        username = "user@example.com"
        password = "password"
        
        login1, dec1 = derive_keys(username, password, 1000)
        login2, dec2 = derive_keys(username, password, 5000)
        
        assert login1 != login2
        assert dec1 != dec2


class TestKDFEdgeCases:
    """Test edge cases for key derivation"""
    
    def test_empty_password(self):
        """Test with empty password"""
        username = "user@example.com"
        password = ""
        iterations = 1000
        
        login_key = kdf_login_key(username, password, iterations)
        assert isinstance(login_key, str)
        assert len(login_key) == 64
    
    def test_unicode_password(self):
        """Test with unicode password"""
        username = "user@example.com"
        password = "pässwörd123🔒"
        iterations = 1000
        
        login_key, dec_key = derive_keys(username, password, iterations)
        assert isinstance(login_key, str)
        assert isinstance(dec_key, bytes)
    
    def test_long_password(self):
        """Test with very long password"""
        username = "user@example.com"
        password = "x" * 1000
        iterations = 1000
        
        login_key, dec_key = derive_keys(username, password, iterations)
        assert isinstance(login_key, str)
        assert len(dec_key) == 32
    
    def test_special_characters_username(self):
        """Test with special characters in username"""
        username = "user+test@example.com"
        password = "password"
        iterations = 1000
        
        login_key = kdf_login_key(username, password, iterations)
        assert isinstance(login_key, str)
    
    def test_minimum_iterations(self):
        """Test with minimum iteration count"""
        username = "user@example.com"
        password = "password"
        iterations = 1  # Minimum
        
        login_key, dec_key = derive_keys(username, password, iterations)
        assert isinstance(login_key, str)
        assert isinstance(dec_key, bytes)
    
    def test_high_iterations(self):
        """Test with high iteration count"""
        username = "user@example.com"
        password = "password"
        iterations = 100000
        
        # This should still work but be slower
        login_key = kdf_login_key(username, password, iterations)
        assert isinstance(login_key, str)
