"""
Tests for lastpass.session module
"""

import pytest
import json
from pathlib import Path
from lastpass.session import Session


class TestSession:
    """Test Session class"""
    
    def test_session_creation(self):
        """Test creating a Session"""
        session = Session(
            uid="123456",
            sessionid="session_abc",
            token="token_xyz",
            private_key="priv_key_123",
        )
        assert session.uid == "123456"
        assert session.sessionid == "session_abc"
        assert session.token == "token_xyz"
        assert session.private_key == "priv_key_123"
    
    def test_session_default_values(self):
        """Test Session with default values"""
        session = Session()
        assert session.uid == ""
        assert session.sessionid == ""
        assert session.token == ""
        assert session.private_key == ""
    
    def test_session_is_valid(self):
        """Test is_valid() method"""
        # Valid session
        valid_session = Session(uid="123", sessionid="sess", token="tok")
        assert valid_session.is_valid() is True
        
        # Invalid sessions
        assert Session().is_valid() is False
        assert Session(uid="123").is_valid() is False
        assert Session(uid="123", sessionid="sess").is_valid() is False
    
    def test_session_to_dict(self):
        """Test to_dict() method"""
        session = Session(
            uid="123",
            sessionid="sess",
            token="tok",
            private_key="key",
        )
        data = session.to_dict()
        
        assert data["uid"] == "123"
        assert data["sessionid"] == "sess"
        assert data["token"] == "tok"
        assert data["private_key"] == "key"
    
    def test_session_from_dict(self):
        """Test from_dict() class method"""
        data = {
            "uid": "456",
            "sessionid": "session_def",
            "token": "token_uvw",
            "private_key": "priv_789",
        }
        session = Session.from_dict(data)
        
        assert session.uid == "456"
        assert session.sessionid == "session_def"
        assert session.token == "token_uvw"
        assert session.private_key == "priv_789"
    
    def test_session_round_trip_dict(self):
        """Test to_dict() and from_dict() round trip"""
        original = Session(
            uid="999",
            sessionid="sess_test",
            token="tok_test",
            private_key="key_test",
        )
        data = original.to_dict()
        restored = Session.from_dict(data)
        
        assert restored.uid == original.uid
        assert restored.sessionid == original.sessionid
        assert restored.token == original.token
        assert restored.private_key == original.private_key


class TestSessionPersistence:
    """Test Session save/load functionality"""
    
    def test_session_save(self, temp_config_dir, mock_encryption_key):
        """Test saving session to disk"""
        session = Session(
            uid="123",
            sessionid="sess",
            token="tok",
            private_key="key",
        )
        
        session.save(mock_encryption_key, temp_config_dir)
        
        # Check file was created
        session_file = temp_config_dir / "session"
        assert session_file.exists()
        assert session_file.stat().st_size > 0
    
    def test_session_load(self, temp_config_dir, mock_encryption_key):
        """Test loading session from disk"""
        # Save a session
        original = Session(
            uid="456",
            sessionid="test_sess",
            token="test_tok",
            private_key="test_key",
        )
        original.save(mock_encryption_key, temp_config_dir)
        
        # Load it back
        loaded = Session.load(mock_encryption_key, temp_config_dir)
        
        assert loaded is not None
        assert loaded.uid == original.uid
        assert loaded.sessionid == original.sessionid
        assert loaded.token == original.token
        assert loaded.private_key == original.private_key
    
    def test_session_load_nonexistent(self, temp_config_dir, mock_encryption_key):
        """Test loading when session file doesn't exist"""
        loaded = Session.load(mock_encryption_key, temp_config_dir)
        assert loaded is None
    
    def test_session_load_wrong_key(self, temp_config_dir, mock_encryption_key):
        """Test loading with wrong encryption key"""
        # Save with one key
        session = Session(uid="123", sessionid="sess", token="tok")
        session.save(mock_encryption_key, temp_config_dir)
        
        # Try to load with different key
        wrong_key = b"wrongkey000000000000000000000000"
        loaded = Session.load(wrong_key, temp_config_dir)
        
        # Should return None or raise error
        # Implementation may vary
        assert loaded is None or loaded.uid != "123"
    
    def test_session_kill(self, temp_config_dir, mock_encryption_key):
        """Test killing/deleting session"""
        # Save a session
        session = Session(uid="123", sessionid="sess", token="tok")
        session.save(mock_encryption_key, temp_config_dir)
        
        session_file = temp_config_dir / "session"
        assert session_file.exists()
        
        # Kill the session
        Session.kill(temp_config_dir)
        
        # File should be deleted
        assert not session_file.exists()
    
    def test_session_kill_nonexistent(self, temp_config_dir):
        """Test killing when session doesn't exist"""
        # Should not raise error
        Session.kill(temp_config_dir)
        
        session_file = temp_config_dir / "session"
        assert not session_file.exists()
    
    def test_session_save_overwrite(self, temp_config_dir, mock_encryption_key):
        """Test saving overwrites existing session"""
        # Save first session
        session1 = Session(uid="111", sessionid="sess1", token="tok1")
        session1.save(mock_encryption_key, temp_config_dir)
        
        # Save second session
        session2 = Session(uid="222", sessionid="sess2", token="tok2")
        session2.save(mock_encryption_key, temp_config_dir)
        
        # Load should get second session
        loaded = Session.load(mock_encryption_key, temp_config_dir)
        assert loaded.uid == "222"
    
    def test_get_config_dir_default(self):
        """Test getting default config directory"""
        config_dir = Session._get_config_dir()
        assert isinstance(config_dir, Path)
        assert ".lpass" in str(config_dir) or ".config" in str(config_dir)


class TestSessionEdgeCases:
    """Test edge cases for Session"""
    
    def test_session_with_empty_strings(self):
        """Test Session with empty strings"""
        session = Session(uid="", sessionid="", token="")
        assert not session.is_valid()
    
    def test_session_with_unicode(self):
        """Test Session with unicode values"""
        session = Session(
            uid="用户123",
            sessionid="会话_abc",
            token="令牌_xyz",
        )
        assert session.uid == "用户123"
        assert session.is_valid()
    
    def test_session_from_dict_missing_keys(self):
        """Test from_dict with missing keys"""
        # Should use defaults for missing keys
        data = {"uid": "123"}
        session = Session.from_dict(data)
        assert session.uid == "123"
        assert session.sessionid == ""
    
    def test_session_from_dict_extra_keys(self):
        """Test from_dict ignores extra keys"""
        data = {
            "uid": "123",
            "sessionid": "sess",
            "token": "tok",
            "extra_field": "ignored",
        }
        session = Session.from_dict(data)
        assert session.uid == "123"
        assert not hasattr(session, "extra_field")
