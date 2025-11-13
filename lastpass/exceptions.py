"""
Exception classes for LastPass Python library
"""


class LastPassException(Exception):
    """Base exception for all LastPass errors"""
    pass


class LoginFailedException(LastPassException):
    """Failed to authenticate with LastPass"""
    pass


class InvalidSessionException(LastPassException):
    """Session is invalid or expired"""
    pass


class NetworkException(LastPassException):
    """Network or HTTP error occurred"""
    pass


class DecryptionException(LastPassException):
    """Failed to decrypt data"""
    pass


class AccountNotFoundException(LastPassException):
    """Account not found in vault"""
    pass


class InvalidPasswordException(LastPassException):
    """Invalid password provided"""
    pass
