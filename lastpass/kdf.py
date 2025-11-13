"""
Key Derivation Functions (KDF) for LastPass encryption
"""

import hashlib
from typing import Tuple


KDF_HASH_LEN = 32  # SHA256 length


def pbkdf2_sha256(password: bytes, salt: bytes, iterations: int) -> bytes:
    """PBKDF2-HMAC-SHA256 key derivation"""
    return hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=KDF_HASH_LEN)


def kdf_login_key(username: str, password: str, iterations: int) -> str:
    """
    Generate the login key hash (hex-encoded)
    This is sent to the server for authentication
    """
    # First iteration uses username as salt
    key = pbkdf2_sha256(password.encode('utf-8'), username.encode('utf-8'), iterations)
    
    # Second iteration with password as salt
    key = pbkdf2_sha256(key, password.encode('utf-8'), 1)
    
    return key.hex()


def kdf_decryption_key(username: str, password: str, iterations: int) -> bytes:
    """
    Generate the decryption key (binary)
    This is used to decrypt vault data locally
    """
    return pbkdf2_sha256(password.encode('utf-8'), username.encode('utf-8'), iterations)


def derive_keys(username: str, password: str, iterations: int) -> Tuple[str, bytes]:
    """
    Derive both login key and decryption key
    Returns: (login_key_hex, decryption_key_bytes)
    """
    login_key = kdf_login_key(username, password, iterations)
    decryption_key = kdf_decryption_key(username, password, iterations)
    return login_key, decryption_key
