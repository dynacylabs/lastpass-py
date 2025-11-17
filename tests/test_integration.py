"""
Integration tests for lastpass-python library

These tests interact with the real LastPass API and require valid credentials.
Run with: pytest --live --username=your@email.com --password=yourpassword

Note: These tests will access your real LastPass vault. Use a test account!
"""

import pytest
import time
from lastpass.client import LastPassClient
from lastpass.exceptions import LoginFailedException, AccountNotFoundException, NetworkException


@pytest.mark.live
class TestLiveLogin:
    """Test login with real API"""
    
    def test_live_login(self, live_credentials, temp_config_dir):
        """Test logging in to real LastPass account"""
        if not live_credentials["username"] or not live_credentials["password"]:
            pytest.skip("No credentials provided")
        
        client = LastPassClient(config_dir=temp_config_dir)
        
        # Try login, handle email verification if needed
        try:
            client.login(
                live_credentials["username"],
                live_credentials["password"],
                otp=live_credentials.get("otp") or None,
            )
        except LoginFailedException as e:
            # Check if it's an email verification error
            if "unifiedloginresult" in str(e) or "verify" in str(e).lower():
                from .conftest import get_otp_message
                pytest.skip(get_otp_message())
            else:
                raise
        
        assert client.is_logged_in()
        assert client.session is not None
        assert client.decryption_key is not None
        
        # Cleanup
        client.logout()
    
    def test_live_login_invalid_credentials(self, temp_config_dir):
        """Test login with invalid credentials"""
        client = LastPassClient(config_dir=temp_config_dir)
        
        with pytest.raises(LoginFailedException):
            client.login("invalid@example.com", "wrongpassword")


@pytest.mark.live
class TestLiveVaultOperations:
    """Test vault operations with real API"""
    
    @pytest.fixture
    def logged_in_client(self, live_credentials, temp_config_dir):
        """Get a logged-in client"""
        if not live_credentials["username"] or not live_credentials["password"]:
            pytest.skip("No credentials provided")
        
        client = LastPassClient(config_dir=temp_config_dir)
        
        # Try login, handle email verification if needed
        try:
            client.login(
                live_credentials["username"],
                live_credentials["password"],
                otp=live_credentials.get("otp") or None,
            )
        except LoginFailedException as e:
            # Check if it's an email verification error
            if "unifiedloginresult" in str(e) or "verify" in str(e).lower():
                from .conftest import get_otp_message
                pytest.skip(get_otp_message())
            else:
                raise
        
        yield client
        
        # Cleanup
        try:
            client.logout()
        except:
            pass
    
    def test_live_get_accounts(self, logged_in_client):
        """Test getting accounts from real vault"""
        accounts = logged_in_client.get_accounts()
        
        assert isinstance(accounts, list)
        # Most accounts will have at least one entry
        # but we can't assume that, so just check type
        print(f"Found {len(accounts)} accounts in vault")
        time.sleep(2)  # Delay to prevent rate limiting
    
    def test_live_get_shares(self, logged_in_client):
        """Test getting shared folders"""
        shares = logged_in_client.get_shares()
        
        assert isinstance(shares, list)
        print(f"Found {len(shares)} shared folders")
        time.sleep(2)  # Delay to prevent rate limiting
    
    def test_live_list_groups(self, logged_in_client):
        """Test listing groups"""
        groups = logged_in_client.list_groups()
        
        assert isinstance(groups, list)
        print(f"Found {len(groups)} groups: {groups}")
        time.sleep(2)  # Delay to prevent rate limiting
    
    def test_live_sync(self, logged_in_client):
        """Test syncing vault"""
        # First sync
        logged_in_client.sync()
        time.sleep(2)  # Delay between syncs
        accounts1 = logged_in_client.get_accounts(sync=False)
        
        # Force sync
        time.sleep(2)  # Delay between syncs
        logged_in_client.sync(force=True)
        accounts2 = logged_in_client.get_accounts(sync=False)
        
        # Should get same accounts
        assert len(accounts1) == len(accounts2)
        time.sleep(3)  # Longer delay to prevent rate limiting
    
@pytest.mark.live
class TestLiveSessionPersistence:
    """Test session save/load with real API"""
    
    def test_live_session_persistence(self, live_credentials, temp_config_dir):
        """Test saving and loading session"""
        if not live_credentials["username"] or not live_credentials["password"]:
            pytest.skip("No credentials provided")
        
        # Login and save session
        client1 = LastPassClient(config_dir=temp_config_dir)
        
        # Try login, handle email verification if needed
        try:
            client1.login(
                live_credentials["username"],
                live_credentials["password"],
                otp=live_credentials.get("otp") or None,
            )
        except LoginFailedException as e:
            # Check if it's an email verification error
            if "unifiedloginresult" in str(e) or "verify" in str(e).lower():
                from .conftest import get_otp_message
                pytest.skip(get_otp_message())
            else:
                raise
        
        session_id1 = client1.session.sessionid
        
        # Create new client and load session
        client2 = LastPassClient(config_dir=temp_config_dir)
        client2.login(
            live_credentials["username"],
            live_credentials["password"],
            force=False,  # Should load existing session
        )
        
        # Should have loaded saved session
        assert client2.is_logged_in()
        
        # Cleanup
        client2.logout()


@pytest.mark.live
class TestLivePasswordGeneration:
    """Test password generation"""
    
    def test_live_generate_password(self):
        """Test password generation works"""
        client = LastPassClient()
        
        # Should work without login
        password = client.generate_password(length=20, symbols=True)
        
        assert len(password) == 20
        assert isinstance(password, str)


# Note: Tests for add/edit/delete operations are not included
# to avoid modifying real vault data during testing.
# Those would need to be tested very carefully on a dedicated test account.
