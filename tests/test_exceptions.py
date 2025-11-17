"""
Tests for lastpass.exceptions module
"""

import pytest
from lastpass.exceptions import (
    LastPassException,
    LoginFailedException,
    InvalidSessionException,
    NetworkException,
    DecryptionException,
    AccountNotFoundException,
    InvalidPasswordException,
)


class TestExceptions:
    """Test exception classes"""
    
    def test_lastpass_exception(self):
        """Test base LastPassException"""
        exc = LastPassException("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)
    
    def test_login_failed_exception(self):
        """Test LoginFailedException"""
        exc = LoginFailedException("Invalid credentials")
        assert str(exc) == "Invalid credentials"
        assert isinstance(exc, LastPassException)
    
    def test_invalid_session_exception(self):
        """Test InvalidSessionException"""
        exc = InvalidSessionException("Session expired")
        assert str(exc) == "Session expired"
        assert isinstance(exc, LastPassException)
    
    def test_network_exception(self):
        """Test NetworkException"""
        exc = NetworkException("Connection failed")
        assert str(exc) == "Connection failed"
        assert isinstance(exc, LastPassException)
    
    def test_decryption_exception(self):
        """Test DecryptionException"""
        exc = DecryptionException("Cannot decrypt data")
        assert str(exc) == "Cannot decrypt data"
        assert isinstance(exc, LastPassException)
    
    def test_account_not_found_exception(self):
        """Test AccountNotFoundException"""
        exc = AccountNotFoundException("Account not found")
        assert str(exc) == "Account not found"
        assert isinstance(exc, LastPassException)
    
    def test_invalid_password_exception(self):
        """Test InvalidPasswordException"""
        exc = InvalidPasswordException("Wrong password")
        assert str(exc) == "Wrong password"
        assert isinstance(exc, LastPassException)
    
    def test_exception_raising(self):
        """Test that exceptions can be raised and caught"""
        with pytest.raises(LoginFailedException) as exc_info:
            raise LoginFailedException("Login failed")
        assert "Login failed" in str(exc_info.value)
    
    def test_exception_inheritance(self):
        """Test exception inheritance chain"""
        # All specific exceptions should inherit from LastPassException
        assert issubclass(LoginFailedException, LastPassException)
        assert issubclass(InvalidSessionException, LastPassException)
        assert issubclass(NetworkException, LastPassException)
        assert issubclass(DecryptionException, LastPassException)
        assert issubclass(AccountNotFoundException, LastPassException)
        assert issubclass(InvalidPasswordException, LastPassException)
    
    def test_catch_base_exception(self):
        """Test catching specific exception with base class"""
        with pytest.raises(LastPassException):
            raise LoginFailedException("Test")
        
        with pytest.raises(LastPassException):
            raise NetworkException("Test")
