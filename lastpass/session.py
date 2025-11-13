"""
Session management for LastPass
"""

import json
import os
from pathlib import Path
from typing import Optional
from .cipher import aes_encrypt, aes_decrypt_base64, encrypt_and_base64, decrypt_private_key
from .exceptions import InvalidSessionException


class Session:
    """LastPass session with authentication tokens"""
    
    def __init__(self, uid: str = "", sessionid: str = "", token: str = "", 
                 server: str = "lastpass.com", private_key: str = ""):
        self.uid = uid
        self.sessionid = sessionid
        self.token = token
        self.server = server
        self.private_key = private_key  # PEM format
    
    def is_valid(self) -> bool:
        """Check if session has required credentials"""
        return bool(self.uid and self.sessionid and self.token)
    
    def to_dict(self) -> dict:
        """Convert session to dictionary"""
        return {
            "uid": self.uid,
            "sessionid": self.sessionid,
            "token": self.token,
            "server": self.server,
            "private_key": self.private_key,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create session from dictionary"""
        return cls(
            uid=data.get("uid", ""),
            sessionid=data.get("sessionid", ""),
            token=data.get("token", ""),
            server=data.get("server", "lastpass.com"),
            private_key=data.get("private_key", ""),
        )
    
    def save(self, key: bytes, config_dir: Optional[Path] = None) -> None:
        """Save encrypted session to disk"""
        if config_dir is None:
            config_dir = self._get_config_dir()
        
        config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        session_file = config_dir / "session"
        data = json.dumps(self.to_dict())
        
        # Encrypt session data
        encrypted = encrypt_and_base64(data, key)
        
        # Write to file with secure permissions
        session_file.write_text(encrypted)
        os.chmod(session_file, 0o600)
    
    @classmethod
    def load(cls, key: bytes, config_dir: Optional[Path] = None) -> Optional["Session"]:
        """Load encrypted session from disk"""
        if config_dir is None:
            config_dir = cls._get_config_dir()
        
        session_file = config_dir / "session"
        
        if not session_file.exists():
            return None
        
        try:
            encrypted = session_file.read_text().strip()
            decrypted = aes_decrypt_base64(encrypted, key)
            data = json.loads(decrypted)
            return cls.from_dict(data)
        except Exception:
            # Session file is corrupted or uses different key
            return None
    
    @staticmethod
    def _get_config_dir() -> Path:
        """Get LastPass configuration directory"""
        # Use XDG_CONFIG_HOME if set, otherwise ~/.config
        if "XDG_CONFIG_HOME" in os.environ:
            config_home = Path(os.environ["XDG_CONFIG_HOME"])
        else:
            config_home = Path.home() / ".config"
        
        return config_home / "lpass"
    
    @staticmethod
    def kill(config_dir: Optional[Path] = None) -> None:
        """Delete session file"""
        if config_dir is None:
            config_dir = Session._get_config_dir()
        
        session_file = config_dir / "session"
        
        if session_file.exists():
            session_file.unlink()
